# packageng

Skill validation + packaging for `[descriptor]-SKILL.md` files. Transforms validated skill folder → distributable `.skill` archive. Pre-flight validation, archive inspection, multi-skill kit bundling.

## Set of Files

| File | Purpose |
|---|---|
| `SKILL.md` | Router — load order |
| `packageng-SKILL.md` | Content — format, validation rules, packaging workflow |
| `scripts/validate_skill.py` | Pre-package frontmatter validation, very shallow, doesn't validate the operational codes in the skill file |
| `scripts/package_skill.py` | Archive creation with `--final` flag |
| `packageng.skill` | Packaged archive for upload to SKILL directory |
| `.github/workflows/build-skill.yml` | CI workflow — auto-builds and publishes `packageng.skill` on push |
| `README.md` | Explanatory instructions and overview for this software package |

## Install

- **claude.ai web platform:** upload `packageng.skill` via skill settings (recommended). Or add `packageng-SKILL.md` contents to Personal Preferences via `Settings > General`.

- **Claude Code desktop app:** copy contents of this folder into `~/.claude/skills/packageng/`.

- **Other platforms:** adapt this set of files to your `harness+model`. Star or Fork the git repo if you like. 

## Quick Use

```bash
python scripts/validate_skill.py path/to/my-skill/
python scripts/package_skill.py path/to/my-skill/ ./dist          # dev build
python scripts/package_skill.py path/to/my-skill/ ./dist --final  # release build
```

`.skill` = ZIP archive with `.zip` extension renamed. No proprietary format.

## When It Triggers

- "build .skill file", "package the skill for release", "bundle this skill folder"
- "create a kit including these skills"
- "unpack this .skill file", "validate this SKILL.md"
- "dry run building the skill package", "edit this .skill file for final release"
- "check for leaks in this .skill file", "is this skill package safe for use"

## Peer Skills

Load on demand when task requires:

- **[prompteng](https://github.com/ecological-codes/prompteng)** — main set of rules + framework for doing better prompt engineering
- **[captureng](https://github.com/ecological-codes/captureng)** — session-knowledge capture, CHECKPOINT mode
- **[safe-skill-creator](https://github.com/ecological-codes/safe-skill-creator)** — skill design + iteration

## Companion Files

Available in - **[ecological-codes/user-prefs](https://github.com/ecological-codes/user-prefs)**

- `agent.md` 

- `trusted-hosts.md` 

## Style Convention

Directives use the following section headers with numbered lists, shared across peer skills: 

- **[RULES]** — enforceable constraints applied at runtime.
- **[ACTIONS]** — autonomous steps agent executes in normal workflow.
- **[HUMAN ACTIONS]** — UI actions; agent skips, cannot delegate.

## License

See [LICENSE](./LICENSE). (C) Copyright 2026 - Sameer Khan - Various and Several Rights Reserved.

---
README.md v2.2.1 - Human Approved
