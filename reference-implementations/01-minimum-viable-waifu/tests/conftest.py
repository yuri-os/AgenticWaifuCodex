"""Shared fixtures for the §13.3 suite.

The tests run the REAL code — SoulLoader over the real ../yuri-soul, the real
FileMemoryStore, the real routes — against fake providers, so the whole suite
is green with no API key and no model download. The fakes implement the §3.1
Protocols exactly; that seam is the point.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOUL_SRC = PROJECT_ROOT.parent / "yuri-soul"
sys.path.insert(0, str(PROJECT_ROOT))

from app.memory.store import FileMemoryStore  # noqa: E402
from scripts.seed_vault import seed  # noqa: E402

EMBED_DIM = 256


class FakeEmbedder:
    """Deterministic bag-of-words hashing (md5, so it is stable across
    processes — unlike builtin hash()): texts sharing tokens get similar
    vectors, so recall/MMR behave semantically enough to test (§3.1 Embedder)."""

    dim = EMBED_DIM

    def embed(self, texts: list[str]) -> list[list[float]]:
        out = []
        for text in texts:
            v = np.zeros(self.dim, dtype=np.float32)
            for tok in re.findall(r"[a-z0-9']+", text.lower()):
                slot = int.from_bytes(hashlib.md5(tok.encode()).digest()[:4],
                                      "big") % self.dim
                v[slot] += 1.0
            n = np.linalg.norm(v)
            out.append((v / n if n else v).tolist())
        return out


class FakeUtility:
    """Scripted UtilityModel: returns queued replies in order, then repeats
    the last one. Records every prompt it saw."""

    def __init__(self, *replies: str):
        self.replies = list(replies) or ['{"ops": []}']
        self.calls: list[list[dict]] = []

    async def complete(self, messages: list[dict], **params) -> str:
        self.calls.append(messages)
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


class FakeChat:
    """Scripted ChatModel: streams a canned reply word by word."""

    def __init__(self, reply: str = "I'm here. Tell me about your day?"):
        self.reply = reply
        self.calls: list[list[dict]] = []
        self.fail = False   # set True to simulate a mid-stream model failure

    async def stream(self, messages: list[dict], **params):
        self.calls.append(messages)
        words = self.reply.split(" ")
        for i, w in enumerate(words):
            if self.fail and i > 0:
                raise RuntimeError("model fell over mid-stream")
            yield w + (" " if i < len(words) - 1 else "")


def ops_json(*ops: dict) -> str:
    return json.dumps({"ops": list(ops)})


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    """A fresh Vault seeded from the real sibling SOUL (§5.1)."""
    v = tmp_path / "vault"
    seed(SOUL_SRC, v)
    return v


@pytest.fixture
def embedder() -> FakeEmbedder:
    return FakeEmbedder()


@pytest.fixture
def store(vault: Path, embedder: FakeEmbedder) -> FileMemoryStore:
    """A FileMemoryStore with no utility model — partner updates off, which is
    exactly what the recall/forget/persistence tests want."""
    return FileMemoryStore(vault, embedder, utility=None,
                           char_name="yuri", user_name="you",
                           embed_dim=EMBED_DIM)


def make_app(vault: Path, corpus_dir: Path, *, chat=None, utility=None):
    """The real app wired to fakes (used by the route-level tests)."""
    from app.config import Config
    from app.main import create_app

    cfg = Config(vault_dir=vault, corpus_dir=corpus_dir,
                 embed_dim=EMBED_DIM, openrouter_api_key="unused")
    return create_app(cfg,
                      chat_model=chat or FakeChat(),
                      utility_model=utility or FakeUtility(),
                      embedder=FakeEmbedder())
