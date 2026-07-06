# Sample intelligence and hardware crates - design

**Date:** 2026-07-06  
**Status:** design approved in chat; written spec awaiting review  
**Repo:** `eidetic-music-tools`  
**Goal:** make the sample library musically reachable for hardware techno production without another destructive reorg.

## Problem

The current library tools are useful but too literal. They can infer role folders,
loop/one-shot type, explicit BPM/key, duration, and hardware-friendly names from
paths and filenames. That is not enough for the production workflow. Robin needs
to reach for sounds by musical character:

- `KICKS/subby-short`
- `KICKS/rumble-long`
- `HATS/metallic-tight`
- `PERC/wood-tribal`
- `LOOPS/sparse-top-132`
- `DRONE/dub-wash`

The real goal is not prettier folders. The goal is fast, playable access on
Octatrack MKII, Digitakt MK1, TR-8S, and Ableton.

There is also a device-native source problem: some packs are Octatrack Sets, not
ordinary sample folders. For example, `Caught on Tape: 808+909` contains an
Octatrack Set/project with `project.work`, `bankNN.work`, `arrNN.work`, `.strd`
files, an `AUDIO/` pool, and install/license documentation. Flattening that into
generic role folders would destroy useful OT context.

## Design stance

Build a read-only intelligence layer before moving more files.

The tool should analyze and index samples, preserve provenance, generate virtual
crates and export manifests, and only later promote or copy selected material into
hardware-ready exports. It should not mutate the master sample tree during phase 1.

## Scope

In scope for the first implementation:

- Add a `sample-analyze` workflow under `library-tools` or a closely related new
  module.
- Build an incremental local analysis cache for audio files.
- Extract lightweight audio features suitable for character tags and similarity.
- Detect Octatrack Set packs and register them as first-class sources.
- Generate virtual crate manifests for `sample-tools`.
- Produce human-readable reports for quick audition and review.
- Run against selected pilot sources before full-library indexing.

Out of scope for the first implementation:

- Moving or deleting samples.
- Rewriting Octatrack project files.
- Creating full ML embedding search.
- Training classifiers.
- A GUI.
- Perfect semantic labels for every sound on the first pass.

## Source model

Every indexed file gets a source kind:

| Kind | Meaning | Handling |
| --- | --- | --- |
| `curated-sample` | Files already under `CURATED/` role folders. | Analyze and include in crates. |
| `vendor-pack-audio` | Files inside raw vendor packs. | Analyze with pack provenance preserved. |
| `octatrack-set-audio` | Audio pool file inside an OT Set. | Analyze, but keep the Set intact. |
| `octatrack-set-project` | OT project/control file such as `.work` or `.strd`. | Register, never classify as a sample. |
| `document` | Install/license PDFs, text docs, URLs, NFO files. | Register as pack context. |
| `staging-system` | `_EXPORT`, `_TO-DELETE`, AppleDouble, `.DS_Store`. | Ignore or report as hygiene. |

This allows the same sample to appear in a virtual crate while the source pack
remains whole and understandable.

## Octatrack Set registry

Add an OT Set detector that scans top-level sample folders and `PACKS/` for the
following signals:

- `project.work`
- `bankNN.work`
- `arrNN.work`
- matching `.strd` files
- `AUDIO/` folder with WAV files
- install/license PDF or text files

For each detected Set, write a registry row with:

- set name
- project root
- audio pool root
- project/control file counts
- audio file count
- install/license doc path
- inferred device: `octatrack`
- pack provenance
- handling policy: `preserve-set`

The registry should support two workflows:

1. **Install as Set:** generate an Octatrack copy plan that keeps the full Set
   folder intact for CF card root install.
2. **Borrow from audio pool:** allow selected samples from the audio pool to enter
   Digitakt/TR-8S/Ableton crates while retaining source metadata such as
   `source_set=Caught On Tape 808+909`.

For the Caught on Tape pilot, the extracted PDF states that the pack is one OT
Set and one Project with 447 samples, 16 patterns, 4 parts, and 16 scenes per
part. It also defines processing suffixes:

- `Orig`: original sample, no tape recording
- `Tape`: recorded to tape
- `TapeSat`: recorded to tape, saturated
- `X` / `X2`: additional processing

Those suffixes should become first-pass character/provenance tags:
`original`, `tape`, `tape-saturated`, `processed`, `processed-more`.

## Audio analysis

Use a tiered analyzer so the M4 Pro can do useful work without requiring heavy
processing up front.

### Tier 0 - existing cheap metadata

Reuse current `library-tools` logic:

- role/category from path and filename
- sample type from path, filename, BPM token, and duration
- explicit BPM/key if present
- hardware-friendly proposed name
- duration via `ffprobe`

### Tier 1 - lightweight audio features

Extract features that are cheap and musically useful:

- duration
- sample rate, bit depth, channel count
- peak and RMS loudness
- crest factor
- silence/head/tail trim estimate
- transient sharpness
- attack time
- decay/tail length
- low/mid/high energy balance
- sub energy ratio
- brightness
- noisiness vs tonal steadiness
- stereo width / mono safety
- onset density
- loop-ishness from duration, onset pattern, and BPM/path hints

Implementation should prefer installed command-line tools and small Python
dependencies:

- `ffprobe` for format and duration
- `ffmpeg`/filters where practical for cheap stats
- optional small numeric helper code for downsampled mono analysis

Avoid phase-1 dependencies such as `torch`, `demucs`, or large embedding models.
`librosa` can remain a later optional tier if the lightweight feature set is not
good enough.

### Tier 2 - optional later similarity embeddings

After the lightweight cartographer works, add heavier semantic search if it is
worth it:

- "find me dirty short 909 kicks"
- "more like this dub chord stab"
- "metallic shaker loops around 132 BPM"

This should not block phase 1.

## Character tags

Tags are derived from a combination of source path, filename, OT pack suffixes,
and audio features. Tags should be explicit and inspectable, not mysterious.

Example first-pass rules:

| Role | Tag | Signals |
| --- | --- | --- |
| `KICKS` | `subby` | high low/sub energy ratio |
| `KICKS` | `short` | short duration/tail |
| `KICKS` | `rumble-long` | long tail plus strong low energy |
| `KICKS` | `clicky` | high transient/brightness |
| `HATS-CYM` | `metallic` | high brightness/noisiness |
| `HATS-CYM` | `tight` | short tail and sharp transient |
| `PERC` | `wood` | path/name hints plus mid-focused transient |
| `PERC` | `tribal` | path/name hints, conga/tom/cowbell families |
| `DRUM-LOOPS` | `sparse` | low onset density |
| `DRUM-LOOPS` | `busy` | high onset density |
| `DRONE-ATMOS` | `dub-wash` | long duration, low transient density, dark/mid energy, dub/path hints |
| any | `tape-saturated` | `TapeSat` suffix or pack docs |
| any | `processed` | `X`/`X2` suffixes |

Each tag should include a reason column so bad labels can be tuned:

```text
tag=rumble-long reason=low_energy=0.72;tail=1.9s
tag=tape-saturated reason=filename_suffix:TapeSat
```

## Similarity and grouping

Build similarity within a role, not across the whole library at first. A kick
should be compared with kicks; a drone with drones. This keeps results musically
useful and avoids expensive global nearest-neighbour infrastructure.

Phase-1 grouping:

- normalize the lightweight feature vectors
- group by role
- cluster with a simple deterministic method
- assign a readable cluster label from dominant tags
- pick representative samples per cluster

Cluster outputs are virtual paths, not physical folders:

```text
KICKS/subby-short
KICKS/rumble-long
HATS-CYM/metallic-tight
PERC/wood-tribal
DRUM-LOOPS/sparse-top-132
DRONE-ATMOS/dub-wash
```

## Crate generation

Add generated manifest files that `sample-tools` can consume. These should be
small, opinionated, and device-aware.

Example outputs:

```text
library-tools/manifests/crates/digitakt/punchy-techno-kit.txt
library-tools/manifests/crates/tr8s/909-plus-weird-perc.txt
library-tools/manifests/crates/octatrack/caught-on-tape-set.txt
library-tools/manifests/crates/octatrack/dub-loop-bed-132.txt
library-tools/manifests/crates/ableton/dub-techno-favourites.txt
```

Device rules:

- **Digitakt:** favor mono one-shots, tight tails, short names, compact kits,
  avoid long loops unless explicitly selected.
- **TR-8S:** favor drum one-shots grouped by instrument lane: BD, SD/CLAP,
  hats, toms, percussion, cymbals, FX.
- **Octatrack:** support both whole Set install plans and curated audio-pool
  crates for Flex/Static use; preserve stereo and longer loops/textures.
- **Ableton:** include broader search/audition crates, including loops,
  atmospheres, vocals, and resampling candidates.

Crates should start as generated suggestions. Human-selected favorites can later
be promoted to stable curated manifests.

## Data outputs

Prefer a small local SQLite cache plus exported TSV/Markdown views:

- `manifests/sample-intelligence.sqlite` for incremental analysis and queries
- `manifests/sample-features-latest.tsv`
- `manifests/source-registry-latest.tsv`
- `manifests/ot-sets-latest.tsv`
- `manifests/clusters-latest.tsv`
- `manifests/crates/<device>/<crate>.txt`
- `manifests/reports/<crate>.md`

SQLite keeps repeated analysis fast and avoids reprocessing unchanged files.
TSV/Markdown keeps the workflow inspectable and easy to share with an assistant
without pasting thousands of rows.

Cache invalidation should use path, file size, modified time, and optionally a
content hash for selected files. Phase 1 can avoid hashing every large file.

## Pilot plan

Start with a narrow pilot before indexing the whole library:

1. Register the two top-level Elektron Octatrack packs:
   - `Caught on Tape: 808+909`
   - `Cult of SP1200`
2. Analyze their audio pools.
3. Detect OT Set/project structure and install docs.
4. Generate:
   - an Octatrack whole-Set install plan
   - a Digitakt one-shot kit proposal
   - a TR-8S drum proposal
   - a small Ableton audition crate
5. Produce a short report showing clusters, representative files, and tag reasons.

Success criteria:

- It is obvious which samples are kicks, hats, snares, percussion, musical hits,
  FX, and loops.
- At least a few useful character groups appear without hand sorting.
- The OT Sets remain intact and installable.
- Generated crates are small enough to audition, not just new huge lists.
- Robin can reject bad labels by editing rules, not by manually moving hundreds
  of files.

## Safety

- Phase 1 is read-only against `/Volumes/Extreme SSD/Production/SAMPLES`.
- No deletes.
- No moves.
- No OT project rewrites.
- Generated artifacts live under `library-tools/manifests/` and remain gitignored
  unless a specific curated manifest is intentionally promoted.
- If future apply/copy steps are added, they must be dry-run by default and
  undo-manifested like existing tools.

## Testing

Unit tests:

- OT Set detector identifies synthetic `project.work` + `AUDIO/` structures.
- Document/source registry ignores AppleDouble and `.DS_Store`.
- Processing suffix parser maps `Orig`, `Tape`, `TapeSat`, `X`, `X2`.
- Character tag rules classify synthetic feature rows.
- Crate generator respects device filters.

Integration tests with tiny fixtures:

- synthetic OT Set with two audio files and one install doc
- synthetic generic pack with kicks/hats/loops
- generated TSV/report outputs are stable

Manual verification:

- run pilot scan on Caught on Tape and Cult of SP1200
- inspect counts and representative clusters
- audition a small generated crate before expanding scope

## Open decisions before implementation

- Whether this should live inside existing `library-tools` or a new sibling
  `analysis-tools` package. Recommendation: start inside `library-tools` because
  the output is curation/indexing, not mix/master analysis.
- Whether SQLite artifacts should live in `library-tools/manifests/` or a new
  `library-tools/cache/`. Recommendation: keep them under `manifests/` initially
  because that directory is already gitignored and familiar.
- Which pilot crate to judge first. Recommendation: use the Elektron OT packs to
  generate both an Octatrack Set registry and one tight Digitakt/TR-8S one-shot
  crate, because that exercises both lanes.
