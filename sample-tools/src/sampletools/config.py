"""Paths and per-device export specifications.

All values are overridable via environment variables so the tool works even if
the SSD mounts at a different point or the library is relocated:

    SAMPLES_ROOT   default: /Volumes/Extreme SSD/Production/SAMPLES
    EXPORT_ROOT    default: <SAMPLES_ROOT>/_EXPORT
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

SAMPLES_ROOT: Path = Path(
    os.environ.get("SAMPLES_ROOT", "/Volumes/Extreme SSD/Production/SAMPLES")
)
EXPORT_ROOT: Path = Path(os.environ.get("EXPORT_ROOT", str(SAMPLES_ROOT / "_EXPORT")))

# Source extensions ffmpeg can decode into our 16-bit/44.1 WAV target.
SOURCE_EXTS: tuple[str, ...] = (".wav", ".aif", ".aiff", ".flac", ".mp3", ".ogg")


@dataclass(frozen=True)
class DeviceSpec:
    """Target audio format + filename constraints for one piece of hardware."""

    name: str          # canonical lowercase key
    export_dir: str    # subfolder name under EXPORT_ROOT
    rate: int          # sample rate (Hz)
    bits: int          # bit depth
    channels: int | None  # 1 = force mono fold-down; None = preserve source
    name_warn: int     # warn if the output basename exceeds this many chars
    can_sync: bool     # True if a mounted card can receive a plain file copy
    sync_note: str     # guidance shown when --sync is used

    @property
    def codec(self) -> str:
        # 16-bit little-endian PCM WAV. (AIFF would be s16be — not used here.)
        return "pcm_s16le"


DEVICE_SPECS: dict[str, DeviceSpec] = {
    "octatrack": DeviceSpec(
        name="octatrack",
        export_dir="OCTATRACK",
        rate=44100,
        bits=16,
        channels=None,  # OT handles mono + stereo
        name_warn=64,
        can_sync=True,  # CF card is a plain filesystem
        sync_note="Octatrack reads WAVs from any folder on the CF card.",
    ),
    "digitakt": DeviceSpec(
        name="digitakt",
        export_dir="DIGITAKT",
        rate=44100,
        bits=16,
        channels=1,  # Digitakt MK1 is mono-only
        name_warn=24,  # small screen; long names truncate
        can_sync=False,  # +Drive is not a mountable disk
        sync_note=(
            "Digitakt +Drive is not a plain disk — drag the staged folder into the "
            "Elektron Transfer app instead of using --sync."
        ),
    ),
    "tr8s": DeviceSpec(
        name="tr8s",
        export_dir="TR8S",
        rate=44100,
        bits=16,
        channels=None,  # TR-8S handles mono + stereo
        name_warn=120,
        can_sync=True,  # SD card is a plain filesystem
        sync_note=(
            "Copies to the SD card; you may still need to Import the samples from the "
            "TR-8S front panel depending on firmware."
        ),
    ),
}


def get_spec(device: str) -> DeviceSpec:
    key = device.strip().lower()
    if key not in DEVICE_SPECS:
        valid = ", ".join(sorted(DEVICE_SPECS))
        raise KeyError(f"unknown device {device!r}; valid devices: {valid}")
    return DEVICE_SPECS[key]


def manifest_path(device: str) -> Path:
    """manifests/<device>.txt next to the package (repo-relative)."""
    return Path(__file__).resolve().parents[2] / "manifests" / f"{get_spec(device).name}.txt"
