#!/usr/bin/env python3
"""Validate all root-level skill directories in the presto-skills monorepo."""

import re
import sys
from pathlib import Path

import yaml


def find_skill_dirs(repo_root: Path) -> list[Path]:
    """Find directories at repo root that contain SKILL.md."""
    skills = []
    for child in sorted(repo_root.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            skills.append(child)
    return skills


def validate_skill(skill_path: Path) -> list[str]:
    """Validate a single skill directory. Returns list of errors."""
    errors = []
    name = skill_path.name

    # 1. SKILL.md exists and has valid frontmatter
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"[{name}] SKILL.md not found")
        return errors

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        errors.append(f"[{name}] No YAML frontmatter in SKILL.md")
        return errors

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        errors.append(f"[{name}] Invalid frontmatter format")
        return errors

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        errors.append(f"[{name}] Invalid YAML in frontmatter: {e}")
        return errors

    if not isinstance(frontmatter, dict):
        errors.append(f"[{name}] Frontmatter must be a YAML dictionary")
        return errors

    if "name" not in frontmatter:
        errors.append(f"[{name}] Missing 'name' in frontmatter")
    elif not isinstance(frontmatter["name"], str) or not re.match(r"^[a-z0-9-]+$", frontmatter["name"]):
        errors.append(f"[{name}] 'name' must be hyphen-case (lowercase letters, digits, hyphens)")

    if "description" not in frontmatter:
        errors.append(f"[{name}] Missing 'description' in frontmatter")

    # 2. Body is non-empty
    body = content.split("---", 2)
    if len(body) >= 3:
        body_text = body[2].strip()
        if not body_text:
            errors.append(f"[{name}] SKILL.md body is empty after frontmatter")
    else:
        errors.append(f"[{name}] SKILL.md has no body after frontmatter")

    # 3. agents/openai.yaml exists and parses
    openai_yaml = skill_path / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        errors.append(f"[{name}] agents/openai.yaml not found")
    else:
        try:
            with open(openai_yaml, encoding="utf-8") as f:
                oa_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"[{name}] agents/openai.yaml parse error: {e}")
            oa_data = None

        if isinstance(oa_data, dict):
            iface = oa_data.get("interface", {})
            required_keys = [
                "display_name", "short_description", "icon_small",
                "icon_large", "brand_color", "default_prompt",
            ]
            for key in required_keys:
                if key not in iface:
                    errors.append(f"[{name}] agents/openai.yaml missing interface.{key}")

            # 4. Icon paths resolve to real files
            for icon_key in ["icon_small", "icon_large"]:
                if icon_key in iface:
                    icon_path = skill_path / iface[icon_key].lstrip("./")
                    if not icon_path.exists():
                        errors.append(f"[{name}] {icon_key} path does not exist: {iface[icon_key]}")
                    elif icon_path.stat().st_size == 0:
                        errors.append(f"[{name}] {icon_key} is empty: {iface[icon_key]}")

    # 5. Relative markdown links in SKILL.md point to existing files
    link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+\.md)\)")
    for link_match in link_pattern.finditer(content):
        link_path = link_match.group(2)
        if link_path.startswith("http"):
            continue
        resolved = skill_path / link_path
        if not resolved.exists():
            errors.append(f"[{name}] Broken link in SKILL.md: {link_path}")

    return errors


def main():
    repo_root = Path(__file__).resolve().parent.parent
    skills = find_skill_dirs(repo_root)

    if not skills:
        print("No skill directories found at repo root.", file=sys.stderr)
        sys.exit(1)

    all_errors = []
    for skill_dir in skills:
        errors = validate_skill(skill_dir)
        all_errors.extend(errors)
        if errors:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
        else:
            print(f"✓ {skill_dir.name} — valid")

    if all_errors:
        print(f"\n{len(all_errors)} error(s) found.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nAll {len(skills)} skill(s) passed validation.")
        sys.exit(0)


if __name__ == "__main__":
    main()
