"""Partner model (§6.3, §13.3): durable facts update USER.md; chit-chat does
not; a low-confidence claim is quarantined until corroborated."""
from __future__ import annotations

import json

from app.memory.store import FileMemoryStore, Record
from tests.conftest import EMBED_DIM, FakeEmbedder, FakeUtility, ops_json


def make_store(vault, utility):
    return FileMemoryStore(vault, FakeEmbedder(), utility,
                           char_name="yuri", user_name="you",
                           embed_dim=EMBED_DIM)


async def test_durable_fact_lands_in_user_md(vault):
    utility = FakeUtility(ops_json(
        {"section": "Don't forget", "text": "anniversary: 14 Feb",
         "op": "add", "confidence": 0.95}))
    store = make_store(vault, utility)
    await store.remember(Record(session_id="s", turn_index=0,
                                user_msg="our anniversary is the 14th of Feb — remember it",
                                reply="the fourteenth. kept, always."))
    user_md = store.read_user_md()
    assert "## Don't forget" in user_md
    assert "anniversary: 14 Feb" in user_md
    # the utility model saw the CURRENT USER.md, so it updates, not duplicates (§6.3)
    prompt_text = json.dumps(utility.calls[0])
    assert "Current USER.md" in prompt_text


async def test_ephemeral_chitchat_changes_nothing(vault):
    store = make_store(vault, FakeUtility('{"ops": []}'))
    before = store.read_user_md()
    await store.remember(Record(session_id="s", turn_index=0,
                                user_msg="haha yeah",
                                reply="mm. stay a while?"))
    assert store.read_user_md() == before


async def test_low_confidence_claim_is_quarantined_then_promoted(vault):
    low = {"section": "Stable", "text": "might be moving to Osaka",
           "op": "add", "confidence": 0.3}
    store = make_store(vault, FakeUtility(ops_json(low), ops_json(low)))
    # first sighting: held out of USER.md (§6.3 — promotion, not capture)
    await store.remember(Record(session_id="s", turn_index=0,
                                user_msg="a friend said I might be moving to Osaka",
                                reply="might you?"))
    assert "Osaka" not in store.read_user_md()
    q = json.loads((vault / "state" / "quarantine.json").read_text())
    assert any("Osaka" in item["text"] for item in q)
    # second turn corroborates → promoted
    await store.remember(Record(session_id="s", turn_index=1,
                                user_msg="yes — I am moving to Osaka in spring",
                                reply="then we'll plan for spring."))
    assert "Osaka" in store.read_user_md()
    q = json.loads((vault / "state" / "quarantine.json").read_text())
    assert not any("Osaka" in item["text"] for item in q)


async def test_unscored_claim_is_quarantined_not_captured(vault):
    """A claim the utility model returns with NO confidence field must wait for
    corroboration, not land on first sighting — a missing score fails safe to
    the quarantine, it is not treated as certainty (§6.3)."""
    unscored = {"section": "Stable", "text": "works night shifts", "op": "add"}
    store = make_store(vault, FakeUtility(ops_json(unscored), ops_json(unscored)))
    # first sighting: held, exactly as a low-confidence claim would be
    await store.remember(Record(session_id="s", turn_index=0,
                                user_msg="I was up all night for work again",
                                reply="the night shift?"))
    assert "night shifts" not in store.read_user_md()
    q = json.loads((vault / "state" / "quarantine.json").read_text())
    assert any("night shifts" in item["text"] for item in q)
    # second turn corroborates → promoted (proves it was quarantined, not dropped)
    await store.remember(Record(session_id="s", turn_index=1,
                                user_msg="yeah, I'm on nights all month",
                                reply="noted — nights it is."))
    assert "night shifts" in store.read_user_md()


async def test_utility_call_is_logged(vault, tmp_path):
    """Every utility-model call leaves a peekable record in corpus/utility.jsonl:
    what it proposed and how triage handled it (§6.3 transparency)."""
    from app.corpus import UtilityLogger
    ulog = UtilityLogger(tmp_path / "corpus")
    utility = FakeUtility(ops_json(
        {"section": "Stable", "text": "likes strong tea",
         "op": "add", "confidence": 0.95}))
    store = FileMemoryStore(vault, FakeEmbedder(), utility,
                            char_name="yuri", user_name="you",
                            embed_dim=EMBED_DIM, utility_log=ulog)
    await store.remember(Record(session_id="s", turn_index=0,
                                user_msg="I love a strong cup of tea",
                                reply="strong it is."))
    lines = (tmp_path / "corpus" / "utility.jsonl").read_text().strip().splitlines()
    rec = json.loads(lines[0])
    assert rec["kind"] == "extract"
    assert rec["raw_reply"]                       # the model's actual words survive
    assert any(o["text"] == "likes strong tea" for o in rec["applied"])


async def test_malformed_utility_reply_is_never_fatal(vault):
    store = make_store(vault, FakeUtility("SORRY I CANNOT JSON TODAY {broken"))
    before = store.read_user_md()
    result = await store.remember(Record(session_id="s", turn_index=0,
                                         user_msg="my name is Grant",
                                         reply="Grant."))
    assert result.chunks_indexed == 1        # the journal + index still happened (§6.2)
    assert store.read_user_md() == before


def test_apply_ops_merges_instead_of_duplicating():
    from app.memory.partner import Op, apply_ops
    md = "## Stable\n\n- prefers mornings quiet\n"
    md = apply_ops(md, [Op("Stable", "prefers quiet mornings", "add", 0.9)])
    assert md.count("mornings") == 1          # near-duplicate add is skipped
    md = apply_ops(md, [Op("Stable", "prefers loud mornings now", "update", 0.9)])
    assert "loud mornings" in md and "quiet" not in md
    md = apply_ops(md, [Op("Stable", "prefers loud mornings now", "remove", 0.9)])
    assert "mornings" not in md
