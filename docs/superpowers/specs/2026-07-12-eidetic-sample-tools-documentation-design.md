# Eidetic Sample Tools Documentation Design

**Date:** 2026-07-12  
**Status:** Approved for specification  
**Scope:** Documentation and product metadata only

## Purpose

Rework the repository documentation so it is clean, concise, professional and
written in plain English. Establish **Eidetic Sample Tools** as the
customer-facing product name while retaining `eidetic-music-tools` as the
repository name.

The repository will remain a serious personal system in the short to medium
term. This work should reveal its future product value without pretending that
it is finished commercial software or forcing an early business model.

## Audience

The primary audience is hardware-based electronic musicians who manage large
sample libraries and need to prepare trusted material for performance hardware.

The first supported context remains the current studio: Octatrack MKII,
Digitakt MKI and TR-8S. Portable instructions should lead; Robin's paths,
profiles and operating notes should remain available as clearly labelled
examples.

## Product Promise

> Eidetic Sample Tools helps hardware-based electronic musicians organise large
> sample libraries, curate trusted collections by ear, and prepare samples for
> performance hardware.

The documentation should make four promises clear:

1. Organise large sample libraries without destructive surprises.
2. Keep human listening and approval at the centre.
3. Prepare curated material for specific hardware correctly.
4. Preserve manifests, hashes and undo records so decisions remain traceable.

## Product Posture

Present the repository as a capable CLI toolkit and the foundation of a
possible future paid product. Do not make claims about pricing, commercial
availability, adoption or release dates.

Source visibility must not be described as an open-source licence. Licensing
remains undecided and is outside this documentation pass.

Productisation means improving boundaries, consistency, reliability and
presentation. It does not mean hiding personal context or research work.

## Information Architecture

### Root documentation

- `README.md` is the product landing page and shortest route to value. It
  explains the problem, audience, current capability, safety model, supported
  hardware, safe first run and next documentation links.
- `STATUS.md` is a concise operational snapshot. It records what works, what is
  experimental, what has been applied to the live library and what should
  happen next.

### User guides

- `docs/GETTING-STARTED.md` covers prerequisites, installation, portable
  configuration and a safe first dry run.
- `docs/WORKFLOWS.md` explains the organise, curate and export workflows.
- `docs/SAFETY.md` explains dry runs, manifests, content hashes, human approval,
  apply steps, undo records and the limits of automation.
- `docs/ROADMAP.md` states the product direction and links to active beta and
  research work without promising delivery dates.

### Command references

- `library-tools/README.md` becomes the focused command reference for library
  review, organisation, curation and analysis.
- `sample-tools/README.md` becomes the focused command reference for validated,
  device-aware export.

### Engineering history

- `decisions/` remains the record of adopted, rejected and downgraded
  approaches.
- `docs/superpowers/specs/` and `docs/superpowers/plans/` remain visible as the
  design and implementation history.
- The root README contains a compact Research and beta work section that points
  users to `STATUS.md`, `decisions/` and the active specifications.

The two existing workflow documents will be consolidated into the new user
guides where that removes duplication. Personal or historical information that
remains useful will be retained in clearly labelled sections or redirected to
the new canonical guide.

## Content Model

Documentation will label capabilities consistently:

- **Stable:** used in the current personal workflow and covered by tests.
- **Beta:** implemented and usable, but still being calibrated or refined.
- **Experimental:** research capability whose output requires extra scrutiny.
- **Planned:** specified or proposed, but not implemented.
- **Retired:** retained for historical context and no longer recommended.

The main README will distinguish working features from experimental and planned
work. Experimental work stays in plain sight but does not interrupt the safe
getting-started path.

Failed or downgraded research remains visible in the decision record. The
user-facing explanation should state the practical conclusion in plain terms;
for example, automated labels are suggestions and never replace listening.

## Writing Standard

- Use plain-spoken English, short paragraphs and task-led headings.
- Lead with user outcomes, followed by the necessary technical detail.
- Use lists for sequences and options; use tables only for genuine comparison.
- Define specialist terms on first use.
- Keep commands close to the explanation of their effect and safety level.
- Avoid inflated claims, vague adjectives and marketing filler.
- Avoid repeating the same workflow across several files. Link to one canonical
  explanation instead.
- Use `Eidetic Sample Tools` for the product and `eidetic-music-tools` only when
  referring to the repository or filesystem path.

## Safety and Error Communication

Every workflow must state whether a command is read-only, a dry run, writes
derived files, copies audio or moves audio. Apply steps must be visually and
verbally distinct from preview steps.

Documentation must not imply that classification confidence equals musical or
semantic correctness. Human audition remains the final gate for curation,
reclassification and hardware crates.

Machine-specific paths must be labelled as examples. Portable environment
variables, profiles or command arguments should be the default explanation.

## Implementation Scope

This pass will:

- rewrite the root README;
- add the four user guides;
- tighten the two package READMEs;
- rewrite the status page;
- consolidate duplicated workflow material;
- update Python package descriptions for consistent product language;
- add and apply the maturity legend; and
- correct broken local documentation links found during the work.

This pass will not:

- change CLI behaviour;
- move, copy, convert or delete audio;
- run a live library migration;
- remove research specifications, plans or decisions;
- choose or add a software licence;
- introduce pricing or commercial claims; or
- package a graphical or paid product.

## Verification

Before completion:

1. Check every local Markdown link and heading anchor.
2. Compare documented commands and flags with the current CLI `--help` output.
3. Scan for stale product names, unexplained personal paths, repeated guidance
   and contradictory safety claims.
4. Run the `library-tools` and `sample-tools` test suites.
5. Review Markdown heading order, paragraph length, tables and code blocks for
   clear rendering.
6. Confirm that research, beta work and personal operating context remain easy
   to find.

## Acceptance Criteria

- A new reader can explain the product, intended user and safety model after
  reading the root README.
- A user can install the tools and complete a read-only or dry-run first use
  without relying on Robin's filesystem layout.
- Stable, beta, experimental, planned and retired work are clearly separated.
- Current personal workflows remain documented and usable.
- Research and decision history remains visible from the main documentation.
- No documentation claims exceed the behaviour supported by the code or tests.
