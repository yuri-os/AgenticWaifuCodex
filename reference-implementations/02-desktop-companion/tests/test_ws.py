"""The /ws/voice route (SPEC §10) — greeting, a turn, and barge-in over the wire.

Runs the real FastAPI route against a FakeBrain + fake voice backends (no Vault,
no models), so it exercises the websocket protocol itself: the concurrent
reader/writer, event encoding, and that a {"type":"bargein"} control message
cancels an in-flight turn.
"""
from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("fastapi")
from starlette.testclient import TestClient  # noqa: E402

from desktop.config import Config             # noqa: E402
from desktop.main import create_app           # noqa: E402
from desktop.voice.backends.fakes import FakeBrain  # noqa: E402


def _app(brain=None):
    cfg = Config(tts_backend="fake", stt_backend="fake", vad_backend="fake",
                 mask_latency=False)
    return create_app(cfg, brain=brain or FakeBrain())


def _drain(ws, cap=40):
    kinds = []
    for _ in range(cap):
        m = ws.receive_json()
        kinds.append(m["type"])
        if m["type"] in ("done", "error", "cancelled"):
            break
    return kinds


def _audio_texts(ws, cap=60):
    """Drain a turn, collecting the spoken text of each audio/filler event."""
    texts = []
    for _ in range(cap):
        m = ws.receive_json()
        if m["type"] in ("audio", "filler") and m.get("text"):
            texts.append(m["text"])
        if m["type"] in ("done", "error", "cancelled"):
            break
    return texts


def test_reconnect_does_not_regreet():
    """She greets on arrival (§7) but a reconnect is not a new arrival: a second
    connection for the same session must not talk a second greeting over the first
    (the 'multiple voices on startup' bug)."""
    app = _app()
    client = TestClient(app)
    with client.websocket_connect("/ws/voice") as ws:
        ws.send_json({"type": "hello", "session_id": None})
        sid = ws.receive_json()["session_id"]
        assert any("there you are" in t for t in _audio_texts(ws))   # first arrival greets
    # reconnect with the same id — no greeting; only the turn we ask for plays
    with client.websocket_connect("/ws/voice") as ws:
        ws.send_json({"type": "hello", "session_id": sid})
        assert ws.receive_json()["type"] == "session"
        ws.send_json({"type": "text", "text": "hi again"})
        texts = _audio_texts(ws)
        assert texts and not any("there you are" in t for t in texts)
        assert any("made it back" in t for t in texts)


def test_greeting_then_typed_turn():
    with TestClient(_app()).websocket_connect("/ws/voice") as ws:
        ws.send_json({"type": "hello", "session_id": None})
        assert ws.receive_json()["type"] == "session"
        greeting = _drain(ws)
        assert greeting[-1] == "done" and "audio" in greeting

        ws.send_json({"type": "text", "text": "hey, i'm home"})
        turn = _drain(ws)
        assert turn[-1] == "done"
        assert "expression" in turn and "audio" in turn


def test_endpoint_drops_noise_but_takes_speech():
    """A mechanical keyboard under the mic (frames the VAD calls non-speech) must
    not become a turn: the server confirms real speech before transcribing (§3.4,
    §4.2). FakeVAD gates on RMS ≥ 0.1, so 'noise' frames never clear the gate."""
    brain = FakeBrain()
    speech = np.full(512, 0.2, dtype=np.float32).tobytes()    # RMS 0.2 → speech
    noise = np.full(512, 0.03, dtype=np.float32).tobytes()    # RMS 0.03 → not speech
    with TestClient(_app(brain)).websocket_connect("/ws/voice") as ws:
        ws.send_json({"type": "hello", "session_id": None})
        ws.receive_json()                       # session
        _drain(ws)                              # greeting (not persisted)

        # clatter the VAD never confirms → this endpoint produces no turn
        for _ in range(6):
            ws.send_bytes(noise)
        ws.send_json({"type": "endpoint"})

        # a real utterance → a turn runs and streams to done
        for _ in range(6):
            ws.send_bytes(speech)
        ws.send_json({"type": "endpoint"})
        assert _drain(ws)[-1] == "done"
    # exactly one turn persisted (the speech one) — the noise endpoint was dropped
    assert len(brain.persist_calls) == 1
    assert brain.persist_calls[0][1] == "hey, i'm back"   # FakeSTT's transcript


def test_typed_turn_persists_via_brain():
    brain = FakeBrain()
    with TestClient(_app(brain)).websocket_connect("/ws/voice") as ws:
        ws.send_json({"type": "hello", "session_id": None})
        ws.receive_json()                       # session
        _drain(ws)                              # greeting (not persisted)
        assert brain.persisted is None
        ws.send_json({"type": "text", "text": "remember milk"})
        _drain(ws)                              # the turn
    assert brain.persisted is not None
    assert brain.persisted[1] == "remember milk"
