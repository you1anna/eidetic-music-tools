# Studio-aware sample foundation

The canonical catalogue, curation and export sequence now lives in
[Workflows](WORKFLOWS.md). Read [Getting started](GETTING-STARTED.md) for portable
setup and the [Safety model](SAFETY.md) before applying the migration.

This page preserves the profile checks that are specific to the current Eidetic
studio.

## Current profile

The `eidetic-studio` profile describes software-actionable capabilities for
Octatrack MKII, Digitakt MKI and TR-8S. It deliberately omits patchbay detail,
purchases and physical build work.

Select it locally:

```toml
# ~/.config/eidetic-music-tools/config.toml
profile = "eidetic-studio"
```

Selection order is command-line `--profile`, `MUSIC_TOOLS_PROFILE`, local
configuration, then the built-in default.

## Check against the Studio Knowledge Base

```bash
sample-profile show --profile eidetic-studio
sample-profile validate \
  --profile eidetic-studio \
  --source-kb "/Users/macmini/Projects/Production/Studio/eidetic-studio-knowledge-base-v2_4.md"
```

Validation reads only the document version and update-date header. It does not
walk the Studio `archive/` directory. The external knowledge base remains the
authority for physical wiring.

## Current operating state

Portable profiles, content-hash inventory, catalogue planning, human-gated
promotion and profile-aware exports are implemented. The live SSD migration and
foundation-v1 ear review have not yet been applied. Follow [`STATUS.md`](../STATUS.md)
for the current next action rather than treating this page as a run log.
