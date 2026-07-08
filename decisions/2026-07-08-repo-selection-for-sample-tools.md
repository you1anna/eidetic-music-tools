# Repo Selection for Sample Tools

Date: 2026-07-08
Project: eidetic-music-tools
State: Active

## Context

Robin asked to review existing GitHub projects before building more custom sample tooling. The
target problem is the SSD sample library plus hardware export workflows for Octatrack, Digitakt,
TR-8S, and later Ableton-facing analysis.

This note is intentionally a selection record, not an implementation plan. The main decision is
to keep `eidetic-music-tools` as the orchestration repo, then integrate or borrow behavior from
specialized projects where they already solve a real part of the workflow.

## Selected Dependencies or Integration Targets

These are worth integrating or depending on where the license and packaging fit.

- [`dagargo/elektroid`](https://github.com/dagargo/elektroid) - use for Digitakt and other
  Elektron device transfer paths instead of building a custom Elektron Transfer replacement.
  It has a CLI, supports sample filesystem operations, and covers the class of hardware that is
  awkward or impossible to sync as plain storage. License: GPLv3, so treat it as an external tool
  boundary rather than code to vendor.
- [`librosa/librosa`](https://github.com/librosa/librosa) - use as the permissive Python analysis
  base for bounce and sample features where `eidetic-music-tools` needs local signal processing.
  This matches the existing A1/bounce-analysis direction.
- [`beetbox/pyacoustid`](https://github.com/beetbox/pyacoustid) plus
  [`acoustid/chromaprint`](https://github.com/acoustid/chromaprint) - use for perceptual
  fingerprinting when exact SHA/file-size duplicate detection is not enough.
- [`unmade/audiomatch`](https://github.com/unmade/audiomatch) - use as a reference or possible
  CLI dependency for similar-audio reports built on Chromaprint.
- [`DBraun/AbletonParsing`](https://github.com/DBraun/AbletonParsing) - use as a concrete Python
  reference for Ableton `.asd` clip analysis sidecars, especially warp-marker and clip metadata
  introspection.

## Behavior References

These are useful design references, but should not be copied directly without a license-specific
review.

- [`brian3kb/digichain`](https://github.com/brian3kb/digichain) - strong reference for sample
  chain creation, Octatrack slice metadata, Digitakt-style 48 kHz / 16-bit / mono exports, and
  browser/offline UX. License: AGPL-3.0, so do not vendor code casually.
- [`ohthepain/octacard`](https://github.com/ohthepain/octacard) - useful Octatrack card-manager
  UX reference: source/destination panes, whole-tree conversion, 44.1/48 kHz conversion, mono
  downmix, normalization, trimming, and pitch-to-C workflows.
- [`KaiDrange/OctaChainer`](https://github.com/KaiDrange/OctaChainer) - older but clean reference
  for Octatrack sample chains and `.ot` files.
- [`davidferlay/octatrack-manager`](https://github.com/davidferlay/octatrack-manager) - reference
  for Octatrack project inspection, audio pool management, and bulk sample-slot workflows.
- [`irpina/Sampson-Sample-Manager`](https://github.com/irpina/Sampson-Sample-Manager) - reference
  for hardware profiles, preview, dry-run, SHA-256 duplicate detection, BPM/key detection, and
  audition stack UX.
- [`swendlcode/stack-desktop`](https://github.com/swendlcode/stack-desktop) - reference for an
  offline desktop sample library UI using Tauri, React, Rust, and SQLite.
- [`jonasblome/Saempl`](https://github.com/jonasblome/Saempl) - reference for automatic sample
  analysis, key/loudness/tempo features, clustering, and DAW drag/drop UX.
- [`spectralliaisons/tr8sify`](https://github.com/spectralliaisons/tr8sify) - small reference for
  TR-8S naming and directory constraints.

## Avoid as Backend Replacements

These projects should not replace the local tooling directly.

- `Sampson-Sample-Manager` explicitly documents unsafe name-collision behavior: two source files
  that map to the same output name can silently overwrite each other. That is unacceptable for the
  SSD sample library. Keep it as UX and profile reference only.
- `beets` and MusicBrainz Picard are mature metadata systems, but their core model is albums and
  tracks. They are not a good direct fit for one-shot, loop, pack, curated-role, and hardware-crate
  sample management.
- Small or unlicensed sample-manager repos are not mature enough to drive the SSD workflow. They
  can be mined for ideas only after the main choices above have been exhausted.
- GPL and AGPL projects can be used as external tools or references, but direct source reuse would
  contaminate this repo's distribution choices unless intentionally accepted.

## Immediate Repo-Informed Decisions

1. Do not build an Elektron device-transfer stack from scratch. First check whether
   `elektroid-cli` can cover Digitakt upload, and document manual Elektron Transfer as the fallback.
2. Do not build a perceptual fingerprinting engine from scratch. Add a manifest-only similar-audio
   report around Chromaprint/pyacoustid/audiomatch before moving or deleting files.
3. Treat the Digitakt export format as unresolved until verified on the real unit or manual.
   Multiple reviewed tools converge on 48 kHz / 16-bit / mono, while current local config still
   says 44.1 kHz / 16-bit / mono.
4. Do not apply the raw SSD intake plan as generated. The top-level `SEAN` directory appears to
   be misplaced `_REVIEW` material, not a vendor pack. Rehome it for review first, then intake the
   three true pack directories into `PACKS/`.
5. Fix the `sample-review` scope before using it as evidence. It currently reports zero files
   because `librarytools.config.IN_SCOPE` still names old pre-two-zone locations, while the live
   library uses `PACKS/`, `CURATED/`, and staging directories.

## Next Implementation Slice

The next safe slice is small and reversible:

- update docs or code to mark Digitakt 48 kHz as pending verification, not silently correct;
- fix `sample-review` source selection so it can inspect the current two-zone library;
- create a filtered SSD move plan that excludes `SEAN` from pack intake;
- rehome `SEAN` under `_REVIEW` only after reviewing the exact destination and using an auditable
  move plan.

## Session Stop Note

Robin stopped the 2026-07-08 session because the work was drifting from repo selection into SSD
cleanup. Preserve this boundary for the next session: repo selection is captured above; SSD moves
remain unapplied.

Important local state:

- Created this decision note to record the GitHub repo shortlist and the decision to keep
  `eidetic-music-tools` as the orchestration repo.
- Added a narrow `sample-review` source-scope fix in the working tree:
  - `library-tools/src/librarytools/review.py`
  - `library-tools/tests/test_review.py`
  - `library-tools/README.md`
- Verification already run after that local fix:
  - `~/.venvs/library-tools/bin/pytest -q` from `library-tools`: `98 passed`
  - `sample-review --root '/Volumes/Extreme SSD/Production/SAMPLES' --no-probe --summary`:
    `files: 4268`, including `_REVIEW: 1894`
- The original zero-file symptom was therefore a stale read-only review scope, not an empty SSD.
- No SSD writes or moves were applied.
- Evidence gathered before stopping:
  - top-level `/Volumes/Extreme SSD/Production/SAMPLES/SEAN` contains 1815 flat files named like
    `review-*`
  - `/Volumes/Extreme SSD/Production/SAMPLES/_REVIEW` was empty
  - this supports treating `SEAN` as misplaced review material, not as a vendor pack
- Do not run the raw `sample-intake` plan from this session because it would move `SEAN` into
  `PACKS/sean-2`. A future plan should exclude `SEAN` and handle only the three true stray packs
  unless Robin decides otherwise.
