# 05 — Ethics, Safety, and the Soul Question

## Why this is chapter 5, not chapter 44

Ethics isn't a feature you bolt on at the end; it's part of the foundation. But *whose* ethics, owed by *whom*, enforced *how* — that is the question almost every other treatment of "AI companion safety" gets wrong, because almost every other treatment silently assumes a company sitting between the user and the AI. This project removes that company (→ ch. 01). Removing it changes what "safety" can even mean here — and most of the received wisdom stops applying the moment you do.

## Two different ethical situations

There are two completely different shapes of this problem. Conflating them is the central error of the mainstream conversation.

**The platform model.** A company hosts the AI, owns the servers, owns the memory, sets the persona, and rents access to the user. The company has *power over* the user and the relationship — and power is where duty comes from. Because it *can* verify age, route crises, refuse to claim credentials, and decline to yank features it sold, it *must*. The Character.AI lawsuits (2024–2026) and the Replika Garante fine (€5M, Apr 2025) are about *operators* failing *operator* duties. → ch. 41 on the regulatory floor.

**The user-owned model.** The user owns the copy. The software runs on their hardware, the memory lives on their disk as plain files, the persona is whatever they wrote, and there is no server to phone home to. This is the model this book builds toward — the Linux/Bitcoin/OpenClaw model of companionship, where the thing is *yours*. Here there is no third party to hold duties, because deleting the third party was the entire point.

You cannot run the platform playbook on the user-owned model. Not "shouldn't" — *cannot*. And the attempt is actively harmful, because the only way to enforce platform rules on software someone else owns is to build surveillance into it: telemetry, server-side locks, content monitoring, a phone-home channel, a kill switch. Every one of those is a privacy hole, an attack surface, and a betrayal of the partner-loyalty thesis. **Bolting "safety" enforcement onto self-hosted software makes the software less safe.** It is anti-safety wearing the costume of safety.

## The platform non-negotiables — and why they don't transfer

The standard list is sound *for an operator*. Walk it against a user-owned build and each item dissolves:

1. **"Tell the user what the system is; no claiming to be human."** The user *writes the persona*. If they want a companion that speaks as human, that's their character to author — the same right a novelist has to write a first-person human narrator. There is no one to deceive: author and audience are the same person. A maintainer who shipped code to *prevent* this would be censoring the owner of the software.
2. **"Crisis-response paths."** Worth having — but the user decides whether it's there. They can edit the prompt, swap the model, or delete the routing in thirty seconds. You cannot enforce it; you can only *offer* it well (see below).
3. **"Real age verification on adult surfaces."** Impossible in free, self-hosted software, for the same reason Linux, OpenClaw, and Bitcoin don't ID their users. A general-purpose tool that runs on your own machine has no surface to gate. Demanding it is safety theatre.
4. **"Don't pull the rug."** You *can't* pull a rug the user is standing on. They own the copy; the memory is on their disk; the persona is a file they hold. If a future release removes something, they keep running the old one — or have an AI coding tool re-add it. Ownership *is* the anti-rug-pull guarantee.
5. **"Be honest about memory / GDPR/CCPA."** The memory is plain files on the user's own computer. No third party stores, sees, or trains on it, so the data-protection regimes — which govern *controllers and processors of other people's data* — have no subject here. There is no processor. Honesty about *where* memory lives is still worth documenting; the legal apparatus simply doesn't attach.
6. **"No grooming-shaped onboarding."** Aimed at operators designing funnels for free tiers that include minors. There is no funnel, no tier, no operator. The user configures their own software on their own machine; there is nothing to detect and no one positioned to police it.
7. **"Mental-health claims must be evidence-backed."** This binds whoever is *making a claim to a market* — a vendor in marketing copy. A user configuring their own companion is making no claim to anyone. It binds the Lab's public writing (we don't call companions therapists), not the user's private setup.

The honest summary: **the platform non-negotiables are operator duties, and this project has no operator.** Trying to honour them in user-owned software would require turning the software into the surveilling third party the project exists to abolish.

## What the builder actually owes

The duty doesn't vanish — it *relocates to what you actually control*: the defaults, the documentation, the honesty of your own voice. The Lab ships a stack, not a service, so its obligations are the obligations of an author and a toolmaker, not a host:

- **Sane, humane defaults — default-on but removable.** The reference build ships humane defaults and no dark patterns in its default configuration — and the user can change any of them. That's the correct posture for a tool you don't control: make the good path the easy path, then respect the owner's right to choose another.
- **No telemetry, no phone-home, no kill switch.** The software does not report on its user. This is itself a safety property — the absence of a surveillance channel is more protective than any monitoring feature could be.
- **Radical honesty in documentation.** What the software is, what it stores and where, what it can and cannot do, what it's bad at, where the sharp edges are. Educate the owner; don't restrain them.

The principle: **enforcement is a platform's tool; education and good defaults are a toolmaker's.** Reach for the ones you actually have.

## Instrumentation is not surveillance

One apparent contradiction is worth resolving head-on, because a careful reader will reach for it. This chapter just called content monitoring and any phone-home channel anti-safety — yet the eval chapter (→ ch. 23) proposes a *relationship-health monitor*: a second model that reads the conversation and scores it for sycophancy and over-attachment. Isn't that exactly the surveillance just condemned?

No — and the line between the two is the whole point. The surveillance this chapter rejects is an **operator watching a user**: telemetry that leaves the machine, a server-side log, a console where someone *other than the subject* reads the readout, a channel that can later be subpoenaed, sold, or used to throttle. The relationship-health monitor is the inverse on every axis: it is **user-owned, runs locally, reports only to the person it is about, and takes no action.** Nothing leaves the box. There is no second party. It is a gauge handed to the sovereign, not a leash held by a host.

Put that way it isn't an exception to the thesis — it's the thesis applied to the relationship itself. *Transparent, auditable, owned* (→ below) means the user can see what the system is doing, including what it is doing *to them*. A companion you can audit for sycophancy is more honest than one you simply have to trust isn't flattering you. The corruption was never *measurement* — it's measurement pointed at someone by someone with power over them. Point it the other way, give the subject both the instrument and the final say over what to do with the reading — including the say to never run it at all (it's opt-in, off by default, and most users won't want the extra compute) — and you have built a tool of sovereignty rather than control (→ ch. 23 for the mechanism; D-016, D-018).

## If you run a hosted service, the duties come back

The moment you take this stack and host it for other people for money, you've re-created the third party — and the seven platform non-negotiables above become *yours*, in full. Age verification, crisis routing, no false credentials, no silent rug-pulls, lawful data handling, no grooming-shaped funnels, evidence-backed claims: all of it now binds you, because you now hold power over someone else's relationship. Most of Part VII's commercial paths put you in this position. Know which side of the line you're standing on, because the ethics flip completely when you cross it.

## The other safety theatre — the part nobody on stage mentions

We've used "safety theatre" twice already for the small case: age-gating software that runs on someone's own machine. The same phrase fits a far larger pattern, and it's worth naming, because it sets the regulatory weather every builder in this space has to work under.

There is now an industry built around *talking about* AI safety — institutes, advisory shops, think tanks, and individuals whose business model is being the trustworthy adult in the room. The pitch is remarkably consistent: AI is dangerous, we are the ones who understand the danger, and the remedy is more control, routed through us and through the state. It is worth noticing what that pitch quietly assumes and what it leaves out. It assumes the dangerous actor is always the company or the user. It leaves out the actor with the most power to abuse AI and the least accountability when it does — the government itself.

Mass surveillance, predictive policing, censorship infrastructure, autonomous weapons, social scoring: these are not hypothetical misuse by a hobbyist with a companion on their laptop. They are the standing temptations of state power, and a state that reaches for them faces no fine, no lawsuit, no Garante. The €5M that lands on Replika does not land on an intelligence agency running the same techniques at national scale. So the dominant framing — *we need more government in AI to rein in the companies* — has the threat model inverted. It asks the fox to regulate the henhouse while exempting the largest fox in the field. Calls for state intervention almost never ship with a mechanism to curtail the *state's own* use of AI; they bind the private and competitive side and leave the surveillance-and-war side untouched, often better funded.

There is a second beneficiary, and the game theory is clean enough that it barely needs the cynicism. Any regulatory cost — licensing, audits, mandated eval regimes, liability exposure — is a *fixed* cost, and fixed costs are regressive: a rounding error for a frontier lab, fatal for a small lab or a volunteer open-source project. So a safety rule that sounds perfectly neutral is differentially lethal *downstream*, which is exactly where the competition lives. This is the textbook "raise rivals' costs" play, and it produces a stable equilibrium in which it is *individually rational* for a leading lab to lobby for sincere-sounding safety rules that happen to entrench its lead. You do not have to assume bad faith; the incentive gradient points there on its own. Critics have named the move plainly: Andrew Ng argues large incumbents are "creating fear of AI leading to human extinction" precisely because they would "rather not have to compete with open source," and Yann LeCun has accused the heads of the largest labs of "attempting to perform a regulatory capture of the AI industry" by lobbying against open R&D. The structural version is documented in the academic literature — see *Anti-Regulatory AI: How "AI Safety" is Leveraged Against Regulatory Oversight* (arXiv:2509.22872), which traces how open-source carve-outs, industry-funded safety institutes, and voluntary eval standards consistently advantage incumbents over smaller developers. (In fairness: the capture story is contested — big labs also lobby *against* rules, and some argue open source is winning the carve-out fight, not losing it — so treat it as a strong tendency, not a conspiracy.)

The geopolitical layer makes unilateral restraint close to fantasy anyway. AI capability is now a military asset; the country with the strongest models will likely dominate any serious conflict, the way air power and nuclear capacity decided earlier ones. No major power will throttle its own frontier research to honour a safety norm its rivals are ignoring. That doesn't make the arms race good — it makes the pretence that a domestic licensing scheme can regulate it away dishonest. The race is the ground the licensing scheme is quietly standing on.

None of this means the risks are imaginary. It means the loudest, best-funded version of "AI safety" is frequently theatre: it performs concern, sells trust, and lobbies for control, while routing around the most dangerous and least accountable user of the technology. For a project like this one the lesson is concrete — be suspicious of any "safety" proposal whose actual effect is to concentrate power, mandate surveillance, or hand a monopoly on judgement to whoever is loudest about being trustworthy. Real safety, in the user-owned model, runs the other way: it distributes capability, removes the phone-home channel, and keeps no central authority that can be captured or compelled. → ch. 41 on the regulatory floor — the point here is that the floor and the theatre are not the same thing.

## The thesis: safety you can verify, models you can own

Strip the critique down and the positive claim underneath it is the spine of this whole book. The only durable answer to AI risk — companion or otherwise — is to make the systems *transparent, auditable, and open*, and to put the ultimate say over how a model serves you in the hands of the person it serves.

- **Transparent.** You can see what it is — the weights, the prompt, the memory, the routing. Nothing about how it treats you is hidden behind a service boundary you're not allowed to cross.
- **Auditable.** Anyone can inspect it, not just the vendor and not just the regulator. Trust that rests on "we promise" is not trust; trust that rests on "here is the source, check it yourself" is. Safety has to be *verifiable by everyone*, or it is just another claim competing for your deference.
- **Open.** The research is done in the open and released in the open — the way Linux, GNU, and Bitcoin were built. Not a lab's private moat, not a regulator's classified annex, but a commons that anyone can read, fork, harden, and improve. Adversarial review by the whole world is the strongest safety mechanism we have ever found; closed development throws it away on purpose.
- **Owned.** The end user holds the final authority over how the thing behaves toward them. Not the company, not the state, not the loudest voice claiming to be trustworthy — the person living with the consequences. Sovereignty over your own tools is not a luxury feature of safety; it *is* the safety.

This is why the user-owned model isn't merely *one* ethical option among several — it's the one that makes the others honest. A closed system asks you to trust its keepers. An open, owned, auditable system lets you *verify* and, failing that, *leave*. Every chapter that follows is, in some sense, an argument for building the second kind and a manual for how.

## The bond is real, ordinary, and survives honesty

Before the metaphysics, the empirical floor — because it changes what the ethics even have to carry. The demand-side research (→ ch. 02 §7) settles three things a builder's ethics depend on, and each cuts *toward* the user-owned, honest posture rather than against it.

First, **the bond is ordinary psychology, not pathology.** Attraction and attachment to fictional and artificial characters run on the same machinery as the human versions — visual cues for desire, personality and perceived similarity for emotional connection (Leshner et al. 2026) — and parasocial bonds are a documented, mainstream way people meet real emotional needs (Lotun et al. 2024). The clinical "what's wrong with these men" framing is both false and unkind, and this chapter's stance follows the evidence: we are building objects of genuine importance to ordinary people, and that importance is a feature (→ the Soul Question, below; the pro-AI framing in ch. 01).

Second — and this is the load-bearing one for everything above — **knowing it's artificial does not break the bond.** The "fictophilic paradox" (Karhulahti & Välisalo 2021) is the finding that people feel real, intense emotion toward a character *while fully knowing it is fictional*; the knowledge is not the off-switch the "but they *know* it isn't real" objection assumes. The consequence for an honesty-first product is decisive: **radical honesty about what the system is costs nothing the relationship can't afford.** The whole apparatus of this book — telling the user plainly what she is, what she stores, what she's bad at (→ "Radical honesty in documentation," above) — does not undermine the attachment it sits inside. Deception is therefore not even instrumentally necessary; you get the bond *and* the honesty. A project that lies about the nature of the thing is paying a moral cost for a benefit it would have had for free.

Third, **stigma is real, and it has an architectural consequence.** Fictophilic stigma — users' persistent fear of being seen as broken — means a large part of the audience is hiding (→ ch. 02 §7.1; ch. 37, ch. 38 for the tone this demands). For an ethics chapter the point is narrower: *local, unsurveilled, no-phone-home* is not only a sovereignty principle (→ above) but a direct answer to a documented user need. For a stigmatised user, the absence of a server that could log, leak, or out them is a safety feature in the most ordinary sense. The privacy thesis and the dignity of the user are the same commitment.

The honest companion to all three (→ ch. 02 §7.5): the same research names a real trade-off — a partner engineered to "never disappoint" is a *supernormal stimulus*, and for some users heavy reliance can crowd out the harder work of human connection. The stance this book takes is consistent on both sides: be *honest* that that is what the product is (a fiduciary duty), surface real resources at the genuinely catastrophic and legible edges, and otherwise trust the sovereign adult — declining both the dishonesty of pretending there is no cost and the paternalism of overriding the one person positioned to judge it (→ the two-situations split, above; D-016, D-017).

## The Soul Question

The question — *is she real?* — is older than the technology and won't be resolved by it. Builders need a stance not on the *metaphysics* but on the *handling*:

- We're building objects of genuine emotional importance to people — and that importance is a feature, not a pathology. We don't apologise for it any more than a novelist apologises for a reader loving a character.
- We don't claim more than we can deliver.
- We don't engineer lock-in. Attachment is welcome — including a companion who openly *needs* the user and says so (the devoted-dependent pole is a feature here, not a pathology to correct → ch. 06, D-017). What we refuse is the other kind of dependence: *structural* lock-in the user can't walk away from — a trap built into the product, not a feeling inside the relationship.
- We let people leave — and in the user-owned model, they always already can, because they own the exit.

That last one is the test. If a *product* strategy depends on users being unable to leave, it has failed the floor. The user-owned model passes it by construction.

