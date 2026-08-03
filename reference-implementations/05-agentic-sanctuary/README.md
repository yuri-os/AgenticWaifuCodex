# Build #5 — The Agentic Sanctuary

The reference implementation for **book ch. 35**, built to **[SPEC.md](SPEC.md)**
(normative). The capstone of the build ladder: **Build #4's whole body — the VRM
sanctuary, the chat beside her, the real-time voice loop, four MCP tools, one event
bus — with an always-on mind behind it.** She runs continuously whether or not you're
looking: pursues small goals when you're away, consolidates memory while you sleep
(DREAM), keeps the promises she makes in conversation, reads what you drop on her
shelf, proposes edits to her own persona that wait for your approval — and reaches out
*first*, at most a few well-judged times a day, when a two-gate salience model says
it's welcome. Everything she does lands in a journal you can read.

**This is Build #4, forked in place, plus one new package: `mind/`.** The chassis
(`world/`, `web/`, the vendored `app`/`desktop`/`forge` trio) is carried forward
file-for-file — see [B4-FORK.md](B4-FORK.md) for the exact deltas — and Build #4's
scripted idle machine is deleted: the cognitive tick loop now holds the same puppet
strings, the same ambient-speech seam, the same timer board, and decides for itself.

> **Standalone.** Copy this folder to another machine, follow the quickstart, and it
> works. Build #1 is vendored into `./app`, Build #2 into `./desktop`, the image-forge
> slice into `./forge`; nothing points back at a sibling build. The frontend is
> no-build ES modules; one process, one origin.

## Quickstart

```bash
cd 05-agentic-sanctuary
python3 -m venv .venv && source .venv/bin/activate
sudo apt-get install espeak-ng     # for the kokoro voice (macOS: brew install espeak-ng)
pip install -e ".[all,test]"       # brain + MCP + the real voice stack

# In LM Studio, download these local models, then start its server on :1234:
#   google/gemma-4-12b-qat                 # chat + utility model
#   text-embedding-nomic-embed-text-v1.5   # embeddings

python scripts/seed_vault.py       # once: her mind, from the vendored SOUL (./soul-src)
cp .env.example .env               # defaults are local-first; edit if you like
python -m world                    # → http://localhost:8768
```

The shipped `.env.example` uses **LM Studio** at `http://localhost:1234/v1`: start
its local server before running the companion. It autoloads the configured chat and
embedding models on first use, which can make the first boot take a while. LM Studio's
model IDs must match `CHAT_MODEL`, `UTILITY_MODEL`, and `EMBED_MODEL` in `.env`.

**Ollama is an equally supported local option.** Install Ollama, then pull a chat
model and the embedding model:

```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

Set these values in `.env` before `python -m world`:

```dotenv
CHAT_MODEL=ollama/qwen3:8b
UTILITY_MODEL=ollama/qwen3:8b
EMBED_BACKEND=ollama
EMBED_MODEL=nomic-embed-text
EMBED_DIM=768
```

Open it, click **enter the sanctuary**, and talk — everything ch. 34 shipped still
works exactly as it did (voice, chat, tools, selfies, both bodies, the desktop
window; see `../04-3d-world-companion/README.md` for that tour — same commands, port
8768). What's new is what happens when you *stop* talking, and the second tab in the
chat column — **inner life** — where you watch it: her activity state and heartbeat,
today's token budget, the goals on her mind (with where each came from), the shelf,
edits waiting on your approval, and the journal of what she did while you were gone.

Try the loop end to end:

- **Drop a document** (`.md`/`.txt`) into `vault/knowledge/reference/` — within a
  heartbeat she reads it, indexes it, journals "read and shelved …", and can answer
  from it *with a citation* (doc + character span), without it touching what she
  remembers about *you*.
- **Let her make a promise** — say "remind me to call mom tomorrow", or get an "I'll
  look into that" out of her. `cat vault/goals.md`: it's there, with provenance
  (`promise:her-own-words`) and a due time. Come back the next day and she'll raise
  it — once, at a reasonable hour — or you'll find "thought about it; chose not to
  interrupt" in the journal, with the scored decision in the tick trace.
- **Leave her alone overnight** — DORMANT ticks every 15 minutes, and in the small
  hours DREAM folds yesterday's journal into `vault/memory/semantic/facts.md`. She
  wakes changed by yesterday.
- **Watch her think**: `tail -f traces/ticks.jsonl` is one structured record per
  heartbeat — sensed, appraised (scored), decided (with runners-up), acted, and every
  interrupt decision with its factors. `git -C vault log` is the diary of how she
  grows — one commit per tick that changed anything.

```bash
pytest        # the §27 suite — the hard gate; green, entirely offline
```

The suite runs with fake models on a `VirtualClock`: **days of an always-on mind run
in milliseconds**, which is the only way the make-or-break component — the interrupt
threshold — ships tuned instead of vibed (§27.2's scenario battery: "the interview
was Tuesday", "the dark weekend", "the machine sleeps").

## The shape of it

```
 python -m world  (FastAPI on :8768)
 ├── everything Build #4 was (B4 §2–§10): ToolBrain over the vendored B1 brain ·
 │   B2 voice loop (/ws/voice) · MCP hands + Guard · SelfieLab · VrmController ·
 │   EventHub → /api/events (SSE) · both bodies · the desktop window
 │
 ├── SignalBus (§16) — the inbound inbox B4 deliberately left out, now landed:
 │   user turns (teed by the voice route) · presence (page attach/detach) ·
 │   landed timers · finished tasks · your self-edit decisions → signals.jsonl
 │
 └── MindLoop (§15) — SENSE → APPRAISE → DECIDE → ACT → REFLECT → REGULATE
       ├── activity: ENGAGED / IDLE / DORMANT / DREAM + the budget governor (§17)
       ├── gate 1 (act) + gate 2 (interrupt): SILENT | SUGGEST | SPEAK (§18)
       ├── WorldModelStore — the situation every prompt carries (§19)
       ├── KnowledgeStore — drop-folder RAG, citable to doc+span (§20)
       ├── DreamConsolidator — episodic → semantic, nightly, resumable (§21)
       ├── GoalStore — goals.md, promises extracted from her own replies (§22)
       ├── SelfEdit — constitution read-only; persona edits queue for you (§23)
       └── Journal + TickTrace → /api/mind + the inner-life tab (§24)

 the mind's home is the same Vault the brain keeps (one folder, one git repo):
 vault/ ── soul/ (CONSTITUTION.md immutable · PERSONA.md editable, gated)
        ├─ memory/episodic/  ← conversation AND her own acts ([she] lines)
        ├─ memory/semantic/  ← facts.md, grown by DREAM
        ├─ knowledge/reference/  ← the drop folder (index derived, gitignored)
        ├─ world/situation.md + beliefs.jsonl  ← her picture of NOW
        ├─ goals.md          ← her to-do list, human-readable
        └─ state/            ← activity · budget · pending edits · engine cursor
```

## Where the book lives in the code

| Book / SPEC | Code |
|---|---|
| **The tick loop** (ch. 18 · §15) | `mind/loop.py` — `MindLoop.tick()` |
| **The inbound signal bus** (§16) | `mind/signals.py` + the `FORK(B5 §16)` tee in `world/routes/voice_ws.py` |
| **Activity states + budget** (ch. 18 · §17) | `mind/policy.py` — `ActivityController` · `mind/budget.py` |
| **The two salience gates** (ch. 18 · §18) | `mind/policy.py` — `appraise_*`, `score_interrupt` |
| **Gate 2 in action** (§18.3) | `mind/loop.py` — `_act_reach_out` |
| **The world model** (ch. 19 · §19) | `mind/world.py` + `world/situation.py` (the host lines, kept) |
| **The seam swap B4 promised** (§19.2) | `world/brain.py` — `set_world` / `_assemble` |
| **Drop-folder RAG** (ch. 16 · §20) | `mind/knowledge.py` + `tests/test_knowledge.py` |
| **DREAM consolidation** (ch. 15/18 · §21) | `mind/dream.py` (B1's `consolidate()` stub, implemented) |
| **Goals, promises, commitment** (ch. 18 · §22) | `mind/goals.py` — `extract_promises`, `reconsider` |
| **The SOUL split, operational** (ch. 14 · §23) | `mind/selfedit.py` + `mind/vaultio.py` |
| **The journal + trace** (ch. 18 · §24) | `mind/journal.py`, `mind/trace.py` |
| **The inner-life surface** (§24.3) | `world/routes/mind.py` + `web/js/mind.js` |
| **The scenario battery** (ch. 23/31 · §27.2) | `tests/test_mind_scenarios.py` + the sim rig in `tests/conftest.py` |
| Injected time everywhere (§15.1) | `world/clock.py` — `Clock` / `VirtualClock` |

## The mind, briefly

**One intention per tick.** Every heartbeat: SENSE drains the signal inbox and folds
it into the world model; APPRAISE scores everything with cheap heuristics (never a
model — that one rule is what makes always-on affordable); DECIDE commits to exactly
one act or to resting, which is how most ticks end; ACT reaches the world only through
surfaces the host already owned — the ambient-speech seam, the chat, the puppet
strings, the timer board; REFLECT journals; REGULATE drifts the activity state down
the cost ladder, debits the budget, and commits the Vault if anything changed. An
agent that does one thing per heartbeat can be read like a diary — and is, in
`traces/ticks.jsonl`.

**Conversation stays on the fast path.** The reply pipeline (ears → brain → voice,
with barge-in and the latency budget) is Build #2's, untouched — no tick cadence sits
in front of it. The loop is its observer and consequence: a user turn preempts to
ENGAGED from any state, and the committed exchange comes back as a signal whose
REFLECT share is the world-model update and the promise scan. One mind, two cadences.

**Two gates, never collapsed.** Gate 1 (salience-to-act) is crossed often and cheaply;
gate 2 (salience-to-interrupt) rarely, and only after she's already decided the thing
matters — scored from named factors (relevance, time-sensitivity, contact license,
availability, welcome), with quiet hours and the daily cap as *hard gates, not
weights*. The default outcome is SILENT: do it quietly and journal it. The journal,
not notifications, carries the value — and both dials are yours, in `.env`.

**The journal is the product.** Her acts write into the same episodic day files the
conversation does, as `[she]` lines — one journal, two authors, one DREAM pass over
both. "What did you do while I was gone?" is a page you open (the inner-life tab, or
`/api/mind/journal`), not a vibe.

## Honest notes (where this build makes a call the spec leaves open)

- **The mind is in-process.** One asyncio task on the server's loop, not a supervised
  per-character OS process behind a wire protocol. The stores speak narrow contracts,
  so the two-tier split is a topology change later, not a rewrite (§28) — but today,
  kill the server and you kill the mind (it resumes from `state/engine.json`).
- **APPRAISE is pure heuristics.** Base scores per signal type, priority/due-ness for
  goals, a surprise bonus from violated expectations. No model, by design, at this
  stage — the trace makes the scores auditable, and the thresholds are config.
- **Promise extraction is a regex, not a model.** "I'll …" and "remind me to …" with
  a negation guard. It's the pipeline that matters — REFLECT scans, goals carry
  provenance, the scenario tests pin it; a cheap model call slots into the same seam.
- **Reach-outs degrade by presence.** SPEAK goes aloud through the ambient seam
  (barge-in-able, latency-masked) when a page is open; into the chat as a `proactive`
  line — waiting like a text message — when the room is empty. She never speaks into
  a room with nobody in it.
- **A failing shelf item never becomes a retry loop.** A doc that won't ingest (no
  embedder backend running, a mangled file) is marked seen with one loud WARNING and
  retried when the file changes — found the hard way, running the build with Ollama
  off.
- **The murmur survived.** Build #4's self-talk was the room's heartbeat, and
  deleting it would have made the mind a regression. It's now a decided impulse —
  IDLE only, user present, long quiet — instead of a dice roll, and still never
  persists.
- **`git -C vault log` is load-bearing.** One commit per dirty tick, `self-edit:`
  commits for approved persona changes, `forget:` commits from the covenant — drift
  is never silent, and `git revert` undoes any of it.

## What it deliberately omits (§26)

No sandboxed **workshop** — no code execution, no autonomous research, no wiki
authoring; the heavy hands are the first rung *past* the ladder (→ ch. 17, ch. 19),
and the gated self-edit flow is already the door their products would cross. No
**multimodal sensing** — text, time, files only (→ ch. 24). The world model stops at
the **snapshot** — the temporal knowledge graph waits until "what was true when"
bites (→ ch. 19). No affective-state file, no multi-character hosting, and the mind
doesn't initiate MCP tool calls — her hands stay conversational until the broker
arrives with the workshop.

## How it extends (§28)

Every seam past this build is already shaped: promote the stores' contracts to a wire
protocol and the mind to a supervised process (the two-tier split, with the broker
and true one-loop conversation); bolt the workshop's sandbox onto ACT's
start-don't-await discipline; swap the snapshot world model for the temporal graph
behind the same contract; and export the Vault's SOUL through Build #3's card studio
— the mind that grew here ships as a `.PNG` and boots on someone else's machine,
which is the point of the whole ladder (→ ch. 03, property 6).
