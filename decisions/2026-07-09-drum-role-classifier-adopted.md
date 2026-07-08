# Drum-Role Classifier Adopted as the Trusted Role Vote

Date: 2026-07-09
Project: eidetic-music-tools
State: Active — productionising

## Decision

Adopt a small pretrained CNN-BiLSTM drum classifier as the trusted role-vote source in
`sample-analyze`, superseding the hand-rolled acoustic `kick_gate` / `curated_role_conflict`
heuristics as the *primary* evidence for role truth. The heuristics stay as cheap cross-checks;
they are no longer the thing we trust to reject contaminated role folders.

This reverses the 2026-07-08 "no external model / prove the cheap features first" direction, which
had produced repeated manifests and gate specs but never a trustworthy classifier. The cheap gate's
failure mode was structural: it rejected genuine kick one-shots as "loops" purely on a ~0.86s
duration, because timbre never entered the decision.

## Why (measured)

Validated against ground truth read from source-pack filename descriptors (`kick-cym-*` = cymbal,
`kick-clap-*` = clap, `kick-clave/conga-*` = perc, `kick-bd/909-*` = true kick):

- Gate "keep as kick only if model top-1 == kick": **12/12 true kicks kept, 0/36 contaminants
  leaked** (cymbal/clap/perc).
- Full `CURATED/KICKS` scan (2,495 files): 1,882 kept (75.4%), 613 flagged as non-kick, each with a
  suggested destination role (PERC 258, CLAP-SNARE 161, HATS-CYM 69, BASS 53, REVIEW 72).
- Precision where it matters is strong; the fuzzy boundary is tuned/soft kicks vs low toms, which
  land below ~0.4 confidence and are handled by confidence bands (trust ≥0.80 / review ≥0.50 / low).

## Implementation

- `librarytools/classifier.py` — clean-room reimplementation of the architecture (matches the
  checkpoint layer names so weights load `strict=True`), safe weights load (`weights_only=True`;
  the pickle references only OrderedDict / storages / `_rebuild_tensor_v2`), batched CPU inference,
  30-class → CURATED-role mapping, and `build_role_audit` → `role-audit-latest.tsv`.
- `sample-analyze --classifier` runs the audit across CURATED roles (classifier-only unless
  `--pilot` is also given). Authoritative for drum roles (KICKS/CLAP-SNARE/HATS-CYM/PERC/DRUM-KITS);
  for non-drum roles it only emits a soft `possible-drum-oneshot` outlier note, never a role verdict.
- Optional heavy deps behind the `classifier` extra (`torch`, `librosa`); core tidy tools stay light.
  `available()` gates cleanly when deps or weights are absent.

## Licensing constraint (important)

The upstream model (`faraway1nspace/DrumClassifer-CNN-LSTM`) has **no license file** — all rights
reserved. Therefore:

- We do **not** vendor its code (reimplemented from the visible architecture) and do **not** commit
  its trained weights.
- Weights are **user-supplied** at `config.DRUM_MODEL_PATH` (default
  `library-tools/models/drum-cnn-lstm.model`), and `models/` is gitignored.
- If this becomes a shared/redistributed tool, replace the weights with a
  clearly-licensed model (or retrain) before shipping.

## Boundaries (unchanged safety model)

Manifest-only. No sample moves, deletes, or renames. Human audition remains the promotion gate;
the audit's confidence bands decide what is trustworthy enough to act on without a full ear-check.

## Next

- Use `role-audit-latest.tsv` to drive the Octatrack export from the high-confidence clean pool.
- Fold the vote into device-crate selection (replace `_passes_kick_gate` reliance with the vote).
- Add a small labelled fixture set so the classifier's precision is regression-tested over time.
