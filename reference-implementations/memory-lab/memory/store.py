"""FileMemoryStore — the five-verb memory contract, file-backed.

This is a teaching extract of Build #1's `app/memory/store.py` (→ book ch. 31),
trimmed to *just the memory subsystem* so you can read the whole thing in one
sitting and run it with no web server, no LLM API, and no git.

The contract is five verbs (→ book ch. 19). Everything a companion's memory
does, and everything a later build bolts onto, goes through these:

    remember(record)     write path — journal + index + partner model
    recall(query, k)     read path — the blended-rank retrieval that feeds the prompt
    consolidate()        offline hygiene — stubbed here (it's the "DREAM" pass, ch. 18)
    forget(selector)     the covenant — supersede, never delete
    inspect(selector)    the audit surface — what she knows, and from which file

Two homes, never conflated:
    <vault>/soul/USER.md              the partner model  — small, durable, whole
    <vault>/memory/episodic/<day>.md  the journal        — append-only, recalled top-k

The markdown files are the truth; the SQLite index is a rebuildable cache of
them. Keep that hierarchy in your head and the rest falls out of it.

Simplifications vs. Build #1, called out so you know what's been left in the
book: `remember` here is synchronous (Build #1's is async because the utility
call is awaited off the hot path); there is no git commit per turn (Build #1
commits the vault every turn so `git log` is her diary); and consolidate() is a
stub in both. None of that changes the contract or the retrieval logic.
"""
from __future__ import annotations

import datetime
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

import numpy as np

from memory.index import Chunk, ChunkIndex
from memory import partner
from memory.partner import Op, Quarantine

MMR_LAMBDA = 0.5   # relevance vs. diversity trade-off in recall (0..1)


# --- contract types ----------------------------------------------------------

@dataclass
class Record:
    """One exchange, handed to remember() after the reply is complete."""
    session_id: str
    turn_index: int
    user_msg: str
    reply: str
    ts: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC))


@dataclass
class Memory:
    """One recalled or inspected memory, traceable to the file it came from."""
    text: str
    source: str          # vault-relative path (+ line span) it came from
    kind: str            # 'turn' | 'summary' | 'user_md' | 'fact'
    created_at: str = ""
    similarity: float = 0.0
    salience: float = 1.0
    score: float = 0.0   # the blended rank recall sorted on


@dataclass
class WriteResult:
    journal_path: str
    chunks_indexed: int
    facts_applied: int
    quarantined: int


class MemoryStore(Protocol):
    """The contract. A Postgres/pgvector backend is a legal drop-in behind these
    five verbs; a cloud memory service is not — it cannot answer inspect()
    ownably (→ book ch. 31)."""
    def remember(self, record: Record) -> WriteResult: ...
    def recall(self, query: str, k: int) -> list[Memory]: ...
    def consolidate(self) -> dict: ...
    def forget(self, selector: str, why: str = ...) -> int: ...
    def inspect(self, selector: str = ...) -> list[Memory]: ...


# --- helpers -----------------------------------------------------------------

def _atomic_write(path: Path, text: str) -> None:
    """Write to a temp file, fsync, then rename over the target. A crash leaves
    the *old* whole file, never a half-written one."""
    import os
    import tempfile
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _atomic_append(path: Path, text: str) -> None:
    current = path.read_text(encoding="utf-8") if Path(path).exists() else ""
    _atomic_write(path, current + text)


# --- the file backend --------------------------------------------------------

class FileMemoryStore:
    def __init__(self, vault: Path, embedder, *,
                 extractor: Callable[[str, str], list[Op]] | None = None,
                 char_name: str = "yuri", user_name: str = "you",
                 embed_dim: int = 256,
                 retrieval_min_sim: float = 0.25,
                 half_life_days: float = 30.0):
        self.vault = Path(vault)
        self.embedder = embedder
        # extractor: exchange → proposed ops. None ⇒ USER.md never grows
        # automatically (fine for the recall/forget demos, which don't need it).
        self.extractor = extractor
        self.char_name = char_name
        self.user_name = user_name
        self.retrieval_min_sim = retrieval_min_sim
        self.half_life_days = half_life_days
        self.index = ChunkIndex(self.vault / "memory" / "index" / "chunks.db",
                                dim=embed_dim)
        self.quarantine = Quarantine(self.vault / "state" / "quarantine.json")

    # -- paths --
    @property
    def user_md_path(self) -> Path:
        return self.vault / "soul" / "USER.md"

    @property
    def facts_path(self) -> Path:
        return self.vault / "memory" / "semantic" / "facts.md"

    @property
    def forgotten_path(self) -> Path:
        return self.vault / "memory" / "semantic" / "forgotten.md"

    def read_user_md(self) -> str:
        return self.user_md_path.read_text(encoding="utf-8") \
            if self.user_md_path.exists() else ""

    # -- remember: journal → index → partner model ----------------------------

    def _journal_append(self, record: Record) -> tuple[str, str]:
        """Append the exchange to today's journal as a dated prose line. Returns
        (vault-relative path, line span) so the index row can point back to it."""
        day = record.ts.strftime("%Y-%m-%d")
        rel = f"memory/episodic/{day}.md"
        path = self.vault / rel
        one = lambda s: " / ".join(s.strip().splitlines())
        entry = (f"### {record.ts.strftime('%H:%M')}  "
                 f"{self.user_name}: {one(record.user_msg)}  ⇄  "
                 f"{self.char_name}: {one(record.reply)}\n")
        before = path.read_text(encoding="utf-8").count("\n") if path.exists() else 0
        if not path.exists():
            _atomic_write(path, f"# Journal — {day}\n\n")
            before = 2
        _atomic_append(path, entry)
        return rel, f"{before + 1}-{before + 1}"

    def remember(self, record: Record) -> WriteResult:
        """Three steps, in order: (1) append to the journal, (2) embed + upsert
        one index chunk pointing back at that line, (3) run the partner-model
        update. Step 3 is tolerant: a bad extractor result is dropped, never
        fatal to the write."""
        rel, span = self._journal_append(record)

        text = f"{self.user_name}: {record.user_msg}\n{self.char_name}: {record.reply}"
        self.index.upsert(
            id=f"turn-{record.session_id}-{record.turn_index}",
            kind="turn", source_path=rel, source_span=span, text=text,
            embedding=self.embedder.embed([text])[0],
            created_at=record.ts.isoformat(), salience=1.0)

        applied = held = 0
        if self.extractor is not None:
            try:
                ops = self.extractor(self.read_user_md(), text)
                apply_now, quarantined = self.quarantine.triage(ops)
                if apply_now:
                    _atomic_write(self.user_md_path,
                                  partner.apply_ops(self.read_user_md(), apply_now))
                applied, held = len(apply_now), len(quarantined)
            except Exception:
                pass  # partner update is best-effort; the turn already happened

        return WriteResult(journal_path=rel, chunks_indexed=1,
                           facts_applied=applied, quarantined=held)

    # -- recall: the blended-rank read path -----------------------------------

    def _recency(self, created_at: str, now: datetime.datetime) -> float:
        """exp(-age_days / half_life) — a memory's pull fades with age but never
        reaches zero. Old memories can still surface; they just have to be more
        relevant to win."""
        try:
            age = (now - datetime.datetime.fromisoformat(created_at)).total_seconds() / 86400
        except ValueError:
            return 1.0
        return math.exp(-max(age, 0.0) / self.half_life_days)

    @staticmethod
    def _mmr(chunks: list[Chunk], k: int, lam: float = MMR_LAMBDA) -> list[Chunk]:
        """Maximal Marginal Relevance: greedily pick the next chunk that is
        relevant but *not* redundant with what's already chosen — so k slots hold
        k different memories, not five paraphrases of the loudest one."""
        selected: list[Chunk] = []
        pool = list(chunks)
        while pool and len(selected) < k:
            def mmr_score(c: Chunk) -> float:
                redundancy = max(
                    (float(np.dot(c.embedding, s.embedding)
                           / ((np.linalg.norm(c.embedding) or 1)
                              * (np.linalg.norm(s.embedding) or 1)))
                     for s in selected), default=0.0)
                return lam * c.similarity - (1 - lam) * redundancy
            best = max(pool, key=mmr_score)
            pool.remove(best)
            selected.append(best)
        return selected

    def recall(self, query: str, k: int = 6) -> list[Memory]:
        """Similarity is not enough. Over-fetch, drop everything below a
        similarity floor, drop anything the user asked to forget, re-rank on
        similarity × salience × recency, then diversify with MMR. An empty index
        returns [] — recall admits when it has nothing, rather than reaching."""
        if self.index.count() == 0:
            return []
        now = datetime.datetime.now(datetime.UTC)
        q = self.embedder.embed([query])[0]
        rows = self.index.search(q, limit=k * 4)                       # over-fetch
        rows = [r for r in rows if r.similarity >= self.retrieval_min_sim]  # floor
        stones = [t.lower() for t in self.tombstones()]                # forget covenant
        rows = [r for r in rows if not any(t in r.text.lower() for t in stones)]
        rows.sort(key=lambda r: r.similarity * r.salience              # blended rank
                  * self._recency(r.created_at, now), reverse=True)
        rows = self._mmr(rows, k)                                      # diversify
        return [Memory(text=r.text, source=f"{r.source_path}:{r.source_span}",
                       kind=r.kind, created_at=r.created_at,
                       similarity=r.similarity, salience=r.salience,
                       score=r.similarity * r.salience
                       * self._recency(r.created_at, now))
                for r in rows]

    # -- consolidate: stubbed (the DREAM pass, ch. 18) ------------------------

    def consolidate(self) -> dict:
        """Offline hygiene — dedupe, merge, decay, promote episodic→semantic.
        Not on the hot path; arrives with the tick loop in Build #5 (→ ch. 18).
        The contract slot exists so nothing above it is rebuilt when it lands."""
        return {"note": "DREAM consolidation arrives in Build #5 (ch. 18)"}

    # -- forget: the covenant (supersede, never delete) -----------------------

    def tombstones(self) -> list[str]:
        """The texts in the forget-ledger. Never read into the prompt; used only
        to suppress recall."""
        if not self.forgotten_path.exists():
            return []
        out = []
        for line in self.forgotten_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"###\s+\d{4}-\d{2}-\d{2}\s+forgot:\s*(.+)", line)
            if m:
                out.append(m.group(1).rsplit("  —", 1)[0].strip())
        return out

    def forget(self, selector: str, why: str = "asked to forget") -> int:
        """Remove matching lines from the working USER.md / facts.md and write a
        tombstone to forgotten.md. The value is gone from every future prompt and
        every future recall — but it survives in git history (if the vault is a
        repo) for auditability. Supersede, not erase. Returns how many memories
        were superseded."""
        sel = selector.lower().strip()
        removed = 0
        for path in (self.user_md_path, self.facts_path):
            if not path.exists():
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            kept = [ln for ln in lines
                    if not (ln.lstrip().startswith("- ") and sel in ln.lower())]
            if len(kept) != len(lines):
                removed += len(lines) - len(kept)
                _atomic_write(path, "\n".join(kept).rstrip() + "\n")
        suppressed = sum(1 for c in self.index.all() if sel in c.text.lower())
        today = datetime.date.today().isoformat()
        _atomic_append(self.forgotten_path,
                       f"### {today}  forgot: {selector}  — {why}\n")
        return removed + suppressed

    # -- inspect: what she knows, and from which file -------------------------

    def inspect(self, selector: str = "") -> list[Memory]:
        """The audit surface. Every memory matching `selector`, each tagged with
        the file it lives in. A dashboard or debug view reads through this — never
        around it — which is exactly why a store you can't inspect ownably fails
        the contract."""
        sel = selector.lower()
        out: list[Memory] = []
        if self.user_md_path.exists():
            for ln in self.user_md_path.read_text(encoding="utf-8").splitlines():
                if ln.lstrip().startswith("- ") and sel in ln.lower():
                    out.append(Memory(text=ln.lstrip("- ").strip(),
                                      source="soul/USER.md", kind="user_md"))
        if self.facts_path.exists():
            for ln in self.facts_path.read_text(encoding="utf-8").splitlines():
                if ln.lstrip().startswith("- ") and sel in ln.lower():
                    out.append(Memory(text=ln.lstrip("- ").strip(),
                                      source="memory/semantic/facts.md", kind="fact"))
        for c in self.index.all():
            if sel in c.text.lower():
                out.append(Memory(text=c.text,
                                  source=f"{c.source_path}:{c.source_span}",
                                  kind=c.kind, created_at=c.created_at,
                                  salience=c.salience))
        return out
