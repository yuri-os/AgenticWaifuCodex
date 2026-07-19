"""Thin client for the GPT-SoVITS ``api_v2.py`` server.

Keeps our code small: the heavy model runs in its own process/env, we just POST
text + a reference voice and get audio back. This is the swappable backend seam
from ch. 26 — the runtime never imports GPT-SoVITS, it calls this.
"""

from __future__ import annotations

import io
import time
from dataclasses import dataclass

import numpy as np
import requests

from .config import Config, Voice, load_config
from .stream import split_sentences


@dataclass
class Chunk:
    index: int
    text: str
    audio: np.ndarray      # float32 mono @ sample_rate
    gen_seconds: float
    sample_rate: int = 32000

    @property
    def audio_seconds(self) -> float:
        return len(self.audio) / self.sample_rate


def _pcm_from_byte_stream(byte_iter):
    """Turn a stream of raw int16-LE PCM byte fragments into float32 frames.

    Network chunks can split mid-sample (odd byte counts), so we carry the
    trailing odd byte across fragments and only emit whole samples. Pure and
    network-free so it's unit-testable (see test_sovits_voice.py).
    """
    carry = b""
    for raw in byte_iter:
        if not raw:
            continue
        buf = carry + raw
        n = len(buf) - (len(buf) % 2)        # largest even prefix
        if n:
            yield np.frombuffer(buf[:n], dtype="<i2").astype(np.float32) / 32768.0
        carry = buf[n:]


class SovitsClient:
    def __init__(self, config: Config | None = None):
        self.config = config or load_config()
        self._weights_set: set[str] = set()

    # --- server liveness ----------------------------------------------------
    def health(self) -> bool:
        """True if the api_v2 server answers at all (root 404 still means up)."""
        try:
            requests.get(self.config.server_url, timeout=3)
            return True
        except requests.RequestException:
            return False

    # --- weight switching (fine-tuned voices) -------------------------------
    def ensure_weights(self, voice: Voice) -> None:
        """Load this voice's fine-tuned checkpoints if it pins any (once)."""
        for kind, path in (("gpt", voice.gpt_weights), ("sovits", voice.sovits_weights)):
            if not path or path in self._weights_set:
                continue
            ep = "set_gpt_weights" if kind == "gpt" else "set_sovits_weights"
            r = requests.get(
                f"{self.config.server_url}/{ep}",
                params={"weights_path": path},
                timeout=self.config.timeout_s,
            )
            r.raise_for_status()
            self._weights_set.add(path)

    # --- synthesis ----------------------------------------------------------
    def _payload(self, text: str, voice: Voice, *, streaming: bool, media_type: str) -> dict:
        inf = self.config.inference
        return {
            "text": text,
            "text_lang": voice.text_lang,
            "ref_audio_path": str(voice.ref_path()),
            "prompt_text": voice.prompt_text,
            "prompt_lang": voice.prompt_lang,
            "top_k": inf.get("top_k", 15),
            "top_p": inf.get("top_p", 1.0),
            "temperature": inf.get("temperature", 1.0),
            "speed_factor": inf.get("speed_factor", 1.0),
            "text_split_method": inf.get("text_split_method", "cut5"),
            "media_type": media_type,
            "streaming_mode": streaming,
        }

    def _decode(self, content: bytes, media_type: str) -> np.ndarray:
        if media_type == "raw":
            pcm = np.frombuffer(content, dtype=np.int16).astype(np.float32) / 32768.0
            return pcm
        import soundfile as sf

        audio, _sr = sf.read(io.BytesIO(content), dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        return audio.astype(np.float32)

    def _tts(self, text: str, voice: Voice, media_type: str = "wav") -> np.ndarray:
        r = requests.post(
            f"{self.config.server_url}/tts",
            json=self._payload(text, voice, streaming=False, media_type=media_type),
            timeout=self.config.timeout_s,
        )
        if r.status_code != 200:
            raise RuntimeError(f"GPT-SoVITS /tts failed ({r.status_code}): {r.text[:200]}")
        return self._decode(r.content, media_type)

    def stream(self, text: str, register: str | None = None):
        """Yield one Chunk per sentence (client-side split) for low TTFA."""
        voice = self.config.voice_for_register(register)
        self.ensure_weights(voice)
        for i, sentence in enumerate(split_sentences(text)):
            t0 = time.perf_counter()
            audio = self._tts(sentence, voice)
            yield Chunk(i, sentence, audio, time.perf_counter() - t0,
                        sample_rate=self.config.sample_rate)

    def stream_pcm(self, text: str, register: str | None = None):
        """Yield float32 PCM chunks as the server generates them (true streaming).

        Uses the api_v2 server's ``streaming_mode`` + ``raw`` media type and reads
        the chunked HTTP response as it arrives, so playback can start on the
        first packet instead of after the whole sentence renders. This is the
        low-latency path GPT-SoVITS is built for (→ ch. 24); the per-sentence
        ``stream()`` above is the simpler, non-streaming fallback.
        """
        voice = self.config.voice_for_register(register)
        self.ensure_weights(voice)
        payload = self._payload(text, voice, streaming=True, media_type="raw")
        with requests.post(
            f"{self.config.server_url}/tts",
            json=payload,
            stream=True,
            timeout=self.config.timeout_s,
        ) as r:
            if r.status_code != 200:
                raise RuntimeError(
                    f"GPT-SoVITS /tts stream failed ({r.status_code}): {r.text[:200]}")
            yield from _pcm_from_byte_stream(r.iter_content(chunk_size=4096))

    def say(self, text: str, register: str | None = None) -> np.ndarray:
        chunks = [c.audio for c in self.stream(text, register)]
        if not chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(chunks)

    def to_wav(self, audio: np.ndarray, path) -> "object":
        import soundfile as sf
        from pathlib import Path

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(path), audio, self.config.sample_rate)
        return path
