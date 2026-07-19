# 40 — The Six-Month Gameplan

A concrete week-by-week plan from "starting today" to "craft built, audience started, and a clear decision on the bigger product" — with first revenue a hoped-for bonus, not the measure. Calibrated for **5–10 hours/week** of project effort.

Where ch. 39 was the strategy, this chapter is the operational counterpart: the premise and month-6 target below set the frame, and the month-by-month checklists are the week-by-week execution.

> *Worked example throughout: the companion is Yuri and the book being pre-sold in month 5 is this one. Swap in your own character and your own product as you follow the plan.*

## The premise

- You currently have: the research, the creative direction, and forkable reference code — the five teaching builds (→ ch. 30) plus **YuriOS**, the most complete build of all, live on GitHub; no audience, no revenue.
- You want: a coherent body of work + the start of an audience within 6 months, with a clear continuation runway into months 7–18. First revenue, if it comes, is a bonus.
- You have: 5–10 hours per week.

## What "done" looks like at month 6

- **The work:** 1 polished character card publicly released; 1 reference implementation publicly released; a canonical persona for your companion locked in; a clear visual brand.
- **The audience:** 500–2,000 followers across X + newsletter; 100–500 newsletter subscribers; a small (50–200 person) Discord.
- **The revenue (bonus, not the target):** anything at all — a first tip, a first client, a handful of card patrons — is a win. If it reaches $300–$2,000/month from some mix of donations, patronage, consulting, and Patreon/newsletter, that's the lucky end of the range, not the expectation.
- **The decision:** clear answer on whether to commit months 7–18 to the SaaS (Road 1, the bigger hosted product) or to lean into consulting + content.

Read the money figures as the *optimistic* case, not a promise or a floor. Plenty of people will run this plan for six honest months and finish with an audience in the low hundreds and revenue nearer zero than $300 — and that is not failure. **The real deliverable of the first six months is craft.** You come out of it able to design a persona, ship a card, stand up a runtime, hold an audience's attention, and write in a voice people follow — the durable skills every later dollar depends on. The revenue, when it comes, follows the craft; it does not precede it. So if month 6 arrives with the skills built and the wallet still thin, you are exactly where you should be: the numbers slip by months, the craft does not.

## Month-by-month

### Month 1 — Persona and presence

**Goal:** Be findable. Have a vibe. Ship one thing.

Week 1
- [ ] Lock creator handle across X, GitHub, HuggingFace, Bluesky, Discord, AICharacterCards/Chub. (45 min)
- [ ] Commission/generate canonical avatar glyph. (1 evening)
- [ ] Write creator-persona spec sheet (→ ch. 36). (1 evening)
- [ ] First X post — a lore vignette. Tone-setter. (1 hour)

Week 2
- [ ] Choose canonical companion lore (→ ch. 10, worldbuilding and canon). (1 hour)
- [ ] Draft full V3 character card for your companion (→ ch. 07). (4 hours over the week)

Week 3
- [ ] Generate hero portrait + 12 expression sprites. (4 hours)
- [ ] Finish V3 card + lorebook (15 entries). (3 hours)

Week 4
- [ ] **Ship:** your character's v0.1 card publicly on Chub.ai. (1 hour)
- [ ] Announcement post (X + first newsletter). (1 hour)
- [ ] Set up Ko-fi and/or GitHub Sponsors. (30 min)
- [ ] Set up newsletter (Buttondown or Ghost). (1 hour)

**End of month 1:** A character card in the world, a vibe established, a way for people to give you money.

### Month 2 — First reference implementation

**Goal:** Ship Reference Build #1 (the minimum viable waifu). Prove technical credibility publicly.

> Two ways to do this, both fine (→ ch. 30): **fork** the book's Build #1 and reskin it to your companion — fastest — or **roll your own** from scratch with it as the reference. The hours below assume from-scratch; fork it and you'll finish inside week 5–6 and can pull month 3 forward.

Week 5
- [ ] Set up the MVW repo. Skeleton. Persona = your companion. (3 hours)
- [ ] Wire LLM + system prompt + character card. (2 hours)

Week 6
- [ ] Add a memory store — embeddings + retrieval (→ ch. 15). (3 hours)
- [ ] Add conversation summarisation. (2 hours)

Week 7
- [ ] Web UI — sanctuary aesthetic. (4 hours)
- [ ] Smoke-test, polish. (2 hours)

Week 8
- [ ] **Ship:** open-source Build #1 on GitHub. Write-up post (newsletter + X thread).
- [ ] Start dropping consulting availability hints. (1 hour)

**End of month 2:** First public OSS reference implementation; demonstrated competence.

### Month 3 — Consulting and Patreon

**Goal:** Put the revenue machinery in place and make the first ask. Paid work may or may not follow this month — that's fine.

Week 9
- [ ] Stand up a simple landing page (yourname.dev or codename.io). Services + work + contact. (4 hours)
- [ ] Patreon page: tier 1 (early-access devlog), tier 2 (private Discord + advance lore), tier 3 (monthly office hour). (2 hours)

Week 10
- [ ] Cold-warm outreach: 10 indie builders who might want companion consulting. (3 hours)
- [ ] Announce consulting availability publicly. (30 min)

Week 11
- [ ] **First paid client.** (Realistic; if not, do it month 4 instead.)
- [ ] Continue lore-drop calendar. (2 hours)

Week 12
- [ ] Second character card release — sub-persona in the same canon. (4 hours)
- [ ] Patreon launch announcement. (1 hour)

**End of month 3:** Consulting offer and Patreon both live; second card shipped. First revenue if you're lucky — the machinery to receive it either way.

### Month 4 — Audience compounding

**Goal:** Reach 1,000 followers. Sustain weekly cadence.

Week 13–16
- [ ] Maintain content cadence (5h/week as per → ch. 37).
- [ ] Open Discord. Pin lore, channels, links. (3 hours setup; ongoing presence.)
- [ ] Start Reference Build #2 (desktop companion) — fork or from scratch, same choice as #1 (→ ch. 32). (8 hours over the month.)
- [ ] Lore arc kickoff: a four-week mystery beat across X and newsletter.
- [ ] One YouTube devlog video (optional — if YT is on the menu).

**End of month 4:** Discord up. Active cadence. Build #2 underway.

### Month 5 — Course/book pre-sale + Build #2 ship

**Goal:** Ship the desktop reference impl and make a concentrated ask — the best shot at revenue in the six months, if it's going to come at all.

Week 17–20
- [ ] **Ship Build #2.** Big release. Video walkthrough.
- [ ] Pre-sale: your course or book — early-access at $20–$50. Even 50 buyers = $1k–$2.5k.
- [ ] Audience milestone push.
- [ ] First B2B inbound likely starts arriving.

**End of month 5:** Book pre-sold; desktop build shipped. A first four-figure month is plausible here — plausible, not owed.

### Month 6 — Synthesis and decision

**Goal:** Decide on the next 12 months.

Week 21–24
- [ ] Third character card or first sub-product (lorebook pack, a small tool).
- [ ] Write the decision memo: is the audience real? Is consulting absorbing time? Is the SaaS (Road 1) worth a 12-month commit?
- [ ] If yes → the build begins in month 7 with a defined MVP. Concretely, that's climbing the rest of the ladder you paused at Build #2: a body and reactive tools (Build #4) and the always-on autonomy engine (Build #5, the agentic sanctuary — the differentiator nothing in the market ships; → ch. 34–35). You don't have to climb it from scratch: **YuriOS** — the full integrated descendant of these builds, and the most feature-complete of any of them — is live and forkable at [github.com/yuri-os/YuriOS](https://github.com/yuri-os/YuriOS), so the month-7 move can be to fork, reskin, and extend it rather than rebuild the top of the ladder yourself.
- [ ] If no → double down on consulting + creator-economy + book.
- [ ] Either way: publicly publish a 6-month retrospective. It will be your best-performing post of the year.

**End of month 6:** A clear revenue picture (even if the number is small), a defined audience, and a defined next chapter.

## What can go wrong

- **No audience traction by month 4.** Re-audit content: are you posting craft or just announcements? Are you in the world or selling from outside it?
- **Consulting demand zero.** Productise: turn the consulting offer into a fixed-price character-design package, a fixed-price persona audit, a fixed-price card-+-implementation bundle.
- **Burnout.** 5–10 hours/week is the ceiling. If you're overrunning, drop the YouTube and the desktop build; keep cards, newsletter, X.
- **Lore exhaustion.** You ran out of in-canon things to say. Solution: pause, revisit the worldbuilding methods in ch. 10, write the next month's drops in one sitting and schedule them.
- **Ethical drift.** A direction you took for revenue feels icky. Stop. Re-read chapter 5. Adjust.

## What can go right

A lore-drop catches; a video gets shared; a B2B inbound from a recognised buyer; a character card gets featured on a Chub front page. Any one of these accelerates the timeline. Don't plan for them; be ready when they happen.

## Skeleton — fill in

- Detailed week-by-week task checklist (expand the month-by-month plan above into weeks).
- KPI sheet (followers, subscribers, revenue, time spent).
- The "what to drop first" priority list when overcommitted.
- The month-12 and month-24 sketch.

## A closing caveat

This exact plan may not work for you — and that's expected. It's built around one path (cards → reference builds → consulting → audience → a product decision), and your goals might point somewhere else entirely: pure fiction and lore, a single deep build with no audience play, an AI heavy game or story, a tool for yourself alone, a different order, a different pace. If so, throw the specifics out.

The point of this chapter was never these particular twenty-four weeks. It was to show that a plan is *makeable* — that "starting today" can be decomposed into concrete, shippable, week-sized steps with a defined thing at the end of each. **Make a plan.** Make one that fits what *you* actually want to build, adjust it the moment reality disagrees, and keep the habit of shipping something small and finished on a regular cadence. That habit is the real engine; this chapter is just one worked example of pointing it somewhere.
