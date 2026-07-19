"""Speaker-embedding similarity for the identity-fidelity axis (clone mode).

Embeds audio with Resemblyzer's VoiceEncoder and compares with cosine similarity.
Optional dependency: absent -> the identity/consistency axes skip cleanly.
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
    if not _HAVE:
        raise RuntimeError("resemblyzer not installed (pip install resemblyzer)")
    wav = preprocess_wav(audio.astype(np.float32), source_sr=sample_rate)
    return _get_encoder().embed_utterance(wav)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
    return float(np.dot(a, b) / denom)
