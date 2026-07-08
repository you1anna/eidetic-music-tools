# High-Precision KICKS Gate Assessment

Date: 2026-07-08
Project: eidetic-music-tools
State: Active

## Assessment

`eidetic-music-tools` should stay Active, not Operationalising. The Active -> Operationalising gate is
not met because the current `sample-analyze` KICKS evidence failed the human role check: the KICKS
representatives included cymbal, snare, hihat, clap, a kick loop, bass material, and non-musical
impact/noise. That means the tool still cannot be trusted as a routine operating surface for sample
management.

The previous next move, adding external model repos, is rejected for this slice. It would add heavy
installs, possible model downloads, and long CPU-bound inference before proving that the local feature
stack has been used properly. The cleaner move is to make KICKS a high-precision gate using the
existing cached acoustic features and a small number of auditable, cheap tests.

## Recommendation

Hold project-state advancement. Advance inside Active with one safe pre-stage:

- design and then implement a manifest-only `sample-analyze` KICKS gate;
- prioritize high precision over high recall;
- classify `CURATED/KICKS` candidates into `likely_kick`, `review`, and `reject_as_kick`;
- exclude rejected rows from KICKS representatives and device crates;
- require a fresh Robin ear-check before any broader taxonomy rollout or file movement.

## Boundaries

This assessment does not authorize:

- sample moves, deletes, renames, or SSD cleanup;
- `sample-sort` / `sample-intake` changes;
- full-library heavy ML inference;
- installation of PANNs, YAMNet, CLAP, Basic Pitch, or ADTOF for the first KICKS pass.

Ask Robin before crossing any of those boundaries.

## Evidence

- Existing Tier-1 audio feature cache already records duration, attack, tail, low/sub/high ratios,
  centroid, flatness, onset density, and zero-crossing rate.
- The failure mode is false positives inside `CURATED/KICKS`, not a need for broad semantic discovery.
- Robin explicitly chose high precision: it is acceptable for real kicks to remain in `review`; it is
  not acceptable for non-kicks to become KICKS representatives.

## Next Move

Write the high-precision KICKS gate design, then implement it with tests against the known failed
examples and synthetic audio fixtures before touching real SSD outputs.
