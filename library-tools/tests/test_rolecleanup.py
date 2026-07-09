from __future__ import annotations

import csv
from pathlib import Path

import pytest

from librarytools import rolecleanup


FIELDS = [
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
]


def _write_audit(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(FIELDS)
        writer.writerows(rows)


def _row(
    path: str,
    current: str,
    suggested: str,
    probability: str,
    *,
    authoritative: str = "yes",
    agree: str = "no",
    band: str = "trust",
) -> list[str]:
    return [
        path,
        current,
        authoritative,
        "snr",
        probability,
        "0.001",
        suggested,
        agree,
        band,
        "",
    ]


def test_read_trust_mismatches_filters_every_non_candidate(tmp_path: Path) -> None:
    audit = tmp_path / "audit.tsv"
    _write_audit(
        audit,
        [
            _row("CURATED/KICKS/a.wav", "KICKS", "CLAP-SNARE", "0.91"),
            _row(
                "CURATED/KICKS/b.wav",
                "KICKS",
                "CLAP-SNARE",
                "0.91",
                band="review",
            ),
            _row(
                "CURATED/KICKS/c.wav",
                "KICKS",
                "KICKS",
                "0.99",
                agree="yes",
            ),
            _row(
                "CURATED/BASS/d.wav",
                "BASS",
                "KICKS",
                "0.99",
                authoritative="",
                agree="",
                band="",
            ),
        ],
    )

    candidates = rolecleanup.read_trust_mismatches(audit)

    assert [(item.path.as_posix(), item.route) for item in candidates] == [
        ("CURATED/KICKS/a.wav", ("KICKS", "CLAP-SNARE")),
    ]
    assert len(candidates[0].candidate_id) == 12


def test_read_trust_mismatches_rejects_wrong_curated_prefix(
    tmp_path: Path,
) -> None:
    audit = tmp_path / "audit.tsv"
    _write_audit(audit, [_row("PACKS/a.wav", "KICKS", "PERC", "0.95")])

    with pytest.raises(ValueError, match="outside current CURATED role"):
        rolecleanup.read_trust_mismatches(audit)


def test_group_routes_uses_fixed_source_role_order(tmp_path: Path) -> None:
    audit = tmp_path / "audit.tsv"
    _write_audit(
        audit,
        [
            _row("CURATED/PERC/p.wav", "PERC", "KICKS", "0.94"),
            _row("CURATED/KICKS/k.wav", "KICKS", "PERC", "0.93"),
            _row("CURATED/HATS-CYM/h.wav", "HATS-CYM", "PERC", "0.92"),
        ],
    )

    routes = rolecleanup.group_routes(rolecleanup.read_trust_mismatches(audit))

    assert list(routes) == [
        ("KICKS", "PERC"),
        ("HATS-CYM", "PERC"),
        ("PERC", "KICKS"),
    ]


def test_select_calibration_is_stable_and_spreads_sources_and_confidence(
    tmp_path: Path,
) -> None:
    audit = tmp_path / "audit.tsv"
    rows = [
        _row(
            f"CURATED/KICKS/pack-{index % 4}/item-{index:02}.wav",
            "KICKS",
            "PERC",
            f"0.{80 + index:02}",
        )
        for index in range(20)
    ]
    _write_audit(audit, rows)
    candidates = rolecleanup.read_trust_mismatches(audit)

    first = rolecleanup.select_calibration(candidates)
    second = rolecleanup.select_calibration(list(reversed(candidates)))

    assert [item.candidate_id for item in first] == [
        item.candidate_id for item in second
    ]
    assert len(first) == 10
    assert len({item.source_group for item in first}) == 4
    assert min(item.top_prob for item in first) == 0.80
    assert max(item.top_prob for item in first) >= 0.98


def test_select_calibration_returns_every_small_route(tmp_path: Path) -> None:
    audit = tmp_path / "audit.tsv"
    _write_audit(
        audit,
        [
            _row(
                "CURATED/CLAP-SNARE/a.wav",
                "CLAP-SNARE",
                "PERC",
                "0.81",
            ),
            _row(
                "CURATED/CLAP-SNARE/b.wav",
                "CLAP-SNARE",
                "PERC",
                "0.99",
            ),
        ],
    )
    candidates = rolecleanup.read_trust_mismatches(audit)

    assert rolecleanup.select_calibration(candidates) == sorted(
        candidates,
        key=lambda item: item.path.as_posix(),
    )


def test_snapshot_audit_is_repeatable_but_refuses_changed_source(
    tmp_path: Path,
) -> None:
    source = tmp_path / "role-audit-latest.tsv"
    source.write_text("header\nfirst\n", encoding="utf-8")
    output = tmp_path / "run"

    baseline = rolecleanup.snapshot_audit(source, output)

    assert baseline.name == "role-audit-baseline.tsv"
    assert baseline.read_text(encoding="utf-8") == "header\nfirst\n"
    assert (output / "role-audit-baseline.sha256").read_text().strip()
    assert rolecleanup.snapshot_audit(source, output) == baseline

    source.write_text("header\nchanged\n", encoding="utf-8")
    with pytest.raises(
        ValueError,
        match="baseline already exists with different content",
    ):
        rolecleanup.snapshot_audit(source, output)


def test_write_prepare_artifacts_creates_route_checklist_playlist_and_labels(
    tmp_path: Path,
) -> None:
    root = tmp_path / "SAMPLES"
    source = root / "CURATED" / "KICKS" / "pack" / "a.wav"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"audio")
    audit = tmp_path / "role-audit.tsv"
    _write_audit(
        audit,
        [
            _row(
                "CURATED/KICKS/pack/a.wav",
                "KICKS",
                "CLAP-SNARE",
                "0.91",
            ),
        ],
    )
    output = tmp_path / "run"

    routes = rolecleanup.write_prepare_artifacts(audit, root, output)

    route_dir = routes[("KICKS", "CLAP-SNARE")]
    assert (route_dir / "candidates.tsv").is_file()
    assert (
        route_dir / "checklist.md"
    ).read_text(encoding="utf-8").count("- [ ]") == 1
    assert (route_dir / "audition.m3u8").read_text(
        encoding="utf-8"
    ).splitlines() == [
        "#EXTM3U",
        str(source),
    ]
    labels = (route_dir / "labels.tsv").read_text(
        encoding="utf-8"
    ).splitlines()
    assert labels[0].split("\t")[-2:] == ["decision", "notes"]
    assert labels[1].split("\t")[-2:] == ["", ""]
    assert (output / "routes.tsv").read_text(
        encoding="utf-8"
    ).splitlines()[1].endswith("\t1\t1")


def test_prepare_cli_reports_candidate_and_route_counts(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from librarytools import rolecleanup_cli

    root = tmp_path / "SAMPLES"
    root.mkdir()
    audit = tmp_path / "role-audit.tsv"
    _write_audit(
        audit,
        [_row("CURATED/KICKS/a.wav", "KICKS", "PERC", "0.91")],
    )
    output = tmp_path / "run"

    result = rolecleanup_cli.main(
        [
            "prepare",
            "--audit",
            str(audit),
            "--root",
            str(root),
            "--output-dir",
            str(output),
        ]
    )

    assert result == 0
    assert capsys.readouterr().out.splitlines()[:2] == [
        "[MANIFEST-ONLY] role cleanup: 1 candidates",
        "  routes: 1",
    ]
