"""Tests for the GPT-SoVITS voice client.

Splitter/config/payload/decode tests run anywhere (no model, no network). The
synthesis tests need a running api_v2 server and skip cleanly when it's down.
"""

import io

import numpy as np
import pytest

from sovits_voice import load_config, split_sentences
from sovits_voice.client import SovitsClient, _pcm_from_byte_stream


# --- splitter ---------------------------------------------------------------

def test_split_basic():
    assert split_sentences("Hello there. How are you?") == [
        "Hello there.", "How are you?"
    ]


def test_split_empty():
    assert split_sentences("   \n ") == []


# --- config -----------------------------------------------------------------

def test_config_and_register_resolution():
    cfg = load_config()
    assert cfg.sample_rate > 0
    assert cfg.active_register in cfg.registers
    v = cfg.voice_for_register(None)
    assert v.prompt_text and v.ref_audio
    with pytest.raises(KeyError):
        cfg.voice_for_register("nope")


def test_ref_path_is_absolute():
    cfg = load_config()
    v = cfg.voice_for_register("default")
    assert v.ref_path().is_absolute()


# --- payload (no network) ---------------------------------------------------

def test_payload_has_required_api_v2_fields():
    cfg = load_config()
    client = SovitsClient(cfg)
    v = cfg.voice_for_register("default")
    p = client._payload("Hi there.", v, streaming=False, media_type="wav")
    for key in ("text", "text_lang", "ref_audio_path", "prompt_text",
                "prompt_lang", "media_type", "streaming_mode"):
        assert key in p
    assert p["text"] == "Hi there."
    assert p["streaming_mode"] is False
    assert p["ref_audio_path"].endswith(".wav")


# --- decode -----------------------------------------------------------------

def test_decode_raw_int16_roundtrip():
    cfg = load_config()
    client = SovitsClient(cfg)
    sig = (np.array([0.0, 0.5, -0.5, 1.0, -1.0], dtype=np.float32) * 32767
           ).astype(np.int16)
    out = client._decode(sig.tobytes(), "raw")
    assert np.allclose(out, sig.astype(np.float32) / 32768.0, atol=1e-4)


def test_streaming_payload_uses_raw_and_streaming():
    cfg = load_config()
    client = SovitsClient(cfg)
    v = cfg.voice_for_register("default")
    p = client._payload("Hi there.", v, streaming=True, media_type="raw")
    assert p["streaming_mode"] is True
    assert p["media_type"] == "raw"


def test_pcm_from_byte_stream_reassembles_split_samples():
    # int16 samples, fed in fragments that split a sample across the boundary
    sig = (np.array([0.0, 0.5, -0.5, 1.0, -1.0, 0.25], dtype=np.float32) * 32767
           ).astype("<i2")
    data = sig.tobytes()
    # 3-byte fragments guarantee odd splits mid-sample
    frags = [data[i:i + 3] for i in range(0, len(data), 3)]
    out = np.concatenate(list(_pcm_from_byte_stream(frags)))
    assert np.allclose(out, sig.astype(np.float32) / 32768.0, atol=1e-4)
    assert len(out) == len(sig)


def test_pcm_from_byte_stream_drops_trailing_odd_byte():
    # a lone trailing byte (incomplete sample) must not be emitted
    out = list(_pcm_from_byte_stream([b"\x01\x00\x02"]))  # 3 bytes = 1 sample + 1
    assert len(out) == 1 and out[0].shape == (1,)


def test_decode_wav_roundtrip():
    import soundfile as sf

    cfg = load_config()
    client = SovitsClient(cfg)
    sig = np.sin(np.linspace(0, 6.28, 2000)).astype(np.float32)
    buf = io.BytesIO()
    sf.write(buf, sig, cfg.sample_rate, format="WAV")
    out = client._decode(buf.getvalue(), "wav")
    assert out.shape == sig.shape
    assert np.allclose(out, sig, atol=1e-3)


# --- live server (skips if down) -------------------------------------------

def _server_up() -> bool:
    return SovitsClient(load_config()).health()


needs_server = pytest.mark.skipif(not _server_up(), reason="api_v2 server not running")


@needs_server
def test_say_produces_audio():
    client = SovitsClient(load_config())
    audio = client.say("Hey. You made it back.")
    assert audio.dtype == np.float32 and audio.ndim == 1
    assert len(audio) > load_config().sample_rate * 0.3


@needs_server
def test_stream_pcm_yields_realtime_chunks():
    client = SovitsClient(load_config())
    chunks = list(client.stream_pcm("Hey. You made it back. I missed you."))
    assert len(chunks) >= 2                      # actually streamed, not one blob
    assert all(c.dtype == np.float32 for c in chunks)
    total = sum(len(c) for c in chunks)
    assert total > load_config().sample_rate * 0.3
