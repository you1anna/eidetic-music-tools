# Where the SAMPLES project stands (plain English)

Last updated: 2026-07-09. This is the one-page "you can close the chat now" summary. Granular
records live in [`decisions/`](decisions/); this ties them together in plain language.

## The goal

Get the messy sample library on the Extreme SSD (`/Volumes/Extreme SSD/Production/SAMPLES/`) into
a **trusted, clean state**, then export the right material — in the right format — onto the
hardware (Octatrack MKII first, then Digitakt, TR-8S). "Trusted" means each sound is actually in
the folder its name claims: a kick in `KICKS/`, a clap in `CLAP-SNARE/`, etc.

## What is built and working

- **`sample-tools/`** — converts and syncs curated samples to each device's spec (16-bit/44.1 WAV,
  mono for Digitakt). Manifest-driven. Done.
- **`library-tools/`** — the review/curation toolkit. Reads the library and emits TSV manifests;
  can dry-run classify, de-dupe, sort, and intake whole vendor packs. **Manifest-only: it never
  moves, renames, or deletes a sample on its own.** Human audition is still the promotion gate.
- **Drum-role classifier** (new, adopted 2026-07-09) — a small pretrained CNN-BiLSTM model that
  listens to each drum sample and votes on what it actually is (kick / clap / hat / perc / etc.).
  This is now the **trusted source of truth for drum-folder correctness**, replacing the old
  hand-written acoustic rules. Run it with `sample-analyze --classifier`.

## The one decision that unblocked everything

For weeks the project kept producing decision docs, CSVs, and hand-tuned acoustic "gates" — but
never a classifier anyone could trust. The old rules had a structural flaw: they rejected genuine
kicks purely on length (~0.86s "too long") because they never actually listened to the timbre.

The fix (~1 hour): stop theorising, install a **pretrained model**, and prove it on real files.
Full record: [`decisions/2026-07-09-drum-role-classifier-adopted.md`](decisions/2026-07-09-drum-role-classifier-adopted.md).

### What was measured (source: development validation, not a saved full run)

- **Contamination test** (labelled slice from pack filenames): keeping a file as a kick only if
  the model's top vote is "kick" → **12/12 true kicks kept, 0/36 contaminants leaked** (cymbals,
  claps, percussion all correctly rejected).
- **Full `KICKS/` scan** (2,495 files): 1,882 kept as real kicks (75.4%); **613 flagged as
  misfiled**, each with a suggested destination — PERC 258, CLAP-SNARE 161, HATS-CYM 69, BASS 53,
  REVIEW 72.
- Confidence is banded: **trust ≥0.80 / review ≥0.50 / low <0.50**. The fuzzy zone is soft/tuned
  kicks vs. low toms, which land low and get a human ear rather than an automatic verdict.

## Important constraints (don't lose these)

- **Model licensing:** the upstream weights (`faraway1nspace/DrumClassifer-CNN-LSTM`) have **no
  license** — all rights reserved. So: the code is a clean-room reimplementation (not vendored),
  and the weights are **user-supplied on this machine only** at
  `library-tools/models/drum-cnn-lstm.model` (7.6 MB, present, gitignored — never committed). If
  this ever becomes a shared/redistributed tool, swap in a clearly-licensed or retrained model
  first.
- **Heavy deps are optional:** `torch` + `librosa` live behind the `classifier` extra, so the core
  tidy tools stay light. `classifier.available()` fails cleanly if the deps or weights are absent.
- **Still manifest-only.** Nothing has been moved on the SSD. The classifier changes what we
  *trust*, not what gets *touched*.

## What is NOT done yet (the actual blocker to shipping)

1. **No saved full-library audit exists.** `sample-analyze --classifier` writes
   `role-audit-latest.tsv`, but that file is not in the repo — the numbers above are from the
   development scan of `KICKS/` only. **First real next step: run the full audit and persist it.**
2. **No samples have been re-filed.** The 613 flagged kicks (and equivalents in other roles) are
   identified but not acted on.
3. **The Octatrack export has not been built** from a validated clean pool.

## Next steps, in order

1. Run the full audit across all CURATED roles and save the output:
   `sample-analyze --classifier` (from the `library-tools` venv, with the `classifier` extra). Read
   the **trust-band (≥0.80)** count — that is the safe-to-act pool.
2. Act on the trust-band misfiles: move each to its suggested role (dry-run first, reversible).
3. Build the **Octatrack export** from the resulting validated clean pool — this is the payoff.
4. Fold the classifier vote into device-crate selection (retire the old `_passes_kick_gate`).
5. Add a small labelled fixture set so the classifier's precision is regression-tested over time.

## How to run it (quick reference)

- Library on SSD: `/Volumes/Extreme SSD/Production/SAMPLES/` — CURATED roles: BASS, CLAP-SNARE,
  DRONE-ATMOS, DRUM-KITS, DRUM-LOOPS, FX-RISE-IMPACT, HATS-CYM, KICKS, MIDI, PERC,
  SYNTH-STAB-CHORD, VOCALS.
- Per-tool venvs live under `~/.venvs/` (not in the repo). Target Python 3.12.
- Classifier command: `sample-analyze --classifier` → writes `role-audit-latest.tsv` + prints a
  per-role summary.
