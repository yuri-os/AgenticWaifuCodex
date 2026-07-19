"""forget: supersede-not-delete. The value leaves USER.md and every future
recall, and a tombstone records that it happened."""
from __future__ import annotations


def test_forget_suppresses_from_recall(store, plant):
    plant(store,
          ("I live in Melbourne by the river", "the river suits you"),
          ("I love rainy nights", "me too"))
    before = store.recall("I live in Melbourne", k=3)
    assert any("melbourne" in m.text.lower() for m in before)

    store.forget("Melbourne", why="user asked")

    after = store.recall("I live in Melbourne", k=3)
    assert not any("melbourne" in m.text.lower() for m in after)


def test_forget_writes_a_tombstone(store, plant):
    plant(store, ("I live in Melbourne", "noted"))
    store.forget("Melbourne")
    assert store.forgotten_path.exists()
    assert "Melbourne" in store.forgotten_path.read_text(encoding="utf-8")
    assert "Melbourne" in store.tombstones()


def test_forget_removes_from_user_md(store):
    store.user_md_path.parent.mkdir(parents=True, exist_ok=True)
    store.user_md_path.write_text("## Stable\n\n- lives in Melbourne\n- plays bass\n",
                                  encoding="utf-8")
    n = store.forget("Melbourne")
    assert n >= 1
    md = store.read_user_md()
    assert "Melbourne" not in md and "plays bass" in md      # only the match goes
