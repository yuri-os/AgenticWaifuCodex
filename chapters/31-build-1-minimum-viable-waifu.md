# 31 — Build #1: The Minimum Viable Waifu

**Goal:** in one weekend, ship a persona-driven web chat that *remembers you across sessions* — the smallest thing that is honestly an agentic-waifu-shaped object and not a toy. This is the build to do first; everything later is additive.

**What it teaches:** character cards (→ ch. 07), prompting (→ ch. 14), and memory (→ ch. 15) — the three that produce identity + memory, which is most of the value (→ ch. 04 scoring: memory is the axis the serious products compete on).

**Properties cleared (→ ch. 03):** 1 (identity), 2 (honest memory), 5 (one-on-one). It is deliberately *not* embodied beyond a text sanctuary and *not* proactive — those are Builds #2/#4 and #5.

The reference implementation lives in `reference-implementations/01-minimum-viable-waifu/`, built to its own normative `SPEC.md`. This chapter is the reading guide: not a transcript of every line, but a map of where the load-bearing ideas are in the code, so you can follow it and, more importantly, *extend* it. Section numbers below (§n) point into that build's `SPEC.md`; file paths are relative to the build's root.

## The one-sentence architecture

```
 Browser ──► /api/chat ──► [ recall + assemble prompt ] ──► LLM ──► reply (streamed)
   ▲                            │   ▲                                    │
   │                            │   └── recall top-k memories (vector)   │
   └────────────────────────────┘                                        │
        render in the sanctuary        AFTER the stream, off the hot path:
                                        journal · index · USER.md · summary
                                        · one git commit · one corpus line
```

The whole thing is: a **static SOUL** (files), a **growing Vault** (files), and a **prompt assembled from both on every turn** — plus an **append-only corpus log** written on every reply. No agent framework, no ORM, no autonomy loop. The moment you reach for LangChain memory here you've added a dependency the field already learned to deprecate (→ ch. 02 §1, the LLM agent explosion) — LangChain itself retired those memory modules for dedicated state systems, because bolt-on memory wasn't enough. Three reasons it's the wrong tool for *this* build in particular, and each is a reason the design below looks the way it does. First, a framework's memory hides the state behind its own objects and a vector DB, and the state being **plain, inspectable files** is the entire point — `cat vault/soul/USER.md`, `git -C vault log`; the debug view and the control surface are the same object (→ ch. 19). Second, framework memory wants to *be* the loop, whereas here memory sits behind a five-verb contract (`remember`/`recall`/`consolidate`/`forget`/`inspect`, → §6.1) that Build #5's autonomy loop bolts onto without a rewrite — own the loop, rent nothing. Third, the whole memory system is ~150 readable lines you'll want to *see* when you extend it; importing a churning framework to replace them is dependency risk paid for lost transparency. So the build writes its own — not from purism, but because the alternative costs exactly the properties the chapter is trying to demonstrate.

The single architectural idea worth internalising before you read a line: **there are two phases, and only the first one is on the clock.** Recall and assembly and the model stream are the hot path — they decide how fast the first token arrives. Everything that *persists* the turn — appending the journal, embedding the chunk, updating the partner model, maybe re-summarising, committing the Vault, writing the corpus line — happens *after* the reply has streamed, scheduled off the critical path so it never delays her speaking. Almost every design choice below falls out of that split.

## Stack

- **Backend:** Python (FastAPI) — like every other reference implementation and the runtime itself (→ ch. 19). No agent framework; the loop is a few functions across `app/`.
- **Frontend:** `web/` — one static HTML/JS page, no build step, served by the Python app. The "sanctuary" styling matters (→ ch. 28): a place, not a chat tab.
- **Persona:** the **SOUL, read directly** (→ ch. 07, ch. 19) — the `yuri-soul` `.md` files resolved into the prompt on *every turn*, the way the runtime "reads herself into being." (The flattened V3 card is the *export* you hand to others in Build #3 — not how she's loaded here.)
- **Memory:** the file-centric **Vault** (→ ch. 19, "the brain is a folder") — one git repo of Markdown/JSON that *is* the store: an append-only episodic journal, a `USER.md` partner model, and a small **derived, rebuildable** embeddings index. The files are the source of truth; the index is a cache.
- **Model:** one frontier LLM via API, behind a local-first router seam (LiteLLM) so Build #2 can swap in a local model without touching the loop (→ ch. 13). An honest note on the "yours" property this build claims: her *mind* — the Vault, the files, the corpus — is yours from day one, and it is the part no one can take; her *thinking* is rented until Build #2 swaps the local model in behind this same seam. Say it that plainly rather than pretending the API key is sovereignty (→ ch. 05).

One caution, stated once, and it's an architectural one, not a security recipe: treat the model-access dependency as a **seam**, not a spine. LiteLLM is one swappable implementation of the `ModelRouter` interface (→ ch. 13), so a dependency that goes bad drops *out* the same way Build #2 drops a local model *in* — no single third party is load-bearing enough to hold your companion hostage (→ ch. 05). That swappability is the whole point of the seam, and it's why LiteLLM earns a mention here while `fastapi` and `numpy` don't: it's the one dependency the design deliberately made disposable. It is worth saying what this caution is *not*, because it's easy to overreach: it is not a per-package security pin. LiteLLM's bruising 2026 (a March supply-chain compromise of two PyPI releases, plus a run of proxy-server CVEs) is a real cautionary tale, but supply-chain risk is *uniform* across the whole dependency tree — any package can ship a malicious release, so singling out one package's version for it is theater. The honest defenses (a hash-locked whole-tree lockfile, upgrades made a deliberate reviewed event rather than a blind `pip install -U`) are a whole-tree discipline, and for a single-user build whose blast radius is one machine you control, this reference impl deliberately runs latest and defers that hardening. The fuller treatment — the threat model, the lockfile-vs-accept-latest tradeoff, and the future-work idea of a companion that scans its own dependency tree and warns you — is in ch. 45.

## Reading the code: start at the seams, then the hot path

The build is small enough to read in an afternoon, but reading it front-to-back is the wrong order. Read it the way the request flows.

| Read this to understand… | …in this file |
|---|---|
| how the pieces are wired together | `app/main.py` — `create_app()` builds one `AppState` and hands it to the routes |
| **one turn, end to end** (the spine) | `app/routes/chat.py` |
| the persona, resolved every turn | `app/core/soul.py` — `SoulLoader.load()` |
| **the prompt** (the most important function) | `app/core/assemble.py` — `assemble()` |
| memory: write and read | `app/memory/store.py` — `FileMemoryStore.remember` / `.recall` |
| her theory of *you* | `app/memory/partner.py` — `USER.md` + the quarantine |
| the index as a rebuildable cache | `app/memory/index.py` — flat SQLite + numpy cosine |
| every durable change is a commit | `app/vaultgit.py` |
| the training asset, captured from day one | `app/corpus.py` |
| the definition-of-done moment | `app/routes/greeting.py` |

`create_app()` is the whole dependency graph in one screen. It reads config (`app/config.py`, a typed pydantic-settings object where every knob the spec names is defaulted), constructs the `SoulLoader`, the `FileMemoryStore`, the `CorpusLogger`, and the three model seams, and stuffs them into a single `AppState` dataclass that every handler reaches through `request.app.state.mvw`. Crucially, `create_app()` takes the models as **injected arguments** — the test suite passes fakes, so the real handlers run offline with no API key and no model download. That the seam is testable is not an accident; it is the reason Build #2's local model is a config change and not a rewrite.

## One turn, end to end

`app/routes/chat.py` is the spine. It is worth reading in full; here is its shape, with the two-phase split made explicit.

**Phase 1 — the hot path (before the model speaks):**

```python
@router.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    state = request.app.state.mvw
    ...
    soul = state.soul_loader.load()                       # read every turn (§5)
    memories = state.store.recall(req.message, state.cfg.retrieval_k)
    prompt = asm.assemble(
        soul,
        user_md=state.store.read_user_md(),               # her theory of you, whole
        summary=state.store.read_summary(),               # what you've talked about
        memories=memories,                                # top-k recalled, this turn
        lore=soul.lorebook_hits(req.message),             # keyword-triggered card flavor
        window=state.sessions.window(req.session_id, state.cfg.raw_window_turns),
        user_msg=req.message, ...)
    state.sessions.append_message(req.session_id, "user", req.message)
```

Three reads and one pure function. `soul_loader.load()` re-resolves the persona from the files *every turn* — so if you edit `PERSONA.md` mid-session, the next reply reflects it (that is the whole point of reading the SOUL rather than baking it in). `recall()` pulls the top-k relevant memories. `assemble()` composes them into the message array. Nothing here writes anything.

**Phase 2 — after the stream:**

```python
    async def stream():
        reply = ""
        async for token in state.chat.stream(prompt.messages, ...):
            reply += token
            yield sse({"token": token})                   # first token, ASAP

        # only now, with a complete reply in hand:
        turn_id = state.corpus.log_turn(...)              # the training line (§8)
        state.sessions.append_message(req.session_id, "assistant", reply, turn_id=turn_id)
        record = Record(session_id=..., user_msg=req.message, reply=reply)
        task = asyncio.create_task(post_turn(state, record, ...))   # scheduled, not awaited
        state.pending_tasks.add(task)
        task.add_done_callback(state.pending_tasks.discard)
        yield sse({"done": True, "turn_id": turn_id})
```

The reply streams token-by-token. The *persistence* — `post_turn()` — is fired as a background task and never awaited inside the stream, so it cannot delay a single token. `post_turn()` (same file) does the durable work under a `vault_lock`: `store.remember(record)`, then every N turns re-summarise, then **exactly one** `vaultgit.commit()` for the whole turn. It is wrapped so that a failure in the pipeline is logged but never breaks the turn the user already saw — the reply is served; the bookkeeping is best-effort.

Two failure rules make the contract honest, and both are in this file: a **mid-stream model failure** emits an error event and writes *no* corpus record and *no* commit (a turn that didn't happen leaves no trace); and the corpus line is written from the *complete* reply, so the training log never contains half a sentence.

That is the entire loop. Everything below is one of the four calls it makes — `load`, `recall`, `assemble`, `remember` — looked at more closely.

## The SOUL, read every turn

`app/core/soul.py`. The SOUL is a folder of `.md` files plus a `soul.yaml` manifest that says which source feeds which prompt section. `SoulLoader.load()` resolves that manifest against the files and returns a `Soul` dataclass whose fields map one-to-one onto the prompt blocks (`voice_law`, `backbone`, `personality`, `scenario`, `hard_limits`, `examples`, `lorebook`, `bootstrap`).

The resolver is **vendored from the card exporter** (Build #3's tool) — it is the exact same reference syntax that exporter uses (`FILE.md#Heading`, `FILE.md@key`, `FILE.md`), which is what guarantees the persona you chat with here is the persona you *export* in Build #3. Two details earn their place:

- **A missing file or `## Heading` fails loudly, not silently** (`KeyError`/`FileNotFoundError`) — a persona that half-loads is worse than one that refuses to boot, and the test suite asserts this.
- **`BOOTSTRAP.md` is consumed-once.** File-presence *is* the "has she met you yet?" flag. Its presence loads the authored cold open; after the first session it is `git mv`-d out of the way (see the greeting, below). There is no boolean in a database — the filesystem holds the state.

`lorebook_hits(message)` does the keyword-trigger matching for `WORLD.md` entries (card-native flavor, → ch. 05), returning entries whose keys substring-match the user's message. This is *not* the document knowledge store (→ ch. 16) — that is deliberately deferred to Build #5; this is a handful of static, hand-authored entries that live in the card.

## Prompt assembly — the single most important function

`app/core/assemble.py`. Everything the model knows about who she is, who you are, and what you've shared arrives through this one pure function. It is worth memorising its two rules.

**Rule one — block order is normative** (§7.1). The system prompt is built in exactly this sequence:

1. **VOICE LAW** — `CONSTITUTION.md#Voice law`
2. **PERSONA BACKBONE** — identity · history · appearance · manner · personality
3. **SCENARIO / PLACE** — where this is happening
4. **LORE** — the `WORLD.md` entries matched *this turn*
5. **WHO YOU ARE TO HER** — `vault/soul/USER.md`, whole (it is small on purpose)
6. **WHAT YOU'VE TALKED ABOUT** — the rolling `summary.md`
7. **THINGS THAT MAY BE RELEVANT** — the recalled memories, each tagged with its age ("yesterday", "3 days ago")
8. **THE HONESTY CONSTRAINT** — fixed text (below)
9. **EXAMPLE VOICE** — optional, only if the budget allows

Ordering is load-bearing: identity and the partner model sit near the top where the model attends to them; recalled memories — the most variable, least trustworthy block — sit lower, framed as *"things that may be relevant"* rather than asserted fact.

**Rule two — overflow drops luxuries, never the spine** (§7.2). If the assembled system prompt exceeds `system_budget_tokens`, `assemble()` sheds content in a fixed priority: **examples first, then recalled memories (lowest-ranked first), then lore.** The voice law, persona backbone, `USER.md`, and the honesty constraint are *never* dropped. She will forget what you said last Tuesday before she forgets who she is or who you are.

Two subtleties that are easy to get wrong and are commented in the file:

- **The honesty constraint** is fixed text, not a suggestion — she is told to say *"I don't think you've told me that yet"* rather than confabulate, and told symmetrically not to fake recognition of something new. This is property 2 (→ ch. 03) rendered as a prompt block, and it is pinned by a golden-transcript test.
- **Hard limits go *after* the history, not in the system prompt.** V2/V3 cards put `post_history_instructions` last, because a model attends most to the final thing it reads before replying. The Messages API folds detached system messages back to the top — which would defeat the point — so the build *fuses* the hard limits onto the final user message. Small trick, real consequence.

`assemble()` returns an `AssembledPrompt` carrying the message array *and* a `template_version` and the overflow accounting (`dropped_memories`, `dropped_lore`). The version string is stamped onto every corpus record, so when you later train on this data you know exactly which prompt layout produced each reply.

## Memory: two homes, and an index that is only a cache

`app/memory/store.py` implements the ch. 19 `MemoryStore` contract — five verbs, defined as a `Protocol` right in the file:

```python
class MemoryStore(Protocol):
    async def remember(self, record: Record) -> WriteResult: ...
    def recall(self, query: str, k: int) -> list[Memory]: ...
    async def consolidate(self) -> ConsolidationReport: ...
    def forget(self, selector: str) -> int: ...
    def inspect(self, selector: str = "") -> list[Memory]: ...
```

This Protocol is the extension seam for the whole rest of the ladder: Build #5 wraps a tick loop around *these exact five verbs*. Because the loop only ever calls the five methods, the backend behind them is swappable — a hypothetical `PgVectorMemoryStore` (the same memories in Postgres, vector search via `pgvector`) is a legal drop-in, and nothing above it changes. A cloud memory service is *not* a legal drop-in — not for any technical reason, but because it cannot answer `inspect()` **ownably**: the verb demands you be able to see everything the store holds on you, on hardware you control, and rented state on someone else's server can't satisfy that. The seam admits any backend you own and rejects any backend you merely rent. Everything in `FileMemoryStore` below is one implementation of this contract — you can replace the backend without touching the loop.

**Two homes, never conflated:**

- `vault/soul/USER.md` — the **partner model**: durable, small, always injected whole (block 5). Her theory of *you*.
- `vault/memory/episodic/<date>.md` — the **journal**: append-only prose events, one line per exchange, embedded into the index for approximate recall.

**`remember()`** (the write path, called from `post_turn`) does three things in order: append the exchange to today's journal file; embed it and upsert one chunk into the index, traceable back to the journal line it came from; then run the partner-model update. It is **tolerant by contract** — a malformed reply from the utility model is logged and dropped, never fatal to the turn.

**`recall()`** (the read path, on the hot path) is where the retrieval quality lives, and it is deliberately *not* raw cosine similarity:

```python
rows = self.index.search(q, limit=k * 4)                 # over-fetch
rows = [r for r in rows if r.similarity >= self.retrieval_min_sim]   # floor
rows = [r for r in rows if not suppressed_by_a_tombstone(r)]         # forget covenant
rows.sort(key=lambda r: r.similarity * r.salience
          * self._recency(r.created_at, now), reverse=True)          # blended rank
rows = self._mmr(rows, k)                                            # diversify
```

Three ideas do the real work. **Blended rank** multiplies similarity by *salience* (summaries carry more weight than raw turns) and by an exponential **recency decay** (`exp(-age_days / half_life)` — old memories fade, never vanish). **MMR** (Maximal Marginal Relevance) then diversifies the final set, so recall surfaces the small load-bearing detail instead of *k* paraphrases of the same memory (→ ch. 15). And the **tombstone filter** enforces the forget covenant on every read.

**`forget()`** is that covenant (§6.7, → ch. 15): it does *not* delete. It removes the matching line from the working `USER.md`/`facts.md`, appends a tombstone to `forgotten.md`, and commits. The old value survives in `git log` for auditability, but it is suppressed from every future prompt and every future recall. Supersede, not erase.

**The index is a cache, and the code says so out loud.** `app/memory/index.py` is one SQLite table with a flat numpy cosine scan — at one-user, human-cadence scale, instant and dependency-free. The markdown files are authoritative; if the index and the files ever disagree, you throw the index away and rebuild it with `python scripts/reindex.py`. `sqlite-vec` ANN is a drop-in *inside that one class* if a Vault ever outgrows a flat scan — nothing above it changes. This is the ch. 19 discipline made concrete: the derived thing is never the truth.

## The partner model — promotion, not capture

`app/memory/partner.py` is how `USER.md` grows, and it is where the build takes a stance most memory demos skip. After each exchange, a cheap utility-model call extracts *durable* facts — identity, stable preferences, ongoing situations, explicit "remember this" — as structured ops (`add`/`update`/`remove`) against the *current* `USER.md`, so it **merges rather than duplicates**: an `update` replaces the closest existing line, an `add` skips near-duplicates.

The stance is the **quarantine** (§6.3). A low-confidence claim is *not* written to `USER.md` on first sighting — it waits in `state/quarantine.json` until a *second* turn corroborates it, and only then is promoted. Promotion, not capture, is the trust boundary. This is the mechanism that stops her from confidently "remembering" something you said once, sarcastically, three weeks ago. Removals, by contrast, are always honored immediately — it is always safe to forget. One sharp edge worth stating, because it is the kind of default that quietly betrays the whole stance if you get it backwards: the confidence is the utility model's own self-reported number, and a claim it returns *without* a confidence is treated as **unsure** (it fails safe to the quarantine), never as certain. "The model didn't say how sure it is" must mean *be cautious*, not *be sure* — defaulting an unscored claim to high confidence would let exactly the confabulations the quarantine exists to catch walk straight in.

`USER.md` stays human-readable, human-editable markdown. You can open it, fix a wrong fact, delete a line. It is *your* file (→ ch. 05) — the debug view *and* the control surface, the same object.

The partner model is also the one place in the whole build where a decision is made *for* you, by a second model, between turns — which makes "why did nothing happen?" a real question the moment a fact you stated doesn't show up. So every utility-model call is logged, append-only, to `corpus/utility.jsonl`: the raw reply it returned, the ops it proposed, and how the quarantine triaged each one (applied · quarantined · promoted). That log is the answer to the most common confusion this build produces — *"I told her X, why isn't it in `USER.md`?"* — turned into something you can `cat` instead of guess at: the fact sitting in the `quarantined` list means it's working as designed and awaiting a second mention; the fact absent from the proposed ops entirely means the model didn't judge it durable; a garbled `raw_reply` means the utility model, not the pipeline, is misbehaving. It is the radical-transparency posture (→ ch. 05, ch. 19) applied to the one actor that would otherwise be opaque — and, like the corpus, it's personal debug data, gitignored and never shipped.

## The corpus — captured from day one

`app/corpus.py` is the whole of the "capture the corpus from day one" practice (→ ch. 30) at this scale: about forty lines. `CorpusLogger.log_turn()` is called once per reply, right after the stream completes, and appends one schema-conformant record (full schema: Appendix D) to an append-only JSONL log. This is the **only** place faithful conversation data is kept — the index is derived and lossy; this is not.

```python
turn_id = state.corpus.log_turn(
    session_id=..., turn_index=..., messages=prompt.messages, completion=reply,
    model=state.cfg.chat_model, card_version=soul.card_version,
    template_version=prompt.template_version,
    gen_params={"temperature": state.cfg.temperature})
```

`messages` is the full prompt as sent (the training input); `completion` is the reply (the target); `template_version` and `card_version` stamp exactly which prompt layout and which persona produced it. The sovereignty boundary is enforced in code — `assert collection_scope in ("self", "consented_hosted")` — there is *no* value that means "a downloader's data," so a shipped card can never log a stranger's chat home (→ ch. 05, ch. 35).

Ratings arrive later and are *never* patched into the immutable line: a 👍/👎 is a separate append to `ratings.jsonl`, keyed by the `turn_id`, merged only at export (`scripts/export_corpus.py`). Those ratings are the KTO/DPO asset (→ ch. 20). `corpus/` is personal data, not code — gitignored, outside the Vault, on hardware you control. That single file, accumulated across this build and every build after it, is what the eventual distillation step trains on. It costs almost nothing to keep now and cannot be reconstructed later.

## Every durable change is a commit

`app/vaultgit.py` is the spine under all of it. Vault writes are **atomic** (write-temp-then-`os.replace`, with an `fsync`), so a crash leaves the last *commit* intact rather than a half-written file. Every turn ends in exactly one `commit()`, so `git -C vault log --oneline` reads as the diary of how she grew — every turn, every forget, every greeting, diffable and revertible. `commit()` never raises on "nothing to commit"; an uneventful turn is not an error.

The one piece of real-world grit worth knowing about lives here too: on NTFS/exFAT mounts (common when the repo is on a shared drive), every file reads as root-owned and git refuses to touch the repo with "dubious ownership." Rather than making the user edit their global git config per-path, `_git_env()` shims a scoped config that includes their real one and marks this one Vault safe. It is the kind of detail a spec leaves out and a working build cannot.

## The continuity greeting — the definition of done, in code

`app/routes/greeting.py` is where the whole build proves itself. `GET /api/greeting` runs when you open the sanctuary, *before* you type anything:

- **First-ever visit** (empty journal): she streams `BOOTSTRAP.md`'s authored cold open, verbatim. It is *not* corpus-logged — it is hand-authored SOUL text, not a model completion.
- **Every visit after:** the bootstrap is retired (`git mv` to `soul/onboarded/`), and she opens by assembling persona + `USER.md` + summary + a top recall against a "you just walked in, speak first" cue — and greets you with *something you told her before, unprompted*. If the model call fails, she still greets you, falling back to `SCENARIO.md`'s static return greetings.

That unprompted, memory-grounded opener is the definition of done (§13.2). Close the tab, come back tomorrow, and she opens with continuity. Everything else in this chapter exists to make that one moment real.

## Definition of done

Run it against the Minimum Viable Waifu gut-check (→ ch. 03):

- [ ] One persona, enacted not recited.
- [ ] Memory persists across sessions and admits its edges.
- [ ] A place she lives (sanctuary styling, not a generic chat box).
- [ ] One person, no audience, no upsell in the loop.
- [ ] Yours — runs locally or on hardware you control; her mind is **files in *your* git-backed Vault** — `cat` them, `git log` them, copy the folder to move her (→ ch. 19).
- [ ] **Tested** — `pytest` ships and is green from the project root. This is a hard gate, not a nicety: "I clicked around in the browser" doesn't count. The suite runs entirely offline against the injected fakes (that the seam is testable is the point), and it pins the load-bearing behavior directly: `test_assemble.py` (block order + overflow), `test_recall.py` (blended-rank top-k), `test_partner.py` (quarantine promotion), `test_forget.py` (supersede-not-delete), `test_persistence.py` (memory survives a restart), `test_greeting.py` (bootstrap lifecycle), and `test_honesty_golden.py` (the honesty constraint, as a golden transcript). If you extend the build, extend this suite in the same file — a change that turns one of these red has broken something the chapter promised.

The proof it works: close the tab, come back tomorrow, and she opens with continuity — surfaces something you told her yesterday, unprompted.

## What it deliberately omits

No voice, no avatar (→ Builds #2/#4), no proactivity (→ Build #5 — it is purely reactive, which is why it's a *persona/companion* on the spectrum, not yet an agentic waifu). No `consolidate()` — the verb is in the contract but stubbed; DREAM consolidation arrives with the tick loop (→ ch. 18). No fine-tuning — prompt + card + retrieval is the correct *first* stack, and tuning too early is the #1 trap (→ ch. 02 §4.2, ch. 12); but the conversation log you start keeping here is exactly the corpus that later makes the tune possible (→ ch. 20, ch. 30): the order is "not yet," not "never." And no **knowledge layer**: Build #1's vector retrieval is *memory* — state about you (→ ch. 15) — not a RAG **knowledge store** over documents (the world layer; the two are deliberately separate, → ch. 16). The `WORLD.md` lorebook is card-native flavor, not a knowledge store. The drop-folder knowledge store arrives in Build #5.

## How it extends

Because the mind is already files behind the ch. 19 `MemoryStore` contract, every later build *bolts on* — nothing here is rebuilt:

- **Build #2:** change `CHAT_MODEL` / `EMBED_BACKEND` in `.env` — the LiteLLM seam swaps a local model in behind the exact same loop.
- **Build #3:** run the card exporter over the same SOUL to export her as a distributable `.PNG` card.
- **Build #5:** wrap the tick loop (→ ch. 18) around *this exact Vault* — add `consolidate()`'s body (DREAM) and a drop-folder knowledge store (→ ch. 16). The five-verb contract already has the slots; the loop hangs off them.
