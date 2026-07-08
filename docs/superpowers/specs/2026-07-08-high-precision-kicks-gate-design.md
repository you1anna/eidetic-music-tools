# High-Precision KICKS Gate Design

Date: 2026-07-08
Project: eidetic-music-tools
Status: Draft for review

## Goal

Fix KICKS first. The tool should stop treating contaminated `CURATED/KICKS` rows as trustworthy just
because they live in the KICKS folder or include stale `kick-` filename prefixes.

The first pass optimizes for precision: a file should enter `likely_kick` only when cheap local
evidence strongly supports it. Real kicks that are unusual or ambiguous can remain in `review`.

## Non-Goals

- No sample moves, deletes, renames, or SSD cleanup.
- No broad taxonomy redesign.
- No external ML/model stack in the first pass.
- No full-library classifier. KICKS is the proving ground; wider roles come later if this works.

## Output

`sample-analyze` writes a new manifest:

```text
library-tools/manifests/sample-intelligence-pilot/kick-audit-latest.tsv
```

Required columns:

- `path`
- `current_role`
- `sample_type`
- `duration_s`
- `attack_ms`
- `tail_ms`
- `sub_ratio`
- `low_ratio`
- `mid_ratio`
- `high_ratio`
- `centroid_hz`
- `flatness`
- `onset_density`
- `zcr`
- `kick_gate`
- `confidence`
- `reasons`
- `review_action`

`kick_gate` values:

- `likely_kick`
- `review`
- `reject_as_kick`

## Gate Logic

The KICKS gate is a small evidence ladder over existing cached features.

Strong reject evidence:

- long loop or one-shot-role duration evidence: long duration, long tail, or high onset density;
- high-frequency dominant profile consistent with hat/cymbal/noise rather than kick;
- obvious sustained tonal/pitched profile: long stable body with weak transient and little kick-like
  low-end concentration;
- existing curated-role conflict signals for clap, snare, hat/cymbal, bass, synth, FX, vocal, or
  drum-loop material.

Likely-kick evidence:

- short or compact duration;
- fast attack;
- meaningful low/sub energy;
- high enough crest/transient character;
- not high-frequency dominant;
- low onset density;
- no conflicting role signals.

Review evidence:

- missing decode/audio features;
- weak but not disqualifying low-end;
- borderline duration or tail;
- mixed evidence where a musical kick may still be present but precision is not high enough.

The exact numeric thresholds should be introduced through tests and tuned against the known failed
KICKS representatives plus synthetic fixtures. Do not invent magic constants without a fixture or
real example that motivates them.

## Integration Points

Add focused code near `librarytools.analyze` rather than changing `sample-review`, `sample-sort`, or
`sample-intake`.

Expected functions:

- `kick_gate(row: FeatureRow) -> KickGateRow`
- `kick_audit(rows: list[FeatureRow]) -> list[KickGateRow]`
- `write_kick_audit(path: Path, rows: list[KickGateRow]) -> None`

`cluster_within_role` and crate selection should treat `reject_as_kick` rows like curated-role
conflicts for KICKS: they remain visible in manifests but cannot become KICKS representatives or
device picks. `review` rows may be excluded from representative picks for the first high-precision
pass unless Robin explicitly asks for a recall-oriented audit.

## Testing

Use tests before real SSD runs.

Required test cases:

- known bad KICKS examples are rejected or routed to review: clap/snare, hat/cymbal, kick loop,
  bass/synth, long impact/noise;
- a synthetic short low-frequency transient is `likely_kick`;
- a synthetic high-frequency transient is `reject_as_kick` or `review`, not `likely_kick`;
- a synthetic loop/multiple-onset file is not `likely_kick`;
- missing audio features produce `review`, not a confident pass;
- `kick-audit-latest.tsv` is written by the pilot command;
- KICKS clusters/crates exclude `reject_as_kick`.

## Success Criteria

The first real run succeeds only if:

- it writes `kick-audit-latest.tsv`;
- no sample files are moved;
- the regenerated KICKS audition packet draws only from `likely_kick`;
- Robin ear-checks the new KICKS representatives and confirms that non-kicks are no longer being
  presented as KICKS representatives.

If the new gate is too strict, loosen it only from concrete false-negative examples, not from a desire
to fill every cluster.

## Wider Rollout

After KICKS passes by ear, generalize the pattern role by role:

- define the role-specific high-precision evidence;
- write the audit manifest;
- exclude rejects from representatives/crates;
- audition;
- only then consider physical reclassification manifests.
