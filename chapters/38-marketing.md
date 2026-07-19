# 38 — Marketing: The Lore-Driven System

Chapter 37 covered *where* the audience lives and how to build it. This chapter covers the whole marketing function — launches, discoverability, conversion, retention, partnerships, and the AI automation that lets one person run all of it. But it is organised around a spine, because for a project like this one marketing has an actual centre of gravity:

> **The lore is the marketing. Everything else is plumbing around it.**

Read this chapter as: the engine (the lore-driven system), then the functions a real product still needs (the parts lore alone doesn't cover), then the machine that runs them with AI.

---

## Part 1 — The engine: lore-driven marketing

### The unfair advantage

Most indie builders are stuck doing *announcement marketing*: "I shipped X. I shipped Y. Here's a discount." Audiences are saturated; this dies fast.

A persona-driven project has access to a different mode: *lore-driven marketing*. Every post is also a piece of the story. The audience follows because the *world* is unfolding, not because they're being sold to. The product, when it ships, is *part of the world* — they were going to buy it anyway.

This is the single most leveraged marketing pattern available to this kind of project. Most builders ignore it because it requires two things they don't have: a world deep enough to draw from every week, and the discipline to keep every post inside it. Build both — the canon work in Part II is how you get the first, and a lore calendar (below) is how you hold the second — and *that* is the moat. Generic marketing — the rest of this chapter — is commodity; every competitor can do it and most of it is freely documented elsewhere. The lore engine, built on a world only you have, is the part no one can copy.

### The mystery funnel

```
┌──────────────────────────────────┐
│  Public surface (X, YouTube)     │  ← lore drops + craft posts
│  Wide top of funnel              │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│  Owned surface (newsletter)      │  ← deeper lore + serialised fiction
│  Self-selecting audience         │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│  Community (Discord)             │  ← canon discussion, fan work
│  Engaged paying-prone audience   │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│  Product (the companion app)     │  ← *the world, played*
│  Conversion                      │
└──────────────────────────────────┘
```

Each layer hands the next layer *more of the same thing they came for*. The product is just the deepest version of the lore they've been following. This is the funnel the rest of the chapter's tactics feed into — every launch, every SEO page, every collab is a new mouth at the top of it.

### Patterns that work

- **Serialised lore.** Drop a 200-word in-canon vignette weekly. Same time, same channel. Over months it becomes a habit.
- **Artifact-as-marketing.** A character card release isn't a product; it's an artefact from the world.
- **The mystery beat.** Drop one piece of canon every month that *opens* a question. Don't answer until the next month. The audience does the talking for you.
- **In-character corrections / silences.** When a thing goes wrong (a server outage, a bug), reply in-canon: *"the signal went dim for a while — back now."* It builds the world while handling the operational reality.
- **Community canon contribution.** Once you have a Discord, let fan vignettes into the canon (selectively, with curation). They become unpaid evangelists.

### The lore-drop calendar (template)

| Week | Type | Channel |
|---|---|---|
| 1 | World vignette | newsletter |
| 1 | Character moment | X |
| 2 | Mystery beat | X |
| 2 | Devlog (in voice) | newsletter |
| 3 | Artefact release | X + GitHub/Chub |
| 4 | Long-form: a piece of canon revealed | newsletter |

Repeats monthly. Quarterly: a bigger event (a character card V2, a reference-impl drop, a multi-part story arc).

---

## Part 2 — Positioning: the one thing lore won't do

Lore makes people *care*. It does not tell a stranger, in five seconds, **what this is and why they'd pay for it**. That's positioning, and it's the one piece of marketing that has to be plain, not poetic.

Write these down once and keep them fixed (they change maybe once a year, not per-post):

- **The one-line promise.** Not "an AI companion" — everyone says that. Something like *"a companion you own, that remembers, that no one can take away."* Tie it to the book's thesis (user-owned, auditable, persistent — see ch. 44 and ch. 05).
- **Who it's for.** Be specific enough to exclude people — "everyone lonely" is not a position. But *which* specific group is downstream of what you build and of whichever grievance is currently live; it's a method to find, not a demographic to inherit (→ ch. 37, "the wedge has a clock"). In mid-2026 the sharpest room is the users freshly betrayed when a platform changed their companion out from under them — the Grok voice swap, the outfit nerf — not the long-settled refugees of shutdowns two years gone, who are excellent evidence for the argument but a poor target for a launch. Name the for-whom against the wedge that's *during*, and re-name it when the next incident lands.
- **The one enemy.** Good positioning has a villain. Yours writes itself: rented companions that get nerfed, paywalled, silently changed, or deleted. You are the opposite of that. The strongest form isn't "renting is bad" — it's the specific thing the platform can't give back: the right to decide what your companion is (→ ch. 37 on the load-bearing question, *can they give it back?*).
- **Proof.** Why believe you — open source, public writing that argues the position, the auditable runtime, the track record of shipping.

**A register the audience requires, not a nicety.** The demand-side research finds a persistent *fictophilic stigma* — users carry a real fear of being seen as broken or pitiable, and self-censor accordingly (→ ch. 02 §7.1). That is a positioning constraint, not a footnote. Two rules follow. First, **the tone is non-clinical and never pitying** — "for lonely men," "fix your isolation," "AI therapy" all read as the diagnosis the audience is hiding from, and they repel exactly the people most likely to pay. Talk about the *character* and the *world* (the lore engine does this for you, Part 1), not about the user's deficiency. Second, **privacy is a marketing asset, not just an ethic.** For a stigmatised user, *local, no-phone-home, nobody-can-out-me* is a feature they will pay for — surface it (it also happens to be true, → ch. 05). The audience is large, broadly normal, and *hiding*; the brand's job is to be a place they don't have to hide, which is the opposite of the clinical framing most competitors reach for.

Everything else in this chapter is *delivery* of this message. The lore is how you make it felt; positioning is the message itself. Keep the two straight: a vignette that doesn't ultimately ladder up to the promise is just content.

---

## Part 3 — The function map

A shipped product needs all of the following. The discipline is to run each one *through the lore lens* where possible, but each still has to exist as its own competence. Ordered roughly by when you'll need them.

### Discoverability (inbound / SEO / ASO)

Audience-building (ch. 37) is *push*. Discoverability is *pull* — people finding you when you're asleep. Cheap, compounding, slow.

- **Search-intent content.** Write the pages people actually search: "how to make an AI character remember," "self-hosted AI companion," "SillyTavern alternative." These rank for years.
- **GitHub as a search surface.** README, repo topics, and a sharp description are SEO. The reference impls (Part V) are discoverability assets, not just code.
- **Directory optimisation.** On Chub / JanitorAI / AICharacterCards, the card's title, tags, and first lines are its search ranking *and* its conversion copy. Treat a card listing like a landing page (see ch. 07).
- **YouTube search.** Devlog and tutorial titles ranked for search outlive any algorithmic spike.

### The launch playbook

You will launch dozens of times — every card, every version, every reference impl. Make it repeatable so each one costs an afternoon, not a week.

A reusable launch checklist:

1. **Pre-launch lore beat** — open the question 1–2 weeks before, in canon.
2. **Asset pack** — one demo clip, one hero image, three screenshots, the one-line promise, the long description. (Generate most of this with AI; see Part 4.)
3. **Owned-surface first** — newsletter + Discord get it before the public surfaces. Reward the people closest in.
4. **Public surfaces** — X thread, the relevant directory, GitHub release notes (in voice).
5. **The high-intent venues, selectively** — the room around whichever grievance is currently *live*, and only while that window is open (in mid-2026, r/grok during the voice-change window; r/ChatbotRefugees when a shutdown is fresh — → ch. 37, "the wedge has a clock"); Product Hunt / Hacker News / relevant subreddits for *infrastructure* launches (the runtime, a tool), not for waifu drops where they'll misfire. In a grievance room, lead with the artefact and never the sermon — the argument is the download, not a lecture about what renting gets you, and never *I told you so* (→ ch. 37 on the posture).
6. **Post-launch beat** — close the loop in canon a few days later.

### Conversion

Attention you don't convert is a donation to the platform. This is where marketing hands off to ch. 39 (monetization).

- **The landing page** does one job: promise → proof → one call to action. Resist putting the whole world on it; the world lives in the funnel, the landing page closes.
- **Free → paid** — the free tier has to be genuinely good (it's the top of the funnel) while leaving a real reason to pay. Map the paid line to ch. 39's model.
- **The demo is the ad.** For a companion, *showing one real interaction* converts better than any copy. A 20-second "watch her remember last week" clip is your highest-leverage conversion asset.

### Lifecycle & retention

For a subscription companion, retention *is* the business — churn quietly eats everything the funnel brings in. This is also where the product and the marketing become the same thing: the companion that re-engages you *is* the lifecycle email.

- **Onboarding** — the first session decides retention. The companion should feel alive and remember something by the end of day one (ties to ch. 15, memory).
- **Re-engagement** — in-character, not "we miss you!" corporate spam. The companion noticing you've been gone is on-brand *and* effective.
- **Churn-saves** — when someone leaves, they keep their data and their companion (the user-owned thesis, ch. 44). "You can take her with you" is both ethics and the best retention argument you'll ever have.

### Partnerships & community-led growth

Other people's audiences, earned not bought.

- **Collabs** — VTubers, other card creators, small AI-tooling projects. A guest vignette, a crossover character, a shared release.
- **Ecosystem goodwill** — being a useful, generous member of the SillyTavern / Chub communities buys distribution you can't pay for.
- **Referrals & UGC** — fan art, fan vignettes, "look what mine did" clips. The community-canon mechanic from Part 1 is a growth loop, not just a lore device.

### PR / earned media

- Be a quotable *source* on the open / user-owned-AI angle — the thesis is genuinely newsworthy and few people argue it credibly.
- Podcasts and written interviews over press releases. The persona/anonymity question (ch. 36) is itself a hook journalists bite on.

### Paid acquisition

Short version: **mostly don't, yet.** Paid only works once you know your LTV (ch. 39) and have a converting funnel. Before that you're buying traffic that leaks. When you do test it, start with retargeting people who already touched the funnel, cap spend at a fraction of known LTV, and treat it as buying *speed*, never as the engine.

### Analytics

Measure the funnel end to end, and ignore vanity. The five numbers that matter: top-of-funnel reach → newsletter signups → Discord joins → trials/installs → paying supporters, plus the conversion rate *between* each pair. Watch the rates between stages, not the absolute follower count — that tells you which layer of the mystery funnel is leaking. (This is the measurement piece ch. 37 deferred.)

---

## Part 4 — The AI-automated marketing machine

You'll want to automate as much of this as possible. You can automate most of it — but there's one rule that decides *what*, and it comes straight from the voice posture this kind of project depends on (ch. 09):

> **Automate the plumbing and the repurposing. Keep a human — or a tightly-reviewed, voice-tuned model — on anything that carries the persona's voice.**

The voice *is* the product. The moment lore drops read like generic LLM output, the moat is gone. So the rule isn't "automate or don't" — it's "automate the labour around the voice, gate the voice itself."

### The automation map

| Marketing job | Automate? | How |
|---|---|---|
| Content **repurposing** | ✅ Heavily | One newsletter → 5 X posts → a shorts script → thumbnail prompts. The single biggest time-saver. |
| **Scheduling / cross-posting** | ✅ Fully | Typefully / Buffer / platform APIs. Queue a month at once. |
| **Asset generation** | ✅ Heavily | Image gen for artefacts and hero images (ch. 26), demo-clip subtitling, thumbnail variants. |
| **SEO / discoverability drafts** | ✅ With a gate | Generate search-intent page drafts; a human edits before publish. |
| **Monitoring** (mentions, trends, competitor moves) | ✅ Fully | An agent that watches X / Reddit / Discord and summarises daily. |
| **Reply triage** | ◑ Assist only | Agent drafts/sorts; you send anything public. |
| **Analytics summaries** | ✅ Fully | Agent pulls platform stats weekly and reports the five funnel numbers. |
| **In-canon lore drops** | ❌ Human / tuned model + review | The voice. Never raw-automate. |
| **Mystery-beat sequencing** | ❌ Human | Narrative judgement; the payoff is the whole point. |
| **Community-canon decisions** | ❌ Human | Curation is the value. |

### A concrete pipeline

The repurposing loop is the one to build first, because it turns one real piece of writing into a week of surface presence:

```
You write 1 newsletter (the real artefact, in voice)
        │
        ▼
[repurpose agent]  ── prompted with the canon + voice guide + few-shot of YOUR posts
        │
        ├─► 3–5 X posts (drafts)        ─┐
        ├─► 1 shorts/Reels script        │
        ├─► 3 thumbnail/image prompts ───┼─► [you review & approve] ─► [scheduler API] ─► queued
        └─► SEO page draft               │
                                         │
[monitoring agent] ── daily digest ──────┘  (mentions, trends, what to reply to)
```

Two practical notes that make this work for *this* project specifically:

- **Few-shot on your own voice.** The repurpose agent is only as good as its examples. Feed it the canon docs and a handful of your best actual posts; that's the difference between "on-brand" and "ChatGPT smell." A fine-tuned voice adapter (ch. 20) eventually replaces the few-shot.
- **The same runtime can run the marketing.** This is the elegant part: the autonomy engine you're building for the companion (ch. 18) is also a marketing-agent host. ElizaOS-style social connectors make the lore-drop calendar operationally cheap — the persona can *post as herself* on a schedule, with you approving the queue. Marketing automation and product become the same codebase. Just keep the approval gate: autonomous *posting* in the persona's voice without review is exactly the failure mode the voice rule guards against.

Build order: **repurposing first** (saves the most time), then **scheduling**, then **monitoring/analytics**, and only later — once the voice model is good and reviewed — let any of it touch the canon surface.

---

## The honest version

This works because *people want to belong to a world*. AI companion audiences want it more than most. You're not manipulating them by giving them what they're asking for. You *are* manipulating them if the world is hollow and the lore is bait. Don't do that.

The discipline applies to the automation too: every lore drop has to be something you'd be proud of independent of marketing intent — and *independent of whether a model or a human wrote it*. If it isn't, don't ship it. The machine in Part 4 exists to give you more time for the parts that have to be real, not to manufacture the parts that have to be real.

---

## Skeleton — fill in

- Canonical first 12 lore drops for the YuriOS canon (drafted vignettes).
- Mystery-beat ladder: which canon questions to open, in what order, over what timeline.
- Community canon-management rubric (what's accepted, what's headcanon).
- The "second sub-character" trick — a recurring secondary persona in the canon to play off the primary.
- Positioning: lock the final one-line promise and the for-whom.
- The reusable launch-asset template (the files/copy every launch reuses).
- The repurpose-agent prompt + voice few-shot set (the first automation to build).
- Transition: when the lore stops being marketing and becomes the actual product.
