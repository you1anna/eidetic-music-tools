"""Normalise output filenames to the hardware-friendly convention.

Convention (see SAMPLES/README.md): lowercase, no spaces, `_` between fields,
`-` within a field. We keep it conservative — only flatten whitespace/illegal
chars and lowercase — rather than trying to reverse-engineer BPM/key/role from
arbitrary source names.
"""

from __future__ import annotations

import re
from pathlib import Path

_ILLEGAL = re.compile(r"[^a-z0-9._-]+")
_DASHES = re.compile(r"-{2,}")
_USCORES = re.compile(r"_{2,}")


def normalise_base(name: str) -> str:
    """Normalise a basename (no extension) to the convention."""
    s = name.strip().lower()
    s = s.replace(" ", "-").replace("'", "")
    s = _ILLEGAL.sub("-", s)
    s = _DASHES.sub("-", s)
    s = _USCORES.sub("_", s)
    return s.strip("-_") or "sample"


def output_name(src: Path) -> str:
    """Output filename (always .wav) for a given source path."""
    return f"{normalise_base(src.stem)}.wav"


def too_long(basename: str, limit: int) -> bool:
    """True if the basename (incl. extension) exceeds the device's display limit."""
    return len(basename) > limit


def dedupe(name: str, taken: set[str]) -> str:
    """Append _2, _3, ... if `name` already exists in `taken`. Records the result."""
    if name not in taken:
        taken.add(name)
        return name
    stem, _, ext = name.rpartition(".")
    i = 2
    while f"{stem}_{i}.{ext}" in taken:
        i += 1
    result = f"{stem}_{i}.{ext}"
    taken.add(result)
    return result
