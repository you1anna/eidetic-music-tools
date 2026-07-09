"""Safe, human-gated cleanup planning from a saved drum-role audit."""

from __future__ import annotations

import csv
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


SOURCE_ROLE_ORDER = ("KICKS", "CLAP-SNARE", "HATS-CYM", "PERC")
VALID_DESTINATIONS = frozenset(
    {"KICKS", "CLAP-SNARE", "HATS-CYM", "PERC", "BASS", "REVIEW"}
)
AUDIT_FIELDS = frozenset(
    {
        "path",
        "current_role",
        "authoritative",
        "top_class",
        "top_prob",
        "kick_prob",
        "suggested_role",
        "agree",
        "band",
        "note",
    }
)


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    path: Path
    current_role: str
    suggested_role: str
    top_class: str
    top_prob: float

    @property
    def route(self) -> tuple[str, str]:
        return self.current_role, self.suggested_role

    @property
    def source_group(self) -> str:
        parts = self.path.parts
        return parts[2] if len(parts) > 3 else "_root"


def _candidate_id(path: str, current_role: str, suggested_role: str) -> str:
    value = f"{path}\0{current_role}\0{suggested_role}".encode()
    return hashlib.sha256(value).hexdigest()[:12]


def read_trust_mismatches(path: Path) -> list[Candidate]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        missing = AUDIT_FIELDS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"audit missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)

    candidates: list[Candidate] = []
    for row in rows:
        if not (
            row["authoritative"] == "yes"
            and row["agree"] == "no"
            and row["band"] == "trust"
        ):
            continue
        current = row["current_role"]
        suggested = row["suggested_role"]
        rel = Path(row["path"])
        if (
            rel.parts[:2] != ("CURATED", current)
            or rel.is_absolute()
            or ".." in rel.parts
        ):
            raise ValueError(f"candidate outside current CURATED role: {rel}")
        if current not in SOURCE_ROLE_ORDER:
            raise ValueError(f"unsupported source role: {current}")
        if suggested not in VALID_DESTINATIONS:
            raise ValueError(f"unsupported suggested role: {suggested}")
        candidates.append(
            Candidate(
                candidate_id=_candidate_id(row["path"], current, suggested),
                path=rel,
                current_role=current,
                suggested_role=suggested,
                top_class=row["top_class"],
                top_prob=float(row["top_prob"]),
            )
        )
    return sorted(
        candidates,
        key=lambda item: (
            SOURCE_ROLE_ORDER.index(item.current_role),
            item.suggested_role,
            item.path.as_posix(),
        ),
    )


def group_routes(
    candidates: list[Candidate],
) -> dict[tuple[str, str], list[Candidate]]:
    grouped: dict[tuple[str, str], list[Candidate]] = {}
    for item in candidates:
        grouped.setdefault(item.route, []).append(item)
    return dict(
        sorted(
            grouped.items(),
            key=lambda item: (
                SOURCE_ROLE_ORDER.index(item[0][0]),
                item[0][1],
            ),
        )
    )


def select_calibration(
    candidates: list[Candidate],
    size: int = 10,
) -> list[Candidate]:
    if size < 1:
        raise ValueError("calibration size must be positive")
    ordered = sorted(candidates, key=lambda item: item.path.as_posix())
    if len(ordered) <= size:
        return ordered

    selected = [
        min(ordered, key=lambda item: (item.top_prob, item.path.as_posix()))
    ]
    remaining = [item for item in ordered if item != selected[0]]
    while len(selected) < size:
        groups = {item.source_group for item in selected}

        def rank(item: Candidate) -> tuple[int, float, str]:
            confidence_distance = min(
                abs(item.top_prob - chosen.top_prob) for chosen in selected
            )
            return (
                -int(item.source_group not in groups),
                -confidence_distance,
                item.path.as_posix(),
            )

        chosen = min(remaining, key=rank)
        selected.append(chosen)
        remaining.remove(chosen)
    return sorted(selected, key=lambda item: item.path.as_posix())


def _digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def snapshot_audit(source: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline = output_dir / "role-audit-baseline.tsv"
    source_digest = _digest(source)
    if baseline.exists():
        if _digest(baseline) != source_digest:
            raise ValueError("baseline already exists with different content")
    else:
        shutil.copyfile(source, baseline)
        baseline.chmod(0o444)
    (output_dir / "role-audit-baseline.sha256").write_text(
        f"{source_digest}  {baseline.name}\n",
        encoding="utf-8",
    )
    return baseline


def _route_slug(route: tuple[str, str]) -> str:
    return f"{route[0].lower()}--{route[1].lower()}"


def _write_candidates(path: Path, candidates: list[Candidate]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(
            [
                "candidate_id",
                "path",
                "current_role",
                "suggested_role",
                "top_class",
                "top_prob",
            ]
        )
        for item in candidates:
            writer.writerow(
                [
                    item.candidate_id,
                    item.path.as_posix(),
                    item.current_role,
                    item.suggested_role,
                    item.top_class,
                    f"{item.top_prob:.3f}",
                ]
            )


def write_prepare_artifacts(
    audit_path: Path,
    root: Path,
    output_dir: Path,
) -> dict[tuple[str, str], Path]:
    baseline = snapshot_audit(audit_path, output_dir)
    routes = group_routes(read_trust_mismatches(baseline))
    result: dict[tuple[str, str], Path] = {}
    route_rows: list[list[str]] = []
    audition_root = output_dir / "audition"
    audition_root.mkdir(parents=True, exist_ok=True)

    for route, candidates in routes.items():
        route_dir = audition_root / _route_slug(route)
        route_dir.mkdir(parents=True, exist_ok=True)
        calibration = select_calibration(candidates)
        _write_candidates(route_dir / "candidates.tsv", candidates)

        with (route_dir / "labels.tsv").open(
            "w",
            encoding="utf-8",
            newline="",
        ) as fh:
            writer = csv.writer(fh, delimiter="\t")
            writer.writerow(
                [
                    "candidate_id",
                    "path",
                    "current_role",
                    "suggested_role",
                    "top_prob",
                    "decision",
                    "notes",
                ]
            )
            for item in calibration:
                writer.writerow(
                    [
                        item.candidate_id,
                        item.path.as_posix(),
                        item.current_role,
                        item.suggested_role,
                        f"{item.top_prob:.3f}",
                        "",
                        "",
                    ]
                )

        playlist = ["#EXTM3U", *(str(root / item.path) for item in calibration)]
        (route_dir / "audition.m3u8").write_text(
            "\n".join(playlist) + "\n",
            encoding="utf-8",
        )

        checklist = [
            f"# Audition: {route[0]} → {route[1]}",
            "",
            f"Candidates: {len(candidates)}",
            f"Calibration files: {len(calibration)}",
            "",
            "Mark each item as move, keep, or unsure in labels.tsv.",
            "",
        ]
        checklist.extend(
            f"- [ ] `{root / item.path}` — confidence {item.top_prob:.3f} — "
            f"`{item.candidate_id}`"
            for item in calibration
        )
        (route_dir / "checklist.md").write_text(
            "\n".join(checklist) + "\n",
            encoding="utf-8",
        )
        route_rows.append(
            [
                route[0],
                route[1],
                _route_slug(route),
                str(len(candidates)),
                str(len(calibration)),
            ]
        )
        result[route] = route_dir

    with (output_dir / "routes.tsv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(
            [
                "current_role",
                "suggested_role",
                "route",
                "candidates",
                "calibration",
            ]
        )
        writer.writerows(route_rows)
    return result
