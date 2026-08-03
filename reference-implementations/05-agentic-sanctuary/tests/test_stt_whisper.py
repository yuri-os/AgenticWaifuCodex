"""Portable faster-whisper construction."""
from __future__ import annotations

import sys
import types

from desktop.voice.backends.stt_whisper import WhisperSTT


def test_whisper_uses_cpu_when_a_host_gpu_is_visible(monkeypatch):
    calls = []

    class FakeWhisperModel:
        def __init__(self, *args, **kwargs):
            calls.append((args, kwargs))

    module = types.ModuleType("faster_whisper")
    module.WhisperModel = FakeWhisperModel
    monkeypatch.setitem(sys.modules, "faster_whisper", module)

    WhisperSTT("base.en", "int8")

    assert calls == [(("base.en",), {"device": "cpu", "compute_type": "int8"})]
