from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _frontmatter(path: Path) -> tuple[dict[str, str], str]:
    content = path.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    match = re.search(r"\n---\n", content[4:])
    assert match is not None
    raw = content[4:match.start() + 4]
    body = content[match.end() + 4:]
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields, body


def test_agent_skill_has_valid_frontmatter_and_scope_guard():
    fields, body = _frontmatter(ROOT / "SKILL.md")

    assert fields["name"] == "ostium-social-volatility-research-kit"
    assert fields["description"].startswith("Use when")
    assert len(fields["description"]) <= 1024
    assert "Static dashboard" in body
    assert "Agent runbook and prompt templates" in body
    assert "Do **not** use this skill to deploy" in body


def test_agent_runbook_and_prompts_exist_and_keep_approval_boundaries():
    required = [
        "docs/agent-runbook.md",
        "docs/adapt-study.md",
        "prompts/reproduce-cached-study.md",
        "prompts/adapt-study.md",
        "prompts/interpret-results.md",
    ]
    for rel in required:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "dashboard" in text
        assert "agent runbook" in text
        assert "deploy" in text or "publish" in text


def test_agent_adaptation_docs_cover_required_inputs():
    text = (ROOT / "docs/adapt-study.md").read_text(encoding="utf-8")

    for phrase in [
        "social.x.query",
        "classification.include_terms",
        "ostium_builder_symbol",
        "ostium_pair_id",
        "validation.fixture_expectations",
    ]:
        assert phrase in text
