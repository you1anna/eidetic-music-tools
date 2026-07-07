# Storage strategy & creative workflow

Context for all future tooling in this repo. Robin (DJ **Eidetic**) runs a hardware
techno studio: **Octatrack MKII** (clock master), **Digitakt MK1**, **TR-8S**, into
**Ableton** on a Mac (mini + MacBook Air M4). Target sound: hypnotic / dub / raw /
hard-groove techno (~130–150 BPM). Everything below is decided unless marked open.

## Storage / format

The Extreme SSD is now **APFS**. Verified on 2026-07-07 with `diskutil info "/Volumes/Extreme SSD"`:
`File System Personality: APFS`, mounted read/write, 2 TB total with about 696 GB free at the time
of the check. Robin also confirmed the SSD is backed up.

**Current layout (decided):**
- **Master library + production archive → APFS SSD.** The sample library is at
  `/Volumes/Extreme SSD/Production/SAMPLES/`.
- **Working repo mirror on the Mac mini → local APFS disk.** Current path:
  `/Users/macmini/Projects/eidetic-music-tools`.
- **Device cards (Octatrack CF, Digitakt +Drive, TR-8S SD) → exFAT/FAT** — required by the hardware.
  These are built by `sample-tools` export, so they stay disposable/re-syncable.

**Resolved gate:** the old "back up before APFS migration" blocker is closed as of 2026-07-07.
Physical sample moves are still review-gated: generate a manifest first, inspect it, then apply only
reversible moves with undo manifests.

Each machine still needs its own venv. On the Mac mini the current convention remains:
`brew install ffmpeg python@3.12`, then `python3.12 -m venv ~/.venvs/<tool>` and editable-install
against `/Users/macmini/Projects/eidetic-music-tools/<tool>`.

## Creative workflow (what the tooling should serve)

Primary capture/production paths (confirmed):
- **Hardware jam → Ableton.** Record live jams (OT clock-master + DT + TR-8S) into Ableton,
  multitrack or master.
- **Resample in hardware.** Octatrack used as a live sampler/mangler — capture, mangle, reuse
  in the box during performance.
- **Arrange/finish in Ableton.** Recorded loops/stems arranged, mixed, finished in Ableton.

Vocals (vocal cuts + loops) enter mainly via Ableton and OT resampling rather than pre-chopped
sample packs — so they need to be **easy to find, audition, and drop in live**, not just sorted.

**The goal in one line:** make sampling, live recording, and techno production *dynamic and
easy to play* — the right sound reachable instantly, low-friction, so the setup amplifies
creativity instead of interrupting it.

What that implies for tooling:
- **Fast, well-labelled content.** Consistent naming + BPM/key tags (techno range ~120–150)
  so the Ableton browser and hardware banks are instantly filterable and auditionable.
- **Two consumers, one library.** Optimise for both Ableton drag-and-drop *and* curated,
  format-correct hardware card sets (already handled by `sample-tools`).
- **Close the resample loop.** Good moments from jams/resampling should flow back into the
  library as reusable, named loops/one-shots.

## Tooling roadmap (this repo)

| Tool | Status | Purpose |
|---|---|---|
| `sample-tools/` | ✅ built | Convert + sync curated samples to device specs (mono for DT). |
| `library-tools/` | ✅ built | Manifest-only review/indexing (`main_category`, `sample_type`, explicit BPM/key, tempo fit, proposed names), plus reversible dry-run classify and de-dupe tools. |
| `inventory/` | folded into `library-tools` for now | `sample-review` writes TSV indexes for curation without moving originals; future audio analysis can build on those manifests. |
| `inbox-sort/` | planned | Fast intake of new downloads from `SAMPLES/00_INBOX/` into roles + naming. |
| vocal/loop prep | idea | Trim silence, normalise, BPM/key-tag vocal cuts & loops → clean drops into Ableton + OT. |
| jam/stem intake | idea | Organise + label recorded Ableton jam stems so good moments become reusable library assets. |
| backup | resolved gate / maintain | SSD backed up per Robin on 2026-07-07; keep ongoing backup/restore checks as maintenance, not a blocker for reviewed sample-management manifests. |

Open: whether to surface curated favourites into Ableton's User Library / Places for one-click
access (worth exploring once `inventory` exists).
