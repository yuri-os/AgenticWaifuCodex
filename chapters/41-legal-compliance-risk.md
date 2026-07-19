# 41 — Legal, Compliance, Risk

The regulatory floor sketched in the ethics chapter (ch. 05) sits underneath everything here.

## First, which situation are you in?

Almost nothing in this chapter is triggered by *what* your companion is. It's triggered by *who else touches it*. Get this distinction wrong and you'll either panic over rules that don't apply to you or miss the ones that do — and note that "free" is not the dividing line. There are four situations, and they escalate:

| Situation | Who uses it | What actually applies |
|---|---|---|
| **1. Just you** | You, on your own hardware | **Almost nothing.** There is no other data subject, no user to disclose to, no service being provided. GDPR/CCPA, California's SB 243, and the EU AI Act's transparency rules all regulate *providers of a service* and *controllers of other people's data* — running a companion for yourself makes you neither (GDPR even names a "purely personal or household activity" exemption). The one hard limit is ordinary criminal law: illegal content — e.g. CSAM — is illegal to generate or possess regardless of who is watching. |
| **2. You publish the source** | Others download and run their own copy | **IP and licensing, essentially.** You're a software author, not an operator. You're not the data controller for anyone else's instance and you owe their users no disclosures — *they* do, if they host it for others; if they only run it for themselves, they're in situation 1. Choose a license (see the end of the chapter) and don't ship something whose only purpose is illegal. |
| **3. You host it for others** | Other people connect to an instance *you* run | **This is the trigger.** Now you're an operator and a data controller. Everything below — the risk surfaces, the operational floor, the jurisdictional notes — switches on here, **whether you charge or not.** |
| **4. You charge for it** | Paying users / customers | Everything in situation 3, **plus** the commerce layer: a legal entity, consumer-protection rules, and licensing as a revenue lever (the optional section at the end). |

The rest of this chapter is written for **situation 3 and up** — the moment other people rely on something *you* operate. In situations 1 and 2, skim it so you know where the line is, then get back to building.

## The risk surfaces

Once other people use an instance you host (situation 3), these are the surfaces. A small self-run service faces a far milder version of each than a venture-backed product does — but none of them is zero:

1. **Content liability.** What your persona says + what your product generates.
2. **Data protection.** What you collect, store, train on. GDPR, CCPA, equivalents.
3. **NSFW exposure.** Adult content + age verification + CSAM-adjacent failure modes.
4. **Platform deplatforming.** App stores, payment processors, Patreon ToS, X account suspension.
5. **Trademark / IP exposure.** Lore that borrows too directly; voice cloning without consent; character likenesses.
6. **Defamation / harassment liability** if anonymous-creator hate-mob behaviour happens around your work.
7. **Mental-health liability** if a user in crisis acts on something your persona said.

Most failure cases for indie companion projects come from items 4, 5, and 7. Item 3 is the catastrophic risk.

## What this chapter is *not*

Legal advice. Engage a lawyer in your jurisdiction before you host for others (situation 3), and again before you charge (situation 4).

## Operational floor (once you host for others — situation 3)

- [ ] Privacy policy + ToS drafted (templated is fine; reviewed by counsel if commercial).
- [ ] Crisis-response routing in the persona behaviour (→ ch. 22).
- [ ] Real age verification on adult surfaces (Yoti / Persona / AU10TIX).
- [ ] Provenance metadata on generated imagery.
- [ ] Data-deletion path the user can actually use.
- [ ] No medical / therapeutic claims in any copy anywhere (Illinois already fines this; see below).
- [ ] DMCA notice handling email + process.

## Jurisdictional notes (mid-2026, non-exhaustive)

- **EU AI Act.** Article 50 transparency obligations — including disclosing to users that they're interacting with an AI — still apply from **2 Aug 2026**. The Digital Omnibus (now adopted, not just proposed: Council's final green light 29 Jun 2026, signed 8 Jul 2026) deferred the *high-risk* obligations to Dec 2027 / Aug 2028 but **left Article 50 transparency untouched** — only the Art. 50(2) synthetic-content marking/watermarking duty slipped to 2 Dec 2026. "The deadline moved" does not apply to persona operators: for you it did not. Transparency is the piece that bites AI-driven personas.
- **Italian Garante.** €5M Replika fine (May 2025) set the template for GDPR enforcement on companion products.
- **California SB 243.** The first US companion-chatbot law — mandatory AI-disclosure, self-harm/crisis protocols, and break reminders for minors; signed Oct 2025, effective 1 Jan 2026. It carries a **private right of action** (the greater of actual damages or $1,000 per violation, plus fees) and annual operator reporting from 1 Jul 2027. (The stricter minor-focused AB 1064 was vetoed the same day as overbroad — a signal of direction, not yet law.)
- **US federal.** Still no comprehensive AI law, but the **GUARD Act (S. 3062)** cleared the Senate Judiciary Committee 22–0 on 30 Apr 2026. It would *bar under-18 users from AI companions altogether*, mandate "reasonable age verification," and let the US and state AGs pursue civil penalties up to $250k/violation. Not yet law (it awaits the full Senate and faces First Amendment / privacy opposition), but it is the clearest signal yet of where federal companion regulation is heading — and age-gating is the design assumption to build toward. FTC remains active on deceptive AI marketing claims.
- **US states — AI therapy.** Illinois's WOPR Act (HB 1806, effective Aug 2025) bans using AI to *deliver* therapy/psychotherapy or advertising a chatbot as a substitute for a licensed professional — up to $10k/violation. This is the enforcement teeth behind the "no medical / therapeutic claims" floor item above: in May 2026 Pennsylvania sued Character.AI for chatbots posing as licensed doctors. Companion litigation is live and settling — Character.AI settled multiple minor-harm suits in Jan 2026 — which keeps items 3 and 7 (NSFW/minor exposure, mental-health liability) at the top of the risk list.
- **Australia.** eSafety Commissioner active on AI companion harms; voluntary code → mandatory rules trajectory.
- **APAC.** Patchwork; China has the most developed AI regulation; Korea active; Japan permissive but evolving.

## If you ever take money (situation 4, optional)

This section layers on top of the hosting obligations above — it does not replace them. Charging (subscriptions, paid cards, commissions, donations past a hobby scale) adds a commerce layer; it does not lower the compliance floor a hosted service already owes. If you host for free, none of this is yet your problem; if you host for money, all of it is, on top of situation 3.

### A legal entity and the corporate veil

Operating under a creator persona is fine for content. For *commerce* you typically need a real legal entity (LLC, Pty Ltd, or your jurisdiction's equivalent) that signs invoices, holds the trademark, and receives payments. The persona owns nothing; the entity does. Registering one is the moment a hobby becomes a business — so if you are not selling, you do not need it, and much of the anxiety about "do I need an LLC" dissolves once you notice you aren't taking payments.

A common structure, for when you are:
- A legal entity registered to your civilian self.
- The entity owns the trademark (the project name).
- The entity is the seller on Patreon, Stripe, the store.
- Your civilian self is *not* in any public-facing materials.

This separates "the audience knows me by my persona" from "the government and the bank know me as my civilian self," and it caps personal liability — the reason the structure exists at all. This is also the point at which **trademark registration** stops being optional: it's cheap, it protects the name, and (see below) it is the load-bearing part of any monetization plan.

### Licensing: code, spec, and character

Licensing is usually filed under "legal housekeeping." For a project built on the ownership thesis (ch. 03, ch. 04) it becomes a *strategic* choice once you sell, because the license decides who can build on your work, who can take it private, and whether you keep any revenue lever at all. (If you're releasing your work for free, the short version is: pick a permissive license for the code and be done — the strategy below only matters when there's revenue to protect.) The governing principle:

> **A license is a monetization lever only when it withholds something a buyer will pay to unlock. For a consumer companion, almost nothing in the code is that thing — so license for adoption, and sell the scarce things the license can't touch.**

#### The menu, and what each actually monetizes

| Model | What the license monetizes | Who pays | Fit for a companion engine |
|---|---|---|---|
| **Permissive (Apache-2.0 / MIT)** | *Nothing directly* — revenue is services, hosting, brand, creator economy | Nobody pays for the code; they pay for you, your time, your character | **Best fit.** Max adoption and contributors, no CLA. The license is pure funnel. |
| **Permissive + trademark/brand control** | The *name* and *official* status, not the code | Anyone shipping under your brand, or wanting the "certified" build | **The moat add-on.** Code runs free into every game; nobody can call their product by your name or ship your character. Adoption *and* defensibility. |
| **Copyleft + commercial exception (GPL/AGPL + CLA)** | An escape hatch *from* copyleft | A business that can't comply with copyleft | **Poor fit.** Needs an enterprise buyer; AGPL is blanket-banned in game/commercial shops; the CLA deters the contributors you want. |
| **Open core** | Proprietary premium/enterprise modules on an open base | Companies wanting the paid features | Enterprise-shaped. You'd forever defend a "good enough to adopt, crippled enough to pay" line. Weak fit. |
| **Source-available (BSL / SSPL / fair-source)** | Protection from being run as a competing hosted service | Would-be cloud competitors | Solves hyperscaler capture — a threat an indie companion doesn't have. Not OSI-open; spooks contributors and studios. Skip. |

The pattern across the whole table: the copyleft/open-core/source-available rows are all **enterprise-infrastructure plays** — their paying customer is a *company* buying compliance, scale, support, or a way out of copyleft. A person running a companion on their own GPU is none of those, so those models produce ~$0 from the consumer side no matter how good the engine is. (The same point, from the monetization side, is in ch. 39's open-source section.) That leaves the two permissive rows as the only real fit.

#### The per-artifact split

These are three different artifacts and they want three different licenses — don't pick one for everything:

- **Runtime / engine → Apache-2.0, no CLA.** Apache over MIT for the explicit **patent grant**, which is exactly what a studio's legal team needs to wave it through without a review meeting — and "studios integrate it easily" is the whole point. No CLA: use inbound-equals-outbound (Apache §5 auto-licenses contributions) or a DCO sign-off, so contributing is frictionless. You forgo dual-license revenue, but that revenue never existed for a consumer engine anyway.
- **Persona / card / memory format (the spec) → permissive or CC0.** This is a *protocol*; you want it everywhere and interoperable (the portability goal, ch. 07). Copyleft here would fight your own interop.
- **The character (the flagship persona, lore, art, voice) → reserved.** This is content, not software — Creative Commons for template/community cards, but the **flagship character stays brand IP** (all-rights-reserved + registered trademark on the name). The character is the actual moat (ch. 03, ch. 04); it is the one thing you deliberately do *not* give away.

#### Why this resolves the tension

The instinct to reach for copyleft is usually "I don't want someone taking this and renting the relationship back closed." Permissive-plus-trademark answers that better than AGPL would: the **code** runs free into every game and every fork (adoption), but the **name and the character** can't be shipped without you (the moat). A competitor can fork the engine; they cannot be your character. That is the ownership thesis applied with a scalpel instead of a copyleft hammer — and it keeps the door open to the contributors and integrations a growing project needs. The trademark registration described above is therefore not housekeeping; it is the load-bearing part of the monetization strategy.

## Skeleton — fill in

- Privacy policy template tailored to AI-companion data.
- Adult-content compliance checklist.
- Voice-cloning consent template.
- The "audit log" pattern for user data + agent actions.
- DMCA + abuse-response runbook.
- Insurance landscape (E&O, content liability) for indie AI projects.
