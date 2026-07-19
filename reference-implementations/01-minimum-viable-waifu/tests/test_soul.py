"""SoulLoader (§5, §13.3): soul.yaml refs resolve to the right .md sections;
macros substitute; a missing section fails loudly, not silently."""
from __future__ import annotations

import shutil

import pytest
import yaml

from app.core.soul import SoulLoader


def loader(vault, user_name="you"):
    return SoulLoader(vault / "soul", user_name=user_name)


def test_manifest_refs_resolve_to_sections(vault):
    soul = loader(vault).load()
    # §5.2 mapping — each block comes from the file soul.yaml says it does
    assert "voice" in soul.voice_law.lower() or len(soul.voice_law) > 50
    assert "Lumina" in soul.backbone                 # CONSTITUTION#Identity
    assert "ferry" in soul.backbone                  # CONSTITUTION#History
    assert len(soul.personality) > 0                 # PERSONA@personality (frontmatter)
    assert "\n" not in soul.personality.strip() or len(soul.personality) < 400
    assert len(soul.scenario) > 0                    # SCENARIO#Scenario
    assert len(soul.hard_limits) > 0                 # CONSTITUTION#Hard limits
    assert len(soul.return_greetings) == 2           # evening + morning


def test_card_version_stamp(vault):
    # "<name lowercased>-v<major>@<canon>" (§5.2)
    assert loader(vault).load().card_version == "yuri-v1@canon-v1"


def test_macros_substitute_everywhere(vault):
    soul = loader(vault, user_name="Grant").load()
    for text in (soul.voice_law, soul.backbone, soul.scenario,
                 soul.examples, soul.hard_limits,
                 *(e.content for e in soul.lorebook)):
        assert "{{user}}" not in text and "{{char}}" not in text
    assert "Grant" in soul.backbone   # CONSTITUTION#Identity speaks about {{user}}


def test_examples_are_start_blocks(vault):
    soul = loader(vault).load()
    assert soul.examples.count("<START>") >= 5   # EXAMPLES.md has many ## Example blocks


def test_lorebook_keyword_trigger(vault):
    soul = loader(vault).load()
    assert len(soul.lorebook) >= 5
    hits = soul.lorebook_hits("wait — what exactly is a Lumina?")
    assert any(e.name == "Lumina" for e in hits)
    assert soul.lorebook_hits("nothing that matches any key at all xyzzy") == []


def test_bootstrap_presence_is_the_flag(vault):
    # §5.4: file-presence IS "has she met you yet?"
    assert loader(vault).load().bootstrap is not None
    onboarded = vault / "soul" / "onboarded"
    onboarded.mkdir()
    shutil.move(vault / "soul" / "BOOTSTRAP.md", onboarded / "BOOTSTRAP.done.md")
    assert loader(vault).load().bootstrap is None


def test_missing_section_fails_loudly(vault):
    manifest = vault / "soul" / "soul.yaml"
    data = yaml.safe_load(manifest.read_text())
    data["fields"]["scenario"] = "SCENARIO.md#No Such Heading"
    manifest.write_text(yaml.safe_dump(data))
    with pytest.raises(KeyError, match="No Such Heading"):
        loader(vault).load()


def test_missing_file_fails_loudly(vault):
    (vault / "soul" / "WORLD.md").unlink()
    with pytest.raises(FileNotFoundError, match="WORLD.md"):
        loader(vault).load()
