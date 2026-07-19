"""Speaker-embedding similarity for the identity-fidelity axis.

Cloning's whole point is that the output sounds like the *target* speaker, so the
eval needs a number for "is this still her?". We embed audio with Resemblyzer's
VoiceEncoder (small, CPU-fine) and compare with cosine similarity. Resemblyzer is
an OPTIONAL dependency: if it's absent the identity axis degrades gracefully.
"""

from __future__ import annotations

import numpy as np

try:
    from resemblyzer import VoiceEncoder, preprocess_wav

    _HAVE = True
except Exception:  # pragma: no cover - optional dep
    _HAVE = False


def available() -> bool:
    return _HAVE


_encoder = None


def _get_encoder():
    global _encoder
    if _encoder is None:
        _encoder = VoiceEncoder(verbose=False)
    return _encoder


def embed(audio: np.ndarray, sample_rate: int) -> np.ndarray:
    """L2-normalized speaker embedding for a float32 mono clip."""
    if not _HAVE:
        raise RuntimeError("resemblyzer not installed (pip install resemblyzer)")
    wav = preprocess_wav(audio.astype(np.float32), source_sr=sample_rate)
    return _get_encoder().embed_utterance(wav)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
    return float(np.dot(a, b) / denom)
