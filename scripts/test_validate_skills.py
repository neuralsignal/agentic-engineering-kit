"""Tests for the agentskills.io skill validator."""
import sys
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_skills import (  # noqa: E402
    NAME_RE,
    parse_frontmatter,
    validate_skill,
)


def _write_skill(tmp_path: Path, dir_name: str, frontmatter: str, body: str = "Body.\n") -> Path:
    d = tmp_path / dir_name
    d.mkdir()
    md = d / "SKILL.md"
    md.write_text(f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8")
    return md


# ---- name regex (property-based) ----

VALID_NAMES = ["pdf-processing", "a", "data-analysis", "brain-knowledge", "skill1", "a1-b2-c3"]
INVALID_NAMES = ["PDF", "-pdf", "pdf-", "pdf--proc", "under_score", "has space", "péd"]


@pytest.mark.parametrize("name", VALID_NAMES)
def test_name_regex_accepts_valid(name):
    assert NAME_RE.match(name)


@pytest.mark.parametrize("name", INVALID_NAMES)
def test_name_regex_rejects_invalid(name):
    assert not NAME_RE.match(name)


@given(st.text())
def test_name_regex_never_crashes(s):
    NAME_RE.match(s)  # must not raise on arbitrary input


# ---- frontmatter parsing ----

def test_parse_frontmatter_ok():
    fm = parse_frontmatter("---\nname: x\ndescription: y\n---\nbody")
    assert fm == {"name": "x", "description": "y"}


def test_parse_frontmatter_missing_open():
    with pytest.raises(ValueError):
        parse_frontmatter("name: x\n")


def test_parse_frontmatter_missing_close():
    with pytest.raises(ValueError):
        parse_frontmatter("---\nname: x\n")


def test_parse_frontmatter_not_mapping():
    with pytest.raises(ValueError):
        parse_frontmatter("---\n- a\n- b\n---\n")


# ---- full skill validation ----

def test_valid_skill_no_errors(tmp_path):
    md = _write_skill(tmp_path, "good-skill", "name: good-skill\ndescription: Does a thing. Use when needed.")
    errors, warnings = validate_skill(md)
    assert errors == []


def test_name_must_match_dir(tmp_path):
    md = _write_skill(tmp_path, "dir-name", "name: other-name\ndescription: x")
    errors, _ = validate_skill(md)
    assert any("match parent directory" in e for e in errors)


def test_uppercase_name_rejected(tmp_path):
    md = _write_skill(tmp_path, "Bad-Name", "name: Bad-Name\ndescription: x")
    errors, _ = validate_skill(md)
    assert any("name:" in e for e in errors)


def test_missing_description(tmp_path):
    md = _write_skill(tmp_path, "no-desc", "name: no-desc")
    errors, _ = validate_skill(md)
    assert any("description: required" in e for e in errors)


def test_description_too_long(tmp_path):
    md = _write_skill(tmp_path, "long-desc", f"name: long-desc\ndescription: {'x' * 1025}")
    errors, _ = validate_skill(md)
    assert any("description: must be 1-1024" in e for e in errors)


def test_compatibility_too_long(tmp_path):
    fm = f"name: c\ndescription: d\ncompatibility: {'x' * 501}"
    md = _write_skill(tmp_path, "c", fm)
    errors, _ = validate_skill(md)
    assert any("compatibility" in e for e in errors)


def test_metadata_non_string_value_rejected(tmp_path):
    fm = "name: m\ndescription: d\nmetadata:\n  version: 1.0"  # 1.0 parses as float
    md = _write_skill(tmp_path, "m", fm)
    errors, _ = validate_skill(md)
    assert any("metadata" in e for e in errors)


def test_metadata_string_values_ok(tmp_path):
    fm = 'name: m\ndescription: d\nmetadata:\n  version: "1.0"\n  category: ops'
    md = _write_skill(tmp_path, "m", fm)
    errors, _ = validate_skill(md)
    assert errors == []


def test_oversized_warns_not_errors(tmp_path):
    body = "\n".join("line" for _ in range(600))
    md = _write_skill(tmp_path, "big", "name: big\ndescription: d", body=body)
    errors, warnings = validate_skill(md)
    assert errors == []
    assert any("lines" in w for w in warnings)
