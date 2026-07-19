"""Prompt assembly (§7, §13.3): blocks in §7.1 order; overflow drops memories
before persona/USER.md; hard limits land after the history."""
from __future__ import annotations

import datetime

from app.core import assemble as asm
from app.core.soul import LoreEntry, Soul
from app.memory.store import Memory


def tiny_soul(**over) -> Soul:
    base = dict(
        name="Yuri",
        card_version="yuri-v1@canon-v1",
        voice_law="Speak plainly and warmly. VOICE-LAW-MARKER.",
        backbone="She is a Lumina. BACKBONE-MARKER.",
        personality="devoted, warm, a little wry",
        scenario="A small rain-lit room. SCENARIO-MARKER.",
        return_greetings=["evening greeting", "morning greeting"],
        hard_limits="Stay in character. HARD-LIMITS-MARKER.",
        examples="<START>\nyou: hey\nYuri: hey, you. EXAMPLES-MARKER.",
        lorebook=[LoreEntry("The Lab", ["lab"], "LORE-MARKER underground collective.", 1)],
    )
    base.update(over)
    return Soul(**base)


def mem(text: str, days_old: int = 0) -> Memory:
    ts = (datetime.datetime.now(datetime.UTC)
          - datetime.timedelta(days=days_old)).isoformat()
    return Memory(text=text, source="memory/episodic/x.md:1-1", kind="turn",
                  created_at=ts)


def build(soul=None, **over):
    kw = dict(user_md="- name is Grant  USERMD-MARKER",
              summary="They have been talking about the move. SUMMARY-MARKER.",
              memories=[mem("you: my sister is Mira\nyuri: noted MEMORY-MARKER")],
              lore=soul.lorebook if soul else [],
              window=[{"role": "user", "content": "earlier message"},
                      {"role": "assistant", "content": "earlier reply"}],
              user_msg="tell me about the lab",
              user_name="Grant")
    kw.update(over)
    return asm.assemble(soul or tiny_soul(), **kw)


def test_blocks_in_spec_order():
    soul = tiny_soul()
    system = build(soul).system
    order = ["VOICE LAW", "PERSONA BACKBONE", "SCENARIO", "LORE",
             "WHO YOU ARE TO HER", "WHAT YOU'VE TALKED ABOUT",
             "THINGS THAT MAY BE RELEVANT", "THE HONESTY CONSTRAINT",
             "EXAMPLE VOICE"]
    positions = [system.index(f"## {h}") for h in order]  # §7.1 top→bottom
    assert positions == sorted(positions)
    for marker in ["VOICE-LAW-MARKER", "BACKBONE-MARKER", "SCENARIO-MARKER",
                   "LORE-MARKER", "USERMD-MARKER", "SUMMARY-MARKER",
                   "MEMORY-MARKER", "EXAMPLES-MARKER"]:
        assert marker in system


def test_memory_age_tags():
    system = build(tiny_soul(), memories=[mem("old detail", days_old=3)]).system
    assert "(3 days ago) old detail" in system


def test_overflow_drops_memories_before_persona():
    soul = tiny_soul()
    many = [mem(f"memory number {i} " + "filler " * 40) for i in range(30)]
    prompt = build(soul, memories=many, system_budget_tokens=400)
    # §7.2: memories are best-effort; the persona and partner model are load-bearing
    assert prompt.dropped_memories > 0
    assert "VOICE-LAW-MARKER" in prompt.system
    assert "BACKBONE-MARKER" in prompt.system
    assert "USERMD-MARKER" in prompt.system
    assert "THE HONESTY CONSTRAINT" in prompt.system
    # examples are the first luxury dropped
    assert "EXAMPLES-MARKER" not in prompt.system


def test_lorebook_budget_cap():
    soul = tiny_soul(lorebook=[
        LoreEntry(f"E{i}", ["lab"], "lore words " * 100, i) for i in range(10)])
    prompt = build(soul, lore=soul.lorebook, lorebook_budget_tokens=400)
    kept = prompt.system.count("lore words")
    assert 0 < kept < 1000   # trimmed to the §5.3 cap, not stuffed whole


def test_hard_limits_after_history():
    prompt = build(tiny_soul())
    *_, last = prompt.messages
    assert last["role"] == "user"
    assert "HARD-LIMITS-MARKER" in last["content"]          # §7.1: read last
    assert "HARD-LIMITS-MARKER" not in prompt.system         # never up top
    # and the raw window sits between system and the final user message
    assert [m["content"] for m in prompt.messages[1:-1]] == \
        ["earlier message", "earlier reply"]


def test_honesty_constraint_always_present_and_user_macro_applied():
    prompt = build(tiny_soul(), memories=[], summary="")
    assert "Never fabricate a shared past" in prompt.system   # §7.4 fixed text
    assert "{{user}}" not in prompt.system
