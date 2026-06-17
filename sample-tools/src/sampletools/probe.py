"""Thin ffprobe wrapper to read an audio file's format."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class FfprobeMissing(RuntimeError):
    pass


@dataclass(frozen=True)
class AudioInfo:
    rate: int | None
    bits: int | None
    channels: int | None
    duration: float | None


def _ffprobe_bin() -> str:
    path = shutil.which("ffprobe")
    if not path:
        raise FfprobeMissing("ffprobe not found on PATH (brew install ffmpeg)")
    return path


def probe(src: Path) -> AudioInfo:
    """Return format info for the first audio stream, or all-None on failure."""
    cmd = [
        _ffprobe_bin(),
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries",
        "stream=sample_rate,bits_per_sample,bits_per_raw_sample,channels:format=duration",
        "-of", "json",
        str(src),
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return AudioInfo(None, None, None, None)

    data = json.loads(out or "{}")
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}

    def _int(value: object) -> int | None:
        try:
            n = int(value)  # type: ignore[arg-type]
            return n or None
        except (TypeError, ValueError):
            return None

    bits = _int(stream.get("bits_per_sample")) or _int(stream.get("bits_per_raw_sample"))
    try:
        duration = float(fmt["duration"])
    except (KeyError, TypeError, ValueError):
        duration = None

    return AudioInfo(
        rate=_int(stream.get("sample_rate")),
        bits=bits,
        channels=_int(stream.get("channels")),
        duration=duration,
    )
