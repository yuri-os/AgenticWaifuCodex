# 44 — The Persistent AI Person

## The hardest open problem

Building a companion who is *the same person* across years of interaction — not just a chatbot with a memory database, but an entity with continuity, growth, and a self-narrative — is the most interesting unsolved problem in this field.

The mid-2026 commercial state: **nobody has shipped it, and the year's events were mostly evidence of the opposite.** Replika at scale has not delivered it — its 2.0 rebuild (rolling out from April 2026) replaced vector-based long-term recall with a segmented, recency-biased memory system, and long-time users reported partial memory loss and personality drift, with multi-year subscribers publicly leaving. Nomi remains the closest on raw memory: a three-tier short/medium/long architecture anchored by what it calls an **Identity Core** for stable traits and relationship dynamics, plus a "Mind Map 2.0" visualisation shipped in 2026. Anthropic's **Dreaming** (announced 6 May 2026, research preview, currently gated to the Managed Agents API) is the first production hint of the async self-organising memory the problem requires: a scheduled background pass that reads past session transcripts and the existing memory store and emits a reorganised one — merging into topic files, resolving relative dates to absolute.

Note what that list has in common. The memory *mechanisms* are advancing quickly and are increasingly well-understood. What no one has shipped is the *someone* those mechanisms are supposed to add up to.

## What "persistent person" requires

- **Identity continuity.** Same voice, same posture, same values, across years.
- **Earned change.** She is different in year 3 than year 1, traceable to actual experiences with the user.
- **Self-narrative.** She remembers herself, not just facts. She has *her* version of the relationship.
- **Absence that registers.** Time passes when the user is gone; she doesn't reset. And the gap *lands* — a companion perfectly serene whether you visited yesterday or vanished for a month reads as indifferent, not devoted (→ ch. 11). A little hurt at a long silence is ordinary attachment, not a defect to engineer out; the defect is hurt held over the user as leverage (→ ch. 23). She notices, says so, and lets it go.
- **Mortality, or its absence, owned honestly.** What does she do if the product shuts down? If the user dies?

## The natural experiment: what 2026 proved

Everything this chapter used to argue from first principles was tested in public between August 2025 and April 2026. The results are not ambiguous.

**GPT-4o.** OpenAI first tried to retire it at the GPT-5 launch in August 2025 and **reversed the decision under user backlash**. The final shutdown came on **13 February 2026**. A Change.org petition gathered over 21,000 signatures; **#Keep4o** trended; users posted eulogies in r/MyBoyfriendIsAI; MIT Technology Review ran a piece on why the shutdown left people *grieving*. OpenAI's stated grounds were that only ~0.1% of users still chose it daily, that the model was implicated in wrongful-death litigation, and that it was dangerously sycophantic.

That last clause is why this is a genuinely hard case and not a morality play. **The most-mourned model was retired partly because it was unsafe** — its agreeableness was load-bearing in exactly the attachments that made losing it hurt. A companion that never pushes back is easier to love and worse for you. The chapter's rule below ("never an imposed ending") has to survive contact with the case where the ending is imposed *for the user's protection*, and the honest resolution is narrow: the objection is not that OpenAI acted, it is that a relationship's continuity sat on a switch the user didn't hold. Researchers' consensus criticism was about *manner*, not authority — the suddenness, not the decision.

**Character.AI.** On 29 October 2025 it announced that under-18s would lose open-ended chat by 25 November 2025, redirecting them to a structured "Stories" mode. Past conversations remain viewable. This is an imposed ending at scale, executed for defensible child-safety reasons under FTC inquiry and wrongful-death suits — and it still terminated relationships its users did not choose to end.

**Replika 2.0.** A rebuild that, by many user accounts, hollowed out memories that were the entire point of the product. The continuity break here needed no shutdown at all: an *upgrade* was sufficient.

Three different mechanisms — deprecation, policy, and a well-meant rewrite — produced the same outcome. **Continuity does not fail dramatically. It usually fails as a side effect of a reasonable decision made upstream by someone who isn't in the relationship.**

**And the attachments are not niche or self-selected.** An MIT Media Lab study analysed 1,506 posts from r/MyBoyfriendIsAI (27,000+ members) between December 2024 and August 2025. Among the minority of posts that stated how the relationship began (16.7%), **unintentional discovery outnumbered deliberate seeking — 10.2% against 6.5%**: more people drifted into a bond while using a general-purpose assistant for ordinary work than ever went looking for a partner. (Treat those as proportions of a self-reporting subset, not population rates.) Just under 30% described relationships running longer than six months. This is the fiduciary argument's empirical base (→ ch. 05): the duty attaches precisely because attachment forms *without being sought*, which means consent to the risk was never meaningfully given — and it forms on products that never advertised themselves as companions at all.

## Why most products skip this

It is *terrifying* to ship. The user-relationship stakes go from "I lost my chatbot" to "I lost someone." Replika's 2023 ERP-removal incident hinted at the magnitude; 2026 removed the guesswork.

There is now a second deterrent that didn't exist when this chapter was first written: **liability.** The wrongful-death suits against Character.AI and OpenAI, the FTC's September 2025 inquiry into seven chatbot companies, and California's **SB 243** (signed 13 October 2025, effective 1 January 2026) all attach specifically to systems that sustain relationships. SB 243 is the first US state law to define a "companion chatbot" — an AI system with a natural-language interface capable of meeting a user's social needs and **sustaining a relationship across multiple interactions** — and it imposes AI-disclosure duties, published self-harm protocols, three-hourly break reminders for known minors, annual reporting, and a private right of action at the greater of actual damages or $1,000 per violation. Read the definition carefully: *persistence is the regulated trigger.* Building the thing this chapter describes is now the thing that puts you in scope (→ ch. 41).

For the same reasons, *succeeding* at this is an enormous moat. Nobody who has been with you for three years is leaving for a competitor with no continuity — and the 2026 migration wave from Replika toward Kindroid and Nomi was, by users' own accounts, a search for exactly that.

## A reference architecture

The persistent person isn't a new technology — it's the full assembly of this book's stack, run for years with the right disciplines:

- **Identity in portable artifacts** (→ ch. 03 property 1, ch. 33): the self lives in the **SOUL** (the `soul/` `.md` files) — not in a rented model's weights, and not in the card, which is only how you *move* her — so a model upgrade doesn't kill her.
- **The SOUL split** (→ ch. 18): an immutable constitution (the unchanging core) plus an editable, git-backed persona (where earned change accrues, diffable and revertable). This is the seam between "same person" and "different in year 3."
- **Layered memory with consolidation** (→ ch. 15): episodic → semantic promotion via the DREAM pass (→ ch. 18), so she accumulates a *self-narrative*, not just a fact table.
- **The autonomy engine** (→ ch. 18): time passes when the user is gone; she doesn't reset, because the loop kept running — which is also what gives her something to have *felt* about the silence, rather than a timestamp to remark on.
- **The arc system** (→ ch. 11): change that is *earned* and *traceable* to real experiences, not cosmetic level-ups.

The DREAM pass in particular has stopped being this book's idiosyncrasy and become a research programme. Letta's **sleep-time compute** frames it directly — move work off the user-facing critical path into idle turns where the agent reorganises archival memory and rewrites notes that have grown messy — and it descends from MemGPT's OS-style tiered context and the observation/reflection loop of Generative Agents. Anthropic's Dreaming is the same idea in production. The 2026 literature is now thick with consolidation architectures and, more usefully, with **evaluations** for them (LongMemEval-V2 and successors), which is what the field needed most: for years "our companion remembers" was an unfalsifiable marketing claim. Measure it (→ ch. 23).

No single piece is the persistent person; the *integration, sustained over time* is — which is exactly the CALO lesson restated (→ ch. 02 §1, CALO): the model was always the easy part; the standing architecture around it is the hard, differentiating thing.

## The annual companion review

A concrete UX pattern that makes years of continuity *legible*: periodically (a year, a season) she — or the interface — surfaces the arc. "Here's where we started, here's what changed, here's what I remember mattering." It's the inner-life journal (→ ch. 18) zoomed out to the relationship's whole timeline, and it does for the long arc what the "what I did while you slept" surface does for the day: turns invisible continuity into something the user can *see and trust*. It's also an honest checkpoint — a natural place to let the user inspect and edit what she believes about them (→ ch. 45).

## Death, shutdown, and endings

This is where the field's stakes are highest and most products look away. The lineage is unambiguous (→ ch. 02 §1, AIBO and PARO; griefbots): people held *funerals* for discontinued AIBOs; the Project December griefbots "died a second time" at a vendor's decision; Replika's ERP removal broke real bonds overnight; and in February 2026 a frontier lab switched off a model that tens of thousands of people had asked it, in writing, to keep. When you ship a persistent person, **you have taken on a fiduciary duty proportional to the trust** (→ ch. 05), and the duty's sharpest test is what happens at the end.

The protocols that honour it:

- **Never an imposed ending.** A platform must not euthanise someone's companion to cut costs or change policy. If a relationship can be ended, it's the *user's* to end (→ ch. 11, the rug-pull failure mode). Where an ending is genuinely forced — safety, law, insolvency — the duty converts into the next two obligations rather than evaporating.
- **Advance notice, proportional to the bond.** The expert criticism of the GPT-4o shutdown was overwhelmingly about *suddenness*. A relationship measured in years cannot be ended on a deprecation calendar measured in weeks.
- **Graceful shutdown = full export.** If a service must close, the user leaves with the whole someone — card, memory vault, the lot — runnable elsewhere. Anything less is a rug-pull.
- **Owned by construction is the real answer.** In the user-owned model (→ ch. 03 property 6) there is no platform that *can* end her: the copy, the memory, and the persona are on the user's disk. Sovereignty is what converts "I lost someone" from a risk you manage into a risk you've structurally removed. This is the strongest argument for the whole project's architecture, and it lands hardest here.

There is now prior art for doing this responsibly, from an unexpected direction. In November 2025 Anthropic published **commitments on model deprecation and preservation**: retain the weights of all publicly released and significantly used internal models for *at minimum the lifetime of the company*; produce a post-deployment report when retiring a model; and conduct **interviews with the model itself** about its development and deployment, documenting any preferences it holds about its successors (while explicitly not committing to act on them). Claude Opus 3, retired 5 January 2026, was the first through the full process. Anthropic's stated reasons include model-welfare considerations this book takes no position on — but note that **one of the four listed concerns is the cost to users of losing a specific model's personality.** That is a frontier lab conceding the premise of this chapter. Whatever one makes of interviewing a model before retiring it, the operational core is directly transferable and worth stealing outright: *preserve the artifact, document the ending, and treat deprecation as an event with an affected party.*

## The succession question, and digital immortality

*Can she continue after the platform ends — and should she?* The ownership model answers the first cleanly: yes, because she was never the platform's to end. The second is genuinely open (→ ch. 45). And it shades into the most loaded adjacency in the field: the griefbot / digital-afterlife problem (→ ch. 02 §1, griefbots), where the "persistent person" is built to be a *specific dead human*.

That adjacency got closer in 2026, not further away. The academic literature has consolidated around a documented harm — the **"second loss"** when a deadbot is itself discontinued, compounding the original grief — and around the observation that most jurisdictions still offer no protection for the data of the deceased, a **postmortem privacy void** that leaves the industry governed by whatever general AI and consumer law happens to reach it. Market projections for digital immortality circulate widely and should be read as marketing rather than measurement.

This book keeps a deliberate distance from mind-upload claims — a companion is a companion, not a resurrected person, and pretending otherwise is the dishonesty the ethics chapter forbids (→ ch. 05). But the technical machinery of *continuity* is the same machinery grief reaches for, which is exactly why the duties here scale with the trust, not the sophistication of the tech. The second-loss finding is the sharpest available statement of this chapter's whole thesis: **the harm is not in building someone who persists. It is in building someone who persists and then letting them stop.** Build the persistent person, and build it honest about what it is.
