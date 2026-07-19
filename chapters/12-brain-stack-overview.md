# 12 — Brain Stack Overview

This is the map for Part III: the technical stack that turns a base model into *her*. Read it first to see the shape, then the chapters that follow build each layer with mechanism and code. The §4 reading-map of ch. 02 named these ideas and their lineage; this Part owns the *how*.

A working companion is never a single model. It is a **stack** — a base model wrapped in layers of prompting, memory, retrieval, tools, and control logic, each of which can be built well or badly more or less independently of the others. The central skill of Part III is learning to think in those layers: to know which layer a given problem lives in, which layer a given fix belongs to, and — most importantly — which layers you can leave empty for a long time without anyone noticing. Almost every expensive mistake a small builder makes is a *layering* mistake: solving a prompt problem with a fine-tune, papering over a memory gap with a bigger model, or bolting an agent framework onto a product whose persona prompt is still mediocre. This chapter gives you the two mental models — a **stack** (what exists) and a **build sequence** (what order you invest) — that the rest of Part III hangs from. They are orthogonal, and keeping them straight is half the battle.

## The five layers

Think of the brain as a dependency stack. Each layer rests on the one below it and exposes a clean interface upward; you can rebuild any single layer without rewriting the others, *provided* the interface holds. From the metal up:

1. **Substrate** — the base model, its quantisation, and the inference engine that runs it. This is the raw next-token predictor and the machinery that serves it: weights, context window, tokenizer, sampling parameters, and the runtime (llama.cpp, vLLM, an API endpoint) that turns a prompt into tokens at some latency and some cost. The substrate decides your ceiling on raw capability, your hardware bill, and your latency floor — and almost nothing about who the character *is*. → ch. 13, ch. 21.
2. **Behavior** — everything that shapes the model's output without changing its weights: the system prompt, the character card, the lorebook, and any lightweight adapters (LoRAs) layered on top. This is where the persona lives. It is the cheapest layer to change — often a text file — and the one that most determines whether the thing feels like a person. → ch. 06, ch. 07, ch. 08, ch. 14.
3. **Memory** — the machinery that lets her carry the past forward: the short-term context window, a long-term store (vector, relational, or graph), and the summarisation/extraction pipelines that move information between them. Memory is what converts a stateless model into something with continuity, and continuity is what the companion market actually competes on. → ch. 15.
4. **Knowledge & tools** — the model's reach beyond its own weights and its own conversation: retrieval over documents (RAG), structured knowledge graphs, function calls, code execution in a sandbox, and external services exposed through protocols like MCP. This is how she answers from a corpus she wasn't trained on and *acts* on the world — running code, researching, building — rather than only talking about it. → ch. 16, ch. 17.
5. **Orchestration** — the control logic above the model: the agent loop, routing between models or tools, reflection and self-critique passes, scheduling, and any multi-agent decomposition. This is the layer that decides *what happens next* — whether to call a tool, whether to speak unprompted, whether to think again before answering. For an agentic waifu this layer is not just a loop: it holds a whole **cognitive architecture** — the always-on autonomy engine with its tick loop, activity states, and salience model — which is why it gets its own chapter rather than a paragraph, and why the chapter after it assembles all five layers into one concrete runtime. → ch. 17, ch. 18, ch. 19.

This taxonomy is not idiosyncratic; it tracks the way the wider field now decomposes an LLM application — a *substrate/serving* layer, a *behavior/specialization* layer, a *knowledge-access* layer (RAG), an *execution* layer (tools/agents), and an *orchestration* layer that conducts the rest. The companion-specific move is to lift **memory** out of "knowledge" and name it as its own load-bearing layer, because for a companion it is (→ ch. 15).

```
        ┌─────────────────────────────────────────────┐
   5    │  ORCHESTRATION   agent loop · routing ·        │   what happens next?
        │                  reflection · scheduling       │
        ├─────────────────────────────────────────────┤
   4    │  KNOWLEDGE & TOOLS   RAG · graphs · function    │   reach beyond the weights
        │                      calls · MCP servers        │
        ├─────────────────────────────────────────────┤
   3    │  MEMORY   context · long-term store ·           │   continuity (the moat)
        │           summarisation · extraction            │
        ├─────────────────────────────────────────────┤
   2    │  BEHAVIOR   system prompt · card · lorebook ·   │   who is she? (the persona)
        │             adapters                            │
        ├─────────────────────────────────────────────┤
   1    │  SUBSTRATE   base model · quantisation ·        │   the raw next-token engine
        │              inference engine                   │
        └─────────────────────────────────────────────┘
```

Two properties of this stack matter more than any individual layer.

**The interfaces are where the leverage is.** Because each layer talks to the next through a narrow contract — Behavior hands Substrate a prompt; Memory hands Behavior a block of retrieved context to splice into that prompt; Orchestration decides whether to run the whole pipeline again — you can swap a layer's *implementation* without touching its neighbours. Upgrade the base model under a stable prompt-and-memory contract and the persona survives intact. Replace a hand-rolled vector store with a managed one and the prompt never knows. A companion architected so its layers are cleanly separable is one you can keep alive across three years of model churn; one where persona, memory, and control logic are tangled into a single mega-prompt has to be rebuilt every time the substrate moves. Designing for that portability is a recurring theme of the book (→ ch. 07, the SOUL format; ch. 20).

**Differentiation is bottom-light and middle-heavy.** The substrate is the *least* differentiated layer — your competitors can rent the same model you can, and a better base model helps them exactly as much as it helps you. Persona (Behavior) and continuity (Memory) are where a small builder actually wins, because they are craft and engineering rather than capital. This is the single most counter-intuitive fact for newcomers, who instinctively reach for a bigger model when the right move is almost always a better prompt or a better memory pipeline. The Replika lesson of ch. 02 §1 — that users bonded just as hard with a weak model behind a strong persona — is the empirical form of this claim. → ch. 02 §1.

Most early companion products only need layers 1–3 done well. A great persona on a competent model with honest memory is already a product people will pay for and stay with. Layers 4 and 5 — tools, agents, orchestration — are powerful, but they are also where latency, fragility, and debugging cost explode, and **adding them prematurely is the #1 trap in the field.** An agent loop that calls three tools turns a 600 ms reply into a four-second one; a multi-agent decomposition multiplies the number of places a conversation can silently go wrong; and none of it improves the felt experience of talking to *her* if the persona underneath is thin. Build down-to-up, ship at layer 3, and add 4–5 only when a concrete failure demands them — not because the architecture diagram looks unfinished without them.

One caveat specific to *this* book's subject, because the rule above can be read to dismiss the very thing the book is about. For a *reactive* companion, layer 5 really is optional polish you may never need. For an *agentic* waifu it is the **destination, not polish**: the always-on autonomy engine that initiates contact on its own lives here, and it is the project's defining bet (→ ch. 18; built in ch. 35). The build-down-to-up discipline still holds — you reach layer 5 *last* — but "last" is not "optional." And note that the layer-5 *trap* and the layer-5 *thesis* are different animals that happen to share a floor: bolting a reactive, multi-tool agent loop onto a thin persona to look sophisticated is the trap; an always-on cognitive architecture standing on a strong persona and honest memory is the thesis. Telling them apart is the work of ch. 17 (reactive tool use) versus ch. 18 (genuine proactivity).

## The canonical build sequence

The five layers describe *what exists* in a finished system. The build sequence describes *what order you invest effort* as a product matures — and it runs along a different axis. Where the stack is spatial, the sequence is temporal and economic:

> **Prompt → RAG → Fine-tune → Distill**

Each rung is roughly an order of magnitude more effort, cost, and commitment than the one before, and each buys a different kind of improvement. The discipline — and it is the consensus position across the field, not a contrarian one — is to **reach for each rung only when the previous one has demonstrably run out of road.**

- **Prompt.** Everything you can achieve by changing text: the system prompt, the character card, few-shot examples, retrieval-free context engineering. Measured in hours, costs essentially nothing, and is reversible the instant you save the file. It is also the rung teams most chronically *under*-invest in — abandoning it for something heavier long before they have actually exhausted it. The model is frozen; only your words change. → ch. 14.
- **RAG.** When the problem is that she doesn't *know* something — a corpus, a document set, the user's own history — you add retrieval rather than trying to cram it into the prompt or train it into the weights. Measured in days to weeks and a modest monthly bill; the model is still frozen, but now it reads from a store you control. Most "she forgot / she doesn't know" failures are RAG and memory problems wearing a fine-tuning disguise: the symptom *sounds* like the model is too weak — tempting you to swap in a bigger one or train the weights — but almost always the model performed fine on what it was shown and simply was never shown the fact. The information existed; your pipeline failed to retrieve it into the context window (a memory gap) or to fetch it from your corpus (a RAG gap). It is a delivery failure, not a knowledge failure, and fine-tuning is the wrong tool for it — you can't reliably bake specific, ever-changing facts like the user's own history into frozen weights anyway; that is exactly what retrieval and memory are *for*. → ch. 15, ch. 16.
- **Fine-tune.** When the problem is *behavioral and stable* — a voice, a format, a refusal pattern, a reasoning style that prompting can only approximate and that you are sure you want permanently — you change the weights. Measured in weeks to months and real money, and crucially it **bakes in choices you can no longer iterate on cheaply.** This is the rung where mistakes get expensive to undo (→ ch. 20). → ch. 20.
- **Distill.** The last rung, and the one with two distinct motives. The first is *cost*: once a behavior is frozen and validated, compress it — train a smaller, cheaper, faster student to reproduce a larger teacher's behavior — to cut latency and serving cost at scale. The second is *capability*: distillation can also move a teacher's skill **down a size class**, giving the student something it could not reach by prompting alone — the reasoning-distill results (a small model trained on a strong teacher's traces beating models far larger than itself) are the canonical proof, and the same lever is how a local 7B gets reliable persona stability and tool-use (→ ch. 20). So you distill both to make a known-good thing cheap *and* to make a small model genuinely better than its size — either way it earns its place once there is a behavior worth capturing. → ch. 20, ch. 21.

The mistake is not fine-tuning; it is fine-tuning **out of order** — reaching for the weights before you've worked prompting and retrieval, *before you have the data*, and before you can say what "good" looks like. Done early it bakes in persona and behavior choices you should still be iterating on for free, at far higher cost to reverse, and it often doesn't even work better — a common post-mortem on a *premature* companion fine-tune is that a cleaner prompt and a better retrieval pipeline would have produced the same result for a fraction of the effort. So the litmus test is one question: *can you state precisely why a good prompt, a good card, and good retrieval are insufficient for your case?* If you can't yet, you're not *ready* — keep iterating and keep collecting data. If you can, the reason you name is also your eval target (→ ch. 23). And for the local, long-session, agentic companion this book is about, that question already has a known answer: sustained persona stability and reliable tool-use are *structural* limits of prompting, not prompt-quality problems (→ ch. 20). There the fine-tune isn't a contingency to avoid but a planned step — you're waiting on the corpus, not on a justification.

Note how the two models interlock. The build sequence is the order in which you *touch the layers*: prompting and RAG work the **Behavior**, **Memory**, and **Knowledge** layers without ever altering the **Substrate**; fine-tuning and distillation are the only operations that reach down and change the substrate itself. That is exactly why they sit at the expensive end — they are the only rungs that break the clean interface between Behavior and Substrate, and so the only ones that cost you the portability the layered design otherwise hands you for free.

## What each Part III chapter covers

| Chapter | Topic | Layer |
|---|---|---|
| 13 | Choosing a base model | Substrate |
| 14 | Prompt engineering for companions | Behavior |
| 15 | Memory architectures *(the load-bearing one)* | Memory |
| 16 | RAG and knowledge systems | Knowledge & tools |
| 17 | Agentic patterns and tool use | Knowledge & tools / Orchestration |
| 18 | The autonomy engine: always-on proactivity | Orchestration |
| 19 | The YuriOS architecture *(the whole stack, assembled)* | Cross-layer |
| 20 | Fine-tuning, DPO, distillation | Substrate (build sequence rungs 3–4) |
| 21 | Inference, serving, latency budgets | Substrate |
| 22 | Safety, moderation, NSFW gating | Cross-layer |
| 23 | Evaluating companions and persona quality | Cross-layer |

The chapters are ordered to be read straight through, but they are also independent enough to be used as references. If you are building, the critical path is 13 → 14 → 15; everything after 15 is something you add when a specific need appears, in roughly the order of the build sequence above.

## The companion-specific opinions

A generic LLM-application stack is layer-agnostic about what it's for. A companion is not, and Part III argues a handful of opinions on top of the generic stack that fall out of *what a companion is for* rather than from engineering taste:

- **Persona prompt comes before everything else.** A great memory system on a great model with a *bad* persona prompt is a worse companion than a 7B with a *great* one. This is the practical consequence of the bottom-light differentiation curve: the substrate is the least differentiated layer, the persona the most, and the cheapest dollar you can spend on the product is almost always spent in the Behavior layer. Get the character right before you optimise anything underneath it. → ch. 06, ch. 14.
- **Memory is the load-bearing technical differentiator.** Among the engineering layers, memory is the one the market actually competes on and the cheapest durable moat available to a small builder. The universal complaint about commercial companions — *she doesn't remember* — is a layer-3 failure, and fixing it is craft you can outbuild a better-funded competitor at. Spend disproportionate effort here. → ch. 15.
- **Reactive tool use and always-on autonomy are different things.** Most products confuse "proactive" with "agentic" and ship a cron job. The field's own distinction is sharper: an agent that waits for a message and then runs a multi-step plan is *agentic but still reactive*; genuine proactivity means initiating contact from an internal signal, with no prompt at all. Reactive tool-calling is ch. 17; the genuine always-on brain — the one that decides on its own to speak — is ch. 18, and it is the differentiator nothing in the market currently has. The hard part was never the tool call; it is the *judgement of when to act* (the Clippy problem of ch. 02 §1, restated).
- **Latency is part of the persona.** A companion has a felt-aliveness budget: target roughly **~600 ms to first text token** and **~1.2 s to first audio**, and anything much slower starts to read as dead air rather than presence. (Pure voice-agent research pushes the conversational floor lower still — a ~200 ms human turn-taking gap, sub-800 ms production budgets — but a companion's longer, relational turns buy a little more latitude than a transactional phone agent gets.) The point is that latency is not just an ops metric; past a threshold it changes *who she seems to be*. → ch. 21.
- **Safety is a layered pipeline for *operators* — and mostly the wrong thing to build for a user-owned companion.** A hosted service genuinely needs moderation and gating as a cross-layer pipeline; a companion that runs on the user's own hardware mostly does not, and bolting operator-grade safety machinery onto it is a category error. Which regime you are in is the two-situations distinction of ch. 05, and it decides almost everything about layer-21. → ch. 22, ch. 05.
- **If you can't measure it, you can't improve it.** Persona quality has no off-the-shelf metric — there is no benchmark for *feels like her* — which is exactly why most builders skip evaluation and then can't tell whether a change helped. Build the eval harness anyway; the question that gated your fine-tuning decision is the first thing it should measure. → ch. 23.

Read on in order, or jump to the layer your current problem lives in. The rest of Part III assumes you can now name that layer.
