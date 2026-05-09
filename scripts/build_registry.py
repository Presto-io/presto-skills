#!/usr/bin/env python3
"""Build registry.json from root-level skill directories."""

import json
import re
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def compute_skill_hash(skill_dir: Path) -> str:
    """Compute a stable SHA256 hash for the skill contents."""
    digest = hashlib.sha256()
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".DS_Store":
            continue
        rel = path.relative_to(skill_dir).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def build_skill_entry(skill_dir: Path) -> dict | None:
    """Build a registry entry from a skill directory."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None

    if not isinstance(frontmatter, dict):
        return None

    name = frontmatter.get("name", skill_dir.name)
    description = frontmatter.get("description", "")
    version = str(frontmatter.get("version", "1.0.0"))

    # Read openai.yaml for UI metadata
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    display_name = name
    if openai_yaml.exists():
        try:
            with open(openai_yaml, encoding="utf-8") as f:
                oa = yaml.safe_load(f)
            if isinstance(oa, dict):
                iface = oa.get("interface", {})
                display_name = iface.get("display_name", display_name)
        except yaml.YAMLError:
            pass

    return {
        "name": name,
        "displayName": display_name,
        "description": description,
        "version": version,
        "author": "Presto-io",
        "repo": "Presto-io/presto-skills",
        "path": skill_dir.name,
        "license": "MIT",
        "category": "productivity",
        "keywords": ["presto", "document", "formatting", "gongwen"],
        "trust": "official",
        "hash": compute_skill_hash(skill_dir),
    }


def main():
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "output" / "deploy"
    output_dir.mkdir(parents=True, exist_ok=True)

    skills = []
    for child in sorted(repo_root.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            entry = build_skill_entry(child)
            if entry:
                skills.append(entry)

    registry = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "skills": skills,
    }

    output_file = output_dir / "registry.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"Built registry with {len(skills)} skill(s) → {output_file}")


if __name__ == "__main__":
    main()
