"""Persistence (§13.3): what one process writes, a fresh one recalls — the
mind is the files, not the process. And `scripts/reindex.py` rebuilds the
derived index from the .md files alone (§4.3)."""
from __future__ import annotations

import shutil

from app.memory.store import FileMemoryStore, Record
from scripts.reindex import reindex
from tests.conftest import EMBED_DIM, FakeEmbedder, FakeUtility, ops_json


def fresh_store(vault):
    """A brand-new store over the same Vault — 'a new process' in miniature."""
    return FileMemoryStore(vault, FakeEmbedder(), utility=None,
                           char_name="yuri", user_name="you",
                           embed_dim=EMBED_DIM)


async def test_user_md_and_journal_survive_a_restart(vault):
    writer = FileMemoryStore(
        vault, FakeEmbedder(),
        FakeUtility(ops_json({"section": "Stable", "text": "name is Grant",
                              "op": "add", "confidence": 0.95})),
        char_name="yuri", user_name="you", embed_dim=EMBED_DIM)
    await writer.remember(Record(session_id="s", turn_index=0,
                                 user_msg="I'm Grant, by the way",
                                 reply="Grant. that's kept now."))

    reader = fresh_store(vault)
    assert "name is Grant" in reader.read_user_md()          # the partner model
    got = reader.recall("what is my name Grant", k=3)         # the journal, via index
    assert any("Grant" in m.text for m in got)
    # and the journal file itself is human-readable prose (§4.2: cat works)
    journal = next((vault / "memory" / "episodic").glob("*.md")).read_text()
    assert "I'm Grant" in journal


async def test_reindex_rebuilds_from_markdown_alone(vault, store):
    await store.remember(Record(session_id="s", turn_index=0,
                                user_msg="my sister Mira visits friday",
                                reply="Mira, friday — kept."))
    (vault / "memory" / "summary.md").write_text(
        "They are planning for Mira's visit on friday.\n")

    # blow the derived cache away entirely — the markdown is authoritative (§4.3)
    shutil.rmtree(vault / "memory" / "index")

    n = reindex(vault, embedder=FakeEmbedder(), embed_dim=EMBED_DIM)
    assert n == 2                                    # 1 journal event + 1 summary

    reborn = fresh_store(vault)
    got = reborn.recall("when does Mira visit?", k=3)
    assert any("Mira" in m.text for m in got)
    assert any(m.kind == "summary" for m in reborn.inspect("mira"))


async def test_inspect_answers_what_and_why(vault, store):
    """inspect() is load-bearing (§6.1): every memory, with its source."""
    await store.remember(Record(session_id="s", turn_index=0,
                                user_msg="I hate mushrooms",
                                reply="no mushrooms. ever. noted."))
    found = store.inspect("mushrooms")
    assert found and all(m.source for m in found)
    assert any("episodic" in m.source for m in found)
