"""Unit tests for the card model + vendored converter reuse (no app, no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from studio import cardmodel
from studio.soulkit import build_card


def test_starter_builds_and_self_verifies(tmp_path):
    draft = cardmodel.starter_draft()
    summary = cardmodel.build(draft, tmp_path / "none.png", tmp_path / "dist", spec="v3")
    # a V3 build carries BOTH the V2 chara chunk and the V3 ccv3 chunk
    assert set(summary["verified_chunks"]) == {"chara", "ccv3"}
    assert summary["verified_chunks"]["chara"] == "Mira"
    assert summary["used_placeholder_portrait"] is True
    assert Path(summary["png"]).exists()
    assert Path(summary["soul_md"]).exists()


def test_built_png_reads_back_as_the_same_character(tmp_path):
    draft = cardmodel.starter_draft()
    summary = cardmodel.build(draft, tmp_path / "none.png", tmp_path / "dist", spec="v3")
    card = build_card.extract_card(Path(summary["png"]))
    assert card["data"]["name"] == draft["name"]
    # examples became <START> blocks; lorebook entry survived
    assert "<START>" in card["data"]["mes_example"]
    assert len(card["data"]["character_book"]["entries"]) == 1


def test_draft_roundtrips_through_card_data():
    draft = cardmodel.starter_draft()
    data = cardmodel.to_card_data(draft)
    back = cardmodel.from_card_data(data)
    assert back["name"] == draft["name"]
    assert back["personality"] == draft["personality"]
    assert len(back["examples"]) == len(draft["examples"])
    assert back["lorebook"]["entries"][0]["keys"] == draft["lorebook"]["entries"][0]["keys"]


def test_import_card_bytes_from_built_png(tmp_path):
    draft = cardmodel.starter_draft()
    summary = cardmodel.build(draft, tmp_path / "none.png", tmp_path / "dist", spec="v3")
    raw = Path(summary["png"]).read_bytes()
    got_draft, portrait = cardmodel.import_card_bytes(raw, "mira.png")
    assert got_draft["name"] == "Mira"
    assert portrait is not None  # the PNG image is the portrait


def test_token_report_flags_over_budget():
    draft = cardmodel.starter_draft()
    draft["description"] = "x " * 2000  # blow the description budget
    data = cardmodel.to_card_data(draft)
    rows = {r["field"]: r for r in cardmodel.token_report(data)}
    assert rows["description"]["over"] is True


def test_voice_warning_on_exclamation():
    draft = cardmodel.starter_draft()
    draft["first_mes"] = "Hello!!!"
    data = cardmodel.to_card_data(draft)
    assert any("first message" in w for w in cardmodel.voice_warnings(data))


def test_soul_zip_contains_soul_files(tmp_path):
    import io
    import zipfile
    draft = cardmodel.starter_draft()
    data = cardmodel.soul_zip(draft, tmp_path / "none.png")
    names = zipfile.ZipFile(io.BytesIO(data)).namelist()
    assert "CONSTITUTION.md" in names
    assert "PERSONA.md" in names
    assert "soul.yaml" in names
