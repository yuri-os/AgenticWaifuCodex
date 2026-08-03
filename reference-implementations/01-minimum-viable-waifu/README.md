# Build #1 — The Minimum Viable Waifu

The reference implementation for **book ch. 31**, built to **[SPEC.md](SPEC.md)** (normative).
A persona-driven web chat that **remembers you across sessions** — one companion, one user,
in a browser. Deliberately reactive (speaks only when spoken to), deliberately text-only.
Rung 1 of the ladder (→ ch. 30); everything later is additive.

The one-sentence architecture (SPEC §1.2):

> A **static SOUL** (files), a **growing Vault** (files), and a **prompt assembled from both
> on every turn** — plus an **append-only corpus log** written on every reply. No agent
> framework, no ORM, no autonomy loop.

## Quickstart

```bash
cd reference-implementations/01-minimum-viable-waifu
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"

# In LM Studio, download these local models, then start its server on :1234:
#   google/gemma-4-12b-qat                 # chat + utility model
#   text-embedding-nomic-embed-text-v1.5   # memory embeddings
cp .env.example .env            # shipped local defaults use LM Studio at :1234/v1
python scripts/seed_vault.py    # once: Vault from ../yuri-soul (§5.1)
python -m app                   # the Build #1 entrypoint → http://localhost:8765
```

The shipped `.env.example` uses LM Studio's OpenAI-compatible server at
`http://localhost:1234/v1`; the companion itself serves on port `8765` through
`python -m app`. LM Studio model IDs must match `CHAT_MODEL`, `UTILITY_MODEL`,
and `EMBED_MODEL`. The first use may take a while while LM Studio loads models.

**Ollama is an equally supported local option.** Pull a chat model and B1's
embedding model:

```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

Replace the model and embedding settings in `.env` before `python -m app`:

```dotenv
CHAT_MODEL=ollama/qwen3:8b
UTILITY_MODEL=ollama/qwen3:8b
EMBED_BACKEND=ollama
EMBED_MODEL=nomic-embed-text
EMBED_DIM=768
```

First visit: she opens with the SOUL's authored cold open (`BOOTSTRAP.md`, consumed once).
Every visit after: she opens with **continuity** — something you told her, unprompted.
That single moment is the definition of done (SPEC §13.2).

```bash
pytest                          # the §13.3 suite — the hard gate; must be green
```

The suite runs entirely offline (fake providers behind the §3.1 seams — that seam being
testable is the point). Set `OPENROUTER_API_KEY` to also run the live honesty golden check.

## Where the book lives in the code

| Book / SPEC | Code |
|---|---|
| The SOUL, read every turn (ch. 07, 19 · §5) | `app/core/soul.py` — vendors `../yuri-soul`'s resolver |
| Prompt assembly, block order + budgets (ch. 14 · §7) | `app/core/assemble.py` |
| The honesty constraint (ch. 03 property 2 · §7.4) | fixed text in `app/core/assemble.py`, tested in `tests/test_honesty_golden.py` |
| MemoryStore contract, file-backed (ch. 15, 19 · §6) | `app/memory/store.py` |
| Derived index — a cache, never truth (§4.3) | `app/memory/index.py` + `scripts/reindex.py` |
| Partner model USER.md + quarantine (ch. 15 · §6.3) | `app/memory/partner.py` |
| Rolling summary (§7.3) | `app/memory/summarise.py` |
| The forget covenant — supersede, not delete (ch. 15 · §6.7) | `FileMemoryStore.forget` + `memory/semantic/forgotten.md` |
| Corpus from day one (ch. 20, 30 · §8) | `app/corpus.py`, `scripts/export_corpus.py` |
| Every durable change is a commit (ch. 19 · §6.5) | `app/vaultgit.py` |
| Provider seams (ch. 13 · §3.1) | `app/providers/` — LiteLLM chat/utility, local embeddings |
| The hot path (§2.2, §10.1) | `app/routes/chat.py` |
| Continuity greeting + bootstrap lifecycle (ch. 28 · §5.4, §9.3) | `app/routes/greeting.py` |
| The sanctuary (ch. 28 · §9) | `web/` — one static page, no build step |

## The mind is a folder

`vault/` is **one git repo, owned by you** (§4). `cat vault/soul/USER.md` is the debug view;
`git -C vault log` is the diary of how she grew; copying the folder moves her. `corpus/`
is your training data (Appendix D schema), outside the Vault, gitignored, never shared.

```bash
git -C vault log --oneline        # every turn, every forget, every greeting
cat vault/soul/USER.md            # what she believes about you, right now
cat vault/memory/summary.md       # what you've been talking about
python scripts/reindex.py         # rebuild the derived index from the .md files
```

> **On NTFS/exFAT mounts** (files show as root-owned), git may refuse your own
> `git -C vault …` commands with "dubious ownership". The app handles this for its
> own commits (see `_git_env` in `app/vaultgit.py`); for your shell, run the
> one-liner git suggests: `git config --global --add safe.directory "$(pwd)/vault"`.

## Debugging — "USER.md didn't update when it should have"

The partner model is the one place a decision is made *for* you, by a utility model,
between turns — so it is the one place "why did nothing happen?" is a real question.
Every utility call is logged to `corpus/utility.jsonl` precisely so you can answer it
without guessing. Walk it in this order:

```bash
# 1. what did the utility model actually propose for that turn, and what did triage do?
tail -n 5 corpus/utility.jsonl | jq 'select(.kind=="extract")
      | {raw_reply, parsed, applied, quarantined}'

# 2. what is currently held, waiting for a second mention?
cat vault/state/quarantine.json

# 3. what actually landed, and when (the applied history)?
git -C vault log -p -- soul/USER.md
```

Read the `utility.jsonl` line for the turn and match the symptom:

- **The fact is in `quarantined`, not `applied`** → *working as designed.* A new,
  low- or unscored-confidence claim waits for a **second** corroborating turn before it
  lands (`QUARANTINE_CONFIDENCE`, `partner.py`). Say it again and it promotes. Note the
  fail-safe default: a claim the model returns with **no** confidence field is treated as
  unsure (`UNSCORED_CONFIDENCE = 0.0`), so it quarantines rather than captures.
- **The fact isn't in `parsed` at all** → the utility model didn't judge it durable. Read
  `raw_reply`: either it genuinely returned `{"ops": []}` (tune the extraction prompt,
  `EXTRACT_SYSTEM`), or it wrote prose/garbage instead of JSON.
- **`raw_reply` is non-JSON or truncated** → `parse_ops()` dropped it silently by contract
  (a malformed reply never breaks a turn, §6.2). The utility model is misbehaving — check
  `UTILITY_MODEL` in `.env`, or that the model returns JSON.
- **There is no `utility.jsonl` line for that turn at all** → the call never ran or threw.
  Either no utility model is configured (partner updates are skipped when `utility is None`),
  or the call errored — check the app log for `mvw.memory` (`partner-model update dropped`).
- **It's in `applied` but you don't see it in `USER.md`** → an `update`/`add` may have
  merged into an existing line (`apply_ops` de-duplicates, §6.3); check the `git log -p`
  diff above rather than eyeballing the file.

Summarisation is logged the same way (`kind:"summarise"`), so a stale or wrong
`summary.md` is debuggable by the same `jq` over `corpus/utility.jsonl`.

## Honest notes (where this build makes a call the spec leaves open)

- **Index search** is the §4.3 schema in plain SQLite + a numpy flat cosine scan — the
  spec's sanctioned FAISS/numpy alternative. `sqlite-vec` ANN is a drop-in inside
  `app/memory/index.py` if a Vault ever outgrows a flat scan; nothing above it changes.
- **Hard limits after history** (§7.1) are fused onto the final user message rather than
  sent as a trailing system message: the Messages API folds detached system messages to
  the top, which would defeat post-history semantics.
- **`remember()`/`consolidate()` are `async`** — same names and semantics as the §6.1
  contract; they await the utility model from the post-turn background task.
- **The verbatim bootstrap cold open is not corpus-logged**: it is hand-authored SOUL
  text, not a model completion. Generated greetings *are* logged, tagged `greeting`.
- **Session bookkeeping** lives in `app/sessions.py` (the spec's suggested layout keeps
  it inside the routes; it earned its own small file).
- **Her thinking is rented until Build #2** (ch. 31): the Vault, the files, and the corpus
  are yours from day one; the chat model is an API behind the LiteLLM seam. Swapping in a
  local model is a config change, not a rewrite.
- **Dependencies run latest, unpinned** — a deliberate call, not an oversight. Supply-chain
  risk is uniform across the whole tree (any package can ship a bad release, not just
  LiteLLM), so per-package pinning is theater; the real defenses (a hash-locked whole-tree
  lockfile, deliberate reviewed upgrades) are a whole-tree discipline discussed in ch. 45.
  For a single-user build on hardware you control, the blast radius is one machine, so this
  build accepts latest and defers that hardening. Bump on your own review, never blind `-U`.

## What it deliberately omits (§12)

No autonomy/tick loop, no voice, no avatar, no tools, no document-RAG knowledge layer,
no fine-tuning (it *collects* the corpus that later makes tuning possible). The lorebook
in `WORLD.md` is card-native flavor, not a knowledge store. See SPEC §12 for where each
lands (Builds #2–#5).

## How it extends (§15)

- Local model: change `CHAT_MODEL`/`EMBED_BACKEND` in `.env` → the road to **Build #2**.
- `python ../yuri-soul/build_card.py --soul vault/soul` → the distributable card, **Build #3**.
- Wrap the tick loop around *this exact Vault* → **Build #5**. Nothing here is thrown away.
