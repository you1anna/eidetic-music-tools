"""Manifest parsing + export orchestration.

A manifest (manifests/<device>.txt) is a plain text file. Each non-blank,
non-`#` line is one entry, resolved relative to SAMPLES_ROOT (absolute paths
also accepted). Entries may be:

    KICKS/Goldbaby-Super-Analog-909/kick-01.wav        # a single file
    DRUM-LOOPS/Riemann-Tribal-Techno-1/*.wav           # a glob
    PERC/conga.wav => conga-hi                          # rename the output base

Output lands in EXPORT_ROOT/<DEVICE>/<normalised-name>.wav and is idempotent:
existing outputs are skipped unless force=True.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .config import EXPORT_ROOT, SAMPLES_ROOT, SOURCE_EXTS, DeviceSpec
from .convert import convert_file
from . import naming


@dataclass
class Item:
    """One resolved source->output pair plus any warnings."""

    src: Path
    out_name: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class Plan:
    """The full resolved export plan for a device."""

    spec: DeviceSpec
    items: list[Item]
    missing: list[str]  # manifest entries that matched nothing


def parse_manifest(path: Path) -> list[tuple[str, str | None]]:
    """Return (pattern, rename_base|None) tuples from a manifest file."""
    if not path.exists():
        return []
    entries: list[tuple[str, str | None]] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=>" in line:
            pattern, _, rename = line.partition("=>")
            entries.append((pattern.strip(), rename.strip() or None))
        else:
            entries.append((line, None))
    return entries


def _resolve_pattern(pattern: str) -> list[Path]:
    """Resolve a manifest pattern to concrete audio files under SAMPLES_ROOT."""
    p = Path(pattern)
    base = p if p.is_absolute() else (SAMPLES_ROOT / p)

    if any(ch in pattern for ch in "*?["):
        root = SAMPLES_ROOT
        matches = [m for m in root.glob(pattern) if m.is_file()]
    elif base.is_dir():
        matches = [m for m in base.rglob("*") if m.is_file()]
    elif base.is_file():
        matches = [base]
    else:
        matches = []

    return sorted(m for m in matches if m.suffix.lower() in SOURCE_EXTS)


def build_plan(spec: DeviceSpec) -> Plan:
    from .config import manifest_path

    entries = parse_manifest(manifest_path(spec.name))
    items: list[Item] = []
    missing: list[str] = []
    taken: set[str] = set()

    for pattern, rename in entries:
        files = _resolve_pattern(pattern)
        if not files:
            missing.append(pattern)
            continue
        for src in files:
            if rename and len(files) == 1:
                out = f"{naming.normalise_base(rename)}.wav"
            else:
                out = naming.output_name(src)
            out = naming.dedupe(out, taken)
            warnings: list[str] = []
            if naming.too_long(out, spec.name_warn):
                warnings.append(f"name >{spec.name_warn} chars (will truncate on device)")
            items.append(Item(src=src, out_name=out, warnings=warnings))

    return Plan(spec=spec, items=items, missing=missing)


def export_device(
    spec: DeviceSpec,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[int, int]:
    """Run the export. Returns (converted, skipped)."""
    plan = build_plan(spec)
    out_dir = EXPORT_ROOT / spec.export_dir
    converted = skipped = 0

    for item in plan.items:
        dest = out_dir / item.out_name
        if dest.exists() and not force:
            skipped += 1
            continue
        if dry_run:
            converted += 1
            continue
        convert_file(item.src, dest, spec)
        converted += 1

    return converted, skipped


def sync_to_card(spec: DeviceSpec, dest_root: Path) -> int:
    """Copy EXPORT_ROOT/<DEVICE>/ into a mounted card. Returns files copied."""
    src_dir = EXPORT_ROOT / spec.export_dir
    target = dest_root / f"EIDETIC-{spec.export_dir}"
    target.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in sorted(src_dir.glob("*.wav")):
        shutil.copy2(f, target / f.name)
        count += 1
    return count
