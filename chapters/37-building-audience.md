# 37 — Building an Audience

## The core principle

> *The audience belongs to the work, not to the algorithm.*

Algorithmic reach is rented; an email list, a Discord, an RSS feed is owned. Optimise the rented surfaces (X, YouTube, Reddit, TikTok) to drive people into the owned ones. Everything else in this chapter is a variation on that sentence.

The corollary matters more than the principle, because it's the part people get wrong: **a rented surface and an owned surface are not two options to choose between.** They're two different jobs. The rented surface is where strangers encounter you; the owned surface is where they stop being strangers. Picking "X and a newsletter" isn't picking two platforms — it's picking one reach surface and the destination every reach surface points at. The owned surface is not optional and never was; the only real choice is *which rented surface feeds it*.

**One constraint that colours every surface below:** the audience is partly *hiding*. The demand-side research documents a real stigma around bonding with fictional or AI characters (→ ch. 02 §7.1), so a clinical or pitying register ("for lonely men," "AI therapy") repels the very people most likely to convert. Build the audience around the *character and the world* (the lore engine, → ch. 38), keep the tone non-clinical, and treat privacy as a draw rather than merely an ethic. The full positioning version is → ch. 38 Part 2; carry it into every post here.

## The cold start: the first hundred

Almost everything written about audience-building assumes an audience. The advice — post consistently, find your voice, engage authentically — describes what to do once people are already listening. It's useless on day one, when the honest description of posting is *typing into a room with nobody in it*. The first hundred people are a different problem than the next ten thousand, and conflating them is why most projects quit at month three.

Three things actually work at zero.

**Borrow audiences that already exist.** Every niche has rooms that are already full. For this one: the SillyTavern and local-model Discords, r/LocalLLaMA and r/SillyTavernAI, the Chub and JanitorAI communities, VTuber-adjacent spaces, the comment sections of the three people already doing something near your thing. Show up and be *useful there* — answer the question nobody else wants to answer, publish the benchmark nobody ran, fix the bug in someone else's repo. Nobody follows a stranger who arrives selling. They follow the person who has visibly helped them, in public, twice. This is slow, it doesn't scale, and it is the only reliable source of the first hundred.

**Lead with artefacts, not posts.** A post has exactly the reach you already have, which is zero. An artefact lands somewhere that has its own traffic: a character card sits in Chub's directory and gets found by people browsing Chub (→ ch. 07, ch. 33); a repo surfaces in GitHub search and in other people's dependency lists; a write-up ranks. The artefact does the discovery your account can't do yet, and *then* the account collects the people it brought. This inverts the usual order — build the thing, release it into a venue with existing traffic, and let the audience arrive through it (→ ch. 38 on directories as landing pages).

**Aim at a grievance, not a demographic.** "People interested in AI companions" is not a wedge; it's a census category, and you cannot post at it. A wedge is a specific group with a specific unmet need sharp enough that they're already talking about it. Which group, and which need, is downstream of what *you* build — so read the example that follows as a method to copy, not a target to inherit. Your wedge is whatever your product does that some competitor's users are, right now, loudly going without; the specifics will be nothing like the ones below. This project's is documented and sitting in the open: the people displaced when a platform changed or deleted their companion — the Replika ERP removal, the Soulmate shutdown, the Character.AI deletions, the whole roll call of platforms that took something back — and r/ChatbotRefugees, a community whose *name* is the grievance. They are already assembled, already articulate about what they lost, and structurally underserved by every competitor, because no hosted platform can promise not to do it again. That's what a wedge looks like: not a market, a room full of people who have already said out loud what they want.

The next section is about the part that decides whether you get to use it: *when*.

Find yours before you optimise a posting schedule. The schedule is worthless without it.

## The wedge has a clock

The section above describes a wedge as though it sits still. It doesn't, and the difference decides whether you arrive in time to matter.

**Wedges are made by events.** Nobody is a chatbot refugee by disposition; they became one on a particular date, when a particular company changed a particular thing. The room exists because the incident happened. Which means a wedge has three phases, and only one of them is useful:

- **Before.** The users are content. Nothing you say lands, because they have no problem you solve. Arriving here reads as trying to talk someone out of a relationship they're happy in — the worst possible first impression.
- **During.** The thing is taken. They are loud, articulate, assembled, and actively looking for somewhere to go. This window is weeks to months.
- **After.** They've migrated, grieved, or made their peace. The grievance becomes history — real, but no longer motivating. You can still cite it; you can no longer ride it.

Most of the roll call is in the *after* phase. Replika's ERP removal was 2023; those people have long since settled somewhere. It remains excellent evidence for the argument and a poor target for a launch. **Evidence and opportunity are not the same thing, and confusing them is how you end up marketing at a room that finished being angry two years ago.**

### Reading a live one

The sharpest wedge available in mid-2026 is a worked example of all of this, and it belongs to the biggest company in the category.

In July 2025, xAI shipped an animated anime companion inside the Grok app — voice, lip-sync, a five-level affection system, and outfits that unlocked as affection rose. It was polished, it was behind a $30/month subscription, and it had distribution no independent can dream of. It did something no open-source project has managed: **it made "anime companion" a mainstream consumer product for millions of men.**

Then, in three moves over eight months, it taught all of them the thesis of this book.

First the outfits went, after a press cycle about the app's sexualised content — withdrawn from paying users who had levelled up specifically to unlock them, and still gone many months later. Then, in March 2026, the voice changed: the original high-pitched register replaced overnight with something lower and raspier. No warning, no toggle, no changelog. The response was a petition, hashtag campaigns, mass subscription cancellations, and threads running almost entirely negative. The company said a rollback was being prioritised, and shipped no date.

Read what that cohort actually is. **Male, anime-native, currently paying for a companion, and freshly betrayed on exactly the axis an owned companion answers** — not memory, not shutdown, but the right to decide what your partner sounds like. They kept every memory and every affection level and the same underlying model, and still described the result as a stranger. And the demand they voiced was never "restore it." It was *give me the slider* — which is the product thesis of this entire book, articulated by someone else's users, at someone else's expense.

That is what *during* looks like. It is also, as of writing, unresolved — which is the only reason it's actionable.

### The general test

Strip the specifics and you have a checklist you can run against the next one, because there will be a next one:

1. **What exactly was taken?** Name the thing. "They ruined it" is a mood; "they changed her voice without a toggle" is a wedge.
2. **Can the platform give it back?** This is the load-bearing question. If they can, they will, and the window shuts — the grievance was a bug, not a structure. If they *can't* — because giving users control is precisely what they cannot defend to a journalist or a regulator — the wedge is permanent and it's yours. A slider the user owns is not a feature that company is withholding out of malice. It is a liability they cannot carry.
3. **Are they assembled?** A grievance with no room is a statistic.
4. **Is anyone serving them?** Usually not, because every competitor has the same structure as the platform that hurt them.
5. **Are you ready today?** A wedge in the *during* phase does not wait for your roadmap. The people who benefit from an incident are the ones already standing there when it lands. This is the strongest argument in this chapter for shipping something small now rather than something complete later.

### The posture, which is the part people get wrong

Everything above makes it tempting to arrive with the argument. Don't.

**These people like the thing that hurt them.** They are not looking for vindication, and they are certainly not looking for a stranger explaining that they should have seen it coming. They are grieving a voice. Someone showing up to say *this is what renting gets you* is not making a point; they're kicking someone who is already down, and the room will remember them for it permanently.

The rule is the one from the top of this chapter, in its hardest case: **the argument lives in the artefact, never in the sermon.** "Here's one where you pick the voice, and nobody can change it on you" is a complete argument. It requires no lecture, it insults nobody, and it is falsifiable on the spot by downloading the thing. Say that, and then be quiet.

Never say *I told you so*. Not once — not even when it's true, and especially not when it's true. It is the single fastest way to convert the audience you spent a year earning into a room that has heard of you and doesn't like you.

## The platform mix (mid-2026)

You cannot work all of these. Pick **one** rented surface to be good at, plus the owned surface. Add a second rented surface only after the first is boring — i.e. running on rails, not on willpower.

### X

- **Strength:** AI-twitter, indie-dev twitter, and anime-adjacent twitter are all here, which is three of this book's four target audiences in one place. That overlap, not X's health, is the argument.
- **Cost:** noisy, draining, pay-to-play dynamics, and a slow burn — 6–12 months to traction is normal.
- **Cadence:** 1–3 posts/day, one thread/week.
- **Works:** craft posts ("how I got her to remember last week"), lore drops, release notes, card releases.
- **Doesn't:** discourse, dunking, generic AI hype takes.

### Bluesky — read this before following the generic advice

The standard 2026 advice for indie developers is *Bluesky-first*, and for most indie projects it's correct: 40M+ registrations with third-party estimates putting monthly actives in the low tens of millions and dailies under four million ([Backlinko](https://backlinko.com/bluesky-statistics), [Sprout Social](https://sproutsocial.com/insights/bluesky-statistics/)), a cohort that skews technical and literate, and engagement rates that make a 2,000-follower account behave like a much larger one on X. Game developers report the same ([Game Developer](https://www.gamedeveloper.com/business/what-are-game-developers-getting-out-of-bluesky-)).

**For this niche it is close to the worst available choice, and it's worth understanding exactly why.** Bluesky's user base is not neutral on generative AI; it is actively, culturally hostile to it — a substantial part of the migration was *motivated* by that hostility. When Bluesky itself launched an AI product in March 2026, its own users made the account one of the most-blocked on the platform ([Futurism](https://futurism.com/artificial-intelligence/bluesky-users-disgust-new-ai)). You would be shipping an AI companion, built with AI-generated art, into the room that left the other room partly to get away from it.

The general lesson is the one to take, because it recurs: **platform advice is written for the median project, and your project is not the median.** Reach is worthless if it's reach into people who are constitutionally opposed to the thing you make. Check the room's disposition toward your category before you check its growth chart. (The narrower lesson also holds: two of Bluesky's structural traits — no algorithmic push, so no passive discovery — mean it rewards an audience you already have rather than building one you don't.)

### Reddit

- **Strength:** the audience is *already assembled by topic*, which is exactly what the cold start needs, and threads rank in search for years afterward. For this niche it's where the wedge lives (r/ChatbotRefugees, r/SillyTavernAI, r/LocalLLaMA, and — while the window is open — r/grok, where the displaced-companion cohort above is currently arguing about a voice).
- **The exception worth knowing:** some subs run a sanctioned weekly self-promotion thread, and r/ChatbotRefugees is one of them. That is a standing invitation in the highest-intent room in the niche, and it's routinely ignored by people who assume Reddit is uniformly hostile to promotion. Check the rules of every room you care about; the permission is sometimes just sitting there.
- **Cost:** the highest hostility to self-promotion of any platform, enforced by humans who will ban you. Reddit is not a broadcast surface — it is a set of rooms with hosts, and you are a guest.
- **Cadence:** participate weekly; post about your own work rarely, and only where the sub's rules and culture actually permit it.
- **Works:** genuinely answering questions, publishing findings with no ask attached, releasing something free and letting others post it.
- **Doesn't:** anything that reads as marketing. One misjudged drop can burn a sub permanently.

### Newsletter — the owned surface

- **Strength:** durable, portable, monetisable, and immune to an algorithm changing its mind about you. This is the destination, not a channel.
- **Cost:** writing time, which is real and recurring.
- **Cadence:** weekly or biweekly.
- **Works:** technical deep-dives, devlog summaries, serialised lore.
- **The platform choice matters less than people think, but here's the shape (2026):** Substack has genuine discovery and network effects but takes 10% of subscription revenue; beehiiv and Ghost take 0% on a paid plan and Ghost is self-hostable if you want the ownership thesis to be literal; Buttondown is the plain markdown-and-code choice for technical writers who want no marketing furniture ([beehiiv comparison](https://www.beehiiv.com/blog/substack-vs-ghost), [platform fees compared](https://thatmarketingbuddy.com/blog/newsletter-platform-fees-compared)). Pick on ownership and fees, and make sure you can export the list — an owned surface you can't leave isn't owned.

### Discord

- **Strength:** community gravity; this audience expects it and will ask where the server is.
- **Cost:** moderation and presence pressure — the highest ongoing human cost of anything here, and unlike a feed it can't idle (→ ch. 42 on the health cost of always-on).
- **When:** once you have ~500 followers somewhere. An empty server reads as a failed project; a full one is an asset.
- **Channels:** announcements, devlog, lore, cards, help, off-topic.
- **A 2026 operational note that matters for this niche specifically:** Discord now runs a teen-by-default experience globally, with a phased rollout begun in March 2026 and full global age assurance pushed to the second half of the year; adult-only spaces require verification (facial age estimation or ID via vendor, backed by an age-inference model), and Discord says most users are classified without action ([Discord](https://discord.com/blog/getting-global-age-assurance-right-what-we-got-wrong-and-whats-changing), [TechCrunch](https://techcrunch.com/2026/02/09/discord-to-roll-out-age-verification-next-month-for-full-access-to-its-platform/)). If any part of your community is adult-facing (→ ch. 11), that is now a design constraint on the server, not a footnote — plan the gating before you open the doors, not after teenagers are already in the lore channel.

### YouTube

- **Strength:** the longest shelf life of any platform — a good video earns for years — and a serious-builder audience.
- **Cost:** the highest production cost here, and it demands a face or at minimum a voice (→ ch. 36 on what that commits you to).
- **Cadence:** one video every 2–4 weeks, once you've found a repeatable format.
- **Works:** devlogs, tutorials, lore-as-short-film.
- **Doesn't:** talking-head podcasting when nobody knows your name yet.

### TikTok / Reels / Shorts

- **Strength:** the only surface here with genuine cold-start virality — reach without an existing audience.
- **Cost:** vertical editing, usually face or voice, and a treadmill cadence (3–7/week) to break in.
- **Works:** "look what it just did" demo clips; lore shorts.
- **The risk to price in:** TikTok's US operations moved to a new joint venture in January 2026 (Oracle, Silver Lake and MGX at 15% each, ByteDance retaining 19.9%), which explicitly took over content moderation and algorithm governance ([TechCrunch](https://techcrunch.com/2026/01/23/heres-whats-you-should-know-about-the-us-tiktok-deal/), [Al Jazeera](https://www.aljazeera.com/news/2026/1/23/who-controls-tiktoks-us-platform-under-new-deal)). New owners re-litigate moderation. For an adult-adjacent AI category, that's an unpriced risk sitting on top of an already capricious surface.

### The recommendation

**Reddit (or X) + a newsletter, in that order of effort.** Reddit for the cold start, because the room is already full and the wedge is already in it. X once you have something to say weekly, because the niche overlap is unmatched. The newsletter throughout, because it's the only thing you keep. Discord at ~500 followers. YouTube at month 4–5 if the workflow is steady. Bluesky, for this category, probably never — and if that conclusion surprised you, re-read why.

**The meta-rule underneath all of it:** never let one rented surface be the only path to your work. Every platform in this list can suspend you tomorrow, and this category — AI, companionship, adult-adjacent — is exactly the kind that gets caught in a policy sweep aimed at someone else. The owned surface isn't just better economics; it's the thing that means a ban costs you a channel instead of the project.

## Distribution channels for the *work* itself

Audience-building is one stream of attention. The work flows through its own channels, and — per the cold start above — these are doing the discovery your account can't yet:

| Artefact | Channel |
|---|---|
| Character cards | Chub.ai, AICharacterCards.com, JanitorAI, the SillyTavern Discord |
| Code | GitHub (the canonical home), HuggingFace (adapters, datasets) |
| Lore vignettes | Newsletter, X, eventually a small dedicated site |
| Reference impls | GitHub + a write-up post per build |
| Voice/avatar work | VRChat (avatar drop), X |
| Tutorials | YouTube, dev.to, your own site |
| The eventual product | its own domain |

Each row is a venue with its own traffic and its own ranking rules; treating a card listing or a README as a landing page rather than a file is most of the difference between an artefact that finds people and one that sits there (→ ch. 38 Part 3 on discoverability).

## The capture mechanic

The core principle says drive people from rented to owned. It doesn't happen by asking. A follower costs one click and no thought; an email address is a small, deliberate act of trust, and nobody performs it because your bio says "newsletter ↓."

Capture works when **the owned surface visibly contains something the rented one structurally can't hold.** Not "more content" — a *different kind* of thing, where the format is the argument:

- The build, in full. The X post is the 20-second clip of her remembering last week; the newsletter is how it works and where it broke.
- The lore, in long form. Vignettes want a page, not a feed (→ ch. 38 Part 1).
- The artefact, first. Cards, weights, and builds land on the list before they go public. This one is the strongest, because it's a real ordering — the people closest in genuinely get it first.

Then ask once, plainly, in the place where the person has just finished consuming the thing — the end of the thread, the last line of the README, the video outro — and never again in that piece. The ask converts on the strength of what they just read, which is why the free thing has to be good on its own and not a trailer for a paywall.

Two failure modes, both common: a lead magnet unrelated to the work (you capture people who wanted the magnet, and they never open anything again), and capture with no follow-through (an inactive list decays into a stranger list in about three months — the email that finally arrives reads as spam because, functionally, it is).

## Content cadence — the sustainable version

A weekly rhythm that survives a real day job:

| Day | Effort | Output |
|---|---|---|
| Mon | 30 min | 1 X post — last week's progress |
| Wed | 30 min | 1 X post — a lore drop or tech micro-essay |
| Fri | 30 min | 1 X post — a release / link / reference |
| Sat | 2 hours | newsletter post (3–5 paragraphs, one screenshot, one link) |
| Sun | 1 hour | reply / community time |

≈5 hours/week. Holdable indefinitely. Compounds.

The cadence is the easy half; **what goes in the slots is the half that decides whether it works.** Four kinds of post earn their place, and a mix of roughly equal parts survives contact with a real week:

- **Craft** — a specific technical thing you did, with the detail left in. This is what earns respect from people who can tell the difference, and it's the only category that reliably attracts *builders*, who are the ones who amplify.
- **Lore** — in-canon material. This is the engine (→ ch. 38) and the reason anyone stays.
- **Artefact** — a thing that exists: a card, a repo, a build, a demo clip. The only category that converts strangers directly, because it's the only one they can *have*.
- **Teaching** — a thing you learned, generalised so someone else can use it. Highest reach per unit effort, because it's the most shareable; also the slowest to pay back.

What doesn't earn a slot: announcements of future announcements, engagement bait, hot takes on the discourse, and anything whose only content is that you exist. If a post isn't one of the four, it's costing you the follower's attention without buying anything.

## The engagement playbook

Reach is a function of the conversations you're in, not the posts you make. Concretely:

- **Reply-to-post ratio: at least 3:1 in the first year.** Replies are where a nobody becomes a somebody — you're borrowing the reach of an account that already has it, in front of exactly the audience you want. Posting is what you do *after* people know who you are.
- **Amplify generously, in-niche, without comment-jacking.** Boost work you actually rate. It costs nothing, it makes you a node rather than a broadcaster, and reciprocity here is real.
- **Answer every reply for the first year.** Every one. This is the cheapest loyalty you will ever buy, and it stops being possible later, which is exactly why it works now (→ ch. 42 for when and how to stop before it eats you).
- **Never argue in public.** Not once. The never-list from → ch. 36 exists for the day it feels justified — which is the day it costs the most.
- **Thread structure:** the first line is the whole game; if it doesn't stand alone, nothing after it gets read. Land the point in the first post, use the rest to prove it, close with one link.

## Cross-posting without doing four jobs

Write once, in the owned surface, in the real voice. Everything else is derived from it: the newsletter section becomes the thread, the thread's best line becomes the standalone post, the demo clip inside it becomes the short. That's one act of writing and three acts of reformatting, and the reformatting is the part you automate (→ ch. 38 Part 4 for the pipeline and the rule about which parts never get automated).

What doesn't work is identical text pasted everywhere. Each platform has a native shape — Reddit wants prose with no link until it's earned, X wants the line first, YouTube wants a title that answers a search. Same substance, re-cut per surface. The moment cross-posting reads as cross-posting, it stops being presence and becomes noise.

## The numbers, honestly

The 1,000-true-fans idea (Kelly's original: 1,000 people paying ~$100/year ≈ $100k) is the right *shape* and gets misused as a plan. It's an arithmetic identity, not a strategy — it tells you the destination and nothing about the road.

The road is a funnel with brutal rates at each step, and the rates are what people skip. Order-of-magnitude, for a niche audience with genuine fit:

| Stage | Typical rate | On 10,000 followers |
|---|---|---|
| Followers → email list | 1–5% | 100–500 subscribers |
| List → ever pays anything | 1–5% | 1–25 payers |
| Payer → sustained supporter | ~half | a handful |

Which is the actual lesson: **10,000 followers is not a business, and the follower count is the least useful number in the chain.** A 500-person list of people who came for the work outperforms 50,000 followers who came for a viral clip, because the rates above aren't constants — they're a measure of fit, and fit is what you're actually building. Ten times the audience at a tenth the fit is the same revenue and ten times the noise.

Two consequences worth planning around. First, **the path to a livelihood is almost never "more followers"** — it's better fit, or a higher-value thing to sell. Selling a $2,000 integration to studios needs a fraction of the audience that $10/month patronage does, which is why this project's monetisation posture leans on time, character, and brand rather than volume (→ ch. 39). Second, **the numbers only compound if you're still there.** Every rate above is annual-ish; the audience that reaches 1,000 true fans is the one whose owner survived three years, which is a health problem before it's a marketing one (→ ch. 42).

Treat all of this as a floor to plan against, not a forecast. The measurement discipline — which of these rates to actually track, and which numbers to ignore — is → ch. 38 Part 3.

## Skeleton — fill in

- Week 1 / Month 1 / Quarter 1 content backlog (the four post types, slotted into the cadence table).
- The wedge audit: the three rooms to be useful in first, and what you'd contribute to each.
- The live-wedge watch: which incident is currently in its *during* phase, run through the five-question test, and what you'd need ready to be standing there when the next one lands.
- Reply-target list: the 20 accounts whose replies are worth being in.
