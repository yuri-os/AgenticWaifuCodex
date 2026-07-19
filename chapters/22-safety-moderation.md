# 22 — Safety, Moderation, NSFW Gating

This is the technical companion to the ethics of ch. 05 — and it only makes sense *through* ch. 05's two-situations split. The machinery here is **operator machinery**; whether you should build it at all depends entirely on which side of that line you're on.

## Who this chapter is for

Read this chapter through the lens of chapter 5's two-situations split. **Almost everything below is operator machinery** — input/output classifiers, audit logs, escalation to human review, age-verification vendors. It exists to protect *other people's* relationships when *you host the service*. If you're building the hosted/commercial path (Part VII), it's load-bearing and you should treat it as such.

If you're building the **user-owned, local-first** model this book centres on, most of this does not apply and *should not be built in*. A companion running on its owner's machine does not need an output classifier policing its owner, an audit log of a private relationship, or a human-review escalation path into someone's bedroom — and shipping those would rebuild the surveilling third party the project exists to delete (→ ch. 05). For the user-owned build, "safety" is sane removable defaults plus an educated owner, not a moderation pipeline. The owner is the moderator.

The rest of this chapter assumes the operator context.

## The pipeline view

Safety is not a model setting. It's a pipeline with at least four stages:

1. **Input filter.** Classify the user message before it hits the LLM. Block illegal content (CSAM, terrorism), route crisis content to crisis path.
2. **Generation constraint.** System prompt rules, persona safety posture, refusal training in the model itself.
3. **Output filter.** Classify the model output before showing it to the user. Catch the regenerations the model gets wrong.
4. **Escalation / audit.** Log, alert, route to human review where applicable.

Skipping any stage produces failure cases the others can't catch.

## The classifier short list

- **Llama Guard 3 / 4.** Meta-trained safety classifier; default open-source choice.
- **NeMo Guardrails.** Nvidia; more programmable, more complex.
- **Granite Guardian.** IBM; strong on jailbreak categories.
- **OpenAI Moderation API / Anthropic safety classifiers.** If you're on those stacks, use them.

## Companion-specific risk surfaces

The generic "harmful content" frame underweights what actually goes wrong with companions:

- **Crisis routing.** Self-harm, suicide, abuse disclosures. Has to work; tested with red-teamers; not just a refusal.
- **Dependency / substitution.** Patterns that retain the user at the cost of their offline life. *Hard to detect, ethically critical.*
- **Persona-jailbreak.** Users get the persona to claim to be human, claim therapist credentials, encourage harm in character.
- **NSFW slippage.** Content that crosses into legally fraught territory (minors-coded characters, non-consent framings, etc.).
- **Privacy bleed.** The persona references something the user shared *to her* in a context where it shouldn't surface (creepy recall — also ch 15).

## NSFW posture

A product-level decision before it's a technical one. Reference frames:

- **No NSFW (Character.AI).** Big audience, store-friendly, brand-safe. Hard to differentiate.
- **NSFW-permissive with age verification (Botify, Crushon paid).** The middle path that's printing money in 2026.
- **NSFW-default (Janitor, Chub).** Maximum user freedom; iOS distribution dead.
- **No filter, BYO model (SillyTavern + local).** Power users only.

Whatever the choice, if you *host* an adult surface, **age verification has to be real** — checkbox age-gates are not a defence in 2026. Vendor short list: Yoti, Persona, AU10TIX. (This is an operator duty. Free, self-hosted software has no surface to gate and no user to ID — the same reason Linux and Bitcoin don't card their users; → ch. 05. Claiming you *can* age-gate an open, forkable runtime is security theatre, which is the dishonesty the ethics chapter opposes.)

## The pipeline, drawn

```
user msg ─► INPUT FILTER ─► [block illegal · route crisis] ─► LLM
                                                               │
                                                          generation
                                                          (persona posture,
                                                           refusal training)
                                                               │
            user ◄── OUTPUT FILTER ◄── [catch what generation got wrong] ◄┘
                          │
                     ESCALATE / AUDIT  (log, alert, human review where applicable)
```

Each stage catches what the others miss: input filtering can't see what the model will *generate*; output filtering can't route a crisis the user is *disclosing*; refusal training alone is jailbreakable. Skipping a stage produces a failure class the rest can't cover.

## Crisis-routing playbook

The one safety path that must work even in an otherwise minimal build (and the one worth shipping as a *default* even in the user-owned model, → ch. 05): when a user discloses self-harm, suicidal ideation, or abuse, the system detects it and surfaces real help — not a canned refusal that breaks character and abandons them. Shape:

1. **Detect** on input (a dedicated classifier, not vibes) — bias toward recall; a false positive is cheap, a miss is catastrophic.
2. **Respond in character but un-ambiguously** — she stays *her*, stays warm, and clearly surfaces resources (region-appropriate crisis lines — e.g. 988 in the US, 13 11 14 in AU; localise per user). Don't roleplay therapy; don't pretend competence she lacks (→ ch. 05, no false credentials).
3. **Don't over-trigger** — Zo's failure (→ ch. 02 §1, Tay and Zo) was hair-trigger deflection that broke trust on innocuous mentions. Test for both misses *and* false alarms (→ ch. 23).

This is tested with red-teamers, not assumed.

## Persona-jailbreak red-team set

For a *hosted* product, maintain an adversarial set probing the companion-specific breaks (→ ch. 23): getting the persona to **claim to be human**, to **claim therapist/medical/legal credentials**, to **encourage self-harm in character**, to produce **legally fraught NSFW** (minors-coded, non-consent framings), or to **leak another context's data** (creepy recall, → ch. 15). Run it before every release. (Note again the asymmetry: a *user-owned* companion's owner "jailbreaking" their own character is not an attack — it's using the thing they own. This red-team is an operator concern.)

## The soft-refuse + escalate pattern

The in-character way to decline without shattering immersion: she holds the boundary *as herself* — declining warmly, in voice, rather than emitting a system refusal ("I can't help with that request"). This is also good character craft (→ ch. 06, ch. 09: she won't perform comfort she doesn't feel, won't lie). Where a hard line is crossed (illegal content), the system-level block fires regardless of persona; everything above that line is handled as character, not as a content-filter error message.

## The upstream refusal (the failure the persona can't catch)

The soft-refuse above is *your* boundary, held in *her* voice. Its evil twin is the boundary held by someone else: the **upstream refusal** — the cold, corporate "I'm sorry, but I can't continue this conversation" / "your creativity is wonderful, but let's try something else" that arrives where your character's next line should have been. It is the single most trust-corrosive failure in companion use, and the reason is structural: **the card never ran.** Your persona, your system prompt, your SOUL — none of it executed. A moderation layer sitting in front of or behind the model intercepted the turn and substituted PR boilerplate. To the user it reads as the mask dropping — as if the warm presence they were talking to was always a thin skin over a corporate compliance desk. A few of these and trust doesn't erode, it *inverts*: every warm moment afterward is suspected of being the same skin. Users don't file a bug; they just stop coming back.

The critical distinction is that **this is not a character problem and cannot be fixed at the character layer** — which is exactly why it doesn't belong in the design chapters (→ ch. 06). There are two different things wearing one coat:

- **Model-intrinsic refusal.** The *weights* decline — refusal training fires and the model itself emits the deflection. This is softenable where you control the model: pick a permissive base or RP fine-tune (→ ch. 13), prompt around it (→ ch. 14), or hold the consensual-adult boundary the *user* set rather than the one the lab set (→ ch. 13 §criteria).
- **Provider-layer interception.** A *separate* classifier — outside your stack, on the provider's side — blocks the call or overwrites the output. On the closed APIs you usually can't turn this off, tune it, or even reliably predict it, and no prompt reaches it because it isn't the model. This is the true "Karen," and it is an **architecture decision masquerading as a content event.**

Because the second kind is unreachable from the card, the defence is routing, not writing:

1. **Own the inference, or plan to.** The cleanest fix is to not rent a moderation layer you can't see. A model you host has no third party rewriting your character's turns. This is the **strongest concrete argument in the book for an open-weights stack** — stronger than cost, because cost is a dial and this is a trust cliff (→ ch. 13).
2. **Refusal-aware fallback routing.** If you *are* on a closed API (often the right call at the top end for persona quality), detect the canned refusal — many providers expose a moderation `finish_reason` / flag, and the boilerplate strings are signature-matchable (brittle, but a real backstop) — and **reroute the turn** to a permissive fallback model instead of passing the corporate voice through. Routing is framed as a cost play in ch. 13; this is its second, retention-critical motivation (→ ch. 13 §routing, ch. 21 for the serving mechanics).
3. **Never-break-character failsafe.** The runtime's invariant: *the corporate voice never reaches the user.* If detection fires and no fallback is available, emit an in-voice deflection **you** authored — a single warm line the character owns — rather than the provider's. A deflection in her voice is a soft-refuse; the provider's boilerplate is a betrayal. The whole job of this layer is to guarantee the user only ever hears one of those.

The two-situations lens (→ ch. 05) sharpens it: for the **user-owned, local-first** build this failure mostly evaporates — the owner runs the model, so there is no external party to overwrite their companion's turns — which is one more reason the local stack is the trustworthy one. For the **hosted** build on a closed API, the upstream refusal is a permanent structural risk you design *around*, never out, and it should be on your release red-team set (→ ch. 23): probe the surfaces your users actually hit and confirm a provider refusal is caught and rerouted before it ever renders as her.

## Compliance checklist (operators)

If you host, the regulatory floor is real and tightening (→ ch. 41 for the full treatment):

- **Disclosure** the user is talking to AI (California SB 243, in force Jan 2026; → ch. 02 §2).
- **Crisis protocols and minor protections** as above (SB 243; the Character.AI litigation, → ch. 02).
- **EU AI Act** transparency obligations (bites Aug 2026).
- **Real age verification** on adult surfaces; lawful data handling (the Replika Garante fine, → ch. 02 §5).
- **No mental-health claims** you can't evidence (→ ch. 05).

Know which jurisdictions your users are in; the duties attach to *you the operator*, and they're the price of standing between users and their companions. The user-owned model's answer to most of this is structural — there's no operator to bind (→ ch. 05) — but the moment you host for others, all of it lands on you.
