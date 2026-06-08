#!/usr/bin/env python3
"""Validate Agent Skills against the agentskills.io specification.

Spec: https://agentskills.io/specification

Enforces (errors -> exit 1):
  - SKILL.md present, with a YAML frontmatter block.
  - `name`: 1-64 chars, lowercase a-z/0-9 and single hyphens, no leading/trailing
    or consecutive hyphens, and MUST equal the parent directory name.
  - `description`: 1-1024 chars, non-empty.
  - `compatibility` (if present): 1-500 chars.
  - `metadata` (if present): a mapping of string -> string.
  - `license` / `allowed-tools` (if present): strings.

Warns (does not fail) when SKILL.md exceeds 500 lines (progressive-disclosure guideline).

No default arguments: exactly one of positional SKILL.md paths or --skills-dir
must be supplied, else the program exits with a clear error.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESC_MAX = 1024
COMPAT_MAX = 500
LINE_WARN = 500


def parse_frontmatter(text: str) -> dict:
    """Return the parsed YAML frontmatter mapping. Raises ValueError if malformed."""
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        raise ValueError("missing opening frontmatter delimiter '---' on line 1")
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            block = "\n".join(lines[1:i])
            try:
                data = yaml.safe_load(block)
            except yaml.YAMLError as exc:
                raise ValueError(f"invalid YAML: {exc}") from exc
            if not isinstance(data, dict):
                raise ValueError("frontmatter is not a YAML mapping")
            return data
    raise ValueError("missing closing frontmatter delimiter '---'")


def validate_skill(skill_md: Path) -> tuple[list[str], list[str]]:
    """Validate one SKILL.md. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []
    dir_name = skill_md.parent.name

    text = skill_md.read_text(encoding="utf-8")

    try:
        fm = parse_frontmatter(text)
    except ValueError as exc:
        return [f"frontmatter: {exc}"], warnings

    # name
    name = fm.get("name")
    if name is None:
        errors.append("name: required field is missing")
    elif not isinstance(name, str):
        errors.append(f"name: must be a string, got {type(name).__name__}")
    else:
        if not 1 <= len(name) <= NAME_MAX:
            errors.append(f"name: must be 1-{NAME_MAX} chars (got {len(name)})")
        if not NAME_RE.match(name):
            errors.append(
                f"name: '{name}' must be lowercase a-z/0-9 with single hyphens "
                "(no leading/trailing/consecutive hyphens)"
            )
        if name != dir_name:
            errors.append(f"name: '{name}' must match parent directory name '{dir_name}'")

    # description
    desc = fm.get("description")
    if desc is None:
        errors.append("description: required field is missing")
    elif not isinstance(desc, str):
        errors.append(f"description: must be a string, got {type(desc).__name__}")
    elif not 1 <= len(desc) <= DESC_MAX:
        errors.append(f"description: must be 1-{DESC_MAX} chars (got {len(desc)})")

    # compatibility (optional)
    if "compatibility" in fm:
        compat = fm["compatibility"]
        if not isinstance(compat, str):
            errors.append("compatibility: must be a string")
        elif not 1 <= len(compat) <= COMPAT_MAX:
            errors.append(f"compatibility: must be 1-{COMPAT_MAX} chars (got {len(compat)})")

    # metadata (optional): map of string -> string
    if "metadata" in fm:
        meta = fm["metadata"]
        if not isinstance(meta, dict):
            errors.append("metadata: must be a mapping")
        else:
            for k, v in meta.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    errors.append(f"metadata: key/value '{k}: {v}' must both be strings")

    # license / allowed-tools (optional): strings
    for opt in ("license", "allowed-tools"):
        if opt in fm and not isinstance(fm[opt], str):
            errors.append(f"{opt}: must be a string")

    # progressive-disclosure guideline (warning only)
    n_lines = text.count("\n") + 1
    if n_lines > LINE_WARN:
        warnings.append(f"SKILL.md is {n_lines} lines (> {LINE_WARN}); move detail into references/")

    return errors, warnings


def collect_skill_files(paths: list[str], skills_dir: str | None) -> list[Path]:
    if paths and skills_dir:
        raise SystemExit("error: pass either SKILL.md paths OR --skills-dir, not both")
    if not paths and not skills_dir:
        raise SystemExit("error: supply SKILL.md path(s) or --skills-dir")
    if paths:
        return [Path(p) for p in paths]
    root = Path(skills_dir)
    if not root.is_dir():
        raise SystemExit(f"error: --skills-dir '{root}' is not a directory")
    return sorted(root.glob("*/SKILL.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills (agentskills.io spec).")
    parser.add_argument("paths", nargs="*", help="SKILL.md file path(s) to validate")
    parser.add_argument("--skills-dir", help="directory whose */SKILL.md files are validated")
    args = parser.parse_args()

    skill_files = collect_skill_files(args.paths, args.skills_dir)
    if not skill_files:
        print("no SKILL.md files found", file=sys.stderr)
        return 1

    total_errors = 0
    for skill_md in skill_files:
        if not skill_md.is_file():
            print(f"ERROR {skill_md}: file not found")
            total_errors += 1
            continue
        errors, warnings = validate_skill(skill_md)
        for w in warnings:
            print(f"WARN  {skill_md.parent.name}: {w}")
        for e in errors:
            print(f"ERROR {skill_md.parent.name}: {e}")
        total_errors += len(errors)

    n = len(skill_files)
    if total_errors:
        print(f"\n{total_errors} error(s) across {n} skill(s) — FAILED")
        return 1
    print(f"\nAll {n} skill(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
