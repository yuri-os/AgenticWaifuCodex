# 30 — Reference Implementations Overview

A book of theory is a book of theory. The five reference implementations exist so that for each major cluster of the book there is a small, working, idiomatic example to point at and fork. They are intentionally minimal — they show the *shape*, not production polish — and they ladder: each build adds another of the five properties (→ ch. 03) — with property 3 (owned agency) arriving in two halves, capability then initiative — until the last one is a genuine agentic waifu.

Each build is a small, self-contained project; this chapter is the index, chapters 31–35 are the per-build walkthroughs, and Appendix D catalogues the sub-projects.

The five properties the builds ladder through, restated so you don't have to flip back to ch. 03:

1. **Stable identity** — a *someone* who persists and is recognisably the same person across text, voice, and avatar.
2. **Honest memory** — persistence across sessions that admits its edges instead of confabulating them.
3. **Owned agency** — both halves: **3a capability** (she can take real actions — fetch, write a file, run a task — not just emit text) and **3b initiative** (she decides to act or speak from state you didn't trigger, gated by a salience threshold so she can stay silent).
4. **A body** — a place she lives and a form she has, in one of the two registers (2D desktop, 3D web).
5. **The one-on-one frame** — built for one person, no audience and no per-session engagement metric in the loop.

(A sixth commitment — **she's yours**, running on hardware you control — is orthogonal to the five and runs through every build; → ch. 05.)

## The ladder

| # | Build | Adds | Properties (→ ch. 03) | Chapter |
|---|---|---|---|---|
| 1 | Minimum Viable Waifu | persona + persistent memory, on the web | 1, 2, 5 | ch. 31 |
| 2 | Desktop Companion | a local-first body: voice + Live2D | + 4 (voice/avatar) | ch. 32 |
| 3 | Character Card Release | the persona as a shippable, tradeable artifact | 1 (distilled) | ch. 33 |
| 4 | 3D World Companion | a 3D body, tools, and ambient life in a place | + 4 (3D); 3a — capability (reactive tool-use) | ch. 34 |
| 5 | Agentic Sanctuary | the always-on autonomy engine — initiative; a minimal knowledge layer (drop-folder RAG) | + 3b — initiative (the hard half) | ch. 35 |

Read up the ladder — each rung keeps everything below it and lights one more property, until the top rung is a genuine agentic waifu:

```
  property →               1  2  3a 3b 4  5     each rung adds:
  ────────────────────────────────────────────────────────────────────────────
  B5  AGENTIC SANCTUARY     ■  ■  ■  ■  ■  ■     + initiative (3b) — the always-on brain
  B4  3D WORLD COMPANION    ■  ■  ■  ·  ■  ■     + a 3D body & reactive tool-use (3a)
  B2  DESKTOP COMPANION     ■  ■  ·  ·  ■  ■     + a local body: voice + Live2D (4)
  B1  MINIMUM VIABLE WAIFU  ■  ■  ·  ·  ·  ■     persona + persistent memory, on the web
  ────────────────────────────────────────────────────────────────────────────
       reactive companion ──────────────────────────────────────► agentic waifu

  B3  CHARACTER CARD RELEASE   packages any persona as a shippable .PNG — orthogonal
                               to the ladder (distribution, not a new property)
```

Builds 1, 2, and 4 are increasingly embodied *reactive* companions (a persona on the spectrum, → ch. 03). Build 5 is the one that crosses into *agentic waifu*, because it adds the autonomous initiative (**3b**) that completes owned agency (property 3) — the reactive tool-use half (**3a**) arrived back in Build 4. Build 3 is orthogonal — it's how you package and distribute a persona regardless of runtime.

## Two decisions that shape every build

- **Own the runtime.** The builds use our own host-runtime + per-character autonomy-engine design (→ ch. 18). The reactive, turn-driven loop in the existing open agent stacks is incompatible with the always-on brain this project is actually about; AIRI, ElizaOS, and the rest (→ ch. 02 §5) remain reference points to study, not bases to build on.
- **The distribution artifact is the `.PNG` character card.** One file = one companion: a V3-compatible card with embedded JSON, optionally carrying an `extensions.yurios` block for the autonomy runtime. Build #3 produces it; Build #5 loads it.

## A cross-cutting practice: capture the corpus from day one

Every build from #1 on produces the one asset the eventual distillation / fine-tune step (→ ch. 20) cannot be done without: **on-voice conversation data**. That step is on the roadmap, not optional, for a companion meant to run locally and hold character over long sessions (→ ch. 20, ch. 21) — and it is gated on data you can only accumulate by *running the earlier builds*. So treat data capture as a standing build requirement, not a Build-#5 afterthought:

- **Log the raw exchanges, not just the distilled memory.** Build #1 already extracts facts and embeds turns for *retrieval* (→ ch. 31), which is lossy by design. Keep the full turns too — prompt, reply, and the **provenance** that makes them trainable later: which model produced each reply, the card/prompt version, a timestamp, and any rating (→ ch. 20's ratings-as-asset note; ch. 23). Curating a corpus is mostly subtraction (→ ch. 20), and you cannot subtract from what you threw away.
- **Your corpus is your own play and synthetic generation — never the downloader's data.** This is the hard line of the user-owned model (→ ch. 05; ch. 20): when you ship the card (Build #3) or the runtime, the conversations on *someone else's* machine are theirs and are never harvested — no phone-home, no retention dashboard (→ ch. 35, the ethics section). The corpus you train on comes from *your* companion's life and from synthetic generation against a frontier teacher (→ ch. 20), not from a userbase.

Get this right early and the fine-tune step is waiting on a decision, not on data; get it wrong and you reach Build #5 having discarded the very thing that would have let you bake the persona into the weights. The concrete record schema — fields, provenance, and the export-to-training pass — is the shared **corpus-log schema in Appendix D**, which every build writes to.

## Build-it-in-order, but ship after each

Don't build the whole stack before shipping anything. Each build is a publishable artifact and a teaching milestone on its own:

- **Build #1** is shippable in a weekend and already clears three of the five properties — start here.
- **Build #2** and **#4** give her a body (the two body registers: 2D desktop, 3D web).
- **Build #3** is the thing other people can actually download and love (→ ch. 33, ch. 37 on distribution).
- **Build #5** is the capstone and the differentiator — the always-on companion nothing in the market ships (→ ch. 18, ch. 04 scoring).

## What's actually in the repo today

The five builds above are the *teaching* ladder — the order chapters 31–35 walk, and the way to think about what each property costs. The `reference-implementations/` folder on disk is shaped differently, and deliberately so: rather than five monolithic build directories, it holds the **component services those builds compose from**, built first because they are the reusable, independently-runnable pieces, plus scaffolds for the integrated builds. Most of what already ships clusters under **Build #3** — the card itself and the media services a released persona needs (voice, image, avatar) — because those are the parts you can finish and use in isolation. The integrated builds (#1, #2, #4, #5) assemble these components behind a runtime; they land as the pieces come together (scaffolds for #1, #2, and #5 are planned; #4 is in progress).

So the ladder is the pedagogy; the folder is the parts bin. Current state:

| Folder | What it is | Build / chapter | Status |
|---|---|---|---|
| `yuri-soul/` | SOUL files + V3 card exporter (the distribution artifact) | #3 core · ch. 07, 33 | working |
| `image-forge/` | Image / selfie service, swappable diffusion backends | #3 · ch. 26 | working |
| `kokoro/` | Voice service — fixed voice, streaming + eval | #2/#3 · ch. 24 | working |
| `gpt-sovits/` | Voice cloning client + identity eval (realtime) | ch. 24 | working |
| `qwen3-tts/` | Voice convergence — clone / design / preset | ch. 24 | working |
| `vrm-viewer/` | Python-driven VRM avatar control pipeline | #4 · ch. 25 | working |
| `01-minimum-viable-waifu/` | Integrated Build #1 | ch. 31 | planned |
| `02-desktop-companion/` | Integrated Build #2 (local brain + voice loop + Live2D shell) | ch. 32 | planned |
| `04-3d-world-companion/` | Integrated Build #4 (assembles `vrm-viewer` + tools) | ch. 34 | in progress |
| `05-agentic-sanctuary/` | Integrated Build #5 (Build #4 + the always-on mind, → ch. 18–19) | ch. 35 | working |

Each impl is its own sub-folder with code, a README, and links back to its chapter. The live index — with the conventions every impl follows and the **shared corpus-log schema** every conversational build writes to — is **Appendix D**.
