---
name: packageng
description: >
  Use when user wants to validate, package, inspect, or distribute a `.skill` file.
metadata:
  version: "2.0.0"
  maintainer: "Human user"
  parent: "prompteng/prompteng-SKILL.md"
  scripts:
    - "scripts/validate_skill.py — pre-packaging frontmatter validation"
    - "scripts/package_skill.py — archive creation with --final flag"
---

# packageng — Load Order

1. `packageng-SKILL.md` — validation rules, packaging workflow, distribution
   checklist. Parse + enforce all `[RULES]` directives.

## Companion Scripts

1. `scripts/validate_skill.py` — run before packaging.
2. `scripts/package_skill.py` — create `.skill` archives. Supports `--final`.

---

*packageng v2.0.0 — standalone skill.*
