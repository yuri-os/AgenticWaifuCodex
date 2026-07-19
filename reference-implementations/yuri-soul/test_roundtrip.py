"""Round-trip tests for the SOUL ⇄ card converter.

Run from this folder:  python -m pytest          (or just `pytest`)

The core guarantee these lock in: a soul exported to a card and imported back
re-exports to the same card — no field is silently dropped or mangled — and the
verifier actually *catches* drift when it happens.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # make build_card / import_card importable standalone

import build_card  # noqa: E402
import import_card  # noqa: E402


def test_real_soul_card_roundtrips_clean():
    """The actual Yuri soul exports to a card, imports back, and re-exports
    unchanged — the whole point of the converter."""
    _, _, _, data = build_card.build_card_data(HERE)
    intended = import_card.intended_card(data)
    assert import_card.verify_roundtrip(intended) == []


def test_real_soul_preserves_examples_and_lorebook():
    """Structured fields (example exchanges, lorebook entries) survive the trip,
    not just the flat text fields."""
    _, _, _, data = build_card.build_card_data(HERE)
    intended = import_card.intended_card(data)
    assert len(import_card.example_blocks(intended["mes_example"])) >= 3
    assert len(intended["character_book"]["entries"]) >= 1


def test_sparse_card_gets_defaults_and_roundtrips():
    """A foreign card missing most fields imports with sensible defaults and
    still round-trips."""
    data = {
        "name": "Mira",
        "description": "A quiet librarian who keeps a candle burning for late readers.",
        "first_mes": "Oh — you're here late.",
        "mes_example": "{{user}}: hello\n{{char}}: *looks up* Welcome back.",
    }
    intended = import_card.intended_card(data)

    assert intended["personality"] == import_card.DEFAULT_PERSONALITY
    assert intended["creator_notes"]                      # defaulted, not empty
    assert intended["scenario"] == ""                     # absent -> empty section
    assert intended["character_book"]["entries"] == []    # absent -> empty lorebook
    assert import_card.verify_roundtrip(intended) == []


def test_keyless_lorebook_entry_gets_a_synthesised_key():
    """A lorebook entry with no trigger keys would be dropped on re-export; the
    importer gives it one so it survives."""
    data = {
        "name": "K",
        "character_book": {"entries": [{"keys": [], "content": "secret lore", "name": "Origin"}]},
    }
    intended = import_card.intended_card(data)
    entries = intended["character_book"]["entries"]
    assert entries and entries[0]["keys"]                 # non-empty key was synthesised
    assert import_card.verify_roundtrip(intended) == []


def test_written_soul_rebuilds_on_disk(tmp_path):
    """write_soul produces a folder that build_card can re-read in place."""
    intended = import_card.intended_card({
        "name": "Mira", "description": "A librarian.", "first_mes": "Hi.",
        "mes_example": "{{user}}: hi\n{{char}}: hey",
    })
    import_card.write_soul(intended, tmp_path)
    assert (tmp_path / "soul.yaml").exists()
    assert import_card.roundtrip_diffs(intended, tmp_path) == []


def test_roundtrip_detects_drift(tmp_path):
    """If the soul on disk no longer matches the card, the verifier reports it —
    otherwise the 'clean' result above would be meaningless."""
    intended = import_card.intended_card({"name": "Mira", "description": "original text"})
    import_card.write_soul(intended, tmp_path)
    tampered = dict(intended, description="completely different text")
    diffs = import_card.roundtrip_diffs(tampered, tmp_path)
    assert any("description" in d for d in diffs)


def test_extract_card_from_png_prefers_v3(tmp_path):
    """A built PNG can be read back, and a V3 build is preferred over the V2
    chunk when both are embedded."""
    _, _, _, data = build_card.build_card_data(HERE, spec="v3")
    out = tmp_path / "card.png"
    chunks = {"chara": build_card.wrap_card(data, "v2"),
              "ccv3": build_card.wrap_card(data, "v3")}
    build_card.embed_png(HERE / "portrait.png", out, chunks)

    card = build_card.extract_card(out)
    assert card["spec"] == "chara_card_v3"
    assert card["data"]["name"] == data["name"]


def test_import_from_built_png_roundtrips(tmp_path):
    """End to end through the real PNG transport: build -> embed -> extract ->
    import -> re-export matches."""
    _, _, _, data = build_card.build_card_data(HERE, spec="v3")
    out = tmp_path / "card.png"
    build_card.embed_png(HERE / "portrait.png", out, {"ccv3": build_card.wrap_card(data, "v3")})

    loaded = import_card.load_card_data(out)
    intended = import_card.intended_card(loaded)
    assert import_card.verify_roundtrip(intended) == []
