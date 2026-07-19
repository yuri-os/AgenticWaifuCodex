# memory-lab — how companion memory actually works

A small, runnable teaching extract of the memory subsystem from Build #1
(→ book ch. 31), pulled out so you can study **just the memory** without a web
server, an LLM API key, or a model download. It is the hands-on companion to
**book chapter 15, "Memory Architectures."**

> *"She doesn't remember"* is the universal complaint about companion products.
> Memory is the cheapest durable moat a small builder has — and the one property
> with a hard honesty constraint: a memory you can't tell from a guess is worth
> less than no memory at all. This lab is the ~600 lines that make "she remembers
> you, and admits what she doesn't" real.

Runs on **numpy alone**. The default embedder is a pure-Python hashing stand-in
and the "utility model" that extracts facts is a rule-based stand-in, so every
number in the demos is reproducible on any machine, offline.

## Run it

Needs **Python 3.11+** (it uses `datetime.UTC`). `numpy` is the only hard
dependency. The surest way to run it — on any machine, without disturbing
whatever else you have installed — is a throwaway virtual environment:

```bash
cd reference-implementations/memory-lab
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"          # numpy + pytest, into this env only

python tutorial.py               # a narrated walk through all five verbs
python scenarios.py              # three "why memory matters" before/afters
pytest -q                        # the behaviour, pinned (16 tests, offline)
```

The `python3 -m venv` line is what saves you the most common snag: running the
lab under some *other* interpreter that happens to be active — an old system
Python, or a conda env on 3.10 — and hitting `module 'datetime' has no
attribute 'UTC'`. The venv pins you to a clean, correctly-versioned Python for
the length of this session; `deactivate` when you're done.

> **In VS Code / Cursor:** the Run/Debug button uses whichever interpreter is
> selected in the status bar, *not* your activated shell. After creating the
> venv, run **“Python: Select Interpreter”** (⇧⌘P / Ctrl+Shift+P) and pick the
> one under `.venv/` — otherwise F5 launches the lab under your last-used conda
> env and you'll see the `datetime.UTC` error above.

No venv? `pip install numpy` and `python tutorial.py` still works — as long as
your `python` is 3.11 or newer (`python --version` to check).

Read `tutorial.py` top-to-bottom next to `memory/store.py` — it is the store's
docstrings turned into something you can watch execute.

## The one idea: memory is five verbs, behind a seam

Everything a companion's memory does goes through one contract (→ book ch. 19):

```python
class MemoryStore(Protocol):
    def remember(self, record): ...          # write: journal + index + partner model
    def recall(self, query, k): ...          # read: the ranked retrieval that feeds the prompt
    def consolidate(self): ...               # offline hygiene (the "DREAM" pass — stubbed here)
    def forget(self, selector): ...          # the covenant: supersede, never delete
    def inspect(self, selector): ...         # the audit surface: what she knows, and from where
```

Why a *contract* and not just a class: the backend behind these five methods is
swappable. A Postgres/`pgvector` store is a legal drop-in; a cloud memory service
is **not** — not for a technical reason, but because it can't answer `inspect()`
*ownably* (you can't see everything it holds on you, on hardware you control).
The seam admits any backend you own and rejects any you merely rent.

`FileMemoryStore` (in `memory/store.py`) is one implementation: plain Markdown
files, with a SQLite + numpy index as a rebuildable cache over them.

## Two homes, never conflated

```
vault/
  soul/USER.md                    the PARTNER MODEL — small, durable, injected WHOLE every turn
  memory/
    episodic/<date>.md            the JOURNAL — append-only prose, recalled a few lines at a time
    semantic/facts.md             consolidated general facts (grows in the DREAM pass)
    semantic/forgotten.md         the forget-ledger (tombstones)
    index/chunks.db               the embedding index — DERIVED CACHE, gitignored, rebuildable
  state/quarantine.json           claims awaiting a second mention
```

The distinction is the whole game: **`USER.md` she always knows** (your name, that
you live by the river); **the journal she only sometimes remembers** (what you said
last Tuesday, surfaced by similarity when it's relevant). Different jobs, different
storage. The Markdown is the source of truth; if the index ever disagrees, you
throw the index away and rebuild it from the files.

## Adding a memory, and fetching one

```python
from memory.store import FileMemoryStore, Record
from memory.embed import HashingEmbedder

store = FileMemoryStore("vault", embedder=HashingEmbedder(dim=256))

# WRITE — one exchange in. Three things happen: a journal line, one embedded
# index row pointing back at that line, and (if an extractor is wired) a
# partner-model update.
store.remember(Record(session_id="s1", turn_index=0,
                      user_msg="my sister Mira visits next Friday",
                      reply="Mira, Friday — I'll hold onto that"))

# READ — the ranked recall that gets pasted into the prompt.
for m in store.recall("when does my sister arrive?", k=3):
    print(f"{m.score:.2f}  {m.text}  ({m.source})")
```

`recall()` is deliberately **not** raw cosine similarity — that's the single most
common thing memory demos get wrong. It:

1. **over-fetches** `k*4` candidates,
2. drops everything below a **similarity floor** (so a query with no real match
   returns *nothing*, rather than reaching — this is the honesty constraint),
3. drops anything the user asked to **forget**,
4. re-ranks on **similarity × salience × recency** (`exp(-age/half_life)` — old
   memories fade, never vanish), and
5. **diversifies with MMR** so `k` slots hold `k` *different* memories, not five
   paraphrases of the loudest one.

## Promotion, not capture: the quarantine

The most opinionated part of the lab. When a fact gets *extracted* from an
exchange, it is **not** written straight into `USER.md`. A low-confidence claim is
**quarantined** — held aside until a *second* turn corroborates it, and only then
promoted. This is the one mechanism that stops a companion from confidently
"remembering" something you said once, sarcastically, three weeks ago.

One sharp default worth internalising: a claim the extractor returns *without* a
confidence is treated as **unsure** (→ quarantine), never as certain. "It didn't
say how sure it is" must mean *be cautious*, not *be sure*. `tutorial.py` step 4
shows a claim wait in quarantine and then get promoted on its second mention.

The lab ships two extractors (`memory/partner.py`): `KeywordExtractor` (offline,
rule-based, deterministic — used by the demos) and `LLMExtractor` (the real path:
one cheap utility-model call per exchange, same Op schema as JSON). Swapping one
for the other changes nothing else.

## The forget covenant

`forget()` does **not** delete. It removes the line from the working files,
suppresses it from every future recall, and writes a tombstone. In the real
build the old value also survives in `git log` for auditability. **Supersede, not
erase.** "Forget that" the user can actually rely on is part of what makes the
remembering safe to trust (`scenarios.py`, Scenario 3).

## Files

| File | What it is |
|---|---|
| `memory/store.py` | `FileMemoryStore` — the five verbs, file-backed. Read this first. |
| `memory/index.py` | The SQLite + numpy cosine index. A cache, never the truth. |
| `memory/partner.py` | `USER.md` growth: extractors, `apply_ops` merge, the quarantine. |
| `memory/embed.py` | `HashingEmbedder` (offline default) + `SentenceTFEmbedder` (real). |
| `tutorial.py` | Narrated end-to-end run of every verb. |
| `scenarios.py` | Three before/after demos of *why* memory is the differentiator. |
| `tests/` | The behaviour pinned: recall ranking, quarantine, forget, persistence. |

## What it deliberately leaves out (see Build #1 for these)

- **The web loop, prompt assembly, streaming, the persona/SOUL** — this lab is
  the memory box, not the companion. Build #1 (`../01-minimum-viable-waifu`) wires
  it into a running chat.
- **`consolidate()` / the DREAM pass** — the hygiene job (dedupe, merge, decay,
  promote episodic→semantic) is stubbed here and in Build #1; it arrives with the
  tick loop in Build #5 (→ book ch. 18). The contract slot exists so nothing above
  it is rebuilt when it lands.
- **A git-per-turn vault** — Build #1 commits the vault every turn so `git log`
  reads as her diary. Here writes are atomic but not committed, to keep the lab
  to one dependency.
- **Async** — `remember` is synchronous here; Build #1's is async because the
  utility call is awaited off the hot path.

None of those change the contract or the retrieval logic — which is exactly the
point of putting them behind a seam.

## Swapping in real semantic embeddings

The default `HashingEmbedder` is *lexical* — it only sees shared words, so it's
perfect for watching the machinery deterministically but has no idea "sofa" ≈
"couch." For real semantics:

```bash
pip install sentence-transformers
```

```python
from memory.embed import SentenceTFEmbedder
store = FileMemoryStore("vault", embedder=SentenceTFEmbedder())  # BAAI/bge-small-en-v1.5, 384-d
```

Nothing above `embed()` changes. With real embeddings you'd raise
`retrieval_min_sim` back toward `0.25` (the lab lowers it for the lexical
default). That one-line swap is the seam doing its job.

License: MIT.
