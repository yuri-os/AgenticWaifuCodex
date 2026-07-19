"""Tests for the Kokoro voice reference implementation.

The splitter/config tests are pure-python and always run. The synthesis tests
require kokoro + espeak-ng + the model weights, so they skip cleanly when the
environment isn't set up — run them once you've installed requirements.
"""

import importlib.util

import numpy as np
import pytest

from kokoro_voice import load_config, split_sentences
from eval.eval import cov, spectral_centroid

HAVE_KOKORO = importlib.util.find_spec("kokoro") is not None
needs_model = pytest.mark.skipif(not HAVE_KOKORO, reason="kokoro not installed")


# --- splitter (pure python) -------------------------------------------------

def test_split_basic():
    assert split_sentences("Hello there. How are you?") == [
        "Hello there.", "How are you?"
    ]


def test_split_keeps_punctuation_and_ellipsis():
    out = split_sentences("Wait… you finished it! Really?")
    assert out == ["Wait…", "you finished it!", "Really?"]


def test_split_newlines_and_whitespace():
    assert split_sentences("  one\n\ntwo  \n three ") == ["one", "two", "three"]


def test_split_empty():
    assert split_sentences("") == []
    assert split_sentences("   \n  ") == []


def test_split_no_terminal_punctuation():
    # A bare phrase is still one chunk.
    assert split_sentences("just sit here a while") == ["just sit here a while"]


# --- config -----------------------------------------------------------------

def test_config_loads_default():
    cfg = load_config()
    assert cfg.sample_rate == 24000
    assert cfg.active_register in cfg.registers
    assert cfg.active.voice  # non-empty


def test_register_resolution_and_fallback():
    cfg = load_config()
    assert cfg.register(None) == cfg.active
    with pytest.raises(KeyError):
        cfg.register("does_not_exist")


# --- eval feature helpers ---------------------------------------------------

def test_spectral_centroid_orders_by_pitch():
    sr = 24000
    t = np.linspace(0, 1, sr, endpoint=False)
    low = np.sin(2 * np.pi * 200 * t).astype(np.float32)
    high = np.sin(2 * np.pi * 2000 * t).astype(np.float32)
    assert spectral_centroid(low, sr) < spectral_centroid(high, sr)


def test_cov_zero_for_constant():
    assert cov([5.0, 5.0, 5.0]) == 0.0
    assert cov([1.0]) == 0.0  # too few values


# --- synthesis (needs the model) -------------------------------------------

@needs_model
def test_synth_produces_audio():
    from kokoro_voice import Synth

    synth = Synth(load_config())
    audio = synth.say("Hey. You made it back.")
    assert audio.dtype == np.float32
    assert audio.ndim == 1
    assert len(audio) > synth.sample_rate * 0.5  # at least ~0.5s of speech


@needs_model
def test_synth_is_stable():
    """The consistency guarantee: same text + pinned voice -> same utterance.

    On GPU exact samples jitter from non-deterministic kernels, so we assert
    stable duration + negligible difference (perceptually identical), not
    bit-equality. The voice *identity* is pinned by construction.
    """
    from kokoro_voice import Synth

    synth = Synth(load_config())
    a = synth.say("I kept the light on.")
    b = synth.say("I kept the light on.")
    assert a.shape == b.shape
    assert np.abs(a - b).mean() < 0.01


@needs_model
def test_stream_yields_one_chunk_per_sentence():
    from kokoro_voice import Synth

    synth = Synth(load_config())
    chunks = list(synth.stream("First sentence. Second one. Third here."))
    assert len(chunks) == 3
    assert all(c.audio.size > 0 for c in chunks)
