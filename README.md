# eidetic-music-tools

Tooling for Robin's (DJ **Eidetic**) hardware techno studio — managing the sample
library on the Extreme SSD and getting curated, format-correct material onto the
**Octatrack MKII**, **Digitakt MK1**, and **TR-8S**.

Target sound: hypnotic / dub / raw / hard-groove techno (~130–150 BPM).

## Layout

| Dir | Status | What it does |
|---|---|---|
| [`sample-tools/`](sample-tools/) | ✅ built | Convert + sync curated samples to each device's spec (16-bit/44.1 WAV; mono for Digitakt). Manifest-driven CLI. |
| [`library-tools/`](library-tools/) | ✅ built | Manifest-only sample review/indexing by category, loop/one-shot type, BPM, key, tempo fit, plus dry-run classify, de-dupe, sort, and **intake** tools. Two-zone model: `CURATED/` (role folders) + `PACKS/` (whole vendor packs). |
| `inbox-sort/` | ✅ folded into `library-tools` as `sample-intake` | Detects whole vendor packs dropped at the top level / `00_INBOX/`, normalizes their names, and moves them into `PACKS/` (reversible, dry-run by default). |
| `inventory/` | folded into `library-tools` for now | `sample-review` emits TSV indexes that drive curation without moving originals. |
| `midi-tools/` | 📋 specced | Generate techno MIDI (Euclidean / bassline / hats) as `.mid` for Ableton + hardware. Spec/plan: [`docs/superpowers/`](docs/superpowers/) `2026-06-26-midi-generator*`. **Build first.** |
| `ableton-tools/` | 📋 specced | Read-only Ableton `.als` introspection: index tempo/key/samples, find missing media, surface reusable loops. Spec/plan: `2026-06-26-ableton-als-introspection*`. |
| `analysis-tools/` | 📋 specced | Tier-A1 bounce analysis: LUFS / true-peak / spectral / mono-compat / BPM / key; feeds `sample-tools` export. Spec/plan: `2026-06-26-bounce-analysis-a1*`. |
| `stem-tools/` | 📋 specced | `demucs` stem separation (drums/bass/vocals/other) for resampling + vocal sourcing. Spec/plan: `2026-06-26-stem-separation*`. **Build last (heavy).** |

## Storage & workflow

See **[`docs/STORAGE-AND-WORKFLOW.md`](docs/STORAGE-AND-WORKFLOW.md)** for the storage
strategy. As of 2026-07-07, the Extreme SSD is **APFS** and Robin has confirmed it is backed up;
device cards still stay exFAT/FAT as required by the hardware. The tooling serves the creative
workflow: hardware jam → Ableton, resample in the OT, finish in Ableton.

## Note on layout

On the Mac mini, this repo currently lives at `/Users/macmini/Projects/eidetic-music-tools`.
The sample library lives on the APFS SSD at `/Volumes/Extreme SSD/Production/SAMPLES/`.
Each tool still uses a per-machine venv under `~/.venvs/` unless deliberately migrated; see each
tool's `README.md` for setup.

The library itself lives at `/Volumes/Extreme SSD/Production/SAMPLES/` (not in this
repo) — see its `README.md` for the taxonomy and naming convention.

For low-token, human-run curation steps, start with
[`library-tools/README.md`](library-tools/README.md#low-token-manual-workflow):
refresh the manifest index locally, inspect focused TSV slices, then bring back
small examples/counts when the rules need improving.
