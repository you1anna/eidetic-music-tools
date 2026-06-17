"""Sort the messy in-scope packs into sound-type buckets (reversible).

Decision precedence (cheapest signal first):
  loop keyword  ->  pad keyword  ->  one-shot keyword  ->  duration  ->  OTHER
"""

from __future__ import annotations

import re
from pathlib import Path

from . import config

_BPM_RE = re.compile(r"\d{2,3}\s?bpm")


def _has(text: str, keywords: tuple[str, ...]) -> bool:
    return any(kw in text for kw in keywords)


def classify_path(rel: Path, duration: float | None = None) -> tuple[str, str]:
    """Return (bucket, reason) for a file from its path relative to SAMPLES_ROOT.

    Keywords are matched against the whole lowercased relative path, so a parent
    folder named "Techno Loops" classifies its files even if the filename is bare.
    """
    text = str(rel).lower()
    if _has(text, config.LOOP_KEYWORDS) or _BPM_RE.search(text):
        return "LOOPS", "keyword:loop"
    if _has(text, config.PAD_KEYWORDS):
        return "PADS-DRONES", "keyword:pad"
    if _has(text, config.ONESHOT_KEYWORDS):
        return "ONE-SHOTS", "keyword:oneshot"
    if duration is not None:
        if duration < config.DURATION_ONESHOT_MAX:
            return "ONE-SHOTS", f"duration:{duration:.2f}<{config.DURATION_ONESHOT_MAX}"
        return "LOOPS", f"duration:{duration:.2f}>={config.DURATION_ONESHOT_MAX}"
    return "OTHER", "unmatched"
