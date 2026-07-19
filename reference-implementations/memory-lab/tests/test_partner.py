"""The partner model: high-confidence facts land immediately; low-confidence
claims are quarantined until a second turn corroborates them; an unscored claim
fails safe to the quarantine; apply_ops merges rather than duplicates."""
from __future__ import annotations

from memory.embed import HashingEmbedder
from memory.partner import (Op, Quarantine, UNSCORED_CONFIDENCE, apply_ops,
                            parse_ops)
from memory.store import FileMemoryStore, Record


def make_store(tmp_path, extractor):
    return FileMemoryStore(tmp_path / "vault", embedder=HashingEmbedder(256),
                           embed_dim=256, extractor=extractor)


def test_confident_fact_lands_immediately(tmp_path):
    store = make_store(tmp_path, lambda user_md, ex: [
        Op("Stable", "their name is Sam", confidence=0.9)])
    store.remember(Record("s", 0, "hi", "hello"))
    assert "their name is Sam" in store.read_user_md()


def test_low_confidence_is_quarantined_then_promoted(tmp_path):
    # every turn proposes the same shaky claim
    store = make_store(tmp_path, lambda user_md, ex: [
        Op("Stable", "lives in Melbourne", confidence=0.5)])

    store.remember(Record("s", 0, "first mention", "ok"))
    assert "Melbourne" not in store.read_user_md()          # held, not written
    assert any("Melbourne" in q["text"] for q in store.quarantine.items)

    store.remember(Record("s", 1, "second mention", "ok"))  # corroborated
    assert "lives in Melbourne" in store.read_user_md()      # promoted
    assert not store.quarantine.items                        # entry cleared


def test_unscored_claim_fails_safe_to_quarantine(tmp_path):
    store = make_store(tmp_path, lambda user_md, ex: [
        Op("Stable", "drinks oat milk")])                    # no confidence given
    assert Op("x", "y").confidence == UNSCORED_CONFIDENCE
    store.remember(Record("s", 0, "once", "ok"))
    assert "oat milk" not in store.read_user_md()            # not treated as certain


def test_removals_apply_immediately(tmp_path):
    store = make_store(tmp_path, None)
    store.user_md_path.parent.mkdir(parents=True, exist_ok=True)
    store.user_md_path.write_text("## Stable\n\n- likes jazz\n", encoding="utf-8")
    q = Quarantine(store.vault / "state" / "q.json")
    apply_now, held = q.triage([Op("Stable", "likes jazz", op="remove")])
    assert apply_now and not held                            # always safe to forget


def test_apply_ops_merges_not_duplicates():
    md = "## Stable\n\n- their name is Sam\n"
    out = apply_ops(md, [Op("Stable", "their name is Sam", confidence=0.9)])
    assert out.count("their name is Sam") == 1               # add skips near-dup
    out2 = apply_ops(md, [Op("Stable", "their name is Samuel", op="update")])
    assert "Samuel" in out2 and "name is Sam\n" not in out2  # update replaces


def test_parse_ops_tolerates_garbage():
    assert parse_ops("not json at all") == []
    assert parse_ops('```json\n{"ops": [{"section":"Stable","text":"x"}]}\n```')
