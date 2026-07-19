"""Qwen3-TTS voice — clone, design, or preset, in one Apache-2.0 model.

Reference implementation for ch. 24. Where ../kokoro picks one fixed voice and
../gpt-sovits clones a specific identity, Qwen3-TTS does both *and* designs a
voice from a text description — the convergence local-voice option (Jan 2026).
Importing the package is cheap; Synth is loaded lazily (it pulls torch).
"""

from .config import Config, Register, load_config
from .stream import split_sentences

__all__ = ["Config", "Register", "load_config", "split_sentences", "Synth"]


def __getattr__(name):
    if name == "Synth":
        from .synth import Synth

        return Synth
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
