#!/usr/bin/env python3
"""
Package a validated skill folder into a distributable .skill archive.

Creates a ZIP archive with the .skill extension, applying exclusion
conventions from packageng-SKILL.md Section 4.

Two packaging modes:
  DEFAULT mode  — excludes evals/ at the skill root only.
                  Nested evals/ (e.g., references/evals/) is preserved.
                  Use this for development builds and internal sharing.

  FINAL mode    — excludes evals/ at EVERY depth in the skill tree.
  (--final)       No evaluation data ships in the archive at all.
                  Use this for public distribution and release builds.

Always excluded (both modes):
  __pycache__/, node_modules/, *.pyc, .DS_Store, .git/

Usage:
    python package_skill.py <skill-folder> [output-dir] [--final]

Examples:
    python package_skill.py ./my-skill/
    python package_skill.py ./my-skill/ ./dist
    python package_skill.py ./my-skill/ ./dist --final

Exit codes:
    0 = success
    1 = error

Reference: packageng-SKILL.md — Sections 4–5
"""

import fnmatch
import sys
import zipfile
from pathlib import Path

# --- Exclusion rules ---

# Excluded at any depth, in all modes.
EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}

# Excluded at the skill root only (default mode).
ROOT_EXCLUDE_DIRS = {"evals"}

# Excluded at every depth (--final mode only).
FINAL_EXCLUDE_DIRS = {"evals"}


def should_exclude(rel_path, final=False):
    """
    Check if a file path should be excluded from the archive.

    Args:
        rel_path: Path relative to skill_path.parent (so parts[0] is the
                  skill folder name, parts[1] is the first child, etc.).
        final:    If True, apply FINAL release rules — evals/ excluded at
                  every depth, not just the skill root.

    Returns:
        True if the file should be excluded.
    """
    parts = rel_path.parts

    # Always-exclude directories (any depth).
    if any(part in EXCLUDE_DIRS for part in parts):
        return True

    # evals/ handling depends on mode.
    if final:
        # FINAL mode: exclude evals/ at every depth.
        if any(part in FINAL_EXCLUDE_DIRS for part in parts):
            return True
    else:
        # Default mode: exclude evals/ only at skill root (parts[1]).
        if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
            return True

    # Excluded individual files.
    if rel_path.name in EXCLUDE_FILES:
        return True

    # Excluded file patterns.
    return any(fnmatch.fnmatch(rel_path.name, p) for p in EXCLUDE_GLOBS)


def package(skill_path, output_dir=".", final=False):
    """
    Package a skill folder into a .skill ZIP archive.

    Args:
        skill_path: Path to the skill folder.
        output_dir: Directory where the .skill file will be written.
        final:      If True, apply FINAL release exclusion rules.

    Returns:
        Path to the created .skill file, or None on error.
    """
    skill_path = Path(skill_path).resolve()
    if not skill_path.is_dir():
        print(f"❌ Not a directory: {skill_path}")
        return None
    if not (skill_path / "SKILL.md").exists():
        print(f"❌ SKILL.md not found in {skill_path}")
        return None

    out = Path(output_dir).resolve() / f"{skill_path.name}.skill"
    Path(output_dir).resolve().mkdir(parents=True, exist_ok=True)

    mode_label = "FINAL" if final else "DEFAULT"
    print(f"📦 Packaging [{mode_label}]: {skill_path.name}")

    added = 0
    skipped = 0

    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_path.rglob('*')):
            if not f.is_file():
                continue
            arcname = f.relative_to(skill_path.parent)
            if should_exclude(arcname, final=final):
                print(f"  Skipped: {arcname}")
                skipped += 1
                continue
            zf.write(f, arcname)
            print(f"  Added:   {arcname}")
            added += 1

    print(f"\n✅ Packaged → {out}")
    print(f"   {added} files added, {skipped} excluded")
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]

    if len(args) < 1:
        print("Usage: python package_skill.py <skill-folder> [output-dir] [--final]")
        print()
        print("Options:")
        print("  --final    Exclude evals/ at every depth (release build)")
        print()
        print("Examples:")
        print("  python package_skill.py ./my-skill/")
        print("  python package_skill.py ./my-skill/ ./dist")
        print("  python package_skill.py ./my-skill/ ./dist --final")
        sys.exit(1)

    skill_folder = args[0]
    output = args[1] if len(args) > 1 else "."
    is_final = "--final" in flags

    result = package(skill_folder, output, final=is_final)
    sys.exit(0 if result else 1)
