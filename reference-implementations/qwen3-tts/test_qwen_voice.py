"""Tests for the Qwen3-TTS reference implementation.

Splitter/config tests run anywhere. The synthesis tests need qwen-tts + weights
+ a GPU, so they skip cleanly when the environment isn't set up.
"""

import importlib.util

import numpy as np
import pytest

from qwen_voice import load_config, split_sentences
from qwen_voice.config import Register, MODES

HAVE_QWEN = importlib.util.find_spec("qwen_tts") is not None
needs_model = pytest.mark.skipif(not HAVE_QWEN, reason="qwen-tts not installed")


# --- splitter ---------------------------------------------------------------

def test_split_basic():
    assert split_sentences("Hello there. How are you?") == [
        "Hello there.", "How are you?"
    ]


def test_split_empty():
    assert split_sentences("  \n ") == []


# --- config -----------------------------------------------------------------

def test_config_loads_all_modes_present():
    cfg = load_config()
    for mode in MODES:
        assert cfg.model_for(mode)  # a model id per mode
    assert cfg.active_register in cfg.registers


def test_register_resolution_and_unknown():
    cfg = load_config()
    assert cfg.register(None).name == cfg.active_register
    with pytest.raises(KeyError):
        cfg.register("nope")


def test_clone_register_resolves_local_ref_path():
    cfg = load_config()
    reg = cfg.register("default")
    assert reg.mode == "clone"
    assert reg.ref_path() is not None and reg.ref_path().is_absolute()


def test_validation_rejects_incomplete_register():
    # a clone register with no ref_text must fail validation
    from qwen_voice.config import _validate

    with pytest.raises(ValueError):
        _validate(Register(name="x", mode="clone", ref_audio="a.wav"))
    with pytest.raises(ValueError):
        _validate(Register(name="x", mode="design"))  # no instruct
    with pytest.raises(ValueError):
        _validate(Register(name="x", mode="bogus"))


# --- synthesis (needs the model + GPU) -------------------------------------

@needs_model
def test_design_mode_produces_audio():
    from qwen_voice import Synth

    synth = Synth(load_config())
    audio, sr = synth.say("Hey, you made it back.", register="designed")
    assert audio.dtype == np.float32 and audio.ndim == 1
    assert sr > 0 and len(audio) > sr * 0.3
