"""Kokoro-82M synthesis wrapper.

Loads one KPipeline per language and renders text to 24 kHz mono audio,
sentence-by-sentence for streaming. Importing this module pulls in torch +
kokoro; keep it out of the import path for pure-python tests.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .config import Register, VoiceConfig, load_config
from .stream import split_sentences

_INSTALL_HINT = (
    "Kokoro is not installed. Run:\n"
    "    pip install -r requirements.txt\n"
    "and install espeak-ng on the system (apt-get install espeak-ng / "
    "brew install espeak-ng)."
)


@dataclass
class Chunk:
    """One synthesized sentence, with timing for the eval harness."""

    index: int
    text: str
    audio: np.ndarray      # float32, mono, sample_rate Hz
    gen_seconds: float     # wall-clock time to synthesize this chunk

    @property
    def audio_seconds(self) -> float:
        return len(self.audio) / 24000.0


def _to_mono_f32(audio) -> np.ndarray:
    """Normalize a Kokoro chunk (torch tensor or ndarray) to float32 mono."""
    if hasattr(audio, "detach"):          # torch tensor
        audio = audio.detach().cpu().numpy()
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim > 1:
        audio = audio.reshape(-1)
    return audio


class Synth:
    """A fixed-voice Kokoro synthesizer. One instance == one loaded model."""

    def __init__(self, config: VoiceConfig | None = None):
        self.config = config or load_config()
        try:
            from kokoro import KPipeline
        except ImportError as e:  # pragma: no cover - environment dependent
            raise RuntimeError(_INSTALL_HINT) from e
        # repo_id pinned explicitly to silence the version warning and to make
        # the asset we depend on legible.
        self._pipeline = KPipeline(
            lang_code=self.config.lang_code,
            repo_id="hexgrad/Kokoro-82M",
        )

    @property
    def sample_rate(self) -> int:
        return self.config.sample_rate

    def stream(self, text: str, register: str | None = None):
        """Yield Chunks as each sentence finishes rendering.

        This is the path that matters for latency: the caller can start playing
        chunk 0 while chunk 1 is still being synthesized (→ ch. 24 streaming).
        """
        reg: Register = self.config.register(register)
        for i, sentence in enumerate(split_sentences(text)):
            t0 = time.perf_counter()
            audio = self._render_one(sentence, reg)
            yield Chunk(
                index=i,
                text=sentence,
                audio=audio,
                gen_seconds=time.perf_counter() - t0,
            )

    def say(self, text: str, register: str | None = None) -> np.ndarray:
        """Render the whole utterance to one audio array (concatenated)."""
        chunks = [c.audio for c in self.stream(text, register)]
        if not chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(chunks)

    def _render_one(self, sentence: str, reg: Register) -> np.ndarray:
        parts = []
        for result in self._pipeline(sentence, voice=reg.voice, speed=reg.speed):
            # KPipeline yields (graphemes, phonemes, audio) per internal chunk.
            audio = result[-1] if isinstance(result, tuple) else result.audio
            parts.append(_to_mono_f32(audio))
        if not parts:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(parts)

    def to_wav(self, audio: np.ndarray, path: str | Path) -> Path:
        import soundfile as sf

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(path), audio, self.sample_rate)
        return path
