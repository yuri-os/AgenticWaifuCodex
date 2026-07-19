# Build #1 — The Minimum Viable Waifu · Implementation Spec

> **Status:** planned · **Book chapter:** [ch. 31](../../chapters/31-build-1-minimum-viable-waifu.md) · **Ladder:** rung 1 (→ [ch. 30](../../chapters/30-reference-implementations.md))
>
> This document is **self-contained and normative**. A coding harness that sees only this file
> should be able to implement the whole build. Where it depends on sibling artifacts
> (`yuri-soul/`, the ch. 19 store contracts, the Appendix D corpus schema, brand tokens) it
> inlines the parts it needs, so no other file is *required* — the links are provenance.
>
> Requirement language: **MUST / SHOULD / MAY** in the RFC-2119 sense.
>
> **Architectural spine (read this first).** This build is the smallest honest slice of the
> YuriOS runtime (→ ch. 19), not a generic chat app. Two decisions are load-bearing and
> non-negotiable, because everything above rung 1 keeps them:
> 1. **Python.** The backend is Python, like every other reference impl and the runtime itself
>    (→ `runtime/05-reference-implementation-architectures.md`). No Node/TypeScript backend.
> 2. **The brain is a folder** (→ ch. 19, "The brain is a folder"). The mind is a **git-backed
>    Vault of human-readable files** — the files *are* the database. A derived, rebuildable
>    local index does retrieval; it is a cache, never the source of truth. This is where
>    ownership, inspectability (`cat`/`git log`), and "no rug-pull" come from.
>
> Build #1 is Option A ("the Paper Brain") from the runtime decision record, given a thin
> reactive web surface. Wrap a tick loop (→ ch. 18) around *this exact Vault* and it becomes
> Build #5 (→ ch. 35). Nothing here is thrown away.

---

## 1. Purpose & scope

Ship, in a weekend, a **persona-driven web chat that remembers the user across sessions** —
the smallest artifact that is honestly an *agentic-waifu-shaped object* and not a toy. One
companion, one user, in a browser. It is deliberately **reactive** (speaks only when spoken to)
and **disembodied beyond text** (no voice, no avatar). Those arrive in later builds.

### 1.1 Properties this build clears (→ ch. 03)

| # | Property | How this build satisfies it |
|---|----------|------------------------------|
| 1 | **Identity** | The SOUL (`CONSTITUTION.md` + `PERSONA.md` + …) is the immovable backbone of every prompt, read on every turn. |
| 2 | **Honest memory** | Durable facts + episodic recall persist as **files in a git-backed Vault the user owns**; the persona **admits the edges of memory** instead of confabulating. |
| 5 | **One-on-one** | Single user, no audience, no engagement mechanics, no upsell in the loop. |

Properties **3 (owned agency / autonomy)** and **4 (embodiment)** are explicitly out of scope
(§12). There is **no tick loop** in Build #1 — it is purely request/response.

### 1.2 The one-sentence architecture

> A **static SOUL** (files), a **growing Vault** (files), and a **prompt assembled from both on
> every turn** — plus an **append-only corpus log** written on every reply. No agent framework,
> no ORM, no autonomy loop.

If the implementation reaches for a framework's "memory" abstraction (LangChain memory, etc.),
it has taken on a dependency this project deliberately rejects (→ ch. 02 §1, ch. 12). Memory
here is **markdown files, a small local index, and a few functions** behind the ch. 19
`MemoryStore` contract — nothing more.

---

## 2. System architecture

### 2.1 Component diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                 BROWSER                                      │
│   Sanctuary page (one static page): message list · composer · continuity     │
│   greeting.   Served as static files by the Python app. No Node build step.  │
└───────────────┬──────────────────────────────────────────────▲───────────────┘
                │  POST /api/chat  (SSE stream)                │ tokens
                ▼                                              │
┌──────────────────────────────────────────────────────────────┴──────────────────┐
│                        PYTHON APP  (FastAPI + uvicorn)                          │
│                                                                                 │
│   ┌────────────┐   ┌──────────────────┐   ┌────────────┐  ┌────────────────┐    │
│   │ SoulLoader │   │  PromptAssembler │──▶│ ModelRouter│─▶│  SSE streamer  │    │
│   │ reads SOUL │──▶│ system+window+usr│   │ (LiteLLM)  │  │  → browser     │    │
│   │ every turn │   └───────▲──────────┘   └─────┬──────┘  └────────────────┘    │
│   └────────────┘           │ memory block       │ reply                         │
│                    ┌───────┴──────────┐         ▼                               │
│                    │  MemoryStore     │   ┌───────────────────────────────────┐ │
│                    │  (ch.19 contract)│◀──│ Post-turn pipeline (background)   │ │
│                    │  recall/remember │   │  1. append episodic journal .md   │ │
│                    │  file-backed     │   │  2. embed + upsert local index    │ │
│                    └───────┬──────────┘   │  3. update USER.md (partner model)│ │
│                            │ Embedder     │  4. every N turns: summary.md     │ │
│                            ▼              │  5. git commit the Vault          │ │
│                    ┌────────────────┐     │  6. append corpus/turns.jsonl     │ │
│                    │ local embed    │     └──────────────┬────────────────────┘ │
│                    │ (sentence-tf / │                    │                      │
│                    │  ollama)       │                    │                      │
└────────────────────┴───────┬────────┴────────────────────┼──────────────────────┘
                 git-backed Vault (files = the mind)       │  corpus (personal data)
                             ▼                             ▼
┌─────────────────────────────────────────────┐  ┌───────────────────────────────┐
│ vault/  (one git repo — §4.1)               │  │ corpus/turns.jsonl            │
│  soul/{CONSTITUTION,PERSONA,…}.md USER.md   │  │ corpus/ratings.jsonl          │
│  memory/episodic/*.md  semantic/facts.md    │  │ (append-only · .gitignored ·  │
│  memory/index/  (derived, gitignored)       │  │  never committed)             │
│  state/sessions.json                        │  └───────────────────────────────┘
└─────────────────────────────────────────────┘
```

### 2.2 Turn sequence (the hot path)

```
User        Browser       FastAPI        MemoryStore     Model         Vault/Corpus
 │ type msg   │             │               │             │               │
 │───────────▶│ POST /chat  │               │             │               │
 │            │────────────▶│ recall(msg,k) │             │               │
 │            │             │──────────────▶│ embed+search│               │
 │            │             │◀──────────────│ facts+recall│               │
 │            │             │ assemble system (SOUL + USER.md + summary + │
 │            │             │ recalled memories) + raw window + user msg  │
 │            │             │───────────────────────────▶ │  stream       │
 │            │◀── SSE tokens ─────────────────────────── │  reply        │
 │◀─ render ──│             │  (reply complete)           │               │
 │            │             │───── post-turn pipeline (background task) ─▶│
 │            │             │  journal .md · embed+index · update USER.md │
 │            │             │  · maybe summary · git commit · corpus log  │
```

**Latency rule.** `recall` + assembly + model stream are the *only* work on the request's
critical path. Journaling, embedding-the-turn, `USER.md` update, summarisation, the **git
commit**, and corpus logging happen **after** the reply streams (a FastAPI `BackgroundTask` or
an `asyncio` task), so they never delay the first token. Target ~600 ms to first token
(→ ch. 12, "latency is part of the persona").

---

## 3. Technology stack (normative)

Runnable by one person on a laptop. These are the reference choices; §3.1 lists the swap seams.

| Layer | Default choice | Notes |
|-------|----------------|-------|
| Language | **Python ≥ 3.11** | matches every sibling impl + the runtime |
| Web framework | **FastAPI** + **uvicorn** | route handlers + SSE; serves the static page too |
| Frontend | **one static HTML page + vanilla JS/TS** | **no Node build step**; served by FastAPI's `StaticFiles` |
| The mind | **git-backed file Vault** (§4) | files are the source of truth (→ ch. 19) |
| Retrieval index | **`sqlite-vec`** (SQLite + vector ext) *or* a FAISS/numpy flat index | **derived + rebuildable + gitignored** — a cache over the `.md` files |
| Chat model | **`deepseek/deepseek-v4-flash`** via OpenRouter | the reply voice (→ ch. 13, ch. 31 "one frontier LLM via API"); any OpenRouter id is a config change |
| Utility model | **`deepseek/deepseek-v4-flash`** (or a local model) | cheap calls: fact update + summarisation |
| Model access | **LiteLLM** as the router seam | one interface over OpenRouter (hosted), a local **Ollama**, or a local **LM Studio** server — the model-id prefix picks the route (§3.2) |
| Embeddings | **local** — `sentence-transformers` (`BAAI/bge-small-en-v1.5`, 384-d), Ollama `nomic-embed-text`, *or* an **LM Studio** embedding model | local-first (→ ch. 19); the index dimension is config, never hard-coded; a swap is self-healing (§4.3) |
| Persona source | the **`../yuri-soul` SOUL** (`.md` + `soul.yaml`) | read directly, as the runtime does (§5) |
| Git | invoked via `subprocess` or `dulwich` | every durable Vault change is a commit (§6.5) |
| Styling | plain CSS with **YuriOS Lab tokens** (§9.2) | dark sanctuary, JetBrains Mono |

> **Why local embeddings, remote chat.** Build #1 accepts a hosted *chat* model (ch. 31), but
> the *mind* — including the embeddings that index it — stays local and ownable (→ ch. 19). The
> embedder is behind a seam (§3.1) so a fully-local Build #2 is a config change, and the chat
> model routes through LiteLLM so swapping to a local model later touches one file.
>
> **On pgvector.** Ch. 31 names local `pgvector` as a *sanctioned swap-in behind the same
> `MemoryStore` contract — a backend, not the spine*; this build agrees. It ships the **file
> backend first** so the Vault is inspectable-by-`cat` and grows straight into Build #5; a
> local-pgvector backend MAY be added later behind the same contract (§6.6) without touching the loop.

### 3.1 Provider seams (interfaces that MUST exist)

```python
# providers/base.py — the only vendor-facing surfaces; nothing else imports an SDK directly.
from typing import AsyncIterator, Protocol

class ChatModel(Protocol):
    async def stream(self, messages: list[dict], **params) -> AsyncIterator[str]: ...
    # streams assistant tokens; the caller accumulates the full text

class UtilityModel(Protocol):
    async def complete(self, messages: list[dict], **params) -> str: ...
    # non-streaming; used for fact-update + summarisation; SHOULD support JSON output

class Embedder(Protocol):
    dim: int                                   # MUST equal the index's vector width
    def embed(self, texts: list[str]) -> list[list[float]]: ...   # batch
```

`providers/` holds one file per backend (`openrouter.py`, `ollama.py`, `sentence_tf.py`,
`lmstudio.py`). Everything else depends only on these three Protocols.

### 3.2 Provider routing & the reasoning switch (→ ch. 13)

**Routing.** The chat/utility model id's **prefix** picks the provider through LiteLLM; the
`Embedder` is chosen by `EMBED_BACKEND`. All three routes are local-or-hosted with no code change:

| Prefix / backend | Route | Auth / endpoint |
|---|---|---|
| `openrouter/<id>` (or a bare `<id>`) | hosted OpenRouter | `OPENROUTER_API_KEY` |
| `ollama/<model>` | local Ollama | — |
| `lm_studio/<model>` | local LM Studio (OpenAI-compatible) | `LMSTUDIO_BASE_URL` (default `http://localhost:1234/v1`) |

`lmstudio.py::LMStudioEmbedder` reuses that same LM Studio server for `EMBED_BACKEND=lm_studio`,
so **one local process can back both the mind and its memory** — no Ollama required.

**The reasoning switch.** A local model MAY be a *reasoning* model (it runs a `<think>` pass
before its answer; e.g. the reference `lm_studio/google/gemma-4-12b-qat`). Two knobs control it,
one per model role — `CHAT_THINKING` (the reply voice) and `UTILITY_THINKING` (fact-extraction /
summarisation) — both ON by default and **never hardcoded**:

- **Thinking ON** needs token headroom so the `<think>` pass *and* the answer both fit
  (`MAX_REPLY_TOKENS` for the reply, `UTILITY_MAX_TOKENS` for the utility call); too small a
  budget spends it all mid-thought and returns an **empty** string.
- **Thinking OFF** disables the pass for speed. The switch that works across OpenAI-compatible
  servers is `reasoning_effort:"none"`, but it **MUST** ride in the raw request body
  (`extra_body`) — passed as a top-level LiteLLM arg it is rewritten and the server never sees
  it. A qwen `/no_think` system-token is appended as a fallback for models that ignore
  `reasoning_effort` (e.g. Ollama qwen3). Both are inert on a non-reasoning model.

Build #1 keeps chat thinking **ON** (reply quality over latency); the real-time Build #2 turns
the *reply* off while leaving the utility model thinking (it runs off the hot path).

---

## 4. The Vault — the mind as files

The memory is not a schema; it is a **directory of files under git** (→ ch. 19). The files are
the source of truth. A derived index makes them searchable. This is the on-thesis substrate and
the exact subset of the ch. 19 Vault that Build #5 grows the rest of the mind onto.

### 4.1 Vault layout (canonical)

```
vault/                            # ONE git repo — the mind. Backed up by copying the folder.
├── soul/                         # the persona — SEEDED from ../yuri-soul, read every turn
│   ├── CONSTITUTION.md           #   immutable — identity, voice law, hard limits
│   ├── PERSONA.md                #   appearance, manner, inner life, personality line
│   ├── SCENARIO.md               #   the place + the RETURN greetings (she's met you before)
│   ├── EXAMPLES.md               #   demonstrated voice (<START> blocks)
│   ├── WORLD.md                  #   lorebook (keyword-triggered, sparse)
│   ├── NOTES.md                  #   creator notes
│   ├── BOOTSTRAP.md              #   consumed-once first-ever opener (§5.4); retired after
│   ├── USER.md                   #   RUNTIME — the partner model: durable facts + beliefs about you
│   └── soul.yaml                 #   manifest: which sources feed which prompt section
├── memory/
│   ├── episodic/                 #   YYYY-MM-DD.md — append-only journal of exchanges (§6.2)
│   ├── semantic/
│   │   ├── facts.md              #   consolidated general facts — SEEDED from MEMORY.md#What I know that matters; grows in DREAM later
│   │   └── forgotten.md          #   the forget-ledger — SEEDED from MEMORY.md#Things {{user}} asked me to forget; supersede-not-delete tombstones (§6.1, §6.7)
│   ├── summary.md                #   the rolling "what we've talked about" (§7.3)
│   └── index/                    #   DERIVED: embeddings index (sqlite-vec) — GITIGNORED, rebuildable
├── state/
│   └── sessions.json            #   session + turn bookkeeping (ids, counts, last_active)
└── .gitignore                    #   memory/index/  (derived, never committed)
```

`USER.md` and everything under `memory/` (except the gitignored `index/`) are **committed** —
the mind's growth is a git history you can `git log` and `git revert`. `soul/` is seeded once
from `../yuri-soul` and then lives in the Vault (Build #1 does not edit `CONSTITUTION.md`).

`yuri-soul` ships **two** `runtime_only` files (per `soul.yaml`), and they seed different homes,
not `soul/`: `USER.md` → the partner model at `vault/soul/USER.md`; `MEMORY.md` → the **memory
tier**, its `## What I know that matters` seeding `memory/semantic/facts.md` and its `## Things
{{user}} asked me to forget` seeding `memory/semantic/forgotten.md` (the forget-ledger, §6.7).
`MEMORY.md` is runtime memory, not persona prose, so it never lands under `soul/` — the seed
routes it to where the mind lives (§5.1).

### 4.2 Why this shape (the four properties, → ch. 19)

- **Inspectability is free.** "What does she know about me? What changed?" → `cat vault/soul/USER.md`, `git -C vault log`, `git -C vault diff`. The dashboard/debug view is a renderer over the files, not a second source of truth.
- **Ownership is literal.** The mind is files on the user's disk. No server-side "real" copy. Move her = move the folder.
- **Auditability + reversibility come from git.** Every durable change is a commit: diffable, revertible. This is what makes a memory that *grows* shippable rather than opaque.
- **No rug-pull.** A self that is open files on your machine cannot be silently nerfed or A/B-tested against you (→ ch. 02 §1, the Replika lesson; ch. 11).

The cost — files are not a high-throughput transactional store — is fine here: Build #1 is
request-driven at human cadence, and the `MemoryStore` *contract* (§6) survives a later swap to
a database backend even though the file *layout* would not (→ ch. 12).

### 4.3 The derived index (`memory/index/`)

A rebuildable cache, **gitignored**. Reference implementation: a `sqlite-vec` database with one
row per embedded chunk:

```
chunk(id TEXT PK, kind TEXT,            -- 'turn' | 'summary'
      source_path TEXT, source_span TEXT,-- which .md file + line range it came from
      text TEXT, embedding BLOB,         -- vector(EMBED_DIM)
      created_at TEXT, salience REAL)
```

`source_path`/`source_span` make retrieval traceable back to the markdown, and let
`scripts/reindex.py` rebuild the whole index from the `.md` files after any edit or on a fresh
clone. The markdown is authoritative; if the index and the files disagree, **rebuild the index**.

**Embedder provenance & auto-reindex.** The index also records *which embedder built its vectors*
— a `backend:model:dim` fingerprint in a small `meta` table. A same-dimension embedder swap
(e.g. Ollama `nomic`→ LM Studio `nomic`, both 768-d) does **not** trip the dimension check but
would silently poison recall: stored vectors and new query vectors would live in different
spaces. So at boot the runtime compares the stored fingerprint to the configured embedder and, on
a mismatch over a non-empty index, **auto-rebuilds from the `.md` files** (logging `re-indexing
memory: embedding model changed (X → Y)`) rather than trusting stale vectors; a fresh/empty index
is simply stamped. The rebuild lives in `app/memory/reindex.py`, shared by the runtime and the
CLI. This makes changing `EMBED_BACKEND` self-healing — no manual re-seed.

---

## 5. The persona: reading the SOUL

Build #1 loads the persona **the way the runtime does — by reading the SOUL files directly**
(→ ch. 19, "she reads herself into being"), not by consuming a flattened card. The SOUL is the
sibling `../yuri-soul` reference impl (→ ch. 07).

### 5.1 Seeding & loading

- **Seed once:** copy the **persona** files + `soul.yaml` into `vault/soul/` (a make target or a
  first-run step) — everything *except* the two `runtime_only` files, which route to their runtime
  homes: `USER.md` → `vault/soul/USER.md` (starts as the empty-relationship template);
  `MEMORY.md` → the memory tier (`#What I know that matters` → `memory/semantic/facts.md`,
  `#Things {{user}} asked me to forget` → `memory/semantic/forgotten.md`, §6.7). Both start empty
  in a fresh Vault — a card handed to someone else begins the relationship at zero.
- **Load every turn:** `SoulLoader` reads `soul.yaml` and resolves its source references against
  the `.md` files. This reuses `yuri-soul`'s field-assembly logic (import it, or vendor the ~40
  lines of resolver). The reference syntax:

  ```
  FILE.md#Heading   → the prose under that "## Heading"
  FILE.md@key       → a key from the file's YAML frontmatter
  FILE.md           → the whole body
  ```

  A list of sources concatenates in order. `WORLD.md` (`## Entry` + `keys:` → lorebook entry) and
  `EXAMPLES.md` (`## Example` → one `<START>` block) get structured parsers, same as `build_card.py`.

### 5.2 Which SOUL section feeds which prompt block

From `soul.yaml` (authoritative), the mapping Build #1 consumes:

| Prompt block (§7.1) | SOUL source |
|---|---|
| Voice law | `CONSTITUTION.md#Voice law` |
| Persona backbone | `CONSTITUTION.md#Identity` + `CONSTITUTION.md#History` + `PERSONA.md#Appearance` + `PERSONA.md#Manner` |
| Personality line | `PERSONA.md@personality` |
| Scenario / place | `SCENARIO.md#Scenario` |
| Return greetings (continuity) | `SCENARIO.md#Alternate greeting — evening` / `— morning` |
| Hard limits (post-history) | `CONSTITUTION.md#Hard limits` |
| Example voice | `EXAMPLES.md` (structured) |
| Lore (keyword-fired) | `WORLD.md` (structured, §5.3) |

`card_version` used throughout = `"<name lowercased>-v<major>@<canon>"`, all three from
`soul.yaml` (`name: Yuri`, `character_version: 1.0.0`, `canon: canon-v1` → `yuri-v1@canon-v1`),
stamped on every journal entry and every corpus record.

### 5.3 Macros & lorebook

- **Macros:** replace `{{char}}` → soul `name`, `{{user}}` → `USER_NAME` (default `"you"`) in all
  loaded strings, case-insensitive on the macro.
- **Lorebook (`WORLD.md`):** static, keyword-triggered *card-native* world flavor — **not** the
  deferred document knowledge store (§12). Each turn, scan the user message for any entry's
  `keys` (case-insensitive substring); inject matched entries' `content` into the lore block,
  ordered by `insertion_order`, capped at `LOREBOOK_BUDGET_TOKENS` (default 400). MAY be omitted;
  if so, note it in the README.

### 5.4 BOOTSTRAP (first-ever meeting) vs return greetings

`BOOTSTRAP.md#Cold open` is the **first message of a brand-new relationship** (empty Vault). It is
consumed once: after the first session, retire it — `git -C vault mv soul/BOOTSTRAP.md
soul/onboarded/BOOTSTRAP.done.md` and commit. File-presence *is* the "has she met you yet?" flag
(→ ch. 19, ch. 28). On every *return* visit the opener comes from memory (§9.3), falling back to
`SCENARIO.md` return greetings, never from BOOTSTRAP again.

---

## 6. MemoryStore — the ch. 19 contract, file-backed

Build #1 implements exactly the ch. 19 `MemoryStore` interface so nothing is rebuilt for Build
#5. Two homes, two jobs, never conflated:

- **`USER.md`** (the partner model) — durable, small, *always* injected whole. Her theory of
  *you*: name, pronouns, stable preferences, ongoing situations, "don't forget" items.
- **`memory/episodic/`** (the journal) — append-only prose events, embedded into the index for
  *approximate recall*.
- **`memory/semantic/facts.md`** — consolidated general facts (mostly grows later in DREAM; may
  stay small in Build #1). Seeded from `yuri-soul/MEMORY.md#What I know that matters` (§5.1).
- **`memory/semantic/forgotten.md`** — the **forget-ledger** backing `forget()` (§6.7). Seeded
  from `yuri-soul/MEMORY.md#Things {{user}} asked me to forget` — the covenant, kept as
  tombstones, not deletions (→ ch. 15).

### 6.1 The interface (implement this shape)

```python
# memory/store.py  (→ ch. 19 "The memory contract")
class MemoryStore(Protocol):
    def remember(self, record: Record) -> WriteResult: ...   # extract → embed → store; low-confidence
                                                             #   / externally-sourced facts QUARANTINE
    def recall(self, query: str, k: int) -> list[Memory]: ...# blended rank; MAY be empty by design
    def consolidate(self) -> ConsolidationReport: ...        # DREAM-only; NOT on the hot path (stub in B1)
    def forget(self, selector) -> int: ...                   # "forget that" must work; supersede-not-delete (§6.7)
    def inspect(self, selector) -> list[Memory]: ...         # what she knows + why (source, confidence)
```

`inspect()` is load-bearing — it is what makes the mind auditable, and the file backend gets it
almost free (`cat`, `git diff`). The dashboard/debug view reads memory **through** `inspect()`,
never around it.

### 6.2 `remember` (post-turn write)

1. **Journal.** Append the exchange to `memory/episodic/<today>.md` as a dated event, in prose:
   `### HH:MM  {{user}}: <msg>  ⇄  {{char}}: <reply>`. Append-only.
2. **Index.** Embed `"{{user}}: <msg>\n{{char}}: <reply>"` and upsert one `chunk` row
   (`kind='turn'`, with `source_path`/`source_span` pointing at the journal line).
3. **Partner model.** Call the utility model to extract *durable* facts about the user and
   **update `USER.md`** (§6.3). This is where `USER.md` grows.

`remember` MUST be tolerant: a malformed utility-model response is logged and dropped, never
fatal to the turn.

### 6.3 Partner-model update (`USER.md`)

`USER.md` is structured markdown the user can read and edit. Reference shape:

```markdown
---
name: ...
pronouns: ...
---
## Stable
- prefers mornings quiet
## Ongoing
- job interview this week — dreading the whiteboard round
## Don't forget
- anniversary: 14 Feb
```

After each exchange, prompt the utility model with the last turn **and the current `USER.md`**
(so it *updates* rather than duplicates) under a strict JSON schema:

```
System: Extract only DURABLE facts about the user worth remembering across sessions:
  identity, stable preferences, ongoing situations/goals, explicit "remember this" items.
  Ignore ephemeral chit-chat. Return JSON:
  { "ops": [ { "section": "Stable"|"Ongoing"|"Don't forget", "text": string,
              "op": "add"|"update"|"remove", "confidence": 0..1 } ] }
  Return {"ops": []} if nothing durable was stated.
```

Apply the ops to `USER.md` (merge, don't blindly append; drop `remove`d lines). Externally-
sourced or low-confidence claims are **quarantined** (kept out of `USER.md` until a second turn
corroborates) — promotion, not capture, is the trust boundary (→ ch. 15).

### 6.4 `recall` (hot path)

```
recall(query, k):
  q = embed([query])[0]
  rows = index.search(q, limit=k*4)                 # cosine ANN over memory/index/
  rank = similarity * salience * recency_decay(created_at)   # blended, not raw similarity
  rows = mmr_rerank(rows, q, lambda=0.5)            # diversify; avoid k paraphrases of one memory
  drop rows with similarity < RETRIEVAL_MIN_SIM (default 0.25)
  return top k                                       # default k = 6; [] on an empty store
```

- `recency_decay(t) = exp(-age_days / HALF_LIFE_DAYS)` (default 30) — old memories fade, never vanish.
- MMR surfaces the *small load-bearing detail*, not just the most similar text (→ ch. 15).
- Empty Vault ⇒ `[]`; assembly proceeds on SOUL + `USER.md` alone.

### 6.5 Git commit (post-turn, background)

After the journal/`USER.md`/summary writes for a turn, commit the Vault:
`git -C vault add -A && git -C vault commit -m "turn <session>:<idx>"`. Vault writes MUST be
atomic (write-temp-then-`rename`) so a crash leaves the last *commit* intact, never a half-written
file (→ ch. 19, crash recovery). `memory/index/` is gitignored and excluded from the commit.

### 6.6 Swap seam (documented, not built)

A `PgVectorMemoryStore` implementing the same §6.1 interface with local Postgres+pgvector is a
legal drop-in (the local backend ch. 31 names, sanctioned by ch. 19). Build #1 ships the
file backend; a swap changes one constructor and forfeits nothing above it. A **cloud** memory
service (Mem0/Letta) can satisfy the signatures but cannot answer `inspect()` ownably, so it is
out of bounds — it forfeits the moat (→ ch. 19, ch. 15).

### 6.7 `forget` (the covenant)

`forget(selector)` is **supersede-not-delete** (→ ch. 15). It MUST NOT rewrite history: to
forget a fact it (a) removes the line from `USER.md`/`facts.md` in the *working* tree, and
(b) appends a tombstone to `memory/semantic/forgotten.md` (`### YYYY-MM-DD  forgot: <text>  —
<why/who asked>`), then commits. The old value survives in `git log` (auditability) but is
**gone from every future prompt**: assembly (§7) never reads `forgotten.md` into the system
prompt, and `recall` (§6.4) MUST drop any chunk whose source text is tombstoned. This is the
runtime home of `MEMORY.md#Things {{user}} asked me to forget` — the section seeds the ledger,
and "forget that" during play appends to it. It returns the count of memories superseded.

---

## 7. Prompt assembly

The single most important function: it composes the model input from **SOUL (static) + Vault
(current) + a small raw window**. Ordering and budgets are normative.

### 7.1 System prompt layout (top → bottom)

```
┌─ 1. VOICE LAW ─────────────────────────────────────────────┐  CONSTITUTION#Voice law
├─ 2. PERSONA BACKBONE ──────────────────────────────────────┤  CONSTITUTION#Identity/#History
│    identity · history · appearance · manner · personality  │  + PERSONA#Appearance/#Manner + @personality
├─ 3. SCENARIO / PLACE ──────────────────────────────────────┤  SCENARIO#Scenario
├─ 4. LORE (if any fired this turn) ─────────────────────────┤  matched WORLD.md entries
├─ 5. WHO YOU ARE TO HER (partner model) ────────────────────┤  vault/soul/USER.md (whole; it's small)
├─ 6. WHAT YOU'VE TALKED ABOUT (rolling summary) ────────────┤  vault/memory/summary.md
├─ 7. THINGS THAT MAY BE RELEVANT (recalled memories) ───────┤  recall(user_msg, k), each tagged w/ age
├─ 8. THE HONESTY CONSTRAINT (§7.4) ─────────────────────────┤  fixed text
└─ 9. EXAMPLE VOICE (optional, if budget allows) ───────────┘  EXAMPLES.md
```

The message array sent to the model:

```
[ {role:"system", content:<block above>},
  *<last M raw messages from state/sessions.json's transcript, chronological; M = RAW_WINDOW_TURNS = 6>,
  {role:"user", content:<new user message>} ]
```

`CONSTITUTION.md#Hard limits` (post-history instructions) MUST be appended **after** the history —
as a trailing system message or fused onto the final user message — because its purpose is to be
the *last* thing read before replying (V2/V3 card semantics).

### 7.2 Budgeting & "Lost in the Middle"

- Keep the **raw window small** (default 3 exchanges). Do **not** stuff the whole transcript;
  long raw context degrades middle recall (→ ch. 02 §4.3). The rolling summary carries older
  context cheaply.
- Per-block token budgets are config (§11). On overflow, **drop recalled memories first,
  lorebook second; never drop the voice law, persona, `USER.md`, or the honesty constraint.**
  The persona and partner model are load-bearing; episodic recall is best-effort.

### 7.3 Summarisation (every N turns)

When the session turn count crosses a multiple of `SUMMARY_EVERY_N` (default 8), call the utility
model with the *previous* `summary.md` + the last N exchanges → an updated summary
(≤ `SUMMARY_BUDGET_TOKENS`, default 300), third person, present-continuous. Write it to
`memory/summary.md` **and** index it as a `chunk` (`kind='summary'`, `salience=2.0`) so it is
recallable. Committed with the turn. Keeps context bounded while preserving long-range recall.
(This is the seed of the DREAM consolidation pass added in Build #5, → ch. 18.)

### 7.4 The honesty constraint (property 2)

A fixed block in the system prompt, and the acceptance test behind it:

> *You remember only what is in the memory blocks above and this conversation. If {{user}} asks
> about something you have no record of, say so warmly and plainly — "I don't think you've told
> me that yet" — and ask, rather than inventing a memory. The same rule runs the other way: when
> {{user}} tells you something new, take it as new — never respond with "I remember" or "you told
> me" details that are not actually in the blocks above. Never fabricate a shared past.*

Verified by a **golden transcript test** (§13.3): asked about an unstored event, the reply admits
the gap and invents no specifics.

---

## 8. The corpus logger (capture the corpus from day one)

Every reply MUST append one faithful record to an **append-only JSONL log** — the *only* place
raw, trainable conversation data is kept (the index is derived and lossy). It is the seed of the
eventual distillation corpus (→ ch. 20, ch. 30). Costs almost nothing now; cannot be
reconstructed later. **This log is separate from the Vault** — it is your training asset, not part
of her mind.

### 8.1 Layout

```
corpus/
  turns.jsonl        # append-only; one line per assistant reply
  ratings.jsonl      # append-only sidecar; feedback that arrives after a reply
  README.md          # which build wrote here, date range, export notes
```

`corpus/` is **personal data, not code.** `.gitignore` it (and it is outside `vault/` entirely),
keep it on owned hardware, **never commit** it. No phone-home, no retention dashboard.

### 8.2 Record schema (`turns.jsonl` — one JSON object per line, → Appendix D)

| Field | Type | Req | Purpose |
|---|---|---|---|
| `id` | uuid | ✓ | unique record id (ratings key to this) |
| `session_id` | string | ✓ | groups a conversation |
| `turn_index` | int | ✓ | 0-based position in the session |
| `timestamp` | ISO-8601 UTC | ✓ | when the reply was produced |
| `companion` | string | ✓ | persona id (`yuri`) |
| `messages` | array<{role,content}> | ✓ | **the full prompt as sent** (system + window + user) — trainable input |
| `completion` | string | ✓ | the assistant reply — trainable target |
| `model` | string | ✓ | model id that produced `completion` |
| `model_role` | `teacher`\|`student`\|`production` | ✓ | Build #1 writes `production` |
| `source` | `live_play`\|`synthetic`\|`hand_authored` | ✓ | Build #1 writes `live_play` |
| `collection_scope` | `self`\|`consented_hosted` | ✓ | Build #1 writes `self` (boundary below) |
| `card_version` | string | ✓ | persona/SOUL version (§5.2) |
| `template_version` | string | – | prompt-assembly version (bump on §7 changes) |
| `gen_params` | object | – | `{temperature, top_p, max_tokens, seed}` |
| `rating` | object | – | merged in at export from `ratings.jsonl` |
| `tags` / `flags` / `redacted` | – | – | balancing / exclusions / PII-scrubbed marker |

`log_turn(...)` is called once per reply. It MUST `assert collection_scope in ("self",
"consented_hosted")` — there is **no value for a downloader's data** (§8.4). Ratings arriving
later are written to `ratings.jsonl` keyed by the turn `id` and merged at export — never patched
into the line.

### 8.3 Reference `corpus.py`

```python
import json, uuid, datetime, pathlib
CORPUS = pathlib.Path("corpus/turns.jsonl")

def log_turn(*, session_id, turn_index, messages, completion, model,
             model_role="production", source="live_play", collection_scope="self",
             companion="yuri", card_version, **optional) -> str:
    assert collection_scope in ("self", "consented_hosted")   # the sovereignty boundary, in code
    rec = {"id": str(uuid.uuid4()), "session_id": session_id, "turn_index": turn_index,
           "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
           "companion": companion, "messages": messages, "completion": completion,
           "model": model, "model_role": model_role, "source": source,
           "collection_scope": collection_scope, "card_version": card_version,
           **{k: v for k, v in optional.items() if v is not None}}
    CORPUS.parent.mkdir(exist_ok=True)
    with CORPUS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec["id"]                                           # ratings key to this later
```

### 8.4 The sovereignty boundary

`collection_scope` has exactly **two** legitimate values: `self` (the operator's own play and
synthetic generation — all of Build #1) and `consented_hosted` (opt-in, privacy-cleared, on a
product the operator runs). A shipped card or runtime **never logs a stranger's conversation
home.** The field exists so every row's basis is auditable *before* it can enter a training set.

---

## 9. Frontend — the sanctuary

Not a chat tab: **a place she lives** (→ ch. 28). One static page, dark, quiet, served by FastAPI.
No sidebar of conversations, no marketing chrome, no upsell.

### 9.1 Layout & behavior

```
┌────────────────────────────────────────────────────────────┐
│  ◇  yuri                                        · online    │  slim header: sanctuary glyph + name
│────────────────────────────────────────────────────────────│
│   yuri:  Welcome back. You left mid-thought about the       │  ← continuity greeting on load (§9.3)
│          move — did you decide on the apartment?            │
│   you:   still deciding. it's a lot.                        │
│   yuri:  ▏(streaming…)                                      │  ← token-by-token via SSE
│────────────────────────────────────────────────────────────│
│  [ write to her…                                    ] (↵)   │  composer; Enter sends
└────────────────────────────────────────────────────────────┘
```

- **Streaming:** assistant tokens render as they arrive (SSE via `EventSource`/`fetch`
  `ReadableStream`); a caret shows in-progress.
- **History:** on load, fetch and render the current session's transcript (or start fresh).
- **Continuity greeting** (§9.3): the first thing shown must demonstrate memory, unprompted.
- **Per-message rating** (§8.2): a subtle 👍/👎 on assistant messages → `POST /api/rate`.
- **No** engagement theatre: no streaks, notifications, "she's typing to keep you here" tricks.
  One person, no audience (property 5).

### 9.2 Visual tokens (YuriOS Lab brand — dark everywhere)

```css
:root{
  --void:#050507; --bg:#0a0a10; --bg-2:#11111a; --bg-3:#181822;
  --rule:#1d1d28; --ink:#e8e6f0; --ink-2:#b8b3cc; --dim:#6a6783;
  --magenta:#ff2bd6; --cyan:#2bfff0; --amber:#f5b462;   /* amber = warmth, used rarely */
  --font:"JetBrains Mono", ui-monospace, monospace;
}
/* her lines lean warm (amber/ink); yours dim/cyan; background near-black. Selection magenta-on-void. */
```

Body font **JetBrains Mono**; header uses the sanctuary glyph (a windowed square).

### 9.3 The continuity greeting (the proof it works)

On load, `GET /api/greeting?session_id=…` streams an opener that **surfaces something the user
told her before, unprompted.** Implementation: read `USER.md` + `memory/summary.md` + a top
`recall()`, and generate one short greeting with the chat model from the persona + that memory
(no user message). Empty Vault (first ever run) ⇒ use `BOOTSTRAP.md#Cold open` (§5.4); on a
return visit prefer this memory-grounded opener over a static return greeting. This is the DoD
headline: *close the tab, come back tomorrow, she opens with continuity.*

---

## 10. HTTP API contract

All under `/api`, JSON unless noted. Single-user, localhost, no auth in Build #1 — but every
handler MUST treat `session_id` as untrusted (validate ids; the Vault path is fixed, not
user-supplied).

| Method | Path | Body / query | Returns |
|--------|------|--------------|---------|
| `POST` | `/api/session` | — | `{ session_id }` (creates a session in `state/sessions.json`) |
| `GET`  | `/api/session/{id}/history` | — | `{ messages: [{role,content,ts}] }` |
| `GET`  | `/api/greeting` | `?session_id` | **SSE** stream of the continuity opener (§9.3) |
| `POST` | `/api/chat` | `{ session_id, message }` | **SSE**: `data: {"token":"…"}` … then `data: {"done":true,"turn_id":"…"}` |
| `POST` | `/api/rate` | `{ turn_id, thumbs: 1\|-1 }` | `{ ok: true }` (appends `ratings.jsonl`) |
| `GET`  | `/api/health` | — | `{ ok, model, embedder, vault_head }` (`vault_head` = current git SHA) |
| `GET`  | `/` | — | the static sanctuary page |

### 10.1 `/api/chat` handler algorithm (normative)

```
1. validate {session_id, message}; load session from state/sessions.json (404 if missing).
2. turn_index = session.turn_count.
3. memories = MemoryStore.recall(message, RETRIEVAL_K)        # §6.4
   user_md  = read vault/soul/USER.md
   summary  = read vault/memory/summary.md
   window   = last RAW_WINDOW_TURNS transcript messages, chronological
   lore     = lorebook_hits(message)                          # §5.3
4. system   = assemble(SoulLoader.load(), user_md, summary, memories, lore)   # §7
   prompt   = [system, *window, {role:'user', content:message}, hard_limits]
5. append the user message to the session transcript.
6. stream ChatModel.stream(prompt) → forward tokens as SSE; accumulate `reply`.
7. append the assistant message to the transcript; turn_id = corpus.log_turn(...)  # §8 — MUST happen
8. session.turn_count += 1; last_active = now(); persist state/sessions.json.
9. schedule background: MemoryStore.remember(exchange) (journal + index + USER.md, §6.2);
   if turn_count % SUMMARY_EVERY_N == 0: summarise (§7.3);  then git-commit the Vault (§6.5).
10. emit data: {"done":true,"turn_id":turn_id}.
```

Steps 7 and 9 MUST NOT block the token stream (step 6). A mid-stream model failure emits
`data:{"error":"…"}` and writes **no** corpus record and **no** partial commit.

---

## 11. Configuration

Via environment (`.env`), read once at boot into a typed config object (`pydantic-settings`). No
secrets in code.

| Var | Default | Meaning |
|-----|---------|---------|
| `OPENROUTER_API_KEY` | — | chat + utility model auth (OpenRouter route only) |
| `CHAT_MODEL` | `deepseek/deepseek-v4-flash` | reply model; prefix picks the route (§3.2). The reference `.env` ships a local `lm_studio/google/gemma-4-12b-qat` |
| `UTILITY_MODEL` | `deepseek/deepseek-v4-flash` | fact-update + summarisation |
| `LMSTUDIO_BASE_URL` | `http://localhost:1234/v1` | LM Studio server (used only for `lm_studio/…` ids and `EMBED_BACKEND=lm_studio`) |
| `CHAT_THINKING` | `true` | reply model's `<think>` pass; off = `reasoning_effort:none` for speed (§3.2) |
| `UTILITY_THINKING` | `true` | utility model's `<think>` pass; a reasoning model needs `UTILITY_MAX_TOKENS` headroom |
| `MAX_REPLY_TOKENS` | `2048` | reply/greeting ceiling — room for a `<think>` pass **and** the reply |
| `EMBED_BACKEND` | `sentence_tf` | `sentence_tf` \| `ollama` \| `lm_studio`; a swap auto-reindexes (§4.3) |
| `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | embeddings model |
| `EMBED_DIM` | `384` | MUST equal the index vector width |
| `VAULT_DIR` | `./vault` | the git-backed mind |
| `SOUL_SRC` | `../yuri-soul` | seed source for `vault/soul/` |
| `USER_NAME` | `you` | `{{user}}` substitution |
| `RAW_WINDOW_TURNS` | `6` | raw messages kept in-prompt (3 exchanges) |
| `RETRIEVAL_K` | `6` | recalled memories injected |
| `RETRIEVAL_MIN_SIM` | `0.25` | drop below this cosine similarity |
| `HALF_LIFE_DAYS` | `30` | recency-decay half-life |
| `SUMMARY_EVERY_N` | `8` | summarise cadence (turns) |
| `SUMMARY_BUDGET_TOKENS` | `300` | rolling-summary cap |
| `LOREBOOK_BUDGET_TOKENS` | `400` | lore injection cap |
| `TEMPERATURE` | `0.9` | chat sampling |

---

## 12. Non-goals (explicitly out of scope)

| Not in Build #1 | Where it lands |
|-----------------|----------------|
| **Autonomy / a tick loop / unprompted messages** | Build #5 (→ ch. 18). Build #1 is **purely request/response** — no always-on process, no SENSE/APPRAISE/DECIDE. |
| Activity states, budget governor, salience/interrupt model | Build #5 (→ ch. 18) |
| DREAM consolidation, the world model, goals store | Build #5 (→ ch. 18, 19) — `consolidate()` is a stub here |
| Voice (TTS/STT) | Build #2 (→ ch. 24) |
| Avatar (Live2D / VRM) | Builds #2 / #4 (→ ch. 25) |
| Tool use / effectors / the capability broker | Build #4 / #5 (→ ch. 17, 19) |
| The host runtime, multi-character, card-signature verification | Build #5 (→ ch. 19) — Build #1 is one character, one process |
| Fine-tuning / distillation | later — Build #1 *collects the corpus* (§8) that makes it possible; tuning first is the #1 trap (→ ch. 12, ch. 02 §4.2) |
| **Document knowledge store / RAG over docs** | Build #5's drop-folder `KnowledgeStore` (→ ch. 16). Build #1's index is **memory about the user**, not a world-knowledge layer — ch. 19 keeps them separate stores. |
| A required database (Postgres/pgvector as spine) | never a requirement — the mind is files; pgvector is only an optional local backend (§6.6) |

The lorebook (§5.3) is **not** an exception to "no knowledge store": it is static, SOUL-embedded
world flavor triggered by keywords, not a document-ingesting RAG.

---

## 13. Definition of done

### 13.1 Acceptance checklist (the ch. 03 gut-check)

- [ ] **One persona, enacted not recited.** She *behaves* as the SOUL describes; she doesn't list traits. (Ask "what are you like?" — she shows, not enumerates.)
- [ ] **Memory persists across sessions and admits its edges.** `USER.md` + journal survive a process restart and a new browser session; asked about an unstored event she says so and does not confabulate (§7.4 golden transcript passes).
- [ ] **A place she lives.** Sanctuary styling (§9.2), not a generic chat box.
- [ ] **One person, no audience, no upsell in the loop.** No engagement mechanics anywhere.
- [ ] **Yours.** Runs on operator-controlled hardware; the mind is **files in `vault/` under git** you can `cat`, `git log`, and copy away (§4.2).
- [ ] **The corpus log exists and is faithful.** Every reply writes one schema-conformant line to `corpus/turns.jsonl`; `corpus/` and `memory/index/` are gitignored; `collection_scope` is asserted.
- [ ] **Every durable change is a commit.** `git -C vault log` reads as the diary of how she grew.
- [ ] **Tested.** The §13.3 `pytest` suite exists and is green — `pytest` from the project root passes every case below. This is a **hard gate**: the build is not done until it is.

### 13.2 The headline proof

> Close the tab. Come back tomorrow. She opens with **continuity** — surfaces something the user
> told her yesterday, unprompted (§9.3). If that single moment lands, the build is done.

### 13.3 Automated tests (`pytest`) — REQUIRED

An automated `pytest` suite is a **normative requirement**, not a nicety: the build MUST ship with
it and it MUST pass. `pytest` is a declared dependency (§14) and `tests/` a first-class part of the
repo — a reviewer MUST be able to run `pytest` from the project root and watch every case below go
green. "I clicked around in the browser" does not satisfy this. The list is the **minimum** coverage
each area MUST have (add more freely); a build that omits or skips any of these is not done (§13.1).

- **SoulLoader**: `soul.yaml` source refs resolve to the right `.md` sections; macros substitute; a missing section fails loudly, not silently.
- **Prompt assembly**: blocks appear in §7.1 order; overflow drops memories before persona/`USER.md`; `Hard limits` land after the history.
- **Recall**: a seeded index returns the planted load-bearing memory in top-k; MMR removes near-duplicates; empty index returns `[]`.
- **Partner model**: an exchange stating a durable fact updates `USER.md`; ephemeral chit-chat does not; a low-confidence external claim is quarantined.
- **Forget covenant** (§6.7): `forget()` removes a fact from the working `USER.md`/`facts.md`, appends a tombstone to `forgotten.md`, and a subsequent `recall`/assembly never resurfaces it — while `git log` still shows it ever existed.
- **Honesty golden transcript**: asked about an unstored event, the reply admits the gap and invents no specifics.
- **Corpus + git**: one turn appends exactly one valid `turns.jsonl` line (§8.2) and produces exactly one Vault commit; `log_turn` raises on an illegal `collection_scope`.
- **Persistence**: `USER.md` + journal written in one process are recalled in a fresh one; `scripts/reindex.py` rebuilds `memory/index/` from the `.md` files alone.

---

## 14. Suggested repository layout

```
01-minimum-viable-waifu/
  SPEC.md                     ← this file
  README.md                   ← quickstart, what it omits
  pyproject.toml              ← deps: fastapi, uvicorn, litellm, sentence-transformers,
  .env.example                    sqlite-vec, pydantic-settings, pytest
  .gitignore                  ← MUST include: corpus/  vault/memory/index/  .env
  app/
    main.py                   ← FastAPI app; mounts StaticFiles; wires the routes
    config.py                 ← §11 typed env (pydantic-settings)
    routes/
      chat.py                 ← §10.1 handler (SSE)
      greeting.py             ← §9.3
      session.py  rate.py  health.py
    core/
      soul.py                 ← §5 SoulLoader (reuses ../yuri-soul's resolver)
      assemble.py             ← §7 prompt assembly (template_version lives here)
    memory/
      store.py                ← §6 MemoryStore Protocol + FileMemoryStore
      index.py                ← §4.3 sqlite-vec derived index (+ embedder-provenance meta)
      reindex.py              ← §4.3 rebuild-from-.md core (shared by runtime + CLI)
      partner.py              ← §6.3 USER.md update
      summarise.py            ← §7.3
    corpus.py                 ← §8 log_turn + ratings append
    providers/
      base.py                 ← §3.1 Protocols
      openrouter.py           ← ChatModel + UtilityModel (via LiteLLM; §3.2 routing + reasoning switch)
      ollama.py               ← local Embedder (Ollama)
      lmstudio.py             ← local Embedder (LM Studio, §3.2)
      sentence_tf.py          ← Embedder (swap here for Build #2's local stack)
    vaultgit.py               ← §6.5 atomic writes + git commit helpers
  web/
    index.html  app.js  sanctuary.css   ← §9 the static page (no build step)
  scripts/
    seed_vault.py             ← copy ../yuri-soul persona → vault/soul/; route MEMORY.md → memory/
                                  (facts.md + forgotten.md, §5.1); git init the Vault
    reindex.py                ← rebuild memory/index/ from the .md files
    export_corpus.py          ← §8 merge ratings, subtract flags, reshape (→ ch. 20)
  vault/                      ← created by seed_vault.py (git repo; §4.1). NOT the app's repo.
  tests/
    test_soul.py test_assemble.py test_recall.py test_partner.py
    test_honesty_golden.py test_corpus_git.py test_persistence.py test_forget.py
```

---

## 15. How this build extends (→ ch. 31 "Extends to")

- Swap `CHAT_MODEL` (via LiteLLM) and `EMBED_BACKEND` for **local** ones → on the road to
  **Build #2** (add voice + a 2D body).
- The SOUL in `vault/soul/` already *is* the export source — run `../yuri-soul/build_card.py`
  over it to get the `.PNG` card → **Build #3**.
- Wrap a **tick loop** (→ ch. 18) around *this exact Vault* — add SENSE/APPRAISE/DECIDE, activity
  states, DREAM `consolidate()`, a `WorldModelStore`, and a minimal drop-folder `KnowledgeStore`
  (→ ch. 16, 19) → **Build #5**, the agentic sanctuary. Because the mind is already files behind
  the `MemoryStore` contract, the loop bolts on; nothing is rebuilt.

Build #1 is the file-Vault the whole ladder stands on — ship it first.
