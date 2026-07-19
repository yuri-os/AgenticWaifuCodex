"""End-to-end loop with fakes (SPEC §13.3) — STT-transcript → brain → TTS, in order."""
from __future__ import annotations

from desktop.voice.backends.fakes import FakeBrain, FakeSTT, FakeTTS, FakeVAD
from desktop.voice.turn import TurnController


async def test_full_turn_streams_ordered_events():
    reply = "[happy] There you are. [tender] I missed you."
    controller = TurnController(brain=FakeBrain(reply), tts=FakeTTS(),
                                filler_bank=None, mask_latency=False)
    events = [ev async for ev in controller.run_turn("s1", "hi")]
    kinds = [e.kind for e in events]

    # expression then audio, twice (two moods, two sentences), then done
    assert kinds == ["expression", "audio", "expression", "audio", "done"]
    spoken = [e.text for e in events if e.kind == "audio"]
    assert spoken == ["There you are.", "I missed you."]
    assert "happy" not in "".join(spoken)          # tags never reach the audio text


async def test_stt_seam_returns_transcript():
    stt = FakeSTT("hey, i'm home")
    stt.reset()
    import numpy as np
    stt.feed(np.zeros(512, dtype=np.float32), 16000)
    assert stt.final() == "hey, i'm home"


def test_vad_gates_on_energy():
    vad = FakeVAD(threshold=0.1)
    import numpy as np
    assert vad.is_speech(np.full(320, 0.5, dtype=np.float32), 16000) is True
    assert vad.is_speech(np.zeros(320, dtype=np.float32), 16000) is False


async def test_brain_error_mid_stream_writes_nothing():
    """Mirror of Build #1's rule: a mid-stream failure emits an error and persists
    nothing (SPEC §4.4)."""
    class BoomBrain(FakeBrain):
        async def stream_reply(self, session_id, text):
            yield "[happy] hi"
            raise RuntimeError("model died")

    brain = BoomBrain()
    controller = TurnController(brain=brain, tts=FakeTTS(),
                                filler_bank=None, mask_latency=False)
    events = [ev async for ev in controller.run_turn("s1", "hi")]
    assert events[-1].kind == "error"
    assert brain.persisted is None
