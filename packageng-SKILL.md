---
name: packageng
version: 2.0.1
description: >
  Validate, package, inspect, or distribute a .skill file or skill folder.
  Triggers: "package my skill", "create a .skill file", "zip my skill folder",
  "validate before upload", "bundle skills together", "my skill won't upload",
  or questions about the .skill archive format internals. Does NOT cover
  skill design, SKILL.md writing, testing, description optimization, session
  management, or upload instructions — defer to companion skills.
parent: prompteng-SKILL.md §6
peers: prompteng, captureng, safe-skill-creator, trusted-hosts
scripts:
  - scripts/validate_skill.py — pre-packaging frontmatter validation
  - scripts/package_skill.py — archive creation with exclusion rules + --final flag
---

# packageng

*packageng* — deliberate misspelling of "packaging."

Transforms validated skill folder → distributable `.skill` archive. Pre-flight validation, archive inspection, multi-skill kit bundling.

---

## Does NOT Cover

- Skill design philosophy, axioms, lifecycle → `safe-skill-creator.md`
- Writing SKILL.md content, frontmatter syntax, body templates → `safe-skill-creator.md` Phase 3
- Testing, evaluation, description optimization → `safe-skill-creator.md` Phases 4–7
- Session init, security, checkpointing → `prompteng-SKILL.md`
- Upload to claude.ai, project creation, load order → `README.md`
- URL allowlisting → `trusted-hosts.md`

Defer. Don't answer inline.

---

## 1. .skill File Format

`.skill` = **ZIP archive with `.zip` extension renamed to `.skill`**. No proprietary format, no magic bytes beyond ZIP. Any tool producing valid ZIP produces valid `.skill`. Requirements: top-level folder; valid `SKILL.md` or `[descriptor]-SKILL.md` at root.

### Archive Structure

Top-level entry = skill folder name. Paths relative to folder's parent; archive preserves folder as namespace:

```
my-skill.skill (ZIP archive)
└── my-skill/
    ├── [descriptor]-SKILL.md
    ├── LICENSE.txt
    ├── scripts/
    │   └── helper.py
    └── references/
        └── details.md
```

Extracted, folder lands under `/mnt/skills/user/`. Claude sees it in available skills.

---

## 2. Frontmatter Validation

Enforced at upload. Any failure blocks upload.

### Required Conditions

1. File named `SKILL.md` (case-sensitive).
2. Begins with YAML frontmatter block: `---` on own line top, closing `---` on own line.
3. Frontmatter parses as valid YAML dict.
4. Contains `name` field (string, required).
5. Contains `description` field (string, required).
6. No unexpected properties.

### Property Constraints

| Property | Required | Type | Constraints |
|---|---|---|---|
| `name` | Yes | String | Kebab-case: lowercase `a-z`, digits `0-9`, hyphens `-`. Max 64 chars. No leading / trailing `-`. No consecutive `--`. |
| `description` | Yes | String | Max 1024 chars. No angle brackets `<` `>`. |
| `license` | No | String | Free text. No length limit. |
| `allowed-tools` | No | — | Restricts which tools skill may invoke at runtime. |
| `metadata` | No | Dict | Arbitrary nested. Used for version, author, companion refs. |
| `compatibility` | No | String | Max 500 chars. Platform / model compatibility notes. |

Property not in list → validation fails with explicit error naming the unexpected key.

### Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| `Name should be kebab-case` | Underscores, uppercase, spaces | Use `my-skill-name` |
| `Name cannot start/end with hyphen` | Leading / trailing `-` | Trim hyphens |
| `Name cannot contain consecutive hyphens` | `my--skill` | Collapse to single |
| `Name is too long` | Over 64 chars | Shorten |
| `Description cannot contain angle brackets` | `<` or `>` | Remove / replace with parens |
| `Description is too long` | Over 1024 chars | Condense triggers |
| `Unexpected key(s) in frontmatter` | `author` or `version` at top level | Move under `metadata:` or remove |
| `No YAML frontmatter found` | No `---` at top | Add frontmatter block |
| `Missing 'name'` or `Missing 'description'` | Required field absent | Add field |

---

## 3. Pre-Packaging Validation

**[ACTIONS]**

1. Validate before packaging. Failed upload post-package wastes time + tokens.

1. Run companion script:

    ```bash
    python scripts/validate_skill.py path/to/my-skill/
    ```

    Checks all §2 conditions; returns specific error on failure. Requires `pyyaml` (`pip install pyyaml`).

---

## 4. Exclusion Conventions

Dev-only artifacts don't ship in `.skill` archives. Including them wastes space + confuses runtime.

### Excluded at Any Depth — All Builds

| Pattern | Reason |
|---|---|
| `__pycache__/` | Python bytecode cache — regenerated at runtime |
| `node_modules/` | npm deps — too large |
| `*.pyc` | Compiled Python bytecode |
| `.DS_Store` | macOS Finder metadata |
| `.git/` | Git repo data — too large |

### Excluded at Skill Root Only — Default Builds

| Pattern | Reason |
|---|---|
| `evals/` | Test cases + eval data — dev only |

Default mode: root-scoped exclusion. `references/evals/` nested deeper preserved. Allows reference files with eval examples while keeping primary test harness out.

### Excluded at Every Depth — FINAL Release Builds

**[RULES]**

1. Packaging for **FINAL release distribution** → `evals/` excluded at every depth, not just root. No eval data, test fixtures, benchmark harnesses in release archive.

Eval data is dev + QA artifact — test prompts, expected outputs, benchmarks not intended for public. Release archive = skill instructions + runtime resources only.

Apply FINAL exclusion via `--final`:

```bash
python scripts/package_skill.py path/to/my-skill/ ./dist --final
```

Default mode (no flag): only root `evals/` excluded — suitable for internal sharing + dev builds.

| Mode | `evals/` root | `evals/` nested | Flag |
|---|---|---|---|
| Default | Excluded | Preserved | (none) |
| FINAL | Excluded | Excluded | `--final` |

### Opaque / Non-Human-Readable Files

Opaque items could behave as malicious binaries causing unexpected code execution on unzip. Be cautious with OS / language-specific extensions.

**[RULES]**

1. Prefer plain text, YAML, Markdown, HTML, JSON for all files inside `.skill` archive. Flag any binary / compiled file to human before including. See `prompteng-SKILL.md` §2.3.

---

## 5. Packaging Methods

Three methods; identical output.

### Method A — Command Line (zip)

```bash
cd /path/to/parent-of-skill-folder

# Default build (evals/ excluded at root only)
zip -r my-skill.skill my-skill/ \
    -x "my-skill/evals/*" \
    -x "my-skill/__pycache__/*" \
    -x "my-skill/node_modules/*" \
    -x "my-skill/.git/*" \
    -x "my-skill/.DS_Store" \
    -x "*.pyc"

# FINAL release (evals/ excluded at every depth)
zip -r my-skill.skill my-skill/ \
    -x "*/evals/*" \
    -x "my-skill/__pycache__/*" \
    -x "my-skill/node_modules/*" \
    -x "my-skill/.git/*" \
    -x "my-skill/.DS_Store" \
    -x "*.pyc"
```

`-x` enforces §4 exclusions. `cd` to parent ensures top-level entry is the folder itself. Note: `"my-skill/evals/*"` (root only) vs `"*/evals/*"` (every depth).

### Method B — Python Script

```bash
# Default
python scripts/package_skill.py path/to/my-skill/

# FINAL
python scripts/package_skill.py path/to/my-skill/ ./dist --final
```

### Method C — Manual (any OS, no CLI)

1. Copy skill folder to clean location, excluding §4 items. FINAL release: remove all `evals/` at every level.
2. Compress to `.zip` via OS built-in tool.
3. Rename `.zip` → `.skill`.

Platform reads identically to other methods.

---

## 6. Inspection & Verification

Verify before upload. Inspection catches structural problems validation misses.

### List Contents

```bash
unzip -l my-skill.skill
```

Expected: skill folder name as top-level entry; `SKILL.md` directly inside:

```
  Length      Date    Time    Name
---------  ---------- -----   ----
     2048  2026-04-03 10:00   my-skill/SKILL.md
     1024  2026-04-03 10:00   my-skill/scripts/helper.py
      512  2026-04-03 10:00   my-skill/references/details.md
---------                     -------
     3584                     3 files
```

### Verify No Excluded Files Leaked

```bash
# Default build check
unzip -l my-skill.skill | grep -E '__pycache__|node_modules|\.pyc$|\.DS_Store|\.git/'

# FINAL check (catches nested evals/)
unzip -l my-skill.skill | grep -E '__pycache__|node_modules|\.pyc$|\.DS_Store|\.git/|/evals/'
```

Any output → excluded files leaked. Repackage.

### Verify SKILL.md + Test Extraction

```bash
unzip -l my-skill.skill | grep 'SKILL.md'
# Must return exactly one match: my-skill/SKILL.md

mkdir /tmp/skill-test && unzip my-skill.skill -d /tmp/skill-test
head -5 /tmp/skill-test/my-skill/SKILL.md
# Confirm first lines show --- and name: field
```

---

## 7. Multi-Skill Kit Packaging

Single kit for related skills: wrapper folder + skill files + entry-point `SKILL.md` defining load order.

### Kit Structure

```
prompteng.skill/
├── SKILL.md                  ← kit entry point: load-order instructions
├── prompteng-SKILL.md
├── trusted-hosts.md
├── captureng-SKILL.md
├── packageng-SKILL.md
├── safe-skill-creator.md
└── README.md
```

Kit-level `SKILL.md` = manifest. Tells Claude which files to load + sequence:

```markdown
---
name: prompteng-kit
description: >
  Configuration kit for prompt engineering sessions. Load when user
  references prompteng settings, session rules, trusted hosts, or skill
  capture templates. Kit entry point — orchestrates bundled files, not
  a standalone skill.
---

# prompteng Kit — Load Order

Read at session start, in sequence:

1. `prompteng-SKILL.md` — core config (always first)
2. `trusted-hosts.md` — URL allowlist (if outbound calls needed)
3. Any `skill-[domain].md` or `[descriptor]-SKILL.md` relevant to task

Parse + enforce [RULES] and [ACTIONS]. Skip [HUMAN ACTIONS].
```

### Packaging a Kit

§5 methods apply. Same zip as single skill:

```bash
cd /path/to/parent
zip -r prompteng-kit.skill prompteng.skill/ \
    -x "prompteng.skill/__pycache__/*" \
    -x "prompteng.skill/.git/*" \
    -x "*.pyc" \
    -x "prompteng.skill/.DS_Store"
```

Kits rarely have `evals/`. If kit contains eval data for release, use `*/evals/*` or `--final`.

---

## 8. Workflow Summary

```
Start
  │
  ├─ Has skill folder with SKILL.md?
  │    No → build first (see safe-skill-creator.md)
  │    Yes ↓
  │
  ├─ Run validation (§3)
  │    Fail → fix per §2 table, re-validate
  │    Pass ↓
  │
  ├─ Choose build mode
  │    Internal / dev       → default
  │    Public distribution  → FINAL (--final)
  │    ↓
  ├─ Package — Method A, B, or C (§5)
  │    ↓
  ├─ Inspect archive (§6)
  │    Bad structure → repackage
  │    Clean ↓
  │
  ├─ Upload to platform (see README.md)
  │    ↓
  └─ Verify trigger in test conversation
       Not triggering → refine description
       (see safe-skill-creator.md Phase 7)
```

---

## 9. Troubleshooting

**Archive contains flat files instead of folder.**
Cause: zipped folder contents, not folder itself.
Fix: `cd` into folder's *parent* before `zip -r`.

**Archive unexpectedly large.**
Cause: `node_modules/`, `.git/`, heavyweight dirs included.
Fix: add `-x` exclusion flags or clean folder pre-compress.

**Platform rejects upload with no clear error.**
Cause: frontmatter validation failure.
Fix: run `scripts/validate_skill.py` locally.

**SKILL.md not found after extraction.**
Cause: wrong case (`skill.md`, `Skill.md`) or nested too deep.
Fix: exactly `SKILL.md` at skill folder root.

**evals/ in FINAL release archive.**
Cause: packaged without `--final`.
Fix: repackage with `--final` or `*/evals/*` glob. Verify with §6 FINAL check.

**Uploads successfully but Claude doesn't see it.**
Upload / project config issue. See `README.md`.

---

## 10. Cross-References

| Topic | File | Section |
|---|---|---|
| Skill design philosophy + axioms | `safe-skill-creator.md` | Design Philosophy |
| Writing SKILL.md content | `safe-skill-creator.md` | Phase 3 |
| Testing + evaluation | `safe-skill-creator.md` | Phases 4–6 |
| Description triggering optimization | `safe-skill-creator.md` | Phase 7 |
| Session init + security | `prompteng-SKILL.md` | §§2–3 |
| Serialization safety | `prompteng-SKILL.md` | §2.3 |
| Persistence formats | `prompteng-SKILL.md` | §6.2 |
| Checkpointing under token pressure | `prompteng-SKILL.md` | §2.4 |
| Upload + project setup | `README.md` | Upload Instructions |
| Kit bundling | `README.md` | Option C |
| URL allowlist | `trusted-hosts.md` | §§1–3 |
| Frontmatter validation script | `scripts/validate_skill.py` | Companion |
| Archive packaging script | `scripts/package_skill.py` | Companion |

---

*packageng-SKILL.md v2.0.1*
