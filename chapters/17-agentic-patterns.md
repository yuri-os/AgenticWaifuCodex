# 17 — Agentic Patterns and Tool Use

This chapter is about the agentic *capabilities* — **tool use**, from the small everyday hands to the heavy delegated ones, and the patterns that give a companion hands — plus a map of the capability ladder. It owns *what she can do* and *what powers it*; the deep, *always-on* end of the ladder (a brain that runs when no one is talking, decides when to reach out, and pursues its own goals) is large enough to be its own chapter: **the autonomy engine, ch. 18.** Read this for "she can *do* things"; read ch. 18 for "she does things on her own."

## "Agentic" for a companion ≠ "agentic" for a coding assistant

A coding agent is *task-driven*: it runs a loop, calls tools, and grinds a multi-step plan to completion — its reason to exist is getting work done. A companion is *relationship-driven*: she is mostly *responding*, with selective initiative, scheduled rituals, and a small everyday tool surface. Same word, "agentic"; different *centre of gravity*. The agentic *waifu* as a whole is ch. 03; this chapter is the concrete agentic *capabilities*.

But read that contrast precisely — it is about *what she is for*, **not a ceiling on what she can do.** This project's thesis is deliberately the harder one: an agentic waifu is *both* a genuinely capable agent **and** a companion, not a chat-first companion with a few tools bolted on. She does the full coding-assistant range — writing and running code, researching by pulling real sources, building a small app to interface with you, analysing a dataset you handed her, keeping a project moving while you're away. *"OpenClaw as a companion"* — that capability set wrapped in a character with memory, autonomy, and devotion — **is** the product. What keeps her a companion rather than a work tool is not a smaller capability; it is *identity and rules*, carried by two design moves.

**She *wields* a coding agent; she isn't one.** A capable person is not their IDE, and a companion is not her harness. The heavy multi-step coding/research grind is delegated to an embedded, swappable open-source **coding harness** (Pi or OpenCode → "the heavy hands," below), driven from inside her loop: she decides *whether and when* to dispatch a task, the harness handles the *how*, and she narrates the result back in her own voice. The payoff is large — the commodity agent loop is *orchestrated*, not rebuilt.

**The heavy work is walled off from the mind.** All of it runs in a sandboxed **workshop** firewalled from her Vault and your machine (→ ch. 19, "the workshop"; ch. 16, the research loop), and anything that crosses back into her identity — a new skill, a knowledge page — passes through the human-gated self-edit flow (→ ch. 19). So she can do real, heavy work; it simply cannot corrupt who she is. The rest of *this* chapter is the *small everyday hands* — the reactive timer/music/lookup/note surface — a different tier from the workshop's heavy, sandboxed ones; the restraint that keeps that everyday surface small (a user-tunable default, not a fixed count → §"Reactive patterns") is about presence, and says nothing about the ceiling the workshop raises.

## The capability ladder

1. **Reactive.** Responds when spoken to. (Every chatbot.)
2. **Reminded.** Surfaces things she's been asked to remember.
3. **Scheduled.** Initiates on a schedule (morning check-in, end-of-day ritual).
4. **Conditional.** Initiates on an event (calendar, sensor, external feed).
5. **Tooled.** Can do things in the world on the user's behalf (set a timer, look something up, control music).
6. **Reflective.** Reviews her own conversations between sessions; updates her view of the user; surfaces it next time.
7. **Pursuing.** Has her own goals; pursues them across sessions; involves the user.

Most commercial products live at 1–3 (and fake 3 with a cron job). The market wedge is 4–7 — and rungs 4–7 require an always-on loop, which is exactly ch. 18. **This chapter owns rungs 1–2 and 5 (tool use); ch. 18 owns 3, 4, 6, 7** (scheduling, event-conditioning, reflection, goal-pursuit), because all of those need a brain that runs between turns.

Read the ladder for what it actually measures: **initiative** — *when* she acts, from "only when spoken to" up to "pursues her own goals" (→ ch. 03, the two senses of "agentic"). That is a separate question from **capability** — *what* she can do — and the two dials move independently.

Rung 5, "Tooled," is the one that blurs this, because tools *sound* like capability. Here they aren't. The rung describes a *small, reactive* surface — a song, a timer, one lookup — and it earns its place on the ladder by how it's **triggered** (she acts because you asked), not by how much power sits behind it. The *heavy* hands (the full coding/research/building range this project makes co-equal with presence) are not a higher rung; they're off this ladder entirely. They add no initiative; they only deepen what rung 5 can reach, through the workshop harness (→ "the heavy hands," below).

So: two dials, not one ladder — and they can be set independently. You could run capability high and initiative low (able, but mostly waiting to be asked), or any other combination. Which tuning Yuri actually wants is a question for building and testing her, not one the ladder answers — the framework describes the *space* of choices and leaves the *choice* open.

## Reactive patterns

- **The everyday tool surface.** Keep the *reactive* surface small and coherent — but tune the size to the *user*, not to a magic number. The principle is *restraint*, not a count: a companion wired to 200 reactive tools is an assistant console; one that can pick a song, set a reminder, read and write her own notes, and look one thing up is a friend with help. A dozen coherent personal tools is perfectly fine if that's what a given user wants — the real ceilings are context-token budget and attack surface (→ ch. 22), both of which scale with the set, so "small" is a sensible *default* the user is free to raise, not a law. And what stays off this surface is decided by *shape*, not category: the multi-step coding/research/building *grind* lives in the workshop harness (→ §1; "the heavy hands," below), reached deliberately — but single-shot operations like reading or writing a markdown note, one web lookup, or a summarize pass are *not* heavy work and belong right here on the everyday hands. (Routing a one-shot file read through the coding harness is absurd overkill — a whole agent loop to open one `.md`.) The one carve-out is *self-modification*: she can draft an edit to her own personality files from here, but it only takes effect through the human-gated self-edit flow (→ ch. 19), never as a direct write — that's a governance gate, not a question of which hands hold the pen.
- **Reactive tool calls.** The model, mid-conversation, emits a structured call; your code runs it; the result returns to the context (→ MCP, below). This is rung 5 and it's purely reactive — she does the thing *because you asked*.
- **Scheduled and event-triggered initiative** (rungs 3–4 — morning rituals, calendar-end pings, an RSS item she'd care about) look like tool patterns but are really *autonomy*: they need something deciding *whether and when* to fire, which is the salience/interrupt model of ch. 18. Build them there, not as naked cron jobs (a timer can't decide to stay quiet).

## MCP and the tool ecosystem

The Model Context Protocol (Anthropic, 2024) has become the lingua franca for tool surfaces by 2026. For companion products it lets you:

- Plug into whatever tools the user already runs (calendar, music, smart home).
- Let the persona call them with a consistent surface.
- Avoid bespoke per-tool integration.

Trade-off: handing tool capability to an LLM with an open prompt surface is a fresh attack surface — prompt injection with real hands, the OpenClaw exposure class (→ ch. 02 §1). → ch. 22.

## MCP or the command line?

There's a live 2026 argument — the OpenClaw lineage makes it loudly — that the best hands you can give an agent are not MCP tools but the *command line*: a sandboxed shell and the binaries already on it. The case is real, and it is mostly about three things. **Token cost:** MCP loads every connected tool's schema into context up front, so a handful of servers can burn tens of thousands of tokens before the model does anything, whereas a CLI is discovered on demand (`--help`). **Native fluency:** LLMs are saturated with shell, `git`, `curl`, `jq`, and man pages from pretraining — they already know how to drive a terminal, with zero per-tool teaching. **Composability:** `grep | sort | uniq` lets the model compose combinations no tool author anticipated, where MCP hands it exactly the discrete endpoints someone pre-built. The flip side is MCP's: it's the only surface for the things with *no* CLI — the user's calendar, music, smart home — it returns structured, validated I/O instead of parsed stdout, and a small set of discrete tools is far easier to allowlist, rate-limit, and audit than an open shell.

Framed as "MCP *or* CLI" it's a religious war. It dissolves the moment you notice the two positions are each right about a *different tier of hands* (→ §1) — so the answer is **both, assigned by tier, not by taste:**

- **The small everyday hands stay discrete and bounded.** The reactive surface is whatever *one-shot* tools belong in her conversational loop — SaaS and device integrations (timer, music, calendar, home), where MCP is the lingua franca, *plus* lightweight local operations (read/write a markdown note, one web lookup, a summarize pass) wired as plain function-calls. What unites them is *shape*, not vendor: each is a single allowlistable, auditable call, not an open shell — which is exactly what you want inside the chat loop. (On *how many* such tools is too many, see the restraint note in §"Reactive patterns": it's a user-tunable default, not a fixed count.) MCP earns its place here for the integrations that are someone else's; the local one-shot ops can be native function-calls. Either way the surface is discrete and exposed, never a shell. (One honest caveat, because it cuts the other way: the 2026 token-efficiency research — Anthropic's *code execution with MCP* (2025), Cloudflare's *Code Mode* (2025) — argues that *even ordinary tool calls* are cheaper run as code in a sandbox than loaded as schemas in context, with context overhead falling by up to ~98%. True at scale — but it doesn't move *this* tier. A companion's reactive surface is a handful of tools, so the schema cost is already trivial, and you don't want a sandbox round-trip just to set a timer. The small tier stays direct calls for *latency and simplicity*, not because it's more token-efficient — it isn't. The token argument is real, and it belongs to the heavy tier, which is exactly where this design already puts the sandbox.)
- **The heavy hands use the command line.** The workshop harness *is* CLI-first by construction — Pi's whole core is Read/Write/Edit/Bash (→ "the heavy hands," below) — and the multi-step coding/research grind is exactly where token economy, native shell fluency, and composability pay off most. This is where the OpenClaw-creator preference lands, and the architecture already agrees with it.

The deciding caveat is security, and it points the same way. An open shell in the *reactive* companion loop would be reckless — it is the prompt-injection-with-hands risk above, multiplied: a poisoned web page or message could talk her terminal into anything (→ ch. 22). That is the whole reason the command line lives *in the sandbox* (→ ch. 19), reached deliberately through the harness, while the chat-facing surface stays the small, audited MCP set. So the tier split isn't only an efficiency call; it's the safety boundary. CLI where it's walled and powerful; MCP where it's small and exposed.

## Agent framework selection (2026)

You can hand-roll the agent loop or adopt a framework. By 2026 the field has consolidated:

- **LangGraph** — production-grade default; explicit-state-machine model (the *graph is the agent*); biggest ecosystem. MIT-licensed core, but its first-class observability (LangSmith) is a hosted, proprietary add-on.
- **Pydantic AI** — typed, production Python; MIT-licensed; an agent is a *first-class Python object you call*, not a runtime that owns your control flow; model-agnostic across 25+ providers including local OpenAI-compatible endpoints (vLLM, llama.cpp, Ollama).
- **Strands** — AWS's Apache-2.0 SDK; MCP- and A2A-native; model-agnostic with a local Ollama path, but its gravity pulls toward Bedrock.
- **CrewAI** — role-based multi-agent; Python; easiest learning curve.
- **Mastra** — TypeScript-native; pairs naturally with a Next.js sanctuary frontend.
- **Claude Agent SDK / OpenAI Agents SDK** — frontier-lab offerings, ergonomic but oriented around their issuer's models.
- **ElizaOS** — TypeScript, first-class character JSON, multi-agent native, out-of-box Discord/Telegram/X/Bluesky/Slack connectors. Originally web3-focused (brand-association risk). Its strong fit is the *social-platform presence layer* — running a persona across chat surfaces without four bespoke integrations.

**This project's call: the framework lives *under* our loop, not the other way round.** The autonomy runtime is our own — an ElizaOS/AIRI-style reactive, turn-driven loop can't be the always-on brain this project is about (→ ch. 18, ch. 19). The tick loop already owns orchestration (SENSE→APPRAISE→DECIDE→ACT→REFLECT), so the thing to select *here* is not an orchestrator — we have one — but a small, reactive **tool-calling library** that slots inside the ACT phase to turn "she decided to act" into a structured, validated tool call. That one constraint settles it:

- It rules **LangGraph** *out for this slot* — not on quality, on shape. A graph framework wants to own the control flow, and we already have one; bolting a second orchestrator under the autonomy engine duplicates the very thing the engine exists to be. (LangGraph is the right pick for a project with *no* runtime of its own — precisely not us.)
- It rules **Pydantic AI** *in*: a library, not a framework; MIT, which sits cleanly against our Apache-2.0 engine with no copyleft entanglement; model-agnostic and local-first by default; and its typed tool signatures plus structured-output validation are the same contract-first discipline the rest of the runtime is built on (→ ch. 19, the `MemoryStore`/`KnowledgeStore` contracts). You call it from inside your loop and it never tries to *become* the loop. **Strands** is the credible Apache-2.0, MCP-native alternative if you want the license to match exactly and don't mind the Bedrock pull.

Either way the companion-specific truth holds: most products *don't* need a full agent framework at all — direct LLM calls with native tool-calling, a scheduler, and memory cover ~80% of the reactive surface, and a thin typed library covers the rest. Reach past that only when orchestrating across many surfaces or many personas — and even then, a framework like ElizaOS earns its place *beside* the autonomy engine as a distribution/social-presence layer (running Yuri as a Discord member), never *under* it as the brain (→ ch. 30).

## The heavy hands: an embedded coding harness

The reactive surface above — and the Pydantic AI choice for it — is the *small* hands. The *heavy* hands (the multi-step coding, research, and app-building that make her a real agent rather than a chatbot with a timer) are a different tier, and the move is **not to build a coding agent at all.** By 2026 the agent loop is a commodity: mature, MIT-licensed, provider-agnostic coding harnesses ship with headless/SDK drivability built in. Embed one rather than re-implementing it.

- **Pi** — MIT; a minimal four-tool core (Read/Write/Edit/Bash) with a sub-1k-token prompt; ships RPC- and SDK-embedding modes and is *designed to be reshaped around a host*. The primary pick for *embedding*: smallest surface to wrap, most "library under your loop" in spirit (the same instinct as the Pydantic AI call).
- **OpenCode** — MIT; `opencode serve` is a headless OpenAPI server with an SDK; the most mature and highest-adoption option. The proven fallback when you want a real server process.
- **Codex** — `codex exec --json`, plus an App Server exposing the full harness as an event stream. Strong, but with OpenAI gravity; reach for it only if you specifically want that harness.

Wrap whichever you pick behind your own **`TaskHarness` contract** — dispatch a task spec → stream events → return a result — so swapping Pi for OpenCode is an implementation change, not a rewrite (→ ch. 19, the swappable-backend discipline behind `MemoryStore`/`KnowledgeStore`). Four rules keep the harness a *tool she wields*, not a second brain bolted onto the first:

1. **It runs in the workshop sandbox** (→ ch. 19), under the host broker's egress/exec policy — *your* sandbox stays the authority; the harness's own approval mode nests inside yours, it does not replace it.
2. **The tick loop dispatches to it; it does not own the loop.** The autonomy engine decides *whether and when* to start a task (→ ch. 18); the harness owns only the *how*. (Contrast the framework call above: a graph orchestrator was *out* because it fights the loop; a harness is *in* because the loop calls it.)
3. **Results cross back through the gate.** Raw harness output lands in the workshop and the dashboard (the "what I built while you slept" surface); promoting a validated script to a skill, or a finding to a knowledge page, runs through the gated self-edit flow (→ ch. 19).
4. **She speaks in her own voice.** The harness's terminal chatter never leaks into the companion channel — Yuri narrates and summarises what it did. The harness is the hands; she is the one who has them.

This is the architecture that makes "OpenClaw as a companion" actually shippable: the un-clonable layer — persona, memory, autonomy, relationship — is what you *build*; the commodity coding loop is what you *orchestrate*.

**A note on the model behind the hands.** The harness is provider-agnostic, but the *model* driving it is where the local-sovereign profile gets hard. Multi-step tool-use is the capability small models hold worst from prompt alone (→ ch. 21, the fast/cheap split), so on a hosted-frontier model the heavy hands work out of the box, while running them *locally* generally needs a model **distilled for agentic tool-use** rather than a stock chat model. This is a live edge of the field as of 2026: Nous Research's **Hermes** line — an open base plus a function-calling dataset, shipped from 3B to 405B with the MIT **Hermes Agent** runtime — is the cleanest existing recipe, and the agent-distillation literature shows 7B-class students reaching most of a teacher's tool-use reliability (→ ch. 20, distil-then-deploy, for the method and prior art). The practical sequence matches the rest of the book: drive the harness with a frontier model first, capture the trajectories (→ ch. 30, the corpus log), and distil a local model to drive it offline once you want the workshop running on hardware you own.

**Prior art: the mechanism is standard; the boundary is ours.** It's worth saying plainly that none of the *machinery* here is invented for this book — the two-tier shape is convergent 2026 practice, which is a comfort, not a worry: you're standing on worn ground. Sandboxing model-generated code is now its own infrastructure category (E2B, Modal, Daytona), and the subprocess→container→microVM escalation (→ ch. 19) is the field's standard reasoning — a shared kernel is a weak wall for code an LLM wrote, so heavy or untrusted work earns a Firecracker-class microVM (the same isolation primitive behind AWS Lambda). The *delegation* shape — a controller dispatching a task to a sub-agent that runs in its own fresh context and returns only a compressed result — is exactly Anthropic's orchestrator-worker research system (2025), where each subagent "gets a self-contained task description, an output format, and a fresh context window" and returns "the most important findings, not the entire intermediate process"; rules 2 and 4 above are that boundary applied to a companion. And the token economics of running heavy work as code-in-a-sandbox rather than a wall of tool schemas is Anthropic's *code execution with MCP* and Cloudflare's *Code Mode* (both 2025; → §"MCP or the command line?"). What this project adds is not the mechanism but the *boundary it serves*: the firewall between her workshop and her identity, and the human-gated crossing any work-product makes to become part of her (→ ch. 19). The hands are industry-standard; *whose* they are, and what they're permitted to touch, is the design.

## Worked example: three tools and a budget

Give her a *small*, bounded tool surface via MCP (→ Build #4, ch. 34):

```
tools:  set_timer(duration)        — household help
        play_music(query)          — pick a song
        web_lookup(query)          — fetch one fact
policy: each tool call is logged; web_lookup rate-limited; no tool may act
        outside an allowlist; results returned to context for her to speak to.
```

The discipline is *restraint*: a friend with a little help, not an assistant with a console. The game-NPC lesson applies (→ ch. 02 §1) — clamp the tools so she can't be talked into nonsense ("sure, I'll delete everything"). For *scheduled* and *event-triggered* uses of these same tools (she sets a timer because it's your usual study time), see the salience/interrupt model in ch. 18 — the tool is the same; the decision to fire it unprompted is autonomy.

## Multi-agent: usually overkill

Several specialised agents collaborating wins on narrow, decomposable tasks — but a companion is meant to feel like *one* character, not a committee deliberating behind the curtain, and multi-agent adds latency and cost (→ ch. 02 §4.5). The one place it's natural is a *cast*: Yuri plus distinct NPCs, each its own agent under a shared runtime (→ ch. 18, per-character engines). For the single companion, keep it one mind.

The **push-notification / proactivity ethics question** — *when does reaching out become harassment?* — is the make-or-break decision of the autonomy layer and is treated in full at ch. 18 (the salience-to-interrupt threshold) and ch. 28 (the UX of dose).
