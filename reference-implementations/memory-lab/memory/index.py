"""The retrieval index — a derived, rebuildable cache (→ book ch. 15, ch. 19).

One SQLite table at `<vault>/memory/index/chunks.db`, one row per embedded
chunk. Search is a flat numpy cosine scan over every stored vector: at one
user, human conversation cadence, a few thousand rows scan in milliseconds, so
there is no ANN library and no service to run. `sqlite-vec` / FAISS is a
drop-in *inside this one class* if a vault ever outgrows a flat scan — nothing
above the index changes.

The rule that makes this safe: **the markdown files are the source of truth;
this index is only a cache of them.** If the two ever disagree, you throw the
index away and rebuild it from the files. That is why memories carry
`source_path` / `source_span` — every row is traceable back to the line of the
journal it came from.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunk(
  id          TEXT PRIMARY KEY,
  kind        TEXT,             -- 'turn' | 'summary'
  source_path TEXT,             -- which .md file this came from (traceability)
  source_span TEXT,             -- line range within that file
  text        TEXT,
  embedding   BLOB,             -- float32 vector, `dim` wide
  created_at  TEXT,             -- ISO-8601 UTC
  salience    REAL              -- importance weight, set at write time
);
"""


@dataclass
class Chunk:
    id: str
    kind: str
    source_path: str
    source_span: str
    text: str
    embedding: np.ndarray
    created_at: str
    salience: float
    similarity: float = 0.0  # filled in by search()


class ChunkIndex:
    def __init__(self, db_path: Path, dim: int):
        self.db_path = Path(db_path)
        self.dim = dim
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.db_path)
        self._db.execute(SCHEMA)
        self._db.commit()

    def upsert(self, *, id: str, kind: str, source_path: str, source_span: str,
               text: str, embedding: list[float], created_at: str,
               salience: float = 1.0) -> None:
        vec = np.asarray(embedding, dtype=np.float32)
        assert vec.shape == (self.dim,), \
            f"embedding is {vec.shape[0]}-d, index is {self.dim}-d — width is config"
        self._db.execute(
            "INSERT OR REPLACE INTO chunk VALUES (?,?,?,?,?,?,?,?)",
            (id, kind, source_path, source_span, text, vec.tobytes(),
             created_at, salience))
        self._db.commit()

    def search(self, query_vec: list[float], limit: int) -> list[Chunk]:
        """Cosine similarity against every row (flat scan), return the top `limit`."""
        rows = self._db.execute("SELECT * FROM chunk").fetchall()
        if not rows:
            return []
        q = np.asarray(query_vec, dtype=np.float32)
        q = q / (np.linalg.norm(q) or 1.0)
        chunks: list[Chunk] = []
        for (cid, kind, spath, span, text, blob, created, salience) in rows:
            v = np.frombuffer(blob, dtype=np.float32)
            v = v / (np.linalg.norm(v) or 1.0)
            chunks.append(Chunk(cid, kind, spath, span, text, v, created,
                                salience, similarity=float(np.dot(q, v))))
        chunks.sort(key=lambda c: c.similarity, reverse=True)
        return chunks[:limit]

    def all(self) -> list[Chunk]:
        rows = self._db.execute("SELECT * FROM chunk").fetchall()
        return [Chunk(cid, kind, spath, span, text,
                      np.frombuffer(blob, dtype=np.float32), created, salience)
                for (cid, kind, spath, span, text, blob, created, salience) in rows]

    def count(self) -> int:
        return self._db.execute("SELECT COUNT(*) FROM chunk").fetchone()[0]

    def wipe(self) -> None:
        """Drop every row. The files survive; a reindex rebuilds from them."""
        self._db.execute("DELETE FROM chunk")
        self._db.commit()

    def close(self) -> None:
        self._db.close()
