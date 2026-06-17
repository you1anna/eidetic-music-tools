"""ffmpeg wrapper: convert one source file to a device's WAV spec."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import DeviceSpec


class FfmpegMissing(RuntimeError):
    pass


def _ffmpeg_bin() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise FfmpegMissing("ffmpeg not found on PATH (brew install ffmpeg)")
    return path


def build_cmd(src: Path, dest: Path, spec: DeviceSpec) -> list[str]:
    """The ffmpeg command line for converting `src` -> `dest` per `spec`."""
    cmd = [
        _ffmpeg_bin(),
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(src),
        "-ar", str(spec.rate),
        "-c:a", spec.codec,
    ]
    if spec.channels is not None:
        cmd += ["-ac", str(spec.channels)]
    # Force the WAV muxer explicitly: the atomic temp file is written as
    # "<name>.wav.tmp", so ffmpeg can't infer the container from the extension.
    cmd += ["-f", "wav", str(dest)]
    return cmd


def convert_file(src: Path, dest: Path, spec: DeviceSpec) -> None:
    """Convert src -> dest. Writes to a temp file then renames (atomic-ish)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    cmd = build_cmd(src, tmp, spec)
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg failed for {src.name}: {exc.stderr.strip()}") from exc
    tmp.replace(dest)
