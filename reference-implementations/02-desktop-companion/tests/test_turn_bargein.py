"""Barge-in as a pipeline cancel (SPEC §4.3–§4.4) — the non-negotiable behaviour.

When the user talks over her, cancel() must (1) stop audio going out, (2) abort
the in-flight brain generation, and (3) leave no trace — no persist, no corpus,
no commit. These three are the difference between a companion that feels alive
and one that keeps talking over you with words it already committed to (ch. 32).
"""
from __future__ import annotations

import asyncio

import pytest

from desktop.voice.turn import TurnController


async def test_bargein_stops_audio_and_aborts_generation(controller, brain):
    """Cancel mid-stream: she stops emitting audio AND the brain stops generating."""
    gate = brain.gate_after(3)          # fire once 3 tokens have streamed
    events = []

    agen = controller.run_turn("s1", "hi there")
    # pull events until the brain is a few tokens in, then barge in
    async def puller():
        async for ev in agen:
            events.append(ev)

    task = asyncio.create_task(puller())
    await asyncio.wait_for(gate.wait(), timeout=2.0)
    controller.cancel()                 # <-- the mic handler fired
    await asyncio.wait_for(task, timeout=2.0)

    # (1) the turn ended in a cancellation, not a normal done
    kinds = [e.kind for e in events]
    assert "cancelled" in kinds
    assert "done" not in kinds
    # (2) generation was aborted early — not every token was emitted
    assert brain.tokens_emitted < len(brain.reply.split())  # far short of the full reply
    # (3) a barged-in turn writes nothing (SPEC §4.4)
    assert brain.persisted is None


async def test_clean_turn_persists_and_reports_latency(controller, brain):
    """The happy path: full audio out, then exactly one persist with the verbatim reply."""
    events = [ev async for ev in controller.run_turn("s1", "hi")]
    kinds = [e.kind for e in events]

    assert kinds[-1] == "done"
    assert "cancelled" not in kinds
    # audio actually streamed, sentence by sentence
    audio = [e for e in events if e.kind == "audio"]
    assert len(audio) >= 2               # the fake reply has two sentences
    # persisted once, with the model's verbatim output (tags kept for the corpus)
    assert brain.persisted is not None
    _, user_text, reply = brain.persisted
    assert user_text == "hi"
    assert "[happy]" in reply            # corpus sees what the model actually produced
    # the done event carries the measured latency report
    assert "latency" in events[-1].detail


async def test_expression_events_precede_their_audio(controller):
    """Face leads voice: an [happy] tag emits an expression event before the audio
    of the sentence it introduces (SPEC §6)."""
    events = [ev async for ev in controller.run_turn("s1", "hi")]
    kinds = [e.kind for e in events]
    first_expr = kinds.index("expression")
    first_audio = kinds.index("audio")
    assert first_expr < first_audio


async def test_cancel_is_idempotent_and_next_turn_is_clean(controller, brain):
    """The mic handler fires cancel() on every speech frame, so it must be safe to
    call repeatedly; and a fresh turn gets a fresh cancel token (SPEC §4.3)."""
    gate = brain.gate_after(2)

    async def puller(agen, sink):
        async for ev in agen:
            sink.append(ev)

    first: list = []
    task = asyncio.create_task(puller(controller.run_turn("s1", "hi"), first))
    await asyncio.wait_for(gate.wait(), timeout=2.0)
    controller.cancel(); controller.cancel(); controller.cancel()   # idempotent
    await asyncio.wait_for(task, timeout=2.0)
    assert brain.persisted is None                    # barged-in turn wrote nothing

    # the NEXT turn is unaffected by the previous cancel — it completes normally
    brain2 = brain
    events = [ev async for ev in controller.run_turn("s2", "again")]
    assert events[-1].kind == "done"
    assert brain2.persisted is not None
