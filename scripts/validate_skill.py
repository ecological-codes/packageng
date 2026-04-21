#!/usr/bin/env python3
"""
Validate a skill folder before packaging.

Checks SKILL.md frontmatter against platform validation rules:
  - YAML frontmatter present and parseable
  - Required fields: name, description
  - Allowed properties only (name, description, license, allowed-tools, metadata, compatibility)
  - Name: kebab-case, max 64 chars, no leading/trailing/consecutive hyphens
  - Description: max 1024 chars, no angle brackets
  - Compatibility: max 500 chars (if present)

Dependency: pyyaml (pip install pyyaml)

Usage:
    python validate_skill.py <skill-folder-path>

Example:
    python validate_skill.py ./my-skill/

Exit codes:
    0 = valid
    1 = invalid or error

Reference: packageng-SKILL.md — Section 2 (Frontmatter Validation Rules)
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ Missing dependency: pyyaml. Install with: pip install pyyaml")
    sys.exit(1)

ALLOWED_KEYS = {
    'name', 'description', 'license', 'allowed-tools',
    'metadata', 'compatibility'
}


def validate(skill_path):
    """
    Validate a skill folder's SKILL.md frontmatter.

    Args:
        skill_path: Path to the skill folder (not the SKILL.md file itself).

    Returns:
        Tuple of (is_valid: bool, message: str).
    """
    skill_path = Path(skill_path)
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    try:
        fm = yaml.safe_load(match.group(1))
        if not isinstance(fm, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {e}"

    unexpected = set(fm.keys()) - ALLOWED_KEYS
    if unexpected:
        return False, (
            f"Unexpected key(s): {', '.join(sorted(unexpected))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_KEYS))}"
        )

    if 'name' not in fm:
        return False, "Missing 'name'"
    if 'description' not in fm:
        return False, "Missing 'description'"

    name = str(fm['name']).strip()
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name '{name}' must be kebab-case (a-z, 0-9, hyphens)"
    if name.startswith('-') or name.endswith('-') or '--' in name:
        return False, f"Name '{name}': no leading/trailing/consecutive hyphens"
    if len(name) > 64:
        return False, f"Name too long ({len(name)} chars, max 64)"

    desc = str(fm['description']).strip()
    if '<' in desc or '>' in desc:
        return False, "Description cannot contain angle brackets"
    if len(desc) > 1024:
        return False, f"Description too long ({len(desc)} chars, max 1024)"

    compat = fm.get('compatibility', '')
    if compat:
        if not isinstance(compat, str):
            return False, f"Compatibility must be a string, got {type(compat).__name__}"
        if len(str(compat)) > 500:
            return False, f"Compatibility too long ({len(str(compat))} chars, max 500)"

    return True, "Valid"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_skill.py <skill-folder-path>")
        print("Example: python validate_skill.py ./my-skill/")
        sys.exit(1)
    ok, msg = validate(sys.argv[1])
    print(f"{'✅' if ok else '❌'} {msg}")
    sys.exit(0 if ok else 1)
