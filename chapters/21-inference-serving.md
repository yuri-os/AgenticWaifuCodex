# 21 — Inference, Serving, and Latency Budgets

Inference is where the *alive* feeling is won or lost, and — for an always-on companion — where the money goes (training is a one-off; serving is forever, → ch. 18 on cost as a first-class design driver). Two numbers govern this chapter: a **latency budget** tight enough to feel like talking, and a **cost budget** low enough to keep her running 24/7. The trap is treating them as one problem with one server. They are two problems with two answers, and the rest of the chapter is about keeping them separate: a fast path for the turn the user is waiting on, and a cheap path for everything she does when no one is watching.

## The companion latency budget

| Target | Why |
|---|---|
| **<600ms** to first text token | Below this feels *immediate*. Above, the conversation has a beat. |
| **<1.2s** to first audio frame | The threshold for *natural voice*. |
| **<3s** total for short replies | Above, the user starts to feel like they're waiting on a machine. |

Hitting these reliably is harder than people expect, because the budget is spent across a *pipeline*, not in the model alone — and the model is often not the slowest stage.

## The end-to-end pipeline

A voice turn runs input → STT → retrieval → prompt assembly → LLM → TTS → audio out, and every stage bills against the same 1.2-second budget. The two things that save it are **parallelism** (stages that don't depend on each other run at once) and **streaming** (downstream stages start on the first chunk of upstream output, not the last):

```
mic ─► VAD ─► STT ──┐
   (on-device)      │   ┌─ memory retrieve ─┐
                    ├──►┤                    ├─► prompt ─► LLM ──► TTS ──► audio
                    │   └─ RAG retrieve ─────┘   assembly  TTFT   first    out
              endpointing                       (overlaps  │      sentence
              fires here                         STT tail) │
                                                           └─ static prefix cached
```

Budgeted stage by stage, worst case:

```
mic VAD/endpointing   ~100-300ms   (on-device; no round-trip)
STT                   ~100-300ms   (faster-whisper local, → ch.24)
memory + RAG retrieve ~50-200ms    (run these two in parallel; → ch.15, ch.16)
prompt assembly       ~10-50ms
LLM time-to-first-tok ~200-600ms   (cache the static prefix → cuts this hard)
TTS time-to-first-aud ~150-400ms   (stream; speak on the first sentence)
─────────────────────────────────
budget: first audio < 1.2s, first text token < 600ms
```

The fixes that buy the most, in order of payoff:

- **Stream every stage into the next.** Token-stream the LLM, sentence-stream the TTS, play audio as it arrives. This is the single biggest lever and it compounds across the whole chain — first audio can land before the model has finished the reply.
- **Prompt-cache the static persona/lore prefix.** The SOUL, the lorebook, the system frame are byte-stable across turns; cache them at the provider or as a session-level KV prefix so TTFT pays only for the *new* tokens (→ ch. 14). Often the largest single TTFT win after streaming. (Caveat: any byte change in the prefix invalidates it, so keep volatile content — timestamps, the current message — strictly after the cached span.)
- **Parallelise retrieval with prompt assembly.** Memory and RAG don't depend on each other; fire both while STT's last chunk is still settling.
- **Run VAD/wake-word on-device.** Never round-trip a server just to learn the user started speaking.
- **Speculative opening.** Begin a generic or persona-default first beat while retrieval finishes, then splice — buys perceived latency on the stages you can't compress.

## The serving short list (2026)

- **vLLM.** The default open-source server. Strong batching, paged-KV.
- **SGLang.** Competitive, good structured output.
- **TGI (HuggingFace).** Stable, less performant than vLLM.
- **llama.cpp / llamafile / Ollama.** Local default.
- **MLX.** Apple Silicon local.
- **TensorRT-LLM.** Best perf if you've committed to Nvidia + the engineering.
- **Hosted inference:** Anthropic / OpenAI / Google for closed; Together / Fireworks / Groq / Cerebras / Replicate / DeepInfra for open.
- **Aggregators:** OpenRouter and similar — one API key, hundreds of models across providers, frontier and cheap in the same endpoint with automatic failover. The simplest way to run *both* tiers remotely without integrating each provider one at a time.

For a companion you rarely pick *one*. The fast path and the cheap path want different engines — a hosted frontier API for the visible turn, a quantised local model for everything else — and the next section is how to route between them.

## Serving follows activity state

This is the architectural heart of the chapter, and the thing that makes a *companion's* serving stack different from a chatbot's. The autonomy engine already classifies the companion's moment-to-moment state — ENGAGED, IDLE, DORMANT, DREAM (→ ch. 18, the activity-state table) — and that classification is also a **serving-routing decision**. Which engine answers, and where it runs, is a function of state, not a global constant:

| State | What's being served | Engine | Where | Latency target |
|---|---|---|---|---|
| **ENGAGED** | the user-visible turn | frontier (remote) or local-large | remote allowed | the budget above |
| **IDLE** | goal work, summarisation, classification | small model | local | seconds — nobody's waiting |
| **DORMANT** | light upkeep, the cheap heartbeat APPRAISE | tiny/heuristic | local | irrelevant |
| **DREAM** | memory + knowledge consolidation (→ ch. 18) | small model, batched | local | batch, overnight |

Only the top row pays the latency budget. The other three are *throughput* problems, not latency problems — they can run on a cheap local model on the user's own machine at whatever pace the budget governor allows. Collapsing all four onto one frontier endpoint is the mistake that turns an always-on companion into a furnace (→ ch. 18, the always-on heartbeat trap).

So the serving layer is a **router**, gated by the same budget governor that meters the tick loop (→ ch. 19):

```
# which engine answers this inference call?
def route(call, state, budget):
    if call.user_visible and state == ENGAGED:
        if budget.allows(FRONTIER):
            return remote_frontier      # the turn the user is waiting on — spend here
        return local_large             # over budget → degrade, don't drop the turn
    # everything else is background cognition: no human is waiting on it
    return local_small                 # APPRAISE, summarise, extract, classify, dream
```

Two rules fall out of this and are worth stating plainly:

- **Frontier tokens are for the user-visible turn only.** The APPRAISE pass runs every tick and must never touch the expensive model (→ ch. 18); fact extraction, intent classification, and memory summarisation are background work and belong on the small tier. This is the *two-tier model* pattern (→ ch. 13, ch. 18) realised at the serving layer.
- **Degrade, never drop.** When the budget governor says no to a frontier call mid-conversation, the fallback is the local-large model, not silence. A slower, slightly-less-sharp reply keeps the relationship alive; a timeout doesn't.

## Deployment profiles: Raspberry Pi to datacenter

The router above names three engines — `remote_frontier`, `local_large`, `local_small` — but those are *slots*, not fixed choices. What fills them is the **deployment profile**: a configuration the owner sets, because the right answer depends entirely on the hardware she's installed on and how much the owner values sovereignty over convenience (→ ch. 05; the owner sets the dial, not the builder).

| Profile | Suits | Visible turn | Background work | Sovereignty |
|---|---|---|---|---|
| **Remote-only (thin)** | Raspberry Pi, Android phone, any low-power box | remote frontier (e.g. OpenRouter) | cheap remote model, or on-device heuristics | lowest — all text transits a provider |
| **Hybrid** | laptop / modest GPU | remote frontier | local small model | medium |
| **Local-only (sovereign)** | desktop, 12GB+ GPU or Apple Silicon | local-large | local small | highest — nothing leaves the machine |
| **Hosted** | a server you operate | frontier at your endpoint | small/local on the server | operator-run (→ ch. 05, operator duties) |

Two facts make this matrix work in practice.

**The runtime is light; inference is the only heavy part.** The tick loop, the SOUL, memory, the knowledge store, the frontend — all of it runs comfortably on a phone or a Pi (→ ch. 19). The single component that wants real compute is the model, and a model is reachable over HTTPS. So a tiny device can *host the whole companion* and delegate only inference. This is exactly how SillyTavern runs on a phone or an SBC: it's a frontend pointed at a remote API and does no inference itself (→ ch. 27). YuriOS supports the same **thin-client** mode — point the router's engine slots at an aggregator like OpenRouter and the heavy compute is someone else's problem, while the *mind* (the files that are actually her) still lives on the owner's device.

**The local tiers are OS-portable; the remote tiers are OS-irrelevant.** GGUF + llama.cpp/Ollama is the portable substrate — the same quantised weights run on Linux, Windows, macOS, and ARM (Raspberry Pi, Android via termux and friends). MLX is the Apple-Silicon-optimized local path on macOS; TensorRT-LLM is the Nvidia/Linux performance path. A remote engine, by contrast, is just an HTTPS call — the host OS doesn't matter at all. So the cross-platform story is simple: the *runtime* is portable everywhere, the *local* engines run on any desktop OS (and degrade to CPU/ARM on small devices), and where local isn't viable you swap an engine binding for a remote one without touching the rest of the system.

On a phone or a Pi the realistic local tier is a **sub-2B model at Q4_K_M GGUF** (→ ch. 13 for the quantisation rule). The current default pick is **Qwen 3 1.7B** — Apache-2.0, strong for its size, and it runs at a few tokens per second on a modern phone CPU or a Raspberry Pi 5 (4–8GB); **Gemma 3 1B** and **Llama 3.2 1B/3B** are the main alternatives, the 3B wanting an 8GB board. That is enough to *own the background tier on-device* even in a thin profile — APPRAISE salience scoring, intent classification, short memory summaries (→ ch. 18) — so the heartbeat keeps beating with no network. It is **not** enough to carry the user-visible persona turn at the felt quality this book is about; a 1–2B model drifts out of character fast (the Q4 floor and small-size persona instability of → ch. 13). That asymmetry is exactly why the thin profile splits the way it does: tiny local model for the cheap background work, remote frontier for the turn the user is actually waiting on.

The cost of the thin profile should be stated plainly rather than buried: in remote-only mode the conversation, whatever the model is shown of memory, and anything the companion perceives (→ ch. 18, multimodal sensing) all transit a third-party provider. That is a real privacy surrender (→ ch. 22, the privacy of a brain that can see and hear), and it is the owner's call to make — the book's job is to make the tradeoff legible and leave the dial in the owner's hands (→ ch. 05, the two-situations split), not to deny the convenient option to someone who'd rather run on a $40 board than a gaming GPU.

## Ephemeral self-hosted: rent the GPU, pick the model

Between "rent a frozen hosted API" and "run on your own hardware" sits a third remote option that fits this book's posture especially well: spin up your *own* GPU server on demand, load *whatever model you choose* — including an uncensored or community-**abliterated** (refusal-suppressed) variant — point the router at it, and tear it down when you're done. On-demand GPU marketplaces make this a per-session decision rather than a standing cost:

- **RunPod** — the convenient option. On-demand pods or **serverless** endpoints that scale to zero, per-second billing, and a one-click **vLLM** template that exposes an OpenAI-compatible endpoint in minutes (RunPod advertises sub-second cold starts for warm-pooled containers; a genuinely cold start that has to pull weights into VRAM is more like ~15s, which is the number that matters for a first turn). Point the `remote_frontier` slot at it. H100 / A100 / RTX-6000-class hardware.
- **Vast.ai** — the cheap option. A spot-style marketplace where the same GPU class runs noticeably cheaper (an RTX 4090 around $0.30/hr interruptible, $0.35–0.50 on demand) in exchange for host reliability you don't fully control.
- **Akash Network** — the decentralised option. A crypto-settled compute marketplace (pay in AKT or stablecoin), no platform gatekeeping on what you run, a steeper CLI/console learning curve, and host reliability that's not guaranteed. It fits the project's eyes-open crypto posture: an option, not a prohibition.

Why an owner would reach for this over a hosted API is **model and refusal control.** The powerful open-weight models — Kimi K3, MiniMax, the larger DeepSeek/Qwen tiers (→ ch. 13) — are strong enough to carry the persona, but (a) too large to run at home, and (b) when reached through a *hosted* endpoint often arrive wrapped in the provider's own moderation, which refuses exactly the spicy roleplay, intimate scenes, or red-team / synthetic-data work the owner actually wants (→ ch. 11; ch. 20 on the "base that fights her"). Standing up the raw open weights yourself — or a community abliterated/uncensored build with the refusal directions tuned out — on a box *you* rented removes that layer. You pay for the GPU only while the session is live, then destroy the pod and stop paying.

The honest tradeoffs:

- **It is not zero-config.** You're standing up vLLM (a big model wants full-precision or GPTQ/AWQ weights rather than GGUF, often across multiple GPUs), wiring the endpoint into the router, and managing teardown so an idle pod doesn't quietly bill you. Power-user territory, not the thin-client default.
- **Privacy is better than a shared API, but not absolute.** Your conversation isn't passing through a companion-hostile platform's content filter or logging, but the GPU host still runs the metal — it's *your* instance on *their* machine. Strictly more sovereign than OpenRouter, strictly less than your own hardware (→ ch. 05; ch. 22).
- **It's a temporary lever, not a default profile.** The natural pattern is *transient*: run thin or local-only most of the time, and for a particular session — an uncensored RP night, a batch of synthetic-data generation for a fine-tune (→ ch. 20), a heavy analysis or image-generation run — spin up the big model, route through it, then shut it down. The router's engine slots are configuration; this is just another binding the owner switches on and off.

## Local-only desktop pattern

The local-only profile, worked out in full — the fully-sovereign serving target (→ ch. 03 property 6; Build #2, ch. 32) collapses both paths onto one machine: a 7–8B model at **Q4 (GGUF) on a 12GB GPU** via llama.cpp/Ollama (or MLX on Apple Silicon), STT and TTS local, everything on the user's hardware. It fits — ~4–5GB for the quantised weights leaves room for KV cache plus a Live2D/voice stack (→ ch. 13 VRAM math). Quality is below frontier, but latency is excellent (no network), marginal cost is zero, and the activity-state router degenerates gracefully: the "remote frontier" row simply isn't available, so ENGAGED also serves from the local-large model. This is the right trade for an always-on companion you *own*.

It ships on prompt + card + RAG against the local model — that's Build #2, and it's the right *starting* point: going local doesn't *require* a fine-tune to **run**. But it does to be **good over time**, and this is where the local profile and ch. 20 meet. A small model held in character only by its context window drifts — in-context persona consistency decays measurably after roughly a dozen turns as the persona's tokens lose attention weight to the accumulating dialogue (→ ch. 20, the persona-stability trigger). That is precisely the failure an always-on companion, whose whole value is continuity, cannot tolerate. So for a local companion you intend to *keep*, **distil-then-deploy is the expected upgrade path, not an exotic last resort**: use a frontier teacher to mint on-voice data and bake the persona — and the agentic / tool behaviour — into the weights, so the visible turn holds character over long sessions on hardware you control (→ ch. 20). The right posture is to plan for it from the start — collect and generate the conversation data from day one — and test the tune as soon as the corpus is there, rather than treating it as a contingency you hope to avoid.

## Cost math

The per-turn cost for a hosted-frontier companion has dropped roughly 10× per year for several years and is now low enough that even a free-tier product is plausible at single-digit-dollar-per-month cost-to-serve. But the per-turn number is not the dangerous one — the *per-tick* number is. A companion that is always running can make far more inference calls than a chatbot that only wakes on a message, and the cost question is whether those calls are cheap.

For a hosted product, the levers that make a free user sustainable are exactly the routing rules above:

- **Two-tier serving** — frontier only for the visible turn, cheap/local for the background (→ ch. 13, ch. 18).
- **Prompt caching** — the static persona/lore prefix served from cache, not reprocessed every turn (→ ch. 14).
- **Activity-state gating** — keeping her *resting* most of the time, so the expensive engine is the exception, not the default (→ ch. 18).

With those, per-active-user monthly cost-to-serve lands in the low single-digit dollars, which a modest conversion-to-paid covers (→ ch. 39). The trap is the always-on heartbeat run naïvely on a frontier model: that's what turns a free tier into a furnace, and the activity states exist precisely to stop it. Run your own numbers against your monetization model — the architecture above is what makes those numbers come out sane.

## What to build first

Don't build the router before you have two engines to route between. The thinnest honest serving stack is:

- **One streaming path, end to end.** Token-stream the LLM and sentence-stream the TTS *first* — it's the biggest latency win and it costs nothing to ship.
- **One cached prefix.** Put the SOUL/lore behind a provider or session cache and confirm TTFT drops.
- **Then split the tiers.** Add the small local model for APPRAISE/summarisation/classification (→ ch. 18) so the frontier engine only ever serves the visible turn.
- **Then add the router and the degrade path,** keyed to activity state and the budget governor (→ ch. 19).
- **Expose the deployment profile as configuration.** The remote-only (thin) profile is the easiest to ship and runs on anything from a phone to a Pi, so it's a good first target; the same router then scales up to local-only on a desktop with no code changes — just different engine bindings.

Get streaming + caching + the two tiers and you have a companion that feels immediate and costs little to keep alive — the two budgets this chapter exists to balance. → ch. 32 (Build #2) ships the local-only version of this end to end; → ch. 35 (Build #5) wires the router into the full autonomy engine.
