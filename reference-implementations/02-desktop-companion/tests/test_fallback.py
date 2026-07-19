"""Backend degradation (SPEC §3) — `python -m desktop` must boot with no models.

The bug this guards: a fresh `pip install -e ".[test]"` has none of the voice
libs, so building the default real backends must NOT crash — it must fall back
to the fakes with a warning, and /api/health must report the truth.
"""
from __future__ import annotations

from desktop.main import _graceful, build_tts, build_stt, build_vad
from desktop.config import Config
from desktop.voice.backends.fakes import FakeTTS


def test_graceful_falls_back_when_real_raises():
    def boom():
        raise RuntimeError("faster-whisper not installed")
    inst, name = _graceful("STT", "faster_whisper", boom, FakeTTS, "stt")
    assert name == "fake" and isinstance(inst, FakeTTS)


def test_graceful_uses_real_when_it_builds():
    inst, name = _graceful("TTS", "kokoro", FakeTTS, lambda: None, "tts")
    assert name == "kokoro" and isinstance(inst, FakeTTS)


def test_fake_backend_requested_is_honoured_directly():
    cfg = Config(tts_backend="fake", stt_backend="fake", vad_backend="fake")
    assert build_tts(cfg)[1] == "fake"
    assert build_stt(cfg)[1] == "fake"
    assert build_vad(cfg)[1] == "fake"
