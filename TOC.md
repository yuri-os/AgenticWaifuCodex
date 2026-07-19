# Table of Contents

*This book is self-contained (D-012): it teaches without requiring the rest of the repo. Sibling-folder links are optional working notes, not dependencies.*

## Part I — Foundations

- [01 — Preface and How to Use This Book](chapters/01-preface.md)
- [02 — Literature Review: The Field of AI Companions](chapters/02-literature-review.md) *(substantive)*
- [03 — What Is an Agentic Waifu?](chapters/03-what-is-an-agentic-waifu.md) *(substantive)*
- [04 — The Market Landscape](chapters/04-market-landscape.md)
- [05 — Ethics, Safety, and the Soul Question](chapters/05-ethics-and-safety.md)

## Part II — Soul: Character, Voice, Lore

- [06 — Character Design Principles](chapters/06-character-design.md)
- [07 — The Character Card (V2/V3) and Prompt Anatomy](chapters/07-character-cards.md)
- [08 — Lorebooks and World Info](chapters/08-lorebooks.md)
- [09 — Voice, Tone, and Speech Patterns](chapters/09-voice-and-tone.md)
- [10 — Worldbuilding and Canon](chapters/10-worldbuilding.md)
- [11 — Devotion, Growth Arcs, and Long-Form Relationship Design](chapters/11-devotion-and-arcs.md)

## Part III — Brain: The Technical Stack

- [12 — Brain Stack Overview](chapters/12-brain-stack-overview.md)
- [13 — Choosing a Base Model](chapters/13-base-models.md)
- [14 — Prompt Engineering for Companions](chapters/14-prompting.md)
- [15 — Memory Architectures](chapters/15-memory.md) *(substantive)*
- [16 — RAG and Knowledge Systems](chapters/16-rag-and-knowledge.md)
- [17 — Agentic Patterns and Tool Use](chapters/17-agentic-patterns.md)
- [18 — The Autonomy Engine: Always-On Proactivity](chapters/18-autonomy-engine.md) *(new, substantive)*
- [19 — The YuriOS Architecture](chapters/19-runtime-architecture.md) *(new, substantive)*
- [20 — Fine-tuning, DPO, Distillation](chapters/20-fine-tuning.md) *(substantive)*
- [21 — Inference, Serving, and Latency Budgets](chapters/21-inference-serving.md)
- [22 — Safety, Moderation, NSFW Gating](chapters/22-safety-moderation.md)
- [23 — Evaluating Companions and Persona Quality](chapters/23-evaluation.md) *(new, substantive)*

## Part IV — Body: Embodiment

- [24 — Voice: TTS, STT, Real-Time Conversation](chapters/24-voice.md) *(substantive)*
- [25 — Avatars: Live2D, VRM, Expression Systems](chapters/25-avatars.md)
- [26 — Generated Imagery and Selfies](chapters/26-imagery.md) *(substantive)*
- [27 — Frontends: Web, Desktop, Mobile, Terminal](chapters/27-frontends.md)
- [28 — Interaction Design, Onboarding, and Relationship UX](chapters/28-interaction-design.md) *(new)*
- [29 — 3D Worlds and VR Companions](chapters/29-3d-and-vr.md)

## Part V — Build: Reference Implementations

- [30 — Reference Implementations Overview](chapters/30-reference-implementations.md)

  The five build sub-projects are catalogued in Appendix D.

- [31 — Build #1: The Minimum Viable Waifu](chapters/31-build-1-minimum-viable-waifu.md) *(new)* — web chat, one persona, persistent memory
- [32 — Build #2: The Desktop Companion](chapters/32-build-2-desktop-companion.md) *(new)* — local LLM + Live2D + voice loop
- [33 — Build #3: The Character Card Release](chapters/33-build-3-character-card-release.md) *(new)* — SillyTavern V3 card with lorebook
- [34 — Build #4: The 3D World Companion](chapters/34-build-4-3d-world-companion.md) *(new)* — VRM in-browser + tool use + ambient behavior
- [35 — Build #5: The Agentic Sanctuary](chapters/35-build-5-agentic-sanctuary.md) *(new)* — proactive, scheduled, always-on

## Part VI — Self: The Creator as Character

- [36 — The Creator Persona](chapters/36-creator-persona.md) *(substantive)*
- [37 — Building an Audience](chapters/37-building-audience.md)
- [38 — Marketing: The Lore-Driven System](chapters/38-marketing.md)

## Part VII — Business

- [39 — Monetization Overview](chapters/39-monetization-overview.md) *(substantive)*
- [40 — The Six-Month Gameplan](chapters/40-six-month-gameplan.md) *(substantive)*
- [41 — Legal, Compliance, Risk](chapters/41-legal-compliance-risk.md)
- [42 — Operating as a One-Person Studio](chapters/42-one-person-studio.md)

## Part VIII — Future

- [43 — Embodied and Robotic Companions](chapters/43-embodied-and-robotic.md)
- [44 — The Persistent AI Person](chapters/44-persistent-ai-person.md)
- [45 — Open Research Questions](chapters/45-open-research.md)

## Appendices

- [A — Glossary](appendices/A-glossary.md)
- [B — Tools and Stacks](appendices/B-tools.md)
- [C — Reading List and References](appendices/C-reading-list.md)
- [D — Reference Implementation Index](appendices/D-reference-implementations.md)
- [E — Communities and Where to Hang Out](appendices/E-communities.md)

---

## Suggested reading paths

**"I want to ship something this weekend."**
→ 01 → 03 → 06 → 07 → 14 → 31 (Build #1) → 37

**"I want to understand the whole field before doing anything."**
→ 01 → 02 → 04 → 12 → 39 → 40 → appendices

**"I want to build a brand and an audience."**
→ 01 → 03 → 06 → 36 → 37 → 38 → 40

**"I'm here for the deep technical."**
→ 12 → 13 → 14 → 15 → 17 → 18 → 19 → 23 (the brain spine, end-to-end)

**"I want the agentic / always-on part specifically."**
→ 03 → 17 → 18 → 28 → 35 (Build #5)

**"I want to make money from this."**
→ 04 → 39 → 40 → 41 → 42
