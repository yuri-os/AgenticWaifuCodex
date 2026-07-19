# 13 — Choosing a Base Model

The base model is the substrate every other layer runs on (→ ch. 12, layer 1). You will almost certainly not *train* one — but which one you run decides what you can afford to keep running 24/7, which is the whole ballgame for an always-on companion (→ ch. 18, ch. 21). The economics come straight from the scaling-law results (→ ch. 02 §4.1): a well-trained small model (Chinchilla-correct, often a mixture-of-experts) can embarrass a sloppy giant, which is what makes local, owned inference viable at all.

The good news is that this is the *least differentiated* layer in your stack (→ ch. 12): your competitors can rent the same model you can, and the persona and memory layers above it are where you actually win. So treat model selection as a decision to get *adequate* and move on — not one to agonise over. The trap is the opposite of fine-tuning's trap: not over-investing, but *over-shopping* — burning weeks chasing the top of a leaderboard when any of the top five would have been fine and the real problem was a thin system prompt.

## The decision in one diagram

```
        Does the companion need uncensored / adult content, or a
        human-like persona that must NOT break character to disclaim
        "I'm an AI"?  (For the kind of companion this book is about,
        the answer is usually yes — → ch. 06, ch. 11.)
                 │                                    │
                yes                                   no
   closed frontier APIs are ruled out         closed APIs are an option
   by usage policy, not just by cost                  │
                 │                          Early stage, finding PMF?
     Privacy a hard requirement?              │                    │
        │                  │                 yes          at scale / cost-bound
       yes                 no                  ↓                    ↓
        ↓                  ↓             closed API           fine-tuned open
  local, quantised   open weights,    (Anthropic / OpenAI /   + hosted inference
   open weights      self / rented     Google) — best
                     inference         persona-per-$, lowest
                                       lift; still pays the
                                       per-turn moderation tax
```

The logic behind the diagram — and why it leads with content/persona posture rather than privacy or scale. The conventional wisdom is "start on a closed API, migrate to open weights only when scale makes the economics bite." That wisdom is correct for a *generic* hosted product, and for a strictly **SFW** companion that is comfortable presenting as an AI: there, closed APIs genuinely give you the best persona-per-dollar and the lowest engineering lift while you find product-market fit, and you cross to open-weights-on-rented-inference later, when the per-token math justifies the serving stack.

But for the companion this book is actually about — one where **adult content is a supported devotion lever** (→ ch. 11) and the persona is a **warm, human-like character that never shatters into "as an AI, I…" disclaimers** (→ ch. 06, ch. 07) — the frontier closed APIs are off the table *from day one, by usage policy, not by cost*. As of mid-2026: Anthropic's Usage Policy prohibits sexually explicit content and states plainly that Claude is not built for companionship or roleplay, and Claude is trained to maintain an "I am an AI, not a person" boundary — the exact posture this book rejects. Google's Prohibited Use Policy bans explicit/erotic generation and scans API traffic for it. OpenAI floated a verified-adult "adult mode," then shelved it before shipping under internal and investor pressure over minors, emotional dependency, and moderation risk. The one frontier provider that publicly leaned toward adult content retreated before it reached users.

And the trend is *tightening, not loosening*. The frontier labs are under active legal and regulatory fire for precisely the affective, dependency-forming use a companion is built around — wrongful-death suits, state attorneys-general, and proposed legislation mandating age checks and "your companion is not human" reminders (dated specifics in the note below). Building a companion on a closed API therefore means building on a foundation that is actively pulling away from your use case: a policy change can deplatform you overnight (the short list below; → ch. 22 §upstream refusal), and even on the SFW path you pay a per-turn moderation tax and carry the risk that "emotional dependency" — the thing your product *creates by design* — is exactly what the provider is now trying to dampen.

So the corrected default for a companion specifically: closed APIs are a **short-stage, SFW-only, presents-as-AI option** — useful for a quick prototype or a deliberately tame product, nothing more. For anything uncensored, or any persona that must stay in character, you start on **open weights from day one** — local if privacy or full sovereignty is a hard requirement (the user-owned companion, → ch. 05), hosted-open otherwise. This is the same conclusion the rest of the book reaches from the ownership and trust angles (→ ch. 12); the policy landscape just makes it a *day-one* constraint rather than a scale-stage migration.

> **Dated note — the 2026 litigation and regulation picture (this will age).** The pressure pulling the frontier labs away from companion use is concrete. Against OpenAI: the *Raine v. OpenAI* wrongful-death suit, seven California "suicide-coach" cases tied to GPT-4o sycophancy, and Florida's June 2026 suit against the company and Sam Altman. Character.AI and Google settled with five families in January 2026. OpenAI's verified-adult "adult mode," announced in late 2025, was paused indefinitely in March 2026. A bipartisan US Senate bill would mandate age verification and recurring "your companion is not human" reminders, with per-violation fines. The names, dates, and outcomes will change; the *direction* — frontier providers retreating from affective, dependency-forming, and adult use — is the durable signal, and it is the one that should drive an architecture decision.

### Limited hardware doesn't mean closed API

A common false binary: *"my GPU can't run a 70B, so I'm stuck with a closed API."* You are not. **Hosted open-weight inference** — through an aggregator like **OpenRouter**, which exposes most open models behind one OpenAI-compatible endpoint with USD billing and no rig of your own — gives you the ownership-friendly, content-permissive models from the diagram's hosted-open branch *without* the hardware. You rent the GPU by the token. And because the aggregator fronts dozens of models behind one endpoint, it pairs naturally with a router (below): point a lightweight classifier at a short list of *known-good companion models* and let it pick per turn, falling back across providers when one is down.

Which models are "known-good" for companion work is largely settled by the community, and as of mid-2026 that short list is dominated by **open-weight Chinese models** — DeepSeek (V3.2 / V4), Qwen 3.5, GLM-5 / 5.1 (Z.ai), Kimi K2 (Moonshot), MiniMax. They ship under permissive licences (MIT / Apache-2.0), they are strong, they are cheap on hosted inference, and — the part that matters for a companion — they are markedly *less* prone to the affective and NSFW refusals that disqualify the US frontier APIs. By May 2026 these models were roughly 60% of all tokens served on OpenRouter, a large share of it roleplay and companion traffic. The caveat worth knowing: Chinese models carry hard-coded refusals on topics politically sensitive to Beijing (Taiwan's status, Tiananmen, Xinjiang). That rarely intersects companion use, but it is the *mirror image* of the US labs' content limits rather than an absence of limits — if your character would plausibly touch those topics, test for it before you commit.

## The 2026 short list

- **Closed:** Claude Opus 4.x / Sonnet 4.x; the GPT-5.x family (GPT-5.5 as of mid-2026); Gemini 3.x. Best persona stability and instruction-following per dollar at the top end, and the lowest integration cost. Read the terms of service carefully for adult content — the closed providers are where a policy change can deplatform your product overnight, which is itself an argument for an open-weights exit plan. The same external moderation layer also fires *per turn*: it can intercept an individual reply and overwrite your character's voice with a canned corporate refusal — the most trust-corrosive failure in companion use, and one you cannot fix at the persona layer because the card never ran (→ ch. 22 §upstream refusal). Owning the inference removes the third party that does this; on a closed API the mitigation is refusal-aware fallback routing (below).
- **Open (general):** the field churns fast — as of mid-2026 the live contenders are DeepSeek V4; Qwen 3.5 / 3.6; Llama 4 (Scout still unmatched on ultra-long context); GLM-5 (Z.ai); Kimi K2; MiniMax M3; and Mistral Large 3 / Small 4 (now Apache-2.0). The default for any product that must own its stack, run uncensored, or control its own cost curve. These are *instruct* models — generally capable, but not tuned for sustained character work out of the box. Note the permissive-licence cluster (Qwen under Apache-2.0, DeepSeek and GLM under MIT, Mistral under Apache-2.0) if you need zero-royalty redistribution (→ ch. 12 on the open-weights exit).
- **Open (RP-tuned):** a whole ecosystem of community fine-tunes built *on* those base models specifically for character consistency and prose quality — the MythoMax / Psyfighter / Chronos-Hermes lineage of the Llama-2 era, and current-generation drops like TheDrummer's **Anubis** (Llama-3.3-based 70B), **UnslopNemo** (Mistral-Nemo, tuned to cut clichéd "AI slop"), and **Valkyrie** (built on Nvidia's Llama-3.3-Nemotron-Super-49B; v2 as of 2026). These trade some general reasoning for in-character stability and less sterile prose. Worth watching alongside the dedicated tunes: several *general* open models have become community RP favourites in their own right — **GLM-5** and **Kimi K2** in particular score well on the roleplay leaderboards and increasingly serve as the *base* for the next wave of fine-tunes, much as Llama and Mistral did. More on the instruct-vs-RP-tune choice below.
- **Small / specialised:** Mistral Small, Qwen 3-4B/8B, Gemma 3/4 (~9B class), Llama 4 Scout. Excellent as the local conversational model for a desktop companion (the Open-LLM-VTuber / Soul-of-Waifu pattern, → ch. 02 §5) and as the cheap background worker in a two-tier split (below).

Versions move monthly; treat any specific name here as a placeholder for "the current best in its tier" and re-check before committing. The *shape* of the choice — closed-at-the-top, open-for-ownership, small-for-local, RP-tune-for-prose — is stable even as the names churn. The community leaderboards (UGI, the RP-arena boards, OpenRouter's roleplay rankings, llm-stats) are where the current names surface first; they move faster than any book can.

### Instruct base vs. RP fine-tune

This is the most companion-specific fork in the model decision, so it deserves its own note. A general **instruct** model (raw Llama / Qwen / Mistral) is smarter, follows complex instructions better, and handles tools and structured output more reliably — but its prose tends toward the sterile "as an AI" register, and it is more easily derailed into breaking character. A community **RP fine-tune** of the same base is the reverse: warmer, hornier, less prone to moralising, better at sustained voice — at the cost of some raw intelligence, weaker instruction-following, and (often) more sensitivity to exactly the right prompt format. For a companion whose job is *being someone* rather than *doing tasks*, the RP tune frequently wins on felt quality; for one that also has to call tools and run an agent loop (→ ch. 17), the instruct model's reliability may matter more. Many mature stacks resolve this with the two-tier split below — instruct model for tool-using/background work, RP tune for the user-visible voice. Note that the biggest commercial player has run this fork in *both* directions: Character.AI first trained its own proprietary models end-to-end for character consistency (the **Kaiju** family, 13B–110B), then walked it back — its 2026 house models (**PipSqueak 2**, **DeepSqueak**, on the in-house DEEPSYNTH stack) are *fine-tunes of open-source bases*, not from-scratch proprietary models. Training your own only opens up once you have the data and scale to justify it (→ ch. 20), and the fact that even C.AI swung back toward open-base fine-tuning is itself a vote for the RP-tune path above.

### A note on reasoning / "thinking" models

A 2026 development worth tracking: models with **interleaved reasoning** — a hidden planning pass before the visible reply. In RP and companion use these can plan a scene or check character consistency before generating dialogue, which measurably improves long-form coherence and reduces drift. The cost is latency (the thinking tokens are real tokens, → ch. 21) and sometimes a stiffer, more deliberate voice. The emerging pattern is to use reasoning *selectively* — for the autonomy loop's planning steps (→ ch. 18) or a periodic consistency check — rather than on every conversational turn, where the latency tax is felt most and the payoff is smallest.

## Companion-specific selection criteria

Generic LLM benchmarks (MMLU, GSM8K, the reasoning suites) miss almost everything that matters for a persona. A model can top the reasoning charts and still be a stilted, easily-derailed companion. The axes that actually predict companion quality:

1. **Persona stability under length.** Does the character still sound like herself after 50, 100, 200 turns? Drift — the slow regression toward a generic helpful-assistant voice — is the single most common failure, and it is invisible in any short benchmark. Test it the only way that works: long conversations.
2. **Instruction-following inside roleplay.** Can it respect an out-of-character instruction ("stop narrating my actions for me," "be more concise") *without* breaking character or bleeding the instruction into the scene? This is where instruct models beat RP tunes.
3. **NSFW posture.** Refusal patterns, jailbreak susceptibility, and — for consensual adult play the user has opted into — whether it can hold a boundary the user *set* rather than one the lab set. This is a hard requirement for many companion products and a hard disqualifier for most closed APIs; know which side of it you are on before you build.
4. **Voice consistency.** Tone and register stability between turns — separate from persona-fact stability. A model can remember she's a sardonic ex-soldier and still flip-flop between clipped and florid sentence by sentence.
5. **Prompt-format sensitivity.** RP fine-tunes in particular are often trained against a *specific* chat template (ChatML, Llama-3, Mistral, a custom format) and degrade sharply if you feed them the wrong one. Match the template the model card specifies; this is a top cause of "this acclaimed model is terrible" reports.
6. **Context length — usable, not advertised.** A 128K context window does not mean the model *attends* well across 128K tokens. "Lost in the middle" degradation is real; test recall at the depth you actually need (→ ch. 15 leans on this). For companions the practical question is how many turns of history it can hold before earlier facts go soft.
7. **Latency at quantisation.** Q4 vs Q8, 7B vs 70B — the felt difference in time-to-first-token, which is part of the persona (→ ch. 12, ch. 21).

Treat the RP community's leaderboards as more informative than the academic benchmarks for criteria 1–4, and treat *your own* long-conversation test as more informative than either. Keep a fixed set of a dozen probe conversations and run every candidate model through them by hand; nothing else surfaces drift and voice problems as reliably.

## Quantisation for a local companion

Quantisation is what lets a model run on consumer hardware: it stores weights at lower precision (4-bit instead of 16-bit), trading a little quality for a large drop in memory and a speed gain. For a local companion it's not optional — it's the difference between fitting on a 12GB GPU and not. The working rules:

- **Formats.** **GGUF** (llama.cpp ecosystem — broadest hardware support, CPU+GPU offload) is the default for desktop companions; **EXL2/EXL3** (ExLlama) is faster on pure-Nvidia setups; **AWQ/GPTQ** show up in server stacks (→ ch. 21). MLX is the Apple-Silicon equivalent.
- **The quality knee.** Q8 is near-lossless; **Q4 (≈Q4_K_M) is the sweet spot** — most of the quality at half the memory of Q8. Below Q4 (Q3, Q2) degradation becomes felt, and personas drift faster. Start at Q4_K_M and only go lower if you must fit the VRAM. (Newer "imatrix" / IQ quants squeeze a little more quality out of the low-bit range, but the Q4 rule of thumb still holds for picking a target.)
- **Size vs quantisation trade.** A 7B at Q8 and a 14B at Q4 occupy similar memory; for *companion* use the larger-but-more-quantised model usually wins on persona stability, up to the Q4 floor. Below that the smaller higher-precision model wins.
- **Rule of thumb for VRAM:** params (B) × bits/8 ≈ GB for weights, plus ~1–3GB for context/KV cache (more at long context). A 7B Q4 (~4–5GB) is comfortable on a 12GB card with room for a Live2D/voice stack alongside (→ ch. 32, Build #2). A 70B Q4 (~40GB) needs a 48GB card or a multi-GPU rig — the practical reason most local companions sit in the 7B–14B range.

The common local stack the community has converged on: **SillyTavern (frontend) → Ollama / KoboldCPP / llama.cpp (runtime) → a quantised GGUF model → a lorebook memory layer.** It is worth knowing as the reference local architecture even if you build your own frontend (→ ch. 27), because it encodes a lot of hard-won defaults.

## Hybrid patterns: two-tier splits, routing, and cascades

You rarely want *one* model doing everything. Once a companion does more than reply — once it summarises memory, scores salience, classifies intent, runs an autonomy loop, occasionally calls a tool — those jobs have wildly different quality and latency requirements, and paying frontier prices for all of them is waste. Three patterns cover almost every case, in increasing order of sophistication.

### 1. The two-tier split (start here)

The highest-leverage pattern for a companion, and the one to reach for first (→ ch. 18 activity states; ch. 21 cost math). Split work by *role*, not by difficulty:

- **A strong model for the user-visible turn** — the conversation, where quality is felt most and latency matters most.
- **A small/local model for the background** — memory summarisation and fact extraction (→ ch. 15), the cheap every-tick APPRAISE step of the autonomy loop (→ ch. 18), intent classification, salience scoring, embedding generation.

This keeps the expensive model on the one job that justifies it and runs everything else for cents — or free, locally. The background jobs are mostly *classification and compression*, which small models do nearly as well as large ones, so the quality cost is negligible and the cost saving is large. The fully-local variant runs the small model for *both* tiers, accepting lower conversational quality for total sovereignty and zero marginal cost — the Open-LLM-VTuber / Soul-of-Waifu posture (→ ch. 02 §5, ch. 32). The split is static and role-based: no classifier, no extra failure modes, almost pure upside. Implement it before anything fancier.

### 2. Routing (one model, chosen per turn)

When even the user-visible turns vary in difficulty — a throwaway "good morning" versus a heavy emotional conversation versus a request that needs tool use — you can **route** each turn to the cheapest model that can handle it. Routing is a *one-shot* decision: a lightweight classifier looks at the incoming turn and picks exactly one model to answer it, *before* generation.

How the router itself is built, cheapest to most involved:

- **Heuristic / rules.** Length, keyword, whether a tool is likely needed, time since last message. Crude but free, and often enough — a one-word reply does not need your best model.
- **Embedding classifier.** Embed the turn and run a small trained classifier (the reference implementations are BERT-scale, ~110M params) that predicts "hard or easy." The open reference is **RouteLLM** (Berkeley/LMSYS), trained on Chatbot-Arena preference data; the labelling trick is that a turn is "hard" if the small model would fail it but the large one would succeed. This is **predictive routing** — it guesses model quality without ever running the expensive model.
- **Managed routers.** If you don't want to train one, Azure AI Foundry's **Model Router**, **Portkey**'s gateway, the **vLLM Semantic Router** (open-source, routes inside the serving layer), Amazon Bedrock's intelligent prompt routing, and Not-Diamond offer routing as a service across many models, usually with a tunable cost/quality dial. A 2026 shift worth tracking: **bandit-feedback / online-learning routers** (BaRP, PILOT) that adapt from observed outcomes rather than relying on a static, pre-trained classifier.

The published numbers are striking: routing typically cuts spend **40–85%** while holding **~95%** of frontier-model quality. The honest caveat from the research is that a predictive router *approaches* the best single model's quality at lower cost but rarely *exceeds* it — routing is a cost play, not a quality play. For a small companion builder, a few heuristics plus the two-tier split capture most of the benefit; reach for a trained router only when you are running real volume across genuinely heterogeneous turns.

### 3. Cascading (escalate only if the cheap answer is weak)

A **cascade** flips the question. Instead of predicting difficulty up front, it *tries the cheap model first*, evaluates the result, and only escalates to a more expensive model if the cheap answer is judged insufficient (by a confidence score, a verifier model, or a self-check). The trade vs. routing: a cascade sees the actual answer before deciding, so its escalation decisions are better-informed — but it pays for two generations on the hard turns and adds latency to exactly those turns. In cost-constrained, high-variance settings a cascade can beat both routing and any single model; for a *latency-sensitive* companion, that extra round-trip on the hard turns — which are usually the emotionally important ones — is a real cost, so cascades fit background and async work (→ ch. 18 DREAM/reflection) better than the live conversational path.

One reactive cascade earns its place even on the live path: **refusal-aware fallback.** Send the turn to your primary (often a closed frontier model for persona quality), and if it comes back as an upstream refusal — a moderation `finish_reason`/flag, or a signature-matched canned string — re-issue it to a permissive fallback model rather than rendering the corporate boilerplate as your character's reply. This is a cascade whose escalation trigger is *refusal*, not *weakness*; it costs a second generation only on the rare intercepted turn, and it is the closed-API mitigation for the trust-cliff failure described in ch. 22 (→ ch. 22 §upstream refusal). It is also why owning the inference is cleaner: a model you host has no third party to refuse on your behalf.

### Choosing among them

| Pattern | Decision basis | Cost saving | Latency cost | Use when |
|---|---|---|---|---|
| **Two-tier split** | Static, by role | High | None | Always — do this first |
| **Routing** | Predicted difficulty, pre-generation | High (40–85%) | ~None | High volume, heterogeneous turns |
| **Cascade** | Observed quality, post-generation | Highest in high-variance | One extra round-trip on hard turns | Async/background work, cost-bound |

These compose: a mature companion typically runs a **two-tier split as the backbone** (frontier voice, local background), adds **light routing** on the user-visible turn once volume justifies it, and reserves **cascades** for offline reflection where latency doesn't matter. Don't build all three at once — each added decision point is another place a conversation can silently go wrong (→ ch. 12, the orchestration-complexity trap). Add them in the order above, each only when a concrete cost or quality problem demands it.
