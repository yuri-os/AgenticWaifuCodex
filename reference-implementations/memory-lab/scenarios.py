#!/usr/bin/env python3
"""Why memory is the differentiator — three scenarios, run:

    python scenarios.py

Each scenario plants a little history, then shows the *context a companion would
have to work with* on a later turn — first with no memory (the stateless chatbot
every product started as), then with the memory store feeding it. There is no
LLM here on purpose: the point isn't the wording of the reply, it's what the
model does or doesn't get to see. Memory is upstream of the prompt; this shows
the prompt.

The through-line (→ book ch. 15): the benefit users report from companions is
*feeling heard*, and feeling-heard is manufactured by recall. A persona can't
write "how did the Monday review go?" — only the memory system can supply the
Monday review.
"""
from __future__ import annotations

import datetime
import tempfile
from pathlib import Path

from memory.embed import HashingEmbedder
from memory.store import FileMemoryStore, Record


def fresh_store() -> FileMemoryStore:
    vault = Path(tempfile.mkdtemp(prefix="memory-lab-scn-")) / "vault"
    # Low floor because the default embedder is lexical (see tutorial.py); a real
    # deployment uses sentence embeddings and keeps this near 0.25. Wide vectors
    # (16k slots) keep hash collisions from faking a match between unrelated
    # sentences — which matters for Scenario 2, where the honest answer is "no match."
    return FileMemoryStore(vault, embedder=HashingEmbedder(dim=16384),
                           embed_dim=16384, retrieval_min_sim=0.12,
                           char_name="yuri", user_name="you")


def plant(store: FileMemoryStore, *exchanges, days_ago: int = 0) -> None:
    ts = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days_ago)
    for i, (msg, reply) in enumerate(exchanges):
        store.remember(Record("hist", i, msg, reply,
                              ts=ts + datetime.timedelta(minutes=i)))


def context_block(store: FileMemoryStore, cue: str, k: int = 3) -> str:
    """The 'things that may be relevant' block a companion would paste into its
    prompt — exactly what recall() returns, formatted the way assembly would."""
    hits = store.recall(cue, k=k)
    if not hits:
        return "    (nothing recalled — she has no prior context to draw on)"
    lines = []
    for m in hits:
        age = m_age(m)
        lines.append(f"    • ({age}) {m.text.splitlines()[0]}")
    return "\n".join(lines)


def m_age(m) -> str:
    if not m.created_at:
        return "just now"
    days = (datetime.datetime.now(datetime.UTC)
            - datetime.datetime.fromisoformat(m.created_at)).days
    return "today" if days == 0 else f"{days}d ago"


def rule(title: str) -> None:
    print(f"\n{'═' * 72}\n {title}\n{'═' * 72}")


# ── Scenario 1: feeling heard ───────────────────────────────────────────────
def scenario_feeling_heard() -> None:
    rule("Scenario 1 — 'how did it go?' (the whole reason memory sells)")
    store = fresh_store()
    plant(store,
          ("I've got a big job interview at Atlas next Thursday, I'm nervous.",
           "You'll be good. Want to run through your answers this week?"),
          ("been prepping the interview all weekend, barely slept",
           "Get some rest tonight — tired-sharp beats wired-sharp."),
          days_ago=6)

    cue = "the Atlas interview is finally today — wish me luck"
    print(f"\nA week passes. The user opens with:\n  “{cue}”\n")

    print("── Stateless companion — its entire context is the current message:")
    print("    (no idea what 'the day' is; best it can do is a generic 'good luck!')")

    print("\n── Memory-backed companion — recall against that cue surfaces:")
    print(context_block(store, cue))
    print("\n    Now she can write the line that lands: 'The Atlas interview —\n"
          "    Thursday finally. Did you sleep? You'll be good.' That line is the\n"
          "    product. The persona didn't know it; the memory system did.")


# ── Scenario 2: honesty over confabulation ──────────────────────────────────
def scenario_honesty() -> None:
    rule("Scenario 2 — the honest 'I don't know' (why recall can return nothing)")
    store = fresh_store()
    plant(store,
          ("I play bass in a covers band on weekends.",
           "A bassist. That explains the rhythm in how you type."))

    cue = "what's my dog's name again?"
    print(f"\nThe user never mentioned a dog. They ask:\n  “{cue}”\n")
    hits = store.recall(cue, k=3)
    print(f"── recall() returns {len(hits)} memories.")
    print("    A store built to always return its top-k would hand her the bass\n"
          "    band and she'd confabulate a connection. This store applies a\n"
          "    similarity floor: nothing clears it, so it returns nothing, and she\n"
          "    can honestly say 'I don't think you've told me that yet.'")
    print("\n    A memory you can't distinguish from a guess is worth less than no\n"
          "    memory at all. The floor is what keeps recall trustworthy.")


# ── Scenario 3: the forget covenant is real ─────────────────────────────────
def scenario_forget() -> None:
    rule("Scenario 3 — 'forget that' has to actually work")
    store = fresh_store()
    plant(store,
          ("I just got out of a rough breakup with Dana.",
           "I'm sorry. I'm here as long as you want to sit with it."),
          ("anyway. tell me something good.",
           "The rain's meant to break by Friday. Small good thing."))

    cue = "how am I holding up after that rough breakup?"
    print(f"\nWeeks later, before forgetting, recall on '{cue}' can still surface Dana:")
    before = store.recall(cue, k=3)
    print(f"    Dana mentioned in recall: "
          f"{any('dana' in h.text.lower() for h in before)}")

    print("\nThe user says: 'please forget about Dana.'")
    store.forget("Dana", why="user asked")
    after = store.recall(cue, k=3)
    print(f"    Dana mentioned in recall now: "
          f"{any('dana' in h.text.lower() for h in after)}")
    print("\n    Suppressed from every future prompt — but preserved as a tombstone\n"
          "    (and in git history, in the real build). A trust feature, not just a\n"
          "    compliance checkbox. 'Forget that' the user can actually rely on is\n"
          "    part of what makes the remembering safe to trust.")


if __name__ == "__main__":
    scenario_feeling_heard()
    scenario_honesty()
    scenario_forget()
    print()
