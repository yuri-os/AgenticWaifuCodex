"""Embedders — turn text into a vector so similar text lands near in space.

The lab ships two, behind the one method `recall` needs (`embed`):

  * HashingEmbedder      — the default. Pure-numpy, deterministic, offline, zero
                           model download. Bag-of-words hashing: texts that share
                           words get similar vectors. It is *not* semantic (it has
                           no idea "sofa" ≈ "couch"), but it is enough to watch the
                           retrieval machinery work, and it makes every example in
                           this repo reproducible on any machine with no API key.
  * SentenceTFEmbedder   — the real thing (BAAI/bge-small-en-v1.5, 384-d), used by
                           Build #1. Optional import: only constructed if you ask
                           for it, so `pip install sentence-transformers` stays
                           optional for the tutorial.

Swapping one for the other changes nothing above `embed()` — that is the whole
point of putting the model behind a seam (→ book ch. 13, ch. 19).
"""
from __future__ import annotations

import hashlib
import re

import numpy as np

_TOKEN = re.compile(r"[a-z0-9']+")


class HashingEmbedder:
    """Deterministic bag-of-words hashing. `dim` slots; each token bumps the
    slot `md5(token) % dim`. md5 (not builtin hash()) so vectors are stable
    across processes and runs — the tutorial's numbers are the same every time."""

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            v = np.zeros(self.dim, dtype=np.float32)
            for tok in _TOKEN.findall(text.lower()):
                slot = int.from_bytes(hashlib.md5(tok.encode()).digest()[:4],
                                      "big") % self.dim
                v[slot] += 1.0
            n = np.linalg.norm(v)
            out.append((v / n if n else v).tolist())   # unit-normalise → cosine
        return out


class SentenceTFEmbedder:
    """Real sentence embeddings. Heavy (torch); imported lazily so the default
    tutorial never pays for it. This is the embedder Build #1 ships."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", dim: int = 384):
        from sentence_transformers import SentenceTransformer  # lazy, optional dep

        self._model = SentenceTransformer(model_name)
        self.dim = dim
        actual = self._model.get_sentence_embedding_dimension()
        if actual != dim:
            raise ValueError(
                f"dim={dim} but {model_name} produces {actual}-d vectors — "
                "the index width is config, not a constant; fix it to match")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()
