"""Shared fixtures. The whole suite runs offline against the fakes (SPEC §13.3)."""
from __future__ import annotations

import pytest

from desktop.voice.backends.fakes import FakeBrain, FakeTTS, FakeVAD
from desktop.voice.fillers import FillerBank
from desktop.voice.turn import TurnController


@pytest.fixture
def tts() -> FakeTTS:
    return FakeTTS()


@pytest.fixture
def brain() -> FakeBrain:
    return FakeBrain()


@pytest.fixture
def controller(brain: FakeBrain, tts: FakeTTS) -> TurnController:
    bank = FillerBank(tts=tts, phrases=("Mm.", "Hm, okay."))
    bank.prime()
    return TurnController(brain=brain, tts=tts, filler_bank=bank,
                          mask_latency=True)


async def drain(controller: TurnController, session: str, text: str) -> list:
    """Collect every OutEvent a turn produces (no barge-in)."""
    return [ev async for ev in controller.run_turn(session, text)]
