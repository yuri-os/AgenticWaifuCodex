"""Kokoro voice — a minimal local TTS service for a fixed companion voice.

Reference implementation for ch. 24 (Voice). Wraps Kokoro-82M behind a small
synth API that streams sentence-by-sentence — the one move that makes spoken
replies feel alive instead of arriving in a single late block.
"""

from .stream import split_sentences
from .config import VoiceConfig, load_config

__all__ = ["split_sentences", "VoiceConfig", "load_config", "Synth"]


def __getattr__(name):
    # Lazily expose Synth so importing the package (e.g. for the pure-python
    # sentence-splitter tests) doesn't drag in torch/kokoro.
    if name == "Synth":
        from .synth import Synth

        return Synth
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
