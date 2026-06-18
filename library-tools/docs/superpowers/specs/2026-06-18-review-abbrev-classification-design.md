# Resolve the 3,898 `_REVIEW` files via token-aware abbreviation matching

Date: 2026-06-18
Status: Approved (design)
Tool affected: `sample-review` (`src/librarytools/review.py`, `src/librarytools/config.py`)

## Problem

A manifest-only review of `/Volumes/Extreme SSD/Production/SAMPLES` (16,181 files)
leaves **3,898 files (24%) in the low-confidence `_REVIEW` category**, every one
with `reason=unmatched`. They are concentrated in exactly two top-level folders:

- `DRUM-KITS/` — 2,098 files (Goldbaby SP-1200, Super Analog 909, TDM packs)
- `_PACKS/` — 1,800 files (mostly `_PACKS/Sean/` personal backup)

### Root cause

`classify_role` in `review.py` matches **substrings of full instrument words**
(`hat`, `clap`, `rim`, `snare`). The drum-machine packs name files with
**abbreviations** those rules never see:

| Token | Count (in unmatched names) | Correct role |
|-------|----------------------------|--------------|
| `hh`  | 631 | HATS-CYM (closed hat) |
| `hho` | 389 | HATS-CYM (open hat) |
| `cow` | 75  | PERC (cowbell) |
| `clave` | 72 | PERC |
| `rs`  | 55  | CLAP-SNARE (rimshot) |
| `block` | 46 | PERC |
| `tamb` | 41 | PERC (tambourine) |
| `cabasa` | 30 | PERC |

## Scope

**Analysis-only.** `sample-review` is manifest-only and moves/renames/deletes
nothing — that is a deliberate safety property given the SSD is exFAT with no
backup. This phase changes only how files are *categorized in the manifest*.
Physically relocating files into role folders is a separate, later decision and
would require a new move step; it is explicitly **out of scope** here.

No audio files are touched in this phase.

## Approach

**Token-aware keyword expansion.**

1. Refactor role matching so short instrument codes are matched at **token
   boundaries**, not as raw substrings. This is a correctness requirement, not a
   nicety: adding `hh`, `oh`, `ch`, `rs`, `bd` as raw substrings would mis-hit
   `chord`, `ohio`, `church`, etc. Token-boundary matching prevents false
   positives in the existing high-confidence categories.
2. Add a curated abbreviation set per role (see Tiers).
3. Re-run `lr --no-probe --summary` after each change to measure the `_REVIEW`
   count dropping. Iterate Tier 1 → Tier 2, then stop.

### Rejected alternatives

- **Probe every file's duration** (drop `--no-probe`): slow over thousands of
  files on exFAT, and only yields weak loop/one-shot labels — no instrument
  role. Lower value.
- **Folder → role mapping**: too coarse. Goldbaby folders interleave hats,
  perc, and toms in the same directory, so a folder-level rule mislabels.

## Tiers of outcome (honest about limits)

**Tier 1 — instrument abbreviations** (token-matched):
- HATS-CYM: `hh`, `hho`, `hhc`, `oh`, `ch` (open/closed hat), plus existing words
- CLAP-SNARE: `rs` (rimshot), existing `rim`/`snare`/`clap`
- PERC: `cow`, `clave`, `cabasa`, `conga`, `block`, `tamb`, `agogo`, `quijada`,
  `timbale`/`timb`, `tabla`, `triangle`/`tri`, `guiro`, `maraca`
Estimated resolution: **~1,749 files (~45% of the gap)**.

**Tier 2 — folder/context signals**: e.g. `AMEN BREAK` → DRUM-LOOPS, a few more
exotic perc tones. A few hundred additional files.

**Tier 3 — unclassifiable by name**: `_PACKS/Sean/*` cryptic personal samples
(`bob4.wav`, `mobb.wav`, `o.wav`, `b.wav`) have **no instrument tokens at all**.
These **stay in `_REVIEW`**. Rules will not be contorted to guess them; they need
ears or a future duration-probe pass.

## Implementation notes

- Short codes (≤3 chars: `hh`, `oh`, `ch`, `rs`, `bd`, `sd`, `tom`, `tri`) MUST
  match only as whole tokens. Longer unambiguous words (`cabasa`, `clave`,
  `tambourine`) may continue to use substring matching.
- Tokenization should reuse the existing path-normalisation (`_parts_text`
  already lowercases and replaces `_`/`.` with spaces); split on non-alphanumeric
  to get tokens.
- Precedence is preserved: drum-loop check first, then role rules in current
  order. New abbreviations slot into their existing role tuples.
- Drum-machine *model* tokens (`cr78`, `xd5`, `pb300`, `tr55`, `sp1200`) are
  noise for categorization and MUST NOT become keywords — they identify hardware,
  not instrument type.

## Testing (TDD)

Real sampled rows become fixtures, asserting `classify_role` output:

| Path fragment | Expected role |
|---------------|---------------|
| `SA909_HH/HH_909D2_AC_R6.wav` | HATS-CYM |
| `SA909_HH/HHo_909D2_AC_R2.wav` | HATS-CYM |
| `CR-78/CR78_Clave_T1S_R1.wav` | PERC |
| `RX-5/RX5_CowHigh_C2A.wav` | PERC |
| `Cabasa_727TR1_SP1200R.wav` | PERC |
| `Sean 80s/o.wav` | _REVIEW (unchanged) |
| `Sean/cloud 909/dms2.wav` | _REVIEW (unchanged) |

Plus regression assertions: a token like `chord` must NOT classify as HATS via
`ch`, and `ohio`-style names must NOT hit `oh`.

## Success criteria

- `_REVIEW` count drops from 3,898 to **≈2,000 or below**.
- Zero false positives introduced into existing high-confidence categories
  (spot-check the regenerated `index-latest/high-confidence/*.tsv`).
- All new rules covered by tests; existing tests still pass.
