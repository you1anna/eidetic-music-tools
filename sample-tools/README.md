# sample-tools

Convert and sync curated samples from the SSD library to **Octatrack MKII**,
**Digitakt MK1**, and **TR-8S**. Reads a per-device manifest, converts each
source to that device's spec with `ffmpeg`, and stages the result in
`SAMPLES/_EXPORT/<DEVICE>/` ready to copy to a card.

Source lives on the SSD (this repo); the **venv lives on the Mac** (APFS). The SSD
is exFAT and a venv there is unreliable (no exec bit / symlinks), so we keep the
venv off it and editable-install it against this source.

## Install

```bash
brew install ffmpeg python@3.12          # prerequisites
/opt/homebrew/bin/python3.12 -m venv ~/.venvs/sample-tools
~/.venvs/sample-tools/bin/pip install -e "/Volumes/Extreme SSD/eidetic-music-tools/sample-tools"
```

That provides the `sample-export` console script inside the venv. The repo's
`bin/sample-export` shim calls it (override the venv path with `$SAMPLE_TOOLS_VENV`).

## Use

```bash
sx() { ~/.venvs/sample-tools/bin/sample-export "$@"; }   # or use bin/sample-export

sx digitakt --list                       # resolve manifest, show planned files
sx digitakt --dry-run                     # show what would convert
sx digitakt                              # convert -> _EXPORT/DIGITAKT/
sx octatrack --sync /Volumes/OCTACF       # convert + copy to CF card
sx --all --dry-run                        # all three devices
```

### Options
| flag | effect |
|---|---|
| `--list` | resolve the manifest and print source → output names + warnings; no conversion |
| `--dry-run` | show what would convert without writing files |
| `--force` | re-convert even if the output already exists (default skips = idempotent) |
| `--sync DEST` | copy the built folder to a mounted card (Octatrack CF, TR-8S SD) |
| `--all` | run every device |

## Device specs

All outputs are **16-bit / 44.1 kHz WAV** (`pcm_s16le`).

| device | channels | sync | notes |
|---|---|---|---|
| octatrack | preserve | ✅ CF card | reads WAVs from any folder |
| digitakt | **mono** (`-ac 1`) | ❌ | +Drive isn't a disk — use Elektron Transfer |
| tr8s | preserve | ✅ SD card | may still need on-device Import |

`--sync` copies into `<DEST>/EIDETIC-<DEVICE>/`.

## Manifests

`manifests/<device>.txt` — one entry per line, resolved relative to
`SAMPLES_ROOT` (absolute paths also work). `#` comments and blank lines ignored.

```
KICKS/GR8_001_TUNED_KICKS                          # a folder (recurses)
DRUM-LOOPS/Riemann Kollektion Riemann Tribal Techno 1
DRONE-ATMOS/Analogue Noise/*.wav                   # a glob
PERC/conga.wav => conga-hi                          # rename the output base
```

Source `.wav/.aif/.aiff/.flac/.mp3/.ogg` all decode; output is always `.wav`.
The seed manifests pull whole packs as a starting point — run `--list` and trim
to the exact files you want on each device.

## Config / env overrides

| var | default |
|---|---|
| `SAMPLES_ROOT` | `/Volumes/Extreme SSD/Production/SAMPLES` |
| `EXPORT_ROOT` | `<SAMPLES_ROOT>/_EXPORT` |

## Layout

```
src/sampletools/  config.py probe.py naming.py convert.py export.py cli.py
manifests/        octatrack.txt digitakt.txt tr8s.txt
bin/sample-export shim
```
