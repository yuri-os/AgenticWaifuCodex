"""Whisper stays on the predictable CPU path, including under WSL."""
from __future__ import annotations

import sys
import types

from desktop.voice.backends.stt_whisper import WhisperSTT


def test_whisper_forces_cpu(monkeypatch):
    calls = []

    class WhisperModel:
        def __init__(self, *args, **kwargs):
            calls.append((args, kwargs))

    monkeypatch.setitem(sys.modules, "faster_whisper",
                        types.SimpleNamespace(WhisperModel=WhisperModel))

    WhisperSTT("tiny.en", compute_type="int8")

    assert calls == [(('tiny.en',), {"device": "cpu", "compute_type": "int8"})]
