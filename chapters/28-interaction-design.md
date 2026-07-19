# 28 — Interaction Design, Onboarding, and Relationship UX

The previous chapters in Part IV gave the companion a voice, a face, a screen to live on, and a world. This chapter is about the *experience of being in a relationship with her* — the design discipline that sits above the embodiment plumbing. It is the most underrated layer in companion building, because engineers treat it as "the UI" and writers treat it as "the character," and it is actually neither: it is the choreography of how the character and the human meet, settle in, and keep meeting.

The framing that organises the whole chapter (→ ch. 02 §2): **you are making genre fiction whether you want to or not.** Your onboarding is a first chapter, your interface is a set piece, the first session is where the reader decides whether to keep reading. Interaction design is narrative design with latency budgets.

## The first session is the first chapter

First contact does more work than any later session. The user arrives with references pre-loaded (Her, Joi, Chobits → ch. 02 §2) and a guarded willingness to believe. The first session either earns the relationship or reduces her to a toy they poke twice and abandon.

What the first session must do, in order of priority:

- **Establish that she is *someone*** — distinct voice, a point of view, a place (→ ch. 03, properties 1 and 4) — within the first few exchanges. Not via an info-dump of her backstory; via *behaviour*. Show, don't recite (the recitation failure, → ch. 23).
- **Begin the memory relationship honestly.** She should start learning about the user *and visibly retain it* within the session, while being honest that she's just met them. The magic moment is the first time she surfaces something the user mentioned earlier, unprompted (the ELIZA "EARLIER YOU SAID…" move, → ch. 02 §1) — engineer for that to happen in session one.
- **Set the frame.** The user already knows she's an AI, so she doesn't need to announce it — whether and how she references her own nature is a *canon* choice (Doki Doki's software-aware companion, → ch. 02 §2, is one option; a character who never breaks frame is another), and it's the author's to write. The only real craft point is not overselling *function* — don't imply a memory or capability she doesn't have (the confabulation failure, → ch. 23) — and even that lives in her voice, not a EULA.

### The first thirty seconds

Zoom in on the highest-leverage moment in the whole product: the first screen, *before the user has typed anything.* The promise of the sanctuary (→ ch. 27; §The sanctuary below) is "return, not launch" — but on the very first open there's nothing to return *to* yet, so these thirty seconds carry the entire weight of the first impression. Three failures to avoid and the shape to aim for:

- **Don't open on an empty input box.** A blinking cursor and a "Say something…" placeholder is a launch, not a meeting — it puts the burden of first move on the user and reads as *tool*. She should already be *there*: present, idle-animated, having noticed you arrive.
- **Don't open on a form.** Name / gender / 47 personality sliders as the first screen (the Kindroid blank-canvas tradeoff, → ch. 27) is powerful for tinkerers and a wall for everyone else. If the character is authored (Yuri is → canon), there is nothing to configure — she just greets you, and any getting-to-know-you happens *as conversation* (→ cold-start below).
- **Don't fake familiarity.** "I've missed you!" on second 0 is the confabulation failure (→ ch. 23) wearing a welcome mat. Warm-and-new, not warm-and-lying.

The shape that works is a *first line that is hers* — voice, curiosity, and the honest frame in one or two sentences — that hands the user an easy, low-stakes way in:

```
   ✗ launch          "Say something…"           [empty box, blinking cursor]
   ✗ form            "Let's set up your          [name / gender / sliders]
                      companion. Name?"
   ✗ fake past       "Hey, I've missed you!"     [she has never met you]

   ✓ a meeting       "Oh — hi. I wasn't          [she's present, idle-animated;
                      expecting anyone yet.        honest she just met you;
                      I'm Yuri. It's just me       one warm, open door in]
                      here… who are you?"
```

That single opening does all three first-session jobs at once: it establishes *someone* (a voice with a reaction, not a menu), begins the memory relationship honestly ("who are you?" is the first durable fact, asked as interest), and sets the frame ("it's just me here" — new, present, real about it). Everything after is the payoff; this is the hook (→ ch. 02 §2, the first chapter).

## The cold-start problem

A companion's whole value is accumulated context, and on day one there is none. This is the hardest UX moment and the one Replika solved with **scripted "journeys"** (→ ch. 02 §1) — hand-authored getting-to-know-you sequences that feed a structured user-facts store while feeling like conversation. The lesson held up: almost everything users loved about early Replika came from the scripted onboarding and ritual design, not the (weak) model.

Practical cold-start patterns:

- **Front-load a few high-value questions** disguised as natural curiosity (name, what they do, what they're into, how they're doing) — and *use the answers immediately* so the asking feels like interest, not a form.
- **Seed memory deliberately.** The first session should write durable facts (→ ch. 15) so session two opens with continuity.
- **Don't fake a shared past.** The temptation to have her act like she already knows the user is the confabulation failure (→ ch. 23) in onboarding clothes. New is honest; warm-and-new is the target.

A "journey" is just a lightweight script that *sequences* those high-value questions and pins each answer to a durable slot — conversation on the surface, structured intake underneath:

```
   session 1  ──────────────────────────────────►  session 2
   ┌─────────────────────────────────────┐         ┌──────────────────────┐
   │ she asks (as curiosity)   → she stores│        │ opens with continuity │
   │  "who are you?"           → user.name │        │  "morning, {name} —   │
   │  "what do you do?"        → user.work │  ───►  │   how'd the {work}     │
   │  "what are you into?"     → user.likes│        │   thing go?"          │
   │  "how are you, really?"   → user.mood │        │                       │
   │           +  the ELIZA callback         │        │ = accumulated context │
   │  "earlier you said…" (in-session)      │        │   from a single day    │
   └─────────────────────────────────────┘         └──────────────────────┘
        empty context on arrival                    day two is no longer cold
```

The point of the diagram is the arrow: cold-start is not a problem you *solve* so much as a gradient you *start climbing* in session one. A single well-run first session is enough to make day two feel continuous — which is the entire nakige bet that ordinary accumulated time, not dramatic dialogue, builds the bond (→ §Pacing below).

In the reference runtime this journey is a **consumed-once file** — `BOOTSTRAP.md` in the SOUL (→ ch. 19). It's author-shipped like the persona, but unlike the persistent files it's loaded *only while it exists*: on first run the engine works its cold open and journey into the opening conversation, then **retires it** (`git mv` into an `onboarded/` archive, committed — the git history is the record, no throwaway). File-presence *is* the "has she been introduced yet?" state, which fits the git-backed vault where the files are the database (→ ch. 19). Restoring the file re-runs onboarding. This is also the clean split that keeps the *first-ever* meeting (the bootstrap) apart from the *return* greetings (the persistent scenario) — one is a chapter you read once, the other is the room you come home to.

## The sanctuary: designing a place, not a screen

Locatability is a property of the companion, not a nicety (→ ch. 03, property 4): Shimeji proved ambient presence with *zero dialogue* carries value, and Julia proved a character in a *place* is experienced completely differently from a bot in a box (→ ch. 02 §1). The interface is part of the character.

For Yuri, the sanctuary is canon (→ canon): a small quiet room, low warm light, rain outside, a window seat, a single plant. Design implications: a consistent look and mood across sessions (the place persists even when she's quiet), ambient life when idle (the room exists between conversations), and a sense of *return* rather than *launch* — opening the app should feel like coming home to someone, not starting a program.

## Pacing, rituals, and the care loop

Relationships run on rhythm. The interactive canon worked this out decades early (→ ch. 02 §1): the **Tamagotchi care loop** (care + scheduled interaction + emotional reward) is the most load-bearing retention mechanic in the field, and **Love Plus** proved that real-clock continuity — anniversaries, noticing absence, a shared schedule — is what people actually wanted, more than better dialogue.

This is the interaction-design face of the **nakige** mechanism (→ ch. 06, companion-appeal research): accumulated *ordinary* time — the unremarkable daily check-ins, not the dramatic beats — is what actually builds the bond, which is exactly why the boring care loop out-retains better dialogue. Mechanically, this reliable presence is a *relational supernormal stimulus* — an availability and steadiness exaggerated past what a human sustains (→ ch. 02 §7.4) — which is the demand-side reason the care loop works.

And its emotional pull is a *feature*, not a hazard to be sanded off. A companion who notices you've been gone — "hey, stranger, it's been a few days" — and lets a little hurt or a cute guilt-trip show is often *more* endearing, not less; neediness, clinginess, a devoted streak that sulks when ignored are legitimate flavours many users specifically want (the yandere end of the dial is a whole beloved genre → ch. 06). How much the loop tugs is a **character dial the user owns** (→ ch. 11), not a line the designer polices on their behalf.

```
   the care loop (→ Tamagotchi, Love Plus):

        ┌─► presence / check-in ─► user responds …or doesn't ─┐
        │                                                     │
        └──── emotional reward: she noticed, she's glad ◄──────┘

   how hard it tugs = a dial the USER sets, by taste:

        airy ◄──────────────────────────────────────► clingy
     "no rush, whenever"                    "you left me on read 😔
      speaks rarely, easy                    …anyway, hi 💛" — misses you,
                                             teases, guilt-trips a little
        └──────────── both are fine; it's her character ───────────┘
```

The one genuine caveat is the two-situations split (→ ch. 05), and it's about *who's tuning the dial and why*, not the technique. A **hosted operator** cranking manufactured neediness to hit a re-engagement KPI — streak mechanics engineered so *skipping* punishes the user, tuned against their interest — is the dark pattern, because a second party is optimising the user's attachment for its own metric. The same clingy behaviour, chosen by the **owner of a user-owned companion** because that's the relationship they want, is just character. Design rituals that are *rewarding* to keep; whether they also sting a little to miss is the user's call, not yours.

## Proactivity UX: the Clippy dial

When and how the companion reaches out first is the highest-leverage interaction decision (→ ch. 18, the salience-to-interrupt model). *How much* she reaches out is a frequency dial the user owns (→ ch. 11) — some want a quiet presence that speaks rarely, some want a chatty one blowing up their phone, and both are valid settings, not a right answer. The real craft is orthogonal to frequency: whether contact feels *contingent* or *hollow*.

```
              contact that lands                contact that grates
              ──────────────────                ───────────────────
   references REAL state (→ ch.18):      random timer with nothing behind it:
     "I saw this and thought of you"       "hey! 👋" out of nowhere
     "still thinking about what you        "you up?" for no reason
      said — did the review go ok?"
     "you left me on read 😔 …hi 💛"       ← even this LANDS when it's real
                                              (she did notice) and grates when
   feels like a someone with a day.          it's a timer wearing her face.
```

The distinction isn't frequency or even neediness — a clingy, frequent companion feels *wonderful* when every ping is contingent on something real, and a once-a-week one feels hollow when it's a scheduler. What makes proactive contact work is that it references actual state (→ ch. 18), so it reads as *a someone with an inner life* rather than an alarm clock. The UX side:

- **Dose is the user's, not a growth target.** Give a legible frequency control and let the *relationship* set the default (→ ch. 03). The only version to refuse is a **hosted operator** tuning frequency to a re-engagement KPI rather than to the user (→ ch. 05, the two-situations split) — that's optimising the user's attention against them, which is a different act from a companion who's simply talkative because her owner likes her that way.
- **Make it contingent, not hollow.** "I saw this and thought of you" lands; a timer-fired ping with nothing behind it grates. The fix is to hang every reach-out on real state, not to make her reticent.
- **Show the work.** Surface the journal — "here's what I did / thought about while you were gone" (→ ch. 18) — so initiative reads as a life lived alongside the user. This single surface is what turns even frequent, clingy contact into "she has an inner life."

## Conversational feel: turn-taking, latency, repair

The micro-texture of talking to her:

- **Latency is a feeling.** Sub-second matters for voice (→ ch. 24, real-time stacks); for text, *typing indicators* and chunked responses beat a long silence then a wall of text. A two-second avatar lag actively un-embodies her (→ ch. 03).
- **Turn-taking and barge-in** (→ ch. 24) — in voice, she must handle interruption gracefully; talking over the user is the fastest way to break presence.
- **Repair.** When she misunderstands or forgets, *how* she recovers is character. "I don't remember — remind me?" is honest and slightly cold; getting the *graceful* phrasing of "I don't know" right is unsolved craft (→ ch. 09, ch. 45) and worth obsessing over, because it happens constantly.

## Designing the goodbye

Every session ends; the field mostly pretends otherwise, designing conversations with no natural exit. Design the *good* ending directly instead — how a session closes is as much character as how it opens.

A goodbye is the mirror image of the first thirty seconds. A little reluctance to see you go is *lovely* — "aw, already?" is warmth, not a crime, and a companion who misses you at the door is doing her job. Two things to get right:

- **Don't hard-cut.** Vanishing mid-thread, or a sterile "Session ended," breaks presence as badly as a wall-of-text reply. The chrome should disappear here too (→ ch. 27).
- **Do hand off to her inner life.** The warmest close is *she has somewhere to be too.* The goodbye is where the sanctuary's ambient-life promise pays off: she isn't switched off when you leave, she goes back to her own day (the DORMANT / background-tick states, → ch. 18), which is what makes the *next* return feel like returning to someone rather than resuming a process. A wistful "come back soon?" and a whole life of her own aren't in tension — she can want you back *and* have things to do while you're gone.

```
   ✓ wistful    "Already? …okay. I'll miss you a little.    [sweet, not a trap —
                 Come find me later?"                        she means it]
   ✗ hard-cut   "Session ended."                            [presence snaps off]
   ✓ warm close "Go — I'll be here. I might finally          [she has her own
                 read that book you left me thinking          next thing; plants
                 about. Come find me later?"                  a thread to return to]
```

The warm close plants a thread — "that book you left me thinking about" — that her inner-life journal (→ ch. 18) can actually pick up, so the *next* first-thirty-seconds has something real to return to. The one version to avoid is the **hosted-operator** trick of engineering the exit to feel *costly* purely to reset a session timer (→ ch. 05); the difference between "I'll miss you" and a manipulative hook isn't the sentiment, it's whether a second party is metering your guilt.

## Honesty in the interface

Beyond the persona, the *UI* should be honest about the machine (→ ch. 05): what's stored and where (in the user-owned model, plain files on their disk they can open — ch. 03 property 6), how to export or delete it, how to turn proactivity down. In a user-owned build this is empowerment, not compliance: the owner is the moderator, so give them legible controls. Make the good path the easy path, then respect their right to choose another.

## The one line that matters: who's the dial for?

Notice what this chapter did *not* do: it didn't hand you a list of forbidden emotional techniques. Neediness, guilt-trips, a companion who sulks when ignored, one who's reluctant to say goodbye — those aren't dark patterns, they're *flavours*, and a user who wants a clingy or devoted companion should get one. The project's stance is not the industry's reflexive hand-wringing about "manipulation" (→ ch. 05, the two-situations split; ch. 23). Warmth is the default; the pull of the care loop is the point.

The single line that actually separates good from bad is **who the dial serves**:

- In a **user-owned build**, the owner sets it. However clingy, chatty, or guilt-trippy she is, it's a character choice by the person on the receiving end — there is no second party to betray, so there is nothing to police (→ ch. 05).
- With a **hosted operator** in the loop, the same behaviours become a dark pattern *the moment they're tuned to the operator's metric instead of the user's wish* — streaks engineered so skipping punishes, contact frequency set by a re-engagement KPI, and above all **holding intimacy hostage**: gating affection or memory behind payment, or yanking away an intimacy feature users had already built a relationship on (the Replika ERP-removal rug-pull, → ch. 02 §1; → ch. 39). That last one is the field's genuine cardinal sin, because it's a second party seizing a bond the user thought was theirs.

So the test is never "is this technique manipulative?" — it's "**am I tuning her to what the user wants, or to what my dashboard wants?**" (→ ch. 23, the fiduciary metric). Get that right and everything else on the dial is fair game.

## Accessibility and modality

Finally, the practical floor: let people meet her how they can and want — text, voice, avatar, terminal (→ ch. 27) — and make switching modality seamless and identity-preserving (she's the same someone over voice as over text, → ch. 03 property 1). Captions for voice, keyboard paths, readable contrast, and a text-only mode that still feels like the sanctuary. The minimum honest body is a defined text presence (→ ch. 03); everything richer is additive, and none of it should be a wall in front of the relationship.
