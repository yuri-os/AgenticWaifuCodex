"""Persistence: memory survives a restart, because the files are the truth and
the index is just a cache rebuilt from them. This is the property the whole
book is about — 'she remembers you across sessions.'"""
from __future__ import annotations

from memory.embed import HashingEmbedder
from memory.store import FileMemoryStore, Record

DIM = 256


def test_memory_survives_a_restart(tmp_path):
    vault = tmp_path / "vault"

    # session 1: tell her something, then "shut down" (drop the object)
    s1 = FileMemoryStore(vault, embedder=HashingEmbedder(DIM), embed_dim=DIM)
    s1.remember(Record("s1", 0, "my sister Mira visits friday", "kept"))
    s1.index.close()

    # session 2: a brand-new store over the same vault dir
    s2 = FileMemoryStore(vault, embedder=HashingEmbedder(DIM), embed_dim=DIM)
    got = s2.recall("my sister Mira visits", k=3)
    assert any("Mira" in m.text for m in got)


def test_index_is_a_rebuildable_cache(tmp_path):
    vault = tmp_path / "vault"
    store = FileMemoryStore(vault, embedder=HashingEmbedder(DIM), embed_dim=DIM)
    store.remember(Record("s1", 0, "my sister Mira visits friday", "kept"))

    # the journal file (the truth) still holds the exchange after wiping the cache
    store.index.wipe()
    assert store.recall("Mira", k=3) == []                  # cache is empty
    journal = (vault / "memory" / "episodic").glob("*.md")
    assert any("Mira" in p.read_text(encoding="utf-8") for p in journal)
