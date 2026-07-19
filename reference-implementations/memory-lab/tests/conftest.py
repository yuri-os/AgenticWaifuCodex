"""Test fixtures. The suite runs the real store against the offline
HashingEmbedder — no network, no model, no API key."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memory.embed import HashingEmbedder            # noqa: E402
from memory.store import FileMemoryStore, Record     # noqa: E402

EMBED_DIM = 256


@pytest.fixture
def store(tmp_path: Path) -> FileMemoryStore:
    return FileMemoryStore(tmp_path / "vault", embedder=HashingEmbedder(EMBED_DIM),
                           embed_dim=EMBED_DIM, char_name="yuri", user_name="you")


@pytest.fixture
def plant():
    """Returns a helper that writes a run of exchanges into a store. Exposed as a
    fixture (not an import) to dodge a name clash with any installed `tests`
    package on sys.path."""
    def _plant(store: FileMemoryStore, *exchanges: tuple[str, str],
               session: str = "s1") -> None:
        for i, (msg, reply) in enumerate(exchanges):
            store.remember(Record(session, i, msg, reply))
    return _plant
