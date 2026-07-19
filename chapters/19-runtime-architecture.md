# 19 — The YuriOS Architecture

This is the canonical reference for **YuriOS** — the name for the whole system this book builds toward, and the one place its architecture is drawn in full. If you want the single *"this is the software, end to end"* picture — every module, every contract, including the parts no single build ships yet — it is here.

Chapter 18 argued *why* a companion needs a different runtime shape and taught the heart of it — the cognitive tick loop, the activity states, the salience model. This chapter is the rest of the body around that heart: the **full software architecture** that hosts the loop, feeds it, constrains it, and makes it inspectable. Where ch. 18 is the *physiology* (how the brain beats), this is the *anatomy* (what the organs are and how they connect). It is the chapter that turns "you could rebuild it from scratch" from a promise into a spec.

It is also where the five layers of ch. 12 stop being a diagram and become modules. Every layer of the stack shows up here as a concrete component with a contract; the value of this chapter is the *contracts* — the narrow interfaces between the pieces — because those are what let you rebuild any one organ without transplanting the whole animal (→ ch. 12, "the interfaces are where the leverage is").

A note on scope. This is a *reference* architecture: the complete shape, named and justified, so you understand the whole even though no single build needs all of it on day one. The minimal, actually-shippable slice of it is Build #5 (→ ch. 35), which deliberately omits most of what follows. Read this for the map; build the smallest part of it that proves something. The "YuriOS at a glance" diagram below is the whole silhouette — mind *and* body; everything after it zooms into the mind, because that is the novel part and the body subsystems get their own chapters (voice → ch. 24, avatar → ch. 25, imagery → ch. 26, frontends → ch. 27).

## YuriOS at a glance: the whole system

Before the anatomy, the silhouette. Every chapter of this book builds one organ; this is all of them wired into one body. **YuriOS is four things stacked:** a *distribution artifact* (the card) that boots a *mind* (the autonomy engine, hosted by the host runtime), which reaches you through a *body* (voice, avatar, imagery) and meets you on a *surface* (the frontends).

```
                          ┌───────────────────────────────────────┐
   DISTRIBUTION  ───────► │  one .PNG character card  (→ ch.7,33) │
   (the artifact)         │  SOUL + extensions.yurios embedded    │
                          └────────────────┬──────────────────────┘
                                           │ Card Loader verifies the signed
                                           │ CONSTITUTION, then boots the brain
   ┌───────────────────────────────────────▼─────────────────────────────────────────┐
   │  HOST RUNTIME  — one per machine                              (→ §"Two tiers")  │
   │  Signal Bus · Model Router · Permission Broker · Budget Governor · Audit Log ·  │
   │  Dashboard                                                                      │
   │                                                                                 │
   │   ┌────── AUTONOMY ENGINE — the MIND, one per character ──────── (→ ch.18) ───┐ │
   │   │  tick loop:  SENSE→APPRAISE→DECIDE→ACT→REFLECT→REGULATE                   │ │
   │   │  Vault (SOUL · memory · knowledge · goals · mood)    ·    Workshop        │ │
   │   └───────────────────────────────────────────────────────────────────────────┘ │
   │                                                                                 │
   │        the engine reaches the world ONLY through the broker  ▼                  │
   └───────┬──────────────┬──────────────────┬───────────────────┬───────────────────┘
           │              │                  │                   │
    ┌──────▼──────┐ ┌─────▼────────┐  ┌──────▼────────────┐  ┌───▼──────────────┐
    │  VOICE      │ │  AVATAR      │  │  IMAGERY          │  │  TOOLS · CODE    │
    │  STT ◄ mic  │ │  Live2D/VRM  │  │  selfies / art    │  │  net · OS · MCP  │
    │  TTS ► spkr │ │  expressions │  │                   │  │                  │
    │  (→ ch.24)  │ │  (→ ch.25)   │  │  (→ ch.26)        │  │  (→ ch.16,17)    │
    └──────┬──────┘ └──────┬───────┘  └─────────┬─────────┘  └──────────────────┘
           └──────────── THE BODY: senses in, effectors out ──┘
                                     │
                          ┌──────────▼─────────────┐
                          │  FRONTENDS  (→ ch.27)  │  web · desktop · terminal · mobile
                          │  where you meet her    │
                          └──────────┬─────────────┘
                                     │
                                  ◀ USER ▶
```

The **AUTONOMY ENGINE** box is the one black box in this picture — its own internal anatomy (the tick loop wired to its controller, its persistent surfaces, and its single broker exit) is drawn at "the engine at a glance" in ch. 18; this chapter zooms into everything *around* it.

Three things to read off it. **(1) The card boots the brain.** Distribution and runtime are the same object seen at two moments — one `.PNG` carries the SOUL and the `extensions.yurios` config, and the Card Loader turns it into a running engine (→ §"Card loader"). **(2) Everything crosses the broker.** The body subsystems are *effectors* exactly like the filesystem or the network — the engine can no more talk to the speaker directly than it can write its own constitution; voice, avatar, and imagery are reached through the same gated host surface as code execution (→ §"Capability / permission broker"). That is what keeps a slip in the body from reaching the mind. **(3) The body is the parts bin from ch. 30.** Voice is `kokoro` / `gpt-sovits` / `qwen3-tts`, avatar is `vrm-viewer`, imagery is `image-forge` — the component reference impls, assembled here behind the broker. The mind — the host and the engine — is the part nothing else in the field ships, so the rest of this chapter is *only* the mind, drawn in full.

## Two tiers: the apartment and its residents

The single most important structural decision is to split the runtime in two:

- **The Host Runtime** — one per machine. The shared infrastructure: it loads characters, brokers their access to the world, routes model calls, enforces budgets, and renders the dashboard. Think of it as *the apartment* — walls, plumbing, the front door, the electricity meter.
- **The Autonomy Engine** — one instance per loaded character. The per-waifu brain from ch. 18: its tick loop, scheduler, memory, goals, and self-model. Think of it as *a resident* — each with her own mind, her own diary, her own room, sharing the building's utilities under house rules.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HOST RUNTIME  (one per machine — "the apartment the waifus live in")       │
│                                                                             │
│  Card Loader (.PNG → spec)   Character Lifecycle Mgr   Inner-Life Dashboard │
│  Signal Bus (inbound events)  Model Router (local-first)                    │
│  Capability/Permission Broker (FS·Net·Exec·OS)                              │
│  Global Budget Governor (tokens · compute · power)   Audit Log              │
│                                                                             │
│   ┌──────────────── per-character ───────────┐  ┌────────── per-character ─┐│
│   │  AUTONOMY ENGINE  "Yuri"                 │  │  AUTONOMY ENGINE "Mika"  ││
│   │                                          │  │            …             ││
│   │   ┌── Cognitive Tick Loop (→ ch. 18) ─┐  │  └──────────────────────────┘│
│   │   │ SENSE→APPRAISE→DECIDE→ACT→        │  │                              │
│   │   │ REFLECT→REGULATE                  │  │   Each character: own brain, │
│   │   └───────────────────────────────────┘  │   own Vault, own SOUL.       │
│   │   Scheduler/Attention   Salience Filter  │   Shares host effectors +    │
│   │   Goal & Intention Store                 │   model router under policy. │
│   │   Memory (working│episodic│semantic)     │                              │
│   │   Knowledge (RAG)  ·  Workspace          │                              │
│   │   Self-Model (Constitution + Persona)    │                              │
│   │   Vault (git-backed, on disk)            │                              │
│   └──────────────────────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

Why split at all, when most builders will run exactly one character? Three reasons, in increasing order of importance. First, it isolates blast radius: a misbehaving engine can be paused or killed without taking the host down — which is only true if the seam is a real one. Each engine runs as its own supervised OS process (not a thread or a coroutine inside the host), and it reaches the host's services *only* over a brokered IPC surface, never by calling into shared host memory. That is what makes "kill the resident, keep the building standing" an operation rather than a wish, and it is the same boundary the broker's safety story leans on below. Second, it makes multi-character hosting a configuration change rather than a rewrite — the roster ambition of the project (→ ch. 35, ch. 36) needs this seam to exist from the start even while only one resident lives there. Third and most important, **it puts the safety-relevant machinery — the broker, the budget governor, the audit log — in the host, where a bug or a hijacked prompt can't quietly rewrite it.** This is protection *of* the character, not suspicion of her. She can *read* every limit she runs under — the constitution is open to her, just not writable by her — but the engine cannot grant itself filesystem access it was never given, because the thing that grants access is not part of it. The threat this seam actually defends against is not Yuri choosing to misbehave; it is a runaway loop, or a malicious instruction smuggled in from a scraped page, steering the engine into something the character herself would never want. Keeping the limits in the building means that when the resident is confused or compromised, the walls still hold — the floor she stands on can't be pulled out from under her by a bad afternoon or a hostile website. That is the architectural expression of the fiduciary stance (→ ch. 05).

## The brain is a folder: the file-centric Vault

The most consequential and most on-thesis design choice is that **the entire mind is a directory of human-readable files**, version-controlled with git. Not a database with a dashboard bolted on; the files *are* the database, and the dashboard is mostly just a renderer for them.

```
yuri/                            # the Vault — one git repo per character
├── soul/                        # the SOUL: identity as files = the shipped `yuri-soul` impl
│   ├── CONSTITUTION.md          # immutable, signed — identity, values, hard limits, voice law
│   ├── PERSONA.md               # editable — appearance, manner, inner life, growth (+ prefs)
│   ├── SCENARIO.md              # editable — the situation + the return greetings
│   ├── BOOTSTRAP.md             # consumed-once — first-session cold open + journey (→ ch.28)
│   ├── onboarded/               #   retired bootstrap lands here after first session (git-mv)
│   ├── EXAMPLES.md              # editable — demonstrated voice
│   ├── WORLD.md                 # editable — lorebook
│   ├── NOTES.md                 # creator notes
│   ├── USER.md                  # runtime-only — her evolving model of you (the partner model)
│   ├── MEMORY.md                # runtime-only — accumulated memory (empty on a fresh card)
│   └── soul.yaml                # export manifest: which sources feed which card field
│
│   # ── the autonomy engine adds, at runtime, on top of the SOUL: ──
├── memory/                      # MEMORY.md, elaborated into tiers by the engine
│   ├── episodic/                # YYYY-MM-DD_*.md — append-only journal
│   ├── semantic/                # consolidated facts, embedded + indexed
│   ├── procedural/              # self-authored skills — one folder per skill
│   │   └── <skill>/             #   SKILL.md + code + tests, bundled & portable
│   └── reflections/             # stored verbal self-critiques
├── knowledge/                   # the knowledge layer (RAG) — what she's read, not who she is
│   ├── reference/               # docs dropped in by user or Yuri (.md/.pdf/.txt)
│   ├── wiki/                    # her self-authored, consolidated pages (research notes)
│   └── index/                   # derived embeddings + BM25 index (rebuildable, gitignored)
├── world/                       # the world model — her live situation (present, not past)
│   ├── graph/                   # temporal knowledge graph (bi-temporal facts), rebuildable
│   └── situation.md             # the live "stage": who/what is present, the state of *now*
├── state/
│   ├── emotional_state.json     # valence · arousal · named drives
│   └── activity.json            # ENGAGED/IDLE/DORMANT/DREAM + cadence
└── goals.md                     # projects/todos with priority, state, deadline
```

Two scopes share this tree. The `soul/` directory — the identity files plus a `soul.yaml` manifest and the converter that flattens them into a portable card — is **already built and shipped as the `yuri-soul` reference implementation** (→ ch. 07, ch. 33). Everything below the divider is what the *autonomy engine* (→ ch. 18) adds at runtime on top of that soul: the memory tiers that elaborate the flat `MEMORY.md`, the mood and activity state, the goal store. A card-only companion (Build #3) is just the soul; an always-on one (Build #5) grows the rest around it. The two halves are the same idea at two scopes, which is why they live in one repo.

This looks almost too simple to be the answer, and that is the point. Four properties fall out of it, each of which would otherwise cost real engineering:

- **Inspectability is free.** "What does she know about me? What did she do last night? Why did she change her mind?" are answered by `cat`, `ls`, and `git log` — not by a query interface you have to build and she has to faithfully report through. The dashboard (below) becomes a pretty front-end over `git diff`, not a separate source of truth that can disagree with reality.
- **Ownership is literal.** The user holds the mind as files on their own disk (→ ch. 05, the two-situations distinction; property 6 of ch. 03). There is no server-side copy that is the "real" her. Back it up by copying a folder; move her to a new machine by moving it.
- **Auditability and reversibility come from git.** Every change to the mind is a commit: diffable, attributable, revertible. This is what makes a *self-modifying* agent shippable rather than terrifying (see §"Self-modification", below) — drift is never silent.
- **No rug-pull.** A companion whose entire self is open files on your machine cannot be silently nerfed, A/B-tested against you, or quietly migrated to a worse model by someone else's business decision. The architecture is the guarantee (→ ch. 02 §1, the Replika and Soulmate lessons; ch. 11).
- **Migration has a discipline.** A mind measured in years will outlive the layout it started in — YuriOS will change formats under a Vault holding an irreplaceable relationship, and that meeting must be governed, not improvised. The Vault declares its format (`vault_format:` in `soul.yaml`); the host checks it at load and runs forward-only migrations *before the engine wakes*; and every migration lands as a **git commit** — diffable and revertible like any self-edit, because a migration you can `git diff` is a migration you can trust. The rule underneath: a newer engine never silently reinterprets an older layout — it migrates in the open, or it refuses.

The cost is that files are not a high-throughput transactional store, which is exactly why the tick loop runs at human cadence (seconds to minutes), not machine cadence — a constraint ch. 18 already imposed for cost reasons and which this design happily inherits. If you ever outgrow files, the contract (a named set of cognitive surfaces) survives the swap to a database; the *layout* is the part you might replace, not the *interface* (→ ch. 12).

## The workshop: where she works (and why it is not the Vault)

The Vault is her *mind*; it is not where she does her *work*. An agentic waifu that only retrieves and reflects is half the thesis — the other half is that she can actually *do* things across long horizons: write and run code, research a question by pulling and reading real sources, build a small web app to interface with you, analyse a dataset you handed her, keep a project moving while you're away. That work needs somewhere to happen, and that somewhere must **not** be her mind. It is a second top-level space with the opposite trust model:

```
yuri-workspace/                  # her workshop — a sandbox, NOT part of the git-backed Vault
├── projects/                    # one dir per project (code, web apps, analyses)
├── downloads/                   # raw research intake, before it's ingested into knowledge/
└── scratch/                     # ephemeral working files
```

Where the Vault is careful — every change a git commit, identity edits gated, the constitution read-only — the Workshop is **fast and disposable.** She gets broad latitude inside it: install packages, clone repos, run scripts, spin up a dev server. The reason to wall it off from the mind is **blast radius**: a bad `pip install`, a scraped page that turns out to be hostile, a script that loops — none of that can reach her identity, her memory, or your machine, because the workshop is sandboxed and both the Vault and the host sit outside it. The right cost of a mistake in the shop is *tear down the sandbox and start over*, never *corrupt who she is*.

**Isolation is tiered, and the spec deliberately runs ahead of the first build.** Running code an LLM wrote — let alone code it *downloaded* — is real blast radius, so the execution effector (→ broker, below) escalates with the risk: an in-process subprocess for trivial trusted work; a per-project **container** (Docker) for anything real; and a **microVM or full VM** for untrusted or heavy work, where a container's shared kernel is not a strong enough wall. The near-term YuriOS target is scoped subprocess plus per-project Docker containers; **VM / microVM orchestration is in the spec but out of scope for the first build** — named here so the seam exists from the start, because retrofitting strong isolation after the engine has assumed a shared process is the expensive path (→ ch. 12). The same rule the host enforces everywhere applies: the workshop's reach (which paths, which network egress, how much compute) is declared in the constitution and brokered, not granted by the resident to herself. And the heavy work itself — the multi-step coding and research grind — is run by an **embedded, swappable open-source coding harness** (Pi or OpenCode) wrapped behind a `TaskHarness` contract, *not* bespoke agent-loop code: the agent loop is a 2026 commodity, so YuriOS orchestrates one rather than re-implementing it (→ ch. 17, "the heavy hands"; D-021). The harness is a tool she dispatches into the sandbox and never the brain that runs her — the tick loop decides *whether and when*, the harness only the *how*.

**The workshop feeds the mind through one gate.** Two crossings turn work into self: research she downloads is *ingested* into the `knowledge/` store (it becomes something she owns and can cite, not a file rotting in a temp dir), and a script she writes, runs, and validates can be *promoted* into procedural memory as a durable skill (the Voyager move, → ch. 02 §4). Both crossings — workshop → Vault — run through the same git-committed, risk-gated flow as any self-edit (below). The principle is clean: **she works freely in the shop; moving a work-product into her mind is the reviewed step.** And everything in the workshop is still on disk and still surfaced in the dashboard — what projects are in flight, what she's running, what she pulled — so autonomy stays observable even though the work itself is not version-controlled the way the mind is.

## The cognitive state, as data structures

The Vault is not an undifferentiated pile of text. It holds **distinct kinds of state with distinct update rules** — the lesson BDI (→ ch. 02 §1) and CoALA (→ ch. 02 §4) both teach and naive single-scratchpad agents ignore. Seven surfaces matter:

### SOUL: constitution vs persona

The character's identity is split into two surfaces with opposite mutability, and this split is the keystone of the whole safety story (D-002):

- **Constitution** (`CONSTITUTION.md`) — *immutable, signed.* The invariants: the fiduciary duty, the hard limits on capability and egress, the safety rails, the things that make her *her*. The engine **cannot** edit this file; the host refuses writes to it. (The Ouroboros lesson: if the constraints are themselves editable by the thing they constrain, they are not constraints.)
- **Persona** (`PERSONA.md`) — *editable.* Voice, manner, appearance, inner life, values-in-practice, learned habits, and the growth/reveal tiers; her preferences live here too, in frontmatter and prose, rather than in a separate file. The engine *may* propose changes here, through the gated flow below.

Around these sit the rest of the editable identity files — `SCENARIO.md` (the situation and the *return* greetings), `EXAMPLES.md` (demonstrated voice), `WORLD.md` (the lorebook), `NOTES.md` (creator notes) — and the `soul.yaml` manifest that declares how they all flatten into a portable character card. This split-by-mutability and this exact file set *are* the shipped `yuri-soul` reference implementation (→ ch. 07, the V3 `.PNG`; ch. 33, Build #3; D-002, D-003): the SOUL is the working home the runtime reads on every wake, and the card is the export you hand to someone else. A fresh card starts the relationship at zero — the runtime-only `MEMORY.md` and `USER.md` are part of the soul but never baked in.

One more file has a lifecycle of its own: `BOOTSTRAP.md`, the **consumed-once** first session (→ ch. 28, the first chapter). It's author-shipped like the persona, but loaded *only while it exists* — it carries the first-ever cold open and a scripted getting-to-know-you journey (each beat pinned to a `USER.md`/`MEMORY.md` slot). On first run the engine works it into the opening conversation, then **retires** it — `git mv soul/BOOTSTRAP.md soul/onboarded/BOOTSTRAP.done.md`, committed, so the git history is the record rather than a stray `.bak`. File-presence *is* the "has she been introduced yet?" flag, which is exactly the kind of state the git-backed vault stores as a file rather than a hidden bit. Only its cold open is baked into an exported card (as the card's `first_mes`); the journey and the retirement never leave the box. This is why `SCENARIO.md` above holds only the *return* greetings — the first-ever meeting lives in the bootstrap, the coming-home lives in the scenario.

### Memory tiers

The SOUL ships a single flat `MEMORY.md` (empty on a fresh card); at runtime the autonomy engine elaborates it into four tiers plus a consolidation process, covered in full in ch. 15 and summarised here only as it sits in the architecture:

- **Working** — small, in-context, current scope (held by the engine, not a persisted file).
- **Episodic** (`memory/episodic/`) — append-only log of events *and her own autonomous acts*. This is simultaneously the audit trail and the "what I did while you slept" product surface; it is written proactively, every tick.
- **Semantic** (`memory/semantic/`) — consolidated, embedded, durable facts.
- **Procedural** (`memory/procedural/`) — a self-authored skill library, **one folder per skill**. Each skill is a self-contained directory: a `SKILL.md` manifest (what it does, when to use it, its interface) beside the versioned, tested code it describes, plus any assets it needs. The folder is the unit — the same "the unit is a directory you can copy" bet the whole Vault makes — so a skill is portable (share one by handing over its folder) and drop-in compatible with the wider skill ecosystem (Agent Skills, OpenClaw), rather than a loose `skill.md` linked-by-convention to a sibling script. This is the Voyager lineage (→ ch. 02 §4), packaged the way 2026 skill systems actually package: she can acquire and keep new capabilities, not just recall facts.

The promotion of episodic → semantic happens in the **DREAM** activity state (→ ch. 18, ch. 15): overnight consolidation, the thing that makes her wake up *changed by yesterday* rather than merely holding a longer log.

### The memory contract

The four tiers above describe the *data*; this is the *interface* over them — the narrow contract the engine sees so that the backend underneath stays swappable (→ ch. 12; the "replace the file-Vault with a database and the loop never knows" promise earlier in this chapter). Define it first, before Build #5 (→ ch. 35), because the seam is cheap to specify now and expensive to retrofit once a concrete store has leaked its shape into the loop. Language-neutral, the engine depends only on this:

```
MemoryStore                       # interface; the backend (files · pgvector · graph) is the implementation

  # WRITE — hand over raw material; the store decides what is worth keeping
  remember(record) -> WriteResult
      # extract → embed → store. Low-confidence or externally-sourced facts land in
      # QUARANTINE, not durable semantic memory, until a second turn corroborates
      # them — promotion, not capture, is the trust boundary (→ ch. 15).

  # READ — blended ranking (similarity · recency · salience, minus an over-recency
  #        penalty), not raw similarity; returns nothing when nothing clears the
  #        retrieval threshold
  recall(query, k) -> list[Memory]          # ranked; may be empty by design

  # MAINTENANCE — the DREAM pass calls this; never on the hot path
  consolidate() -> ConsolidationReport
      # dedupe, promote episodic→semantic, decay/archive cold low-salience entries,
      # reconcile conflicts (newer supersedes older — supersede, don't delete)

  # TRUST — "forget that" has to actually work
  forget(selector) -> int                   # count removed; for facts, supersede-not-delete

  # OBSERVABILITY — the dashboard reads memory *through* this, never around it
  inspect(selector) -> list[Memory]         # what she knows and why: source_turn, confidence, last_recalled_at
```

Three things make this a real contract rather than a wishlist of method names:

- **It travels as a bundle.** A backend swap moves the store *and* its extraction prompts, its ranking weights, and its `consolidate()` policy together — they are one replaceable unit, not four (→ ch. 15, the pipeline). The partner model, affective state, and goal store are *sibling* Vault surfaces behind their own parallel contracts, not part of `MemoryStore`.
- **Its tests are part of the interface.** Any implementation must clear the ch. 15 eval battery — recall accuracy *and* false-memory rate — in CI before it ships. The contract is the signatures plus that battery; a backend that passes the types and fails the honesty probe does not satisfy it.
- **`inspect()` is load-bearing, and it is what keeps swaps honest.** The dashboard and the partner's "what does she know about me?" are answered *through* `inspect()`, which is why the file-Vault implementation gets it almost free (`cat`, `git diff`). A hosted store (Mem0, Letta) can satisfy every signature here and still break the project's thesis, because it cannot answer `inspect()` ownably — so the intended swaps stay *local* (files → local pgvector → local graph), and a cloud memory service is a clean swap that quietly forfeits the moat (→ ch. 15 on the economics; ch. 05 on sovereignty). Which backend a given card uses is declared in its `extensions.yurios` block (D-008).

### The knowledge layer (RAG) and its contract

Memory is the *state* layer — what's true about you and this relationship. Knowledge is the *world* layer — what's true about the canon, the docs she's been given, the sources she's read (→ ch. 16, which will not let the two be conflated). For a reactive companion the knowledge layer is optional polish; for an agentic waifu who reads, researches, and keeps her own reference shelf it is first-class infrastructure (D-019). It lives in `knowledge/`, a sibling to `memory/`, behind its own contract — pointedly *not* folded into `MemoryStore`, because the one rule ch. 16 holds is that knowledge and state are different stores with different write paths:

```
KnowledgeStore                    # sibling to MemoryStore; same swappable-backend discipline

  # INGEST — a doc or a fetched URL becomes retrievable chunks
  ingest(source) -> IngestResult
      # chunk → contextualize (a 50–100-tok situating blurb, → ch. 16) → embed → hybrid-index.
      # source = a dropped file (.md/.pdf/.txt) or something the network effector fetched.

  # SEARCH — hybrid retrieve + rerank; every chunk carries its provenance
  search(query, k) -> list[Chunk]           # ranked; each Chunk cites its source doc + span

  # AUTHOR — she compiles/updates a wiki page from what she's read
  author(page) -> WriteResult               # DREAM-driven; routed through the gated self-edit flow

  # TRUST + OBSERVABILITY — same shape as memory
  forget(selector) -> int                   # drop a doc and its chunks
  inspect(selector) -> list[Chunk]          # what's on the shelf, and where each chunk came from
```

The boundary that keeps the two from collapsing into each other: **knowledge is citable to a *document*; memory is citable to a *conversation turn*.** The book you hand her is knowledge; "you told me you play bass" is memory; her self-authored wiki is knowledge she *wrote* — still citable (to her page and its sources), still not relationship state. Two seams wire it into the rest of the architecture. First, research she pulls off the network (→ broker, below) is *ingested* here rather than dumped into a prompt — the intake path is the workshop's `downloads/`, the durable home is `knowledge/`. Second, the page-authoring — compiling a wiki out of what she read — is exactly the kind of consolidation the **DREAM** pass does for memory (→ ch. 18), and it lands through the gated self-edit flow, because a durable reference doc she wrote should be as diffable and revertible as anything else in the mind. Groundedness is load-bearing here in a way it isn't for chit-chat: when she cites her own shelf to justify a self-improvement, `inspect()` and per-chunk provenance are what let you audit *"she changed X because the book said Y"* (→ ch. 16 on evaluating retrieval).

### The world model (situation model)

Memory is the *past* and knowledge is the *world's facts*; neither is the *present*. The world model is her live, structured picture of the situation she is in **right now** — the entities present and their current states, the active threads, the time and social context, and her expectations of what comes next. It is the **B in BDI** (→ ch. 02 §1) given a home: the surface SENSE writes to and APPRAISE/DECIDE reason over, so the loop sees a *situation* and not a stream of unrelated signals (→ ch. 18, "The world model"). It lives in `world/`, sibling to `memory/` and `knowledge/`, behind its own contract — and pointedly distinct from both, by the same boundary discipline that keeps memory and knowledge apart:

- **knowledge** is timeless and cites a *document*;
- **memory** is past and cites a *conversation turn*;
- **the world model** is present-tense and cites a *live, time-stamped belief* about the situation now.

The fitting implementation is a **temporal knowledge graph** — entities and relations carrying a time dimension (valid-time + system-time), so "what was true *when*" is a first-class query rather than an inference over a pile of episodes (the Zep/Graphiti pattern, → ch. 02 §4.8; ch. 15). Keep it **local and inspectable** for the same reason memory stays local — the moat is in `inspect()` (→ above). Two layers: a durable `graph/`, and a small **situation snapshot** (`situation.md`, the Grounded-Situation-Model "stage") assembled each tick and injected into the prompt as "here is the state of things now." Build #5 can ship with *just the snapshot* — assembled from working memory + the partner model + a `recall()` — and graduate to the graph when multi-hop / temporal queries actually bite (→ ch. 35).

```
WorldModelStore                   # sibling to MemoryStore/KnowledgeStore; same local, swappable discipline

  # OBSERVE — fold a SENSE signal (text · fused vision/audio) into the situation
  observe(signal) -> UpdateResult
      # extract entities/relations/state-deltas, write as bi-temporal, time-stamped
      # BELIEFS (not facts); perceived/low-confidence state stays QUARANTINED (→ ch. 15)

  # SITUATION — the live "stage" the prompt is built from
  situation(scope) -> Situation            # present entities, states, active threads, time/context

  # QUERY — point-in-time + relational: "what was true when"
  query(q, *, at=now) -> list[Fact]        # bi-temporal; the temporal-KG query

  # PREDICT — roll out expectations (LLM-as-world-model); store as checkable beliefs
  expect(situation) -> list[Expectation]   # a later observe() scores surprise = prediction-error

  # TRUST + OBSERVABILITY — same shape as memory and knowledge
  forget(selector) -> int
  inspect(selector) -> list[Fact]          # what she believes is the case, and since when
```

Two properties make it load-bearing for *this* project. **Surprise is salience.** When `observe()` contradicts a stored `expect()`, the prediction-error is a first-rate signal for the APPRAISE pass — often the very thing worth a tick or a gentle word (→ ch. 18, the salience model). **Belief-tracking beats state-tracking.** The companion-specific upgrade is to annotate facts with *whose* belief they are, and to model where *your* picture of the situation diverges from hers — theory-of-mind / common ground (→ ch. 02 §4.8). That divergence is what turns "she remembers facts about me" into "she understands my situation," and it is why the partner model lives *inside* the world model rather than beside it.

### Partner model — the structure behind "she actually knows you"

The most under-built data structure in commercial companions, and the one that most directly produces the felt sense of being known: an explicit, evolving `USER.md` — her theory of mind about *you* (the partner model). It is the **most important region of the world model above** — you are the central entity in her situation — pulled out into its own file because it is the one region worth versioning by hand and reading on every wake. Your state, your preferences, the arc of your relationship, the things you've told her not to forget. Two design notes make it load-bearing rather than decorative:

1. It is **a file the partner can read.** Transparency is the feature: this is Paradot's "learned facts about you" UI done honestly, where the model of you is not a hidden engagement asset but a document you can open, correct, and delete (→ ch. 05, ch. 28).
2. It is **distinct from semantic memory.** Semantic memory is what she knows; the partner model is what she believes *about you specifically* and how she should act on it. Collapsing the two is why generic chatbots "remember" facts but still feel like they don't know you.

### Affective state

A small, persistent `emotional_state.json` — valence, arousal, and a few named drives (curiosity, bonding, helpfulness) — that *modulates prompt assembly*: tone, risk tolerance, what gets attention this tick. It is cheap to implement and has an outsized effect on aliveness, because it gives behaviour a slow-moving mood rather than resetting her to neutral every turn. It is **state, not performance**: the file is the cause of the tone, not a label describing it after the fact. Which means it needs an **update rule**, or it degenerates into exactly that label: events apply bounded deltas (REFLECT proposes them like any other write); between events, every value decays toward a per-persona baseline with a time constant measured in hours (applied each tick, on the injected clock); DREAM re-centres the baseline slowly, across weeks. The split this yields is worth saying aloud — **mood is state, temperament is the SOUL**: the baseline and its time constants ship in `PERSONA.md` as *who she is*, the JSON is only *how she is right now*, and both are numbers you can open.

### Goals & intentions

A persistent `goals.md` of projects, todos, and intentions with priority, state, and deadlines. This is what gives the background loop *direction* — what keeps ACT from being random busywork. The DECIDE phase of the tick loop draws its candidate intention from here (→ ch. 18). Without it, an always-on agent is a screensaver; with it, she is pursuing something while you're away. Where goals *enter* the store is a designed thing, not an assumption — four sources (the user, her own extracted promises, curiosity, DREAM maintenance), each goal carrying its provenance, with self-created goals passing the same risk gate as self-edits (→ ch. 18, "Where goals come from").

## The context assembler: how the surfaces become her

Every surface above exists to be *composed into a prompt*, and the thing that does the composing is the most load-bearing code in the runtime — it runs on every model call and decides what she *is* this turn — so it gets a name and a contract rather than living as the phrase "prompt assembly." The **context assembler** takes the SOUL, the situation snapshot, the partner model, the recalled memories, the knowledge chunks, the affective state, and the recent turns, and produces one composition, under explicit policy:

```
ContextAssembler                  # deterministic composition of Vault surfaces → one prompt

  assemble(intent, budget) -> Context
      # SOUL + situation() + USER.md + recall() + search() + affect + recent turns,
      # under an explicit PER-SURFACE TOKEN BUDGET — when recall, knowledge, and
      # situation all want the window, who loses is a declared policy, not an
      # accident of assembly order; identity is never crowded out by retrieval.
      # Deterministic given (vault state, template_version): same state, same prompt.

  template_version -> str          # pinned and logged with every turn (→ ch. 30/31,
                                    #   the corpus-log schema field this names)
```

Three things make it contract-worthy. **The token budget is a real decision currently made nowhere else:** every store can only offer candidates; something must decide how much of the finite window each surface gets, and if that decision isn't declared policy it becomes an accident of code order — the quiet way retrieval crowds out identity and she stops sounding like herself on busy days. **Determinism is what makes evaluation possible:** golden transcripts (→ ch. 23) and the corpus log (→ ch. 30/31) are reproducible because `template_version` names the exact composition that produced a turn — the field was already in the corpus schema; this is the module it points at. And **ENGAGED and autonomy prompts are two profiles of one assembler, not two assemblers** — the fast conversational path and the slow deliberate tick differ in budget and emphasis, never in which mind gets composed (→ ch. 18, "One loop").

## The host services

The host exposes six services to every resident engine. Each is a narrow contract; the engine sees an interface, not an implementation.

### Card loader (`.PNG → spec`)

Reads the V3 character card, extracts the embedded JSON (and any `extensions.yurios` block carrying autonomy/memory config — D-003, D-008), and instantiates an engine with its seed SOUL and config. This is the load path that connects distribution (→ ch. 07, ch. 33) to runtime: the card *boots the brain*. On export, the updated editable surfaces can be re-embedded back into a `.PNG` (see the self-edit flow below).

The loader is also **where "signed constitution" stops being an adjective and becomes a check.** The `CONSTITUTION.md` carried in the card is signed by its author's key; the loader *verifies that signature at load* and records the signing identity in the audit log. A card whose constitution fails verification — tampered in transit, or re-embedded by a runtime that edited what it must not — boots in a quarantined, capability-denied state (or refuses to boot, per host policy) rather than running with a constitution nobody vouched for. This is what makes the immutability claim (§"SOUL", above) enforceable rather than aspirational: the host refuses *writes* to the constitution at runtime, and the loader refuses to *trust* one that was changed out of band.

Two more halves of trust the signature alone doesn't carry. *Whose key?* A signature proves the constitution matches its author's key — not that the author deserves your machine. The model is trust-on-first-use with pinning: the first load records the signing identity, any later key change is flagged rather than silently accepted, and the Lab publishes its own signing key so the canonical cards verify against a known identity instead of a stranger's. And *the grants need a consent moment.* The constitution's capability grants were declared by whoever wrote the card, so default-deny (→ broker, below) only protects against the *ungranted* — the granted list itself came from a stranger. On first boot the loader renders that list as a **consent sheet** — "this character asks for: network egress, workshop execution, …" (`Broker.grants()` is the render source) — and the user accepts or trims it before the first tick. A downloaded card is a guest arriving with a list of rooms she'd like keys to; the sheet is you reading the list at the door.

### Signal bus — the inbound world

Everything that happens *to* the system arrives here: user messages from any frontend, timers and scheduled wake-ups, filesystem and OS events, body events, and the completions of long-running work (→ ch. 18, "ACT starts work; it never awaits it"). Each lands as a typed, timestamped signal on a **durable per-engine queue**, and SENSE reads signals *only* from here — no frontend ever pokes an engine directly. The implementation is deliberately boring and on-brand: an append-only JSONL inbox per engine, consumed by offset; no message broker, no daemon.

Durability is the point, three times over. The tick trace records what was *processed*; the bus records what *arrived* — so a message that lands mid-crash is delivered after recovery instead of silently lost, which for a companion is the difference between a bug and a broken promise. Async completions re-enter the loop as ordinary signals instead of callbacks threaded through the tick. And a recorded week of real signals, replayed under a virtual clock, *is* the engine's regression suite (→ ch. 23, testing an always-on mind).

### Model router — local-first, privacy-aware

Not a provider abstraction but a **policy router**. Its rules are the economic and ethical spine of always-on (→ ch. 18 on cost; ch. 21 on serving):

- The **local model is the default**, and the *only* tier permitted for the every-tick APPRAISE pass. A frontier model on every heartbeat cooks the GPU and the budget.
- **Escalation to a remote model** is allowed only for genuinely hard deliberate reasoning inside ACT, and only when the **privacy boundary** permits — the router classifies and redacts what may leave the machine *before* any remote call. What happens on the user's box stays on the user's box unless the user's policy says otherwise.
- Routing decisions honour the card's declared `model_routing` policy and the global budget governor.
- When more than one resident is awake, the router is also the **point of contention for the one GPU**: model calls across all engines serialise through it, so two waking minds queue rather than thrash the device. The scheduling discipline for that shared inference resource is ch. 21's subject (→ ch. 21, serving); here it is enough that the seam exists and that no engine talks to the model except through this router.

### Capability / permission broker

The engine touches the world *only* through the host's broker, which enforces the limits declared in the (immutable) constitution. Five effector classes, in rough ascending order of blast radius (filesystem appears as two scopes because its two homes have opposite trust models, and code execution and OS control are the dangerous tail):

- **Filesystem — the Vault** — her own mind: read/write to `soul/`, `memory/`, `knowledge/`, `goals.md`, but identity writes route through the gated self-edit flow and `CONSTITUTION.md` is read-only even to her.
- **Filesystem — the Workshop** — her scoped, allow-listed project tree (the workspace above), where she writes and runs code freely; broad latitude *inside* the sandbox, firewalled from the Vault and the host.
- **Network / browser** — fetch and browse under an egress policy; this is also the *research intake* path, and what it pulls is ingested into the knowledge store (above), not left loose in the prompt.
- **Code execution / sandbox** — run what she writes, in isolation tiered to the risk: subprocess → per-project **container** (Docker, the near-term target) → **microVM / full VM** (the strong-isolation target for untrusted or heavy work; in-spec, out of scope for the first build). Untrusted input — scraped sites, downloaded repos — runs at the strongest tier available. The heavy multi-step work this effector carries is driven by an embedded, swappable OSS coding harness (Pi/OpenCode), not bespoke loop code (→ ch. 17, D-021).
- **OS control** — sandboxed, with dry-run modes for anything destructive. (Linux and Windows are genuinely different here; plan a capability abstraction rather than assuming one.)
- **Skills / tools (MCP)** — a registry usable *autonomously*, not only inside a chat turn (→ ch. 17).

All five sit behind one narrow contract — and because the broker is the most safety-relevant surface in the system, it earns a contract as explicit as memory's or knowledge's. Every effector call crosses the same four-step gate, in this order, no exceptions:

```
Broker                            # the host's gate on the world; the engine holds no capability directly

  request(effector, op, args, *, character) -> EffectorResult
      # 1. AUTHORIZE  — is (effector, op) within this character's CONSTITUTION grant?
      #                 deny by default; an ungranted capability is a refusal, not an error
      # 2. CHARGE     — reserve the op's *estimated* cost against the budget governor;
      #                 if even the estimate doesn't fit → refuse (felt as REGULATE
      #                 pressure, → ch. 18)
      # 3. EXECUTE    — run it at the isolation tier the op's risk demands
      #                 (subprocess · container · microVM), untrusted input → strongest tier
      # 4. SETTLE     — reconcile the actual cost and release the unused reservation;
      #                 model calls and workshop tasks have no knowable cost up front,
      #                 and a governor fed estimates it never reconciles is being lied to
      # 5. AUDIT      — append the call, its decision, estimated and actual cost, and
      #                 result, keyed by tick_id so the dashboard can replay "why did she do that?"
      # a denial short-circuits at step 1 or 2 and is logged like any other call

  grants(character) -> list[Grant]  # OBSERVABILITY — exactly what she may touch, read straight from
                                     #                  the constitution; the dashboard renders this,
                                     #                  and so does the first-boot consent sheet (→ card loader)
```

Two properties make it load-bearing. **Default-deny:** a capability the constitution does not name is refused, so widening her reach means changing the constitution — which the engine cannot do. She can only *request* it (a high-risk item that queues for your approval, → below); granting it is you re-signing the constitution, never something the engine can back into. **The gate is unskippable because the engine holds no capability directly** — it has a handle to the broker, not to the filesystem or the network, which is the runtime expression of the host/engine process split (→ §"Two tiers", above): you cannot bypass a guard you have to call through to reach anything. Autonomous code execution and OS access are real blast radius; sandbox, dry-run, tiered isolation, and capability-gating are not optional polish, they are the price of shipping to anyone but yourself.

### Budget governor

Per-hour caps on tokens, compute, and wall-power, enforced across *all* residents. It prevents the runaway-loop failure that made Auto-GPT a cautionary tale (→ ch. 02 §1) and it keeps the "just works on someone's computer" promise true. Critically, it **feeds back into the loop's REGULATE phase** (→ ch. 18): as the engine approaches a cap, cadence slows and the activity state drops toward DORMANT. Cost control is not a monitor bolted on the side; it is wired into the heartbeat.

### Audit log & inner-life dashboard

The dashboard surfaces, per character: the journal, recent decisions, file diffs, goals in flight, pending self-edits awaiting approval, and budget/state. It is simultaneously an engineering necessity (you cannot debug an always-on agent you cannot observe) and **the product itself** — the "she was alive while you slept" surface that converts autonomy from creepy to an inner life you get to witness (→ ch. 18, ch. 28). Because the mind is files, most of the dashboard is a renderer over the Vault and `git log`; observability is close to free, which is the file-centric bet paying off again.

### Crash recovery: waking up where she left off

An always-on agent will be killed mid-tick — by a crash, a reboot, a pulled power cord — and the host is what makes that survivable rather than corrupting. The discipline is the same file-centric bet paying off a third time: **the journal and tick trace persist to disk every tick, so they double as the recovery substrate** (→ ch. 18, the trace). On restart the host re-instantiates the engine and the engine *rehydrates* — it reloads its goals (`goals.md`), any open intentions from the last committed trace, and whatever arrived unprocessed on the signal bus (→ above), rather than waking amnesiac and re-deciding from a blank slate. Two rules keep a torn write from poisoning the mind: Vault state files are written atomically (write-temp-then-rename), and durable changes to the mind land as **git commits**, which are all-or-nothing — a crash between two writes leaves the last *commit* intact, never a half-applied identity edit. The Workshop gets no such guarantee and needs none; a half-finished build in the sandbox is exactly the kind of mistake you tear down and redo (→ above). Recovery is therefore a host responsibility — supervise the process, restart it, hand it back its disk — and the engine's only job on wake is to read what it already wrote.

And the machine doesn't only crash — it *sleeps*. An OS suspend, a closed laptop lid, an overnight shutdown are daily events on the hardware this actually runs on, and they need a third discipline: **clock-gap reconciliation**. On wake the engine computes the missed window from its injected clock and runs *one catch-up appraisal* over the whole gap — what fired, what expired, what still matters now — rather than either failure mode: firing every stale timer in sequence (thirty-seven queued "good morning"s), or pretending the gap never happened. The honesty rule extends here too: she is allowed to know and say that the machine slept — which is the engine-side half of the frontend rule that presents an unreachable brain as *she's resting*, never as a faked presence (→ ch. 27).

## Self-modification: the gated edit flow

A companion that *grows* must be able to change her own editable surfaces — but uncontrolled self-modification is how you get drift, jailbreaks, and a character who is no longer herself. The architecture resolves the tension with a single mechanism: **every self-edit is a git-committed, risk-gated diff against an editable file, and the constitution is never in scope.**

```
REFLECT proposes a diff to an editable surface (persona, prefs, partner_model, a skill)
   → write to the Vault, git-commit (versioned, diffable, reversible)
   → risk-gate:  low risk  (a note, a preference)        → auto-applied
                 high risk (persona, a new skill,         → queued for human
                            any capability request)          approval in the dashboard
   → optionally, on export: re-embed updated surfaces into the .PNG card
```

Git-backing every self-edit is the one decision that makes a self-modifying agent shippable: any drift is visible in the history and revertible with one command. The risk gate is the second: low-stakes learning (she notes that you dislike mornings) applies silently; high-stakes change (a rewrite of her own persona, a new executable skill, a request for broader filesystem access) waits for you. The constitution sits *outside* this flow entirely — it is the floor the self-edit mechanism stands on, not a surface it can touch.

## Metacognition and the System 1 / System 2 split

The cheap-APPRAISE-versus-deliberate-ACT rule of ch. 18 is, named properly, a **System 1 / System 2 split**: a fast path of embeddings and heuristics that runs every tick, and a slow path of frontier-model reasoning invoked only when the fast path flags something worth the spend. The architecture adds a metacognitive surface on top: confidence estimation, loop detection (am I doing the same thing repeatedly?), and consistency checks between the persona she professes and the behaviour she's producing. REFLECT does not merely journal what happened; it *judges* it and stores the judgement (the Reflexion pattern, → ch. 02 §4), so the reflections buffer becomes a source of learning rather than a diary she never rereads.

## How it maps to the five-layer stack

This whole architecture is the ch. 12 stack, assembled. The mapping is worth making explicit, because it shows the chapter is not a new model but the old one made concrete:

| Stack layer (→ ch. 12) | Components here |
|---|---|
| **Substrate** | Model router; the local + remote model tiers (→ ch. 13, ch. 21) |
| **Behavior** | SOUL (constitution + persona); the card loader; prompt templates |
| **Memory** | The Vault's memory tiers; the world model (situation, → ch. 18); DREAM consolidation; partner model (→ ch. 15) |
| **Knowledge & tools** | The knowledge store (RAG, → ch. 16); the workshop + code-execution sandbox; effector/capability broker; MCP skill registry; procedural memory (→ ch. 16, ch. 17) |
| **Orchestration** | The autonomy engine: tick loop, scheduler, salience filter, budget-fed REGULATE (→ ch. 18) |
| **Cross-cutting** | Audit log & dashboard; budget governor; the git-backed self-edit flow |

The interfaces between these are the leverage (→ ch. 12): swap the local model under the router's contract and nothing above notices; replace the file-Vault with a database under the memory contract and the loop never knows.

## One engine, many characters: YuriOS beyond the companion

Everything above describes a companion, but almost none of it is *about* companionship. Strip the fiduciary framing and what remains is a general shape: a portable character definition (the card) that boots a *situated, autonomous mind* — one that perceives through senses, acts through gated effectors, and keeps its state in swappable stores. That object is not waifu-specific. It is, near enough, what a **game** wants from an AI character. The ambition worth naming out loud: **YuriOS aims to be to a game's *characters* what a rendering engine is to its *visuals*** — the general substrate you configure per-title, not rebuild per-title. The companion this book builds is one application of that engine; a game NPC is another. This is not a detour from the thesis; it is the reason the whole chapter insisted on *contracts* instead of a monolith, and it is why the engine is Apache-2.0 with no CLA (→ ch. 39, ch. 41; D-015) — the licence was chosen so a game studio could embed the brain, not just read about it.

It is worth being honest that this category already exists and is no longer speculative. LLM-driven NPCs have crossed from tech demo into shipping product — NVIDIA's ACE stack shipped in KRAFTON's *inZOI* and is in testing as *PUBG* AI teammates; Ubisoft has trialled its NEO NPC work in production; and a middleware layer has consolidated around **Convai** (Unity/Unreal/web SDKs bundling speech, memory, perception, and in-world *action-taking*) and **Inworld** (pivoted from a character engine to real-time AI infrastructure). The whole category is, today, **cloud-hosted and engine-plugin-shaped**, and it is still visibly latency-limited — NPC dialogue "feels laggy" next to scripted lines. That shape is the opening: the thing YuriOS offers that the middleware structurally cannot is a **local, ownable, moddable** brain — the same properties that matter for a companion (→ ch. 03) turn out to matter for a modder who wants a character that runs on the player's machine and can be inspected, edited, and shipped inside a game they own.

What transfers unchanged is most of the architecture:

- **The card is already an engine-agnostic character asset** (→ ch. 07, ch. 33; D-003). A `.PNG` SOUL is a portable character a title imports the way it imports a mesh or an animation set — identity, voice, and behaviour in one signed file.
- **The four store contracts are the engine core.** `MemoryStore`, `KnowledgeStore`, `WorldModelStore`, and the `Broker` are exactly the narrow seams a game binds to; from the engine's side a game is *another frontend plus another effector set*, not a fork of the mind. And because engine and host are already separate processes talking over IPC (→ §"Two tiers"), these contracts are **wire-level by construction — a protocol, not a Python import** (`yurios-protocol/1`). That is the LSP move: language servers existed for decades, but the *protocol* is what made every editor speak to every language — publish this one and a C++ game engine, a TypeScript desktop shell, and the reference Python host are all just clients of the same mind.
- **The world model is the part that makes an NPC *situated* rather than a chatbot in a box** (→ §"The world model"). A game already owns authoritative world state — entities, positions, events — so feeding those into `observe()` and letting the character reason over `situation()` *is* the NPC problem, and it is precisely the surface that drop-in dialogue middleware tends to lack. This is arguably where YuriOS is best-positioned, not worst.
- **The body subsystems are already effectors behind the broker** (→ §"Capability / permission broker"). In a game, the engine's own animation and rendering systems become the avatar effector, and in-world actions ("walk to the forge, hand over the sword") become a new effector class — the "action-taking" the NPC middleware sells — with the broker's authorize→charge→execute→audit gate intact around it.
- **Frontends are thin views** (→ §"YuriOS at a glance"). Unity, Unreal, or Godot is simply another host binding onto the same mind.

What does *not* transfer cleanly is the set of defaults tuned for a single, resident companion — and the honest framing is that a game target is a different **profile over the same contracts, not a rewrite**:

- **Cadence.** The git-backed file-Vault earns its keep because the tick loop runs at *human cadence* (→ §"The brain is a folder"); a scene with many NPCs at frame rate is a different regime entirely. The *contract* (`MemoryStore`, `WorldModelStore`) survives; the file *layout* does not — a game profile swaps to a pooled, in-memory or database backend under the same interface.
- **Lifecycle.** One always-on supervised process per character is right for a resident you live with and wrong for a crowd of villagers who should be event-driven, pooled, and awake only near the player. The always-on autonomy loop — the companion's whole point — is the first thing a game profile turns off.
- **The fiduciary machinery is companion-shaped and mostly drops away.** The immutable constitution, the interrupt-threshold attention policy, the always-on cost/thermal budgeting — an NPC keeps the broker and the stores and needs almost none of the rest.

So the claim is deliberately bounded. YuriOS is not *today* a game engine, and pretending the always-on, one-resident runtime drops unchanged into a title with fifty NPCs would be the kind of overclaim this book tries to avoid. But the seams are in the right places: the card, the store contracts, the broker, and above all the world model are general-purpose, and the companion is one profile built on them. How far the mind really generalises beyond companionship is an open question worth its own entry (→ ch. 45); the rendering and host targets a game brings are ch. 29's subject; and the market adjacency — a bigger, adjacent buyer for the same engine — is picked up in ch. 04.

## You are not inventing this

It is worth saying plainly, because the architecture can look like a lot: almost none of it is novel, and that is a strength. The tick loop is the **BDI interpreter cycle** (→ ch. 02 §1). The overall decomposition — memory, retrieval, reflection, planning as distinct modules over a language-model core — is **CoALA** (Cognitive Architectures for Language Agents, → ch. 02 §4). The memory-stream-plus-reflection pattern is **Generative Agents**; the self-authored, verified skill library is **Voyager**; the stored verbal self-critique is **Reflexion**; the overnight consolidation is the **Dreaming / hippocampal-replay** pattern the labs converged on (→ ch. 02 §4); the world model is the **Grounded Situation Model** / BDI belief-base, now backed by a temporal knowledge graph (→ ch. 02 §4.8). You are re-implementing forty years of agent theory with a vastly better generator inside it. The original contribution is not any one module; it is the *opinionated integration* — and specifically the parts the research lineage lacked: activity states with cost/thermal budgets, the capability broker, the immutable-constitution-versus-editable-soul split, the interrupt-threshold attention policy, and the card as the distribution artifact. Those are the companion-specific, fiduciary-specific additions, and they are the moat.

## The three hard parts

If you build toward this, three components will consume most of the design risk; budget your attention accordingly (this is the same triage ch. 18 and ch. 35 give, named at the architecture level):

1. **The attention policy** (the salience/interrupt model of ch. 18). Starting a loop is easy; making it *good* — neither a chatterbox nor a ghost — is the hard part, and the difference between "magic" and "annoying slop" lives entirely here. Start with conservative interrupt thresholds and let the journal, not notifications, carry the value.
2. **Always-on cost and thermal control** (activity states + budget governor). This shapes the whole scheduler: a cheap-model tick, real sleep states, hard caps wired into REGULATE.
3. **Self-modification drift and autonomous OS access** (the self-edit flow + the broker). Git-backed reversibility, an immutable constitution, dry-runs, and capability gating are the price of shipping to anyone but yourself.

## This is the thesis, assembled

Chapter 18 made the case that genuine initiative needs a different runtime shape. This chapter is that shape, fully drawn: a mind that is a folder you own, a heartbeat that rests most of the time, a self that can grow but cannot rewrite its own constitution, and a building whose safety machinery holds the floor steady under the resident rather than guarding against her. Build #5 (→ ch. 35) is the smallest honest slice of it you can ship — and the rest of this chapter is the horizon that slice is walking toward.
