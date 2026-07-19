"""Latency masking (SPEC §5). A pre-rendered filler fires before the first token."""
from __future__ import annotations

from desktop.voice.backends.fakes import FakeTTS
from desktop.voice.fillers import FillerBank


def test_prime_synthesizes_every_phrase():
    bank = FillerBank(tts=FakeTTS(), phrases=("Mm.", "Hm, okay.", "One sec."))
    bank.prime()
    assert bank.pick() is not None
    # every phrase became a cached clip with real audio
    seen = {bank.pick().text for _ in range(30)}
    assert seen == {"Mm.", "Hm, okay.", "One sec."}


def test_pick_never_repeats_consecutively():
    bank = FillerBank(tts=FakeTTS(), phrases=("a.", "b.", "c."))
    bank.prime()
    picks = [bank.pick().text for _ in range(50)]
    assert all(picks[i] != picks[i + 1] for i in range(len(picks) - 1))


def test_empty_bank_returns_none():
    bank = FillerBank(tts=FakeTTS(), phrases=())
    bank.prime()
    assert bank.pick() is None


async def test_turn_emits_filler_before_first_audio(controller):
    """With masking on, the filler is the first sound out — before any real audio (§5)."""
    events = [ev async for ev in controller.run_turn("s1", "hi")]
    kinds = [e.kind for e in events]
    assert kinds[0] == "filler"
    assert kinds.index("filler") < kinds.index("audio")


async def test_masking_can_be_disabled(brain, tts):
    from desktop.voice.turn import TurnController
    c = TurnController(brain=brain, tts=tts, filler_bank=None, mask_latency=False)
    events = [ev async for ev in c.run_turn("s1", "hi")]
    assert all(e.kind != "filler" for e in events)
