"""recall: the load-bearing detail comes back in top-k; MMR removes
near-duplicates; an empty index and a no-match query both return []."""
from __future__ import annotations


def test_planted_memory_in_top_k(store, plant):
    plant(store,
          ("I love rainy nights", "me too — the window seat exists for them"),
          ("my sister Mira is visiting next week", "Mira — I'll remember her name"),
          ("work was long today", "then sit down; you're here now"))
    got = store.recall("when does my sister Mira arrive?", k=3)
    assert any("Mira" in m.text for m in got)


def test_mmr_removes_near_duplicates(store, plant):
    plant(store,
          ("I love rainy nights", "noted"),
          ("I really love rainy nights", "noted again"),
          ("truly I love rainy nights so much", "yes, rainy nights"),
          ("my sister Mira visits on friday", "Mira, friday — kept"))
    got = store.recall("rainy nights and my sister Mira friday", k=2)
    texts = " | ".join(m.text for m in got)
    assert "Mira" in texts
    assert sum("rainy" in m.text for m in got) <= 1


def test_empty_index_returns_empty(store):
    assert store.recall("anything at all", k=6) == []


def test_min_similarity_floor(store, plant):
    plant(store, ("I love rainy nights", "noted"))
    assert store.recall("zzz qqq xyzzy plugh", k=6) == []


def test_recall_is_traceable_to_the_journal(store, plant):
    plant(store, ("my sister Mira is visiting", "kept"))
    got = store.recall("sister Mira visiting", k=1)
    assert got and got[0].source.startswith("memory/episodic/")
