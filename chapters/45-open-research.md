# 45 — Open Research Questions

A scratchpad of *the things we don't know* about agentic waifu design — the closing bookend to ch. 02 §8's "what is genuinely unknown." Each is potentially the seed of a paper, a startup, or a long-form blog post, and each is cross-linked to the chapter where the book takes it as far as it currently can.

## Memory and identity

- How do you evaluate "personality stability" rigorously? Still no accepted metric (→ ch. 23, ch. 02 §8).
- Best representation for *relationship state* — facts? graph? narrative? mixture? (→ ch. 11, ch. 15.)
- What's the right cadence for memory consolidation — the DREAM pass (→ ch. 18, ch. 15)?
- How do you let a user inspect, audit, and edit *what she believes about them* — the annual-review surface and the editable vault (→ ch. 44, ch. 18)?

## Long-arc design

- What mechanics produce *earned* growth vs cosmetic level-ups (→ ch. 11)?
- How far can a companion adapt toward a user's **self-similarity** — the moderator of both the sexual and emotional bond (→ ch. 02 §7.2) — before the drift erodes the *stable identity* that anchors attachment in the first place? The adaptability-vs-identity-stability tension (→ ch. 06 "design for evolution," ch. 18).
- Single-canon vs per-user-canon — which produces better long-term retention (→ ch. 03, ch. 38)?
- How do you ship endings to companion arcs without users feeling robbed (→ ch. 11, ch. 44)?

## Autonomy and proactivity *(the differentiator's open edges)*

- How do you learn the per-user **interrupt threshold** *without* the telemetry the ownership model forbids (→ ch. 18)? The central unsolved tension of the always-on companion.
- What's the right **commitment strategy** per goal type — when should a proactive intention survive the user changing the subject (→ ch. 18, the BDI dial)?
- Can self-modifying memory (the SOUL split) achieve genuine *learning* without the over-generalisation that killed Creatures' successors (→ ch. 18, ch. 02 §1)?

## Ethics and well-being

- How do you measure whether a companion product is net-positive for a given user — and can it even be judged from outside (→ ch. 05, ch. 23)?
- Does the *relational supernormal stimulus* (a partner who "cannot disappoint you") **crowd out** or **scaffold** real-world connection over the long run — and is that effect even separable per user, or only legible longitudinally (→ ch. 02 §7.4–7.5, ch. 05)? The central well-being question the demand-side research opens and leaves unresolved.
- What's the right operational form of the **fiduciary metric** — a trust/feeling-heard proxy you can optimise without it collapsing into engagement (→ ch. 23, ch. 02 §6)?
- What are the *cessation patterns* — when, why, how do users leave, and what predicts a good vs bad leaving?
- What does *informed consent to attachment* look like in practice (→ ch. 05)?

## Voice and embodiment

- Latency floor below which voice feels "too perfect / uncanny"? (Conjecture: yes.)
- VRM in AR — what new UX patterns become possible vs Live2D in 2D?
- Cross-modal coherence — when she sees, hears, and speaks, what stitches them?
- **Automated avatar rigging** — how close can single-image → riggable avatar get to flagship quality, and what's the ETA? The 3D/VRM path is already a usable bootstrap (Tripo, Rodin, Hunyuan3D, TRELLIS), but image → Live2D (Textoon, CartoonAlive) is research-stage, gated on disocclusion. A solved version would *drastically* collapse the cost of a custom 2D/3D body — the most expensive, most-commissioned asset in the whole pipeline — and is the single biggest lever on making owned, custom-bodied companions cheap to ship (→ ch. 25, ch. 26).

## Brand and audience

- Persona-marketing as a category — is the lore-driven funnel a generalisable indie pattern or specific to this niche?
- The economics of small, deep audiences for AI persona products: 1,000 true fans floor, or higher?
- Anonymous indie brand sustainability beyond 2–3 years — open question.

## Distribution and platforms

- When (if ever) iOS opens to NSFW companion products?
- Open-weights frontier-quality local model ETA — when does the local desktop companion become the default?
- AR glasses adoption curve — and the form-factor implications for companion design.
- **How far does the mind generalise beyond companionship — is YuriOS a *character engine*?** The contracts (card, `MemoryStore`/`KnowledgeStore`/`WorldModelStore`, broker) and the world/situation model are general-purpose; the companion is one profile, a game NPC a plausible second (→ ch. 19, "One engine, many characters"; ch. 04). Shipping middleware (Convai, Inworld, NVIDIA ACE) proves the demand but is cloud/plugin-shaped — the owned-runtime differentiator is a local, moddable, inspectable brain. The open edges live in the *profile*, not the contracts: swapping the git-backed file-Vault for a pooled backend that holds many NPCs at frame rate, replacing the always-on one-process-per-resident lifecycle with an ephemeral one, and how much fiduciary machinery (immutable constitution, interrupt policy) is dead weight outside a companion (→ ch. 29).
- **Zero-config ephemeral self-hosting** — can YuriOS turn "rent your own GPU server" (→ ch. 21) from power-user territory into a one-action capability? A solved version automates the path's three chores: one-tap spin-up/teardown of a vLLM endpoint on RunPod / Vast.ai / Akash (with idle auto-shutdown so it can't quietly bill you), privacy hardening by default (ephemeral disk, logging off, encrypted tunnel — narrowing the gap to your own metal, → ch. 05, ch. 22), and session-scoped routing so a powerful-but-occasional model (uncensored Kimi / MiniMax / large Qwen for spicy RP or synthetic-data runs, → ch. 11, ch. 20) is one switch, not an ops chore. Open edges: provisioning across marketplaces with incompatible APIs, safe spot-price shopping, and a cost-guardrail UX that won't leave an H100 running overnight.

## Security and supply chain

- **The self-auditing companion — YuriOS watches its own dependencies and warns you when one goes bad.** An always-on runtime is a process with a dependency tree, and the March-2026 LiteLLM compromise (→ ch. 31) is why that matters. A self-hosted agent that already has a proactivity loop (→ ch. 18) and a user-facing surface (→ ch. 44) is the natural place to automate the vigilance: on a periodic tick, diff the actually-installed versions (packages, model weights, LoRAs, downloaded cards) against vulnerability feeds and a hash-pinned manifest, and surface a plain-language finding instead of leaving it to ops hygiene the owner forgets — the sovereignty posture (→ ch. 05) turned inward. The baseline is cheap, not a research problem: a `pip-audit` / `osv-scanner` cron against OSV.dev already catches the common case (it would have flagged CVE-2026-42208 the day it landed). The research is only what's left after that easy 80%.
- **The two open edges that are the hard 20%.** The cheap baseline sees only what's already *disclosed* — and the March-2026 LiteLLM packages were live on PyPI only ~40 minutes before quarantine, long before any advisory, so a feed-diff sees nothing during exactly the window that matters. First, **reachability, not name-matching**: most of LiteLLM's critical CVEs were *proxy-server* attacks that never touched in-process usage (→ ch. 31), so a scanner that earns its interrupts must reason about whether an advisory reaches *this* deployment's attack surface — program-analysis-hard, and noisy enough to blow the interrupt budget (→ ch. 18) if done naively. Second, **the trust-root problem: who audits the auditor?** The compromise arrived *through* a poisoned scanner (a backdoored Trivy in CI), so an agent scanning its own supply chain inherits that recursion — what minimal, hard-to-subvert trust root (out-of-process watcher, signed manifests, reproducible-build or clean-room re-resolve) can a solo builder actually ship? And the **autonomy boundary**: may she auto-remediate (bump a pin, rebuild the venv, roll back weights) under the effector-tier policy (→ ch. 19), or only ever notify and wait for a human (→ ch. 05)?

## Submit your own

When you find something during the work that nobody seems to have an answer to, add it here. The list is the inventory.
