#!/usr/bin/env python3
"""A narrated walk through the memory subsystem. Run it:

    python tutorial.py

It builds a throwaway vault in a temp dir, then exercises every verb of the
memory contract in order, printing what happened and why at each step. Nothing
here needs a network, an API key, or a model download — the default embedder is
pure numpy and the "utility model" is a rule-based stand-in.

Read this top to bottom alongside `memory/store.py`; it is the store's
docstrings turned into something you can watch execute.
"""
from __future__ import annotations

import datetime
import tempfile
from pathlib import Path

from memory.embed import HashingEmbedder
from memory.partner import KeywordExtractor
from memory.store import FileMemoryStore, Record


def rule(title: str) -> None:
    print(f"\n{'─' * 72}\n▶ {title}\n{'─' * 72}")


def show_user_md(store: FileMemoryStore) -> None:
    text = store.read_user_md().strip() or "(empty)"
    print("\nvault/soul/USER.md now reads:\n")
    for line in text.splitlines():
        print(f"    {line}")


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="memory-lab-"))
    vault = tmp / "vault"
    store = FileMemoryStore(
        vault,
        embedder=HashingEmbedder(dim=256),
        extractor=KeywordExtractor(),   # the offline stand-in for the utility model
        char_name="yuri", user_name="you",
        # The default HashingEmbedder is *lexical*, not semantic — it only sees
        # shared words. A real deployment uses sentence embeddings and keeps the
        # floor near 0.25; we drop it here so word-overlap recall reads cleanly.
        retrieval_min_sim=0.12,
    )
    print(f"Fresh vault at: {vault}")

    # ── 1. remember: the write path ─────────────────────────────────────────
    rule("1. remember() — three exchanges enter memory")
    exchanges = [
        ("I love rainy nights — the sound on the window.",
         "Me too. The window seat exists for exactly that."),
        ("My sister Mira is visiting next Friday.",
         "Mira, Friday. I'll hold onto that."),
        ("Work was brutal today, three deadlines.",
         "Then put it down. You're here now, not there."),
    ]
    for i, (msg, reply) in enumerate(exchanges):
        r = store.remember(Record("s1", i, msg, reply))
        print(f"  turn {i}: appended to {r.journal_path}, "
              f"indexed {r.chunks_indexed} chunk, "
              f"{r.facts_applied} fact(s) applied, {r.quarantined} quarantined")
    print("\nEach exchange did three things: a prose line in today's journal, one\n"
          "embedded row in the index that points back at that line, and a pass\n"
          "through the partner-model extractor.")

    # ── 2. recall: the read path ────────────────────────────────────────────
    rule("2. recall() — the load-bearing detail comes back")
    query = "when is my sister arriving?"
    print(f"query: {query!r}\n")
    for m in store.recall(query, k=3):
        print(f"  score={m.score:.3f}  sim={m.similarity:.3f}  «{m.text.splitlines()[0]}»")
    print("\nNote what won: not the most words, but the memory about Mira. And\n"
          "note the source — recall is traceable back to the journal line:")
    top = store.recall(query, k=1)[0]
    print(f"    {top.source}")

    # ── 3. the two homes ────────────────────────────────────────────────────
    rule("3. Two homes — the journal is top-k, USER.md is whole")
    print("The extractor pulled a durable fact out of turn 0 ('my name is' would\n"
          "land immediately; 'I live in' is lower-confidence — see step 4). The\n"
          "journal is recalled a few lines at a time; USER.md is injected whole,\n"
          "every turn. Different jobs, different storage.")
    show_user_md(store)

    # ── 4. the quarantine — promotion, not capture ──────────────────────────
    rule("4. Quarantine — a shaky claim waits for a second mention")
    print("The user mentions a city once. The extractor rates 'I live in …' at\n"
          "0.5 confidence — below the 0.6 bar — so it is NOT written yet:")
    store.remember(Record("s1", 3, "I live in Melbourne, near the river.",
                          "By the river — that fits the rainy-night thing."))
    print(f"  quarantine holds: {[q['text'] for q in store.quarantine.items]}")
    show_user_md(store)
    print("\nThe user says it a second time, a later turn. Now it's corroborated,\n"
          "and it gets promoted:")
    store.remember(Record("s1", 4, "Honestly? I live in Melbourne. The grey is relentless.",
                          "Grey suits you, apparently."))
    print(f"  quarantine holds: {[q['text'] for q in store.quarantine.items]}")
    show_user_md(store)
    print("\nThis is the whole anti-confabulation stance in one mechanism: she does\n"
          "not commit to 'remembering' something said once in passing.")

    # ── 5. forget — supersede, never delete ─────────────────────────────────
    rule("5. forget() — the covenant")
    print("The user asks her to forget the city. forget() removes it from the\n"
          "working files AND suppresses it from every future recall:")
    n = store.forget("Melbourne", why="user asked")
    print(f"  superseded {n} memory(ies); wrote a tombstone to memory/semantic/forgotten.md")
    show_user_md(store)
    hits = store.recall("where do I live?", k=3)
    print(f"\n  recall('where do I live?') now returns {len(hits)} Melbourne-mentioning "
          f"memory: {sum('melbourne' in h.text.lower() for h in hits)}")
    print("  The line is gone from the prompt — but still in git history, if the\n"
          "  vault is a repo. Supersede, not erase.")

    # ── 6. inspect — the audit surface ──────────────────────────────────────
    rule("6. inspect() — what she knows about 'rainy', and from where")
    for m in store.inspect("rainy"):
        print(f"  [{m.kind:8}] {m.source}\n             «{m.text.splitlines()[0]}»")
    print("\nEvery memory, tagged with the file it lives in. A store you can't\n"
          "inspect like this — a cloud memory API — can't answer 'what do you know\n"
          "about me, and why?' ownably. That's the line the contract draws.")

    print(f"\n{'═' * 72}\nDone. The whole vault is plain files under:\n  {vault}\n"
          f"Poke around: `cat` the journal, open USER.md, read forgotten.md.\n{'═' * 72}")


if __name__ == "__main__":
    main()
