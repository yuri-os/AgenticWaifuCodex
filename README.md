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

## How this repo fits together

```
AgenticWaifuCodex/
├── chapters/                   ← the book itself, one .md file per chapter
├── appendices/                 ← glossary, tools, communities, reading list, impl index
├── reference-implementations/  ← the Build chapters as independently runnable code
├── pdf/                        ← stylesheet + fonts for the PDF build
├── build-pdf.sh                ← concatenate chapters → single PDF
└── TOC.md                      ← full table of contents + reading recommendations
```

Everything needed to follow the argument lives here — the book is self-contained, and the reference implementations are the Build chapters made runnable.

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

## Status

The book is under active, single-author development — chapters are written and revised as the underlying work happens, so depth varies across Parts. See `TOC.md` for the full table of contents, current reading order, and recommendations.

## Contributing (future)

For now this is single-author. If/when contributions open up, the model will be: PRs against chapters welcomed; lore canon decisions belong to the project lead.
