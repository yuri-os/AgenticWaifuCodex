"""Qwen3-TTS synthesis wrapper (clone / design / custom).

Runs the model in-process. Each mode uses a different model variant, so we lazy-
load and cache one model per variant — switching registers across modes loads a
second model, switching within a mode reuses it. Importing this module pulls in
torch + qwen_tts; keep it off the import path for pure-python tests.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .config import Config, Register, load_config
from .stream import split_sentences

_INSTALL_HINT = (
    "qwen-tts is not installed. Run:\n"
    "    pip install -r requirements.txt\n"
    "(first synthesis downloads the model weights from Hugging Face)."
)


@dataclass
class Chunk:
    index: int
    text: str
    audio: np.ndarray
    gen_seconds: float
    sample_rate: int

    @property
    def audio_seconds(self) -> float:
        return len(self.audio) / self.sample_rate


def _dtype(name: str):
    import torch

    return {"bfloat16": torch.bfloat16, "float16": torch.float16,
            "float32": torch.float32}.get(name, torch.bfloat16)


def _to_mono_f32(audio) -> np.ndarray:
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    audio = np.asarray(audio, dtype=np.float32)
    return audio.reshape(-1) if audio.ndim > 1 else audio


class Synth:
    def __init__(self, config: Config | None = None):
        self.config = config or load_config()
        try:
            import qwen_tts  # noqa: F401
        except ImportError as e:  # pragma: no cover - environment dependent
            raise RuntimeError(_INSTALL_HINT) from e
        self._models: dict[str, object] = {}

    def _get_model(self, model_id: str):
        if model_id not in self._models:
            import torch  # noqa: F401
            from qwen_tts import Qwen3TTSModel

            self._models[model_id] = Qwen3TTSModel.from_pretrained(
                model_id,
                device_map=self.config.device,
                dtype=_dtype(self.config.dtype),
                attn_implementation=self.config.attn,
            )
        return self._models[model_id]

    def _generate(self, sentence: str, reg: Register):
        """Dispatch one sentence to the right mode; return (audio_f32, sr)."""
        model = self._get_model(self.config.model_for(reg.mode))
        lang = self.config.language
        if reg.mode == "clone":
            ref = reg.ref_audio
            if not str(ref).startswith(("http://", "https://")):
                ref = str(reg.ref_path())
            wavs, sr = model.generate_voice_clone(
                text=sentence, language=lang, ref_audio=ref, ref_text=reg.ref_text)
        elif reg.mode == "design":
            wavs, sr = model.generate_voice_design(
                text=sentence, language=lang, instruct=reg.instruct)
        else:  # custom
            wavs, sr = model.generate_custom_voice(
                text=sentence, language=lang, speaker=reg.speaker)
        return _to_mono_f32(wavs[0]), int(sr)

    def stream(self, text: str, register: str | None = None):
        reg = self.config.register(register)
        for i, sentence in enumerate(split_sentences(text)):
            t0 = time.perf_counter()
            audio, sr = self._generate(sentence, reg)
            yield Chunk(i, sentence, audio, time.perf_counter() - t0, sr)

    def say(self, text: str, register: str | None = None):
        chunks = list(self.stream(text, register))
        if not chunks:
            return np.zeros(0, dtype=np.float32), 0
        return np.concatenate([c.audio for c in chunks]), chunks[0].sample_rate

    def to_wav(self, audio: np.ndarray, sample_rate: int, path) -> Path:
        import soundfile as sf

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(path), audio, sample_rate)
        return path
