"""recall (§6.4, §13.3): the planted load-bearing memory comes back in top-k;
MMR removes near-duplicates; an empty index returns []."""
from __future__ import annotations

from app.memory.store import Record


async def plant(store, *exchanges: tuple[str, str], session="s1"):
    for i, (msg, reply) in enumerate(exchanges):
        await store.remember(Record(session_id=session, turn_index=i,
                                    user_msg=msg, reply=reply))


async def test_planted_memory_in_top_k(store):
    await plant(store,
                ("I love rainy nights", "me too — the window seat exists for them"),
                ("my sister Mira is visiting next week", "Mira — I'll remember her name"),
                ("work was long today", "then sit down; you're here now"))
    got = store.recall("when does my sister Mira arrive?", k=3)
    assert any("Mira" in m.text for m in got), \
        "the load-bearing detail must surface (§6.4, ch. 15)"


async def test_mmr_removes_near_duplicates(store):
    await plant(store,
                ("I love rainy nights", "noted"),
                ("I really love rainy nights", "noted again"),
                ("truly I love rainy nights so much", "yes, rainy nights"),
                ("my sister Mira visits on friday", "Mira, friday — kept"))
    got = store.recall("rainy nights and my sister Mira friday", k=2)
    texts = " | ".join(m.text for m in got)
    # raw similarity would return two rain paraphrases; MMR diversifies (§6.4)
    assert "Mira" in texts
    assert sum("rainy" in m.text for m in got) <= 1


async def test_empty_index_returns_empty(store):
    assert store.recall("anything at all", k=6) == []


async def test_min_similarity_floor(store):
    await plant(store, ("I love rainy nights", "noted"))
    # a query sharing no tokens has ~zero cosine → dropped by RETRIEVAL_MIN_SIM
    assert store.recall("zzz qqq xyzzy plugh", k=6) == []


async def test_recall_is_traceable_to_the_journal(store):
    await plant(store, ("my sister Mira is visiting", "kept"))
    got = store.recall("sister Mira visiting", k=1)
    assert got and got[0].source.startswith("memory/episodic/")  # §4.3 source_path
