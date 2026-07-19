# The Agentic Waifu Codex

*A practitioner's guide to designing, building, shipping, and monetizing AI companions.*

Published by YuriOS Lab as **the Codex, Vol. I**. Filed by the Operator.

---

## What this is

A book-shaped synthesis of the field — the technical research, the creative and embodiment craft, and the brand and business pieces — written to stand on its own. It's intended to function as:

1. **A textbook** for someone learning to build serious AI companions from scratch (the author included).
2. **A self-contained reference** — everything needed to follow the argument lives in these pages; primary sources are cited inline as further reading, never as a dependency.
3. **A playbook** for turning the work into a creator-economy livelihood — a few hours per week, six months to first revenue, growth from there.

It is opinionated. It assumes you want to ship something that feels *alive*, not a generic chatbot wrapper.

## How the repo fits together

```
AICompanionResearch/
├── brain_research/      ← deep technical reference (the "brain" stack)
├── competitors/         ← per-product intel (what's already out there)
├── analysis/            ← market, monetization, regulation, gaps
├── concepts/            ← companion lore + creator lore concepts
├── monetization/        ← business paths + 6-month gameplan
└── book/                ← you are here — the synthesis
```

The book is the layer that ties it all together for a builder who wants to **make and ship**, not just analyse.

## How to read this book

You can read it linearly, but each Part stands on its own:

- **Part I — Foundations.** What an agentic waifu actually is, why this matters now, the landscape, and the ethical floor you should not go beneath.
- **Part II — Soul.** Character design, persona, voice, lore, worldbuilding. Borrows heavily from the AI roleplay community (SillyTavern, Chub, JanitorAI) and from anime/visual-novel character writing.
- **Part III — Brain.** The full technical stack: models, prompts, memory, RAG, agents, fine-tuning, inference.
- **Part IV — Body.** Voice, avatars (Live2D/VRM), images, frontends, 3D and VR.
- **Part V — Build.** Reference implementations from the simplest viable companion up to a tool-using 3D world companion.
- **Part VI — Self.** The *creator* as a character: building a mysterious persona, audience, and brand around the YuriOS lineage.
- **Part VII — Business.** Monetization strategy, legal/risk, the six-month gameplan.
- **Part VIII — Future.** Embodied companions, long-arc storytelling, open research.
- **Appendices.** Glossary, tools, communities, reading list, reference-implementation index.

## Status of each chapter

Most chapters are intentionally **skeletons** — section headings, key questions, and the bones of what belongs there. The author is filling them in over time as the work happens. Substantive chapters as of the initial scaffold:

- `02-literature-review.md` (Part I)
- `35-creator-persona-yuri.md` (Part VI)
- `38-monetization-overview.md` (Part VII)
- `39-six-month-gameplan.md` (Part VII)

See `TOC.md` for the full table of contents and reading recommendations.

## Conventions

- Each chapter is a single `.md` file under `chapters/`, numbered to keep ordering stable in the filesystem.
- Internal references point to chapters by number (e.g. "ch. 15"), so the book reads standalone.
- External references cite URLs inline; the master reading list lives in `appendices/C-reading-list.md`.
- **No AI-attribution trailers** in commits — house style.
- Lore-side writing aims for *Chobits warmth × Ghost in the Shell weight*. Technical writing aims for terse and useful.

## Contributing (future)

For now this is single-author. If/when contributions open up, the model will be: PRs against chapters welcomed; lore canon decisions belong to the project lead.
