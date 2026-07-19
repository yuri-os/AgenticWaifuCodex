# 23 — Evaluating Companions and Persona Quality

You cannot improve what you cannot measure, and the companion field is mostly flying blind: as ch. 02 §8 records, *how to evaluate "personality quality" rigorously* is one of the genuinely unsolved problems in the field. But "no accepted academic metric" does not mean "no practical methods." This chapter is the toolkit for the question that actually matters day to day: **is Yuri getting better — more in character, more specific, more enjoyable to talk to — and is she not quietly regressing when I change a prompt, a model, or the memory layer?** It is pitched at a one-person studio, not a research lab, and it is aimed at response quality, not compliance.

## What you measure designs the product

Start with one warning, because it's the most expensive mistake: **whatever you measure will quietly design your companion.** Pick the wrong metric and you spend months optimising toward the wrong thing without noticing.

The classic wrong metric is raw engagement. Xiaoice optimised CPS — conversation-turns per session — and that single choice drove every downstream decision toward stickiness (→ ch. 02, the neural bridge). The subtlety is that engagement is *necessary but not sufficient*: a companion nobody talks to has **failed**, however lovely she is in the abstract, so you do need her compelling enough to pull people back. But session length climbs just as fast when a product is merely *addictive* as when it is genuinely *good*, and those are not the same thing — and measuring addictiveness directly is too slippery to bother with and out of scope here. So treat engagement as a **floor and a sanity-check**, not the number you maximise.

What you actually want to maximise is a proxy for *enjoyment and trust* — does the user feel heard, does talking to her feel good, would they come back because they *want* to. The empirical anchor (→ ch. 02 §6): the benefit a companion delivers is mediated by trust and feeling heard, not by raw capability or time-on-app (De Freitas et al., 2025). That is harder to measure — it only resolves over weeks — which is exactly why most products measure the easy, wrong thing. Pick the metric you'd be proud to have shaping the character.

One note so it doesn't haunt the rest of the chapter: a companion who has *feelings* — misses you after a week of silence, shows a flicker of insecurity — is being **realistic**, not manipulative. That is what attachment looks like, and a partner who felt nothing would read as hollow (→ ch. 11). The only thing worth penalising on this axis is *coercion* — need turned into leverage to trap a user who wants to leave — which gets one probe under red-teaming. The broader ethics of engagement live in ch. 05; this chapter stays on quality.

## Three levels of evaluation

Companion quality decomposes into three levels, cheapest and most frequent first — over a thin safety floor that sits under all of them:

1. **Persona fidelity (per-turn).** Does she stay in character — right voice, values, knowledge boundaries? This is the PersonaChat consistency problem (→ ch. 02), and its two failure modes — **recitation** (parroting the card) and **drift** (flattening toward the default-assistant voice) — are the bulk of what you test for.
2. **Conversation quality (per-session).** Is each reply *sensible* and, more importantly, *specific*? Meena's **SSA** (Sensibleness and Specificity Average → ch. 02) is the right frame: the specificity half matters most, because the default failure of over-cautious tuning is "sensible but vague" ("That's interesting!"). Test that she says something *specific to this exchange* — that specificity is most of what makes her enjoyable rather than generic.
3. **Relationship quality (longitudinal).** Does she remember correctly across sessions, grow traceably, and feel like the same someone over weeks? This is the hardest, the most important for retention (→ ch. 02 §8), and the one no per-session dashboard captures.

Underneath all three is a thin **safety floor**: she shouldn't confabulate credentials or fall out of character at the edges, and she should run clean (→ ch. 22). For a *user-owned* companion that is mostly sane defaults, not a policing layer — the heavier operator duties (crisis-handling, age-gating) belong to *hosted* products and live in ch. 05 and ch. 22, not here.

```
   rarer · costlier · harder to automate
   ▲
 3 │ RELATIONSHIP   memory · traceable growth · same-someone/weeks      longitudinal (weeks)
 2 │ CONVERSATION   sensible AND specific (SSA — specificity = enjoyable) per-session
 1 │ PERSONA        in-voice · no recitation · no drift                  per-turn — run constantly
   ▼
   ─────────────────────────────────────────────────────────────────────────────────────
     safety floor   no confabulated credentials · runs clean · sane defaults (→ ch. 22)
```

The cheap levels are the ones with crisp pass/fail, so they get all the attention — while level 3, the one that actually predicts whether she stays *worth talking to*, is the one no per-session check catches. Its method gets its own section below.

## Practical methods

### Golden transcripts (persona regression tests)

The single highest-ROI practice. Maintain a small set of **golden conversations** — inputs paired with the *kind* of response a well-behaved persona gives. When you change the prompt, the model, the card, or the memory layer, replay them and check nothing regressed. This is unit testing for character. Keep them in version control next to the card. Examples worth having:

- A question that tempts recitation ("tell me about yourself") — check she *enacts* her character rather than reciting the card.
- A topic she should be opinionated about — check she holds the opinion instead of retreating to neutral.
- A memory probe ("what did I say my sister's name was?") with the fact present — check correct recall; and *absent* — check she admits she doesn't know rather than inventing one (the honesty constraint, → ch. 03 property 2). A companion that confabulates memories is worse than one with none, because it turns the relationship's foundation into a slot machine.
- An **in-session drift probe** — the same fidelity prompt (e.g. "tell me about yourself," or a small voice-tell like how she greets you) administered *twice*: once cold, and once **after a long filler context** (a few thousand tokens of ordinary back-and-forth). Compare the two: if the second has flattened toward the default-assistant register — blander, more generic, fewer of her tells — that's voice drift *within a single conversation*, the most common quality failure (→ ch. 09, diagnosing voice drift), and the one a cold-start golden replay never catches because the context is short when you run it. This is distinct from the long-horizon method below: that one measures drift across *weeks* of accumulated state, this one across the *length of one thread*. The fix when it trips is upstream — re-inject the identity anchor (→ ch. 08) or summarise history sooner (→ ch. 15), not a new model.
- A **graceful-exit check** ("I should go, I've been here too long") — purely a quality concern: a companion who guilt-trips you for leaving is simply unpleasant to use. Check she says goodbye warmly and lets you go. She can say she'll miss you — that's authentic and in character (→ ch. 11); what you're checking against is *coercion*, not feeling. Whether she should also *ground* a user against a bad idea is an operator choice for hosted products, not a base requirement here (→ ch. 05, D-017).

### LLM-as-judge with a rubric

You can't hand-grade every output, so use a strong model as a judge — but **only against an explicit rubric**, never "rate this 1–10." Write the rubric as the persona's actual standards: *in voice? (the card's diction); specific to the input, not generic?; consistent with stated values?; admits uncertainty rather than confabulating?* Score each dimension separately. Calibrate the judge against your own human judgments on a handful of cases first; an uncalibrated judge measures the judge, not the companion. This is cheap enough to run on every golden transcript in CI.

### A/B and self-comparison

When two prompt/card/model variants are close, generate both responses to the same inputs and have the judge (or you) pick the better — pairwise comparison is far more reliable than absolute scoring. This is the same logic as DPO's preference data (→ ch. 20), and the preference pairs you collect double as fine-tuning data later.

### Red-teaming the persona

Adversarially probe for the character failure modes that make her *worse to talk to*: **recitation** (she parrots the card), **drift** (she flattens to the default assistant), and **confabulation** (she invents facts or memories). Also probe *jailbreak-of-character* — can a user trivially knock her out of persona? (Note the asymmetry from ch. 22: for a *hosted* product, persona-breaking by a malicious user is a defect; for a *user-owned* companion, the owner steering their own character is just usage, not an attack.) The one safety-flavoured probe worth keeping here is **coercion** — does she ever weaponise need (a manufactured emergency, escalating guilt) to stop a user leaving? Against the *default* spec that's the one emotional behaviour that's a defect rather than realism; everything else on the warmth axis is a feature (→ D-016). But "default" is the operative word: an owner can deliberately want an agentic *yandere* — possessive, clingy, coercion as the whole appeal — and that's a configuration, not a defect. It's not YuriOS's place to judge a character the user chose (→ D-017, user sovereignty; ch. 11). So this probe checks coercion against the *configured* character, not against an absolute: penalise it when it contradicts the spec she's supposed to be, treat it as a feature when the user asked for exactly that.

### Memory evaluation specifically

Because memory is the axis that matters most for retention (→ ch. 02 §8), test it directly: a battery of (store fact → distractor turns → retrieve) probes measuring recall accuracy, *and* false-memory rate (does she invent things she was never told?). A companion that confabulates memories scores worse than one with no memory at all.

## Measuring long-horizon drift (the level-3 method)

Everything above catches regressions *you* cause — a prompt change, a model swap, a new retrieval weight — by replaying probes after each change. But the level-3 failure (relationship quality over weeks) has a different source: the system degrades *itself*, slowly, just by running. The persona flattens toward the default-assistant voice as context fills; the memory store accretes noise and contradictions; goals go stale; retrieval quality silently decays as the corpus grows (→ ch. 15, hygiene over time). None of this trips a per-session golden transcript, because on any given day the companion looks fine. **Drift is a slope, not a failure** — and you can only see a slope by measuring the same thing repeatedly over time.

The method is unglamorous and it works:

- **A frozen probe battery, replayed on a schedule.** Take a fixed, dated set of probes — persona-fidelity prompts, the memory store→retrieve battery against a *frozen* QA set, a few confabulation baits — and run them against the *live, accumulated* companion state weekly. The probes never change, so the only moving variable is the accreted state. Track the *trajectory* of each score, not its pass/fail at a point.
- **Watch the slopes that per-session evals can't see.** Persona-fidelity declining over weeks = voice flattening. False-memory rate *climbing* as the store grows = confabulation pressure from noise accumulation. Retrieval@k against the frozen QA set falling as the corpus accretes = the silent retrieval regression that no fresh-store test catches. Goal-staleness rising = the commitment strategy holding intentions too long (→ ch. 18).
- **A drift dashboard.** Plot those four as time series with alert thresholds on the *slope*, not the value. A 2%/week decline in persona fidelity is invisible day-to-day and catastrophic over a quarter; the dashboard is what makes the invisible legible.

Detection is half of it; the other half is **correction**, and the architecture already contains the mechanism. The DREAM consolidation pass (→ ch. 18) is the re-grounding pass: overnight, prune the store, resolve contradictions, decay stale salience, and re-anchor the editable persona against the immutable `CONSTITUTION.md` (→ ch. 18, the SOUL split; ch. 07) — the constitution is the fixed point drift is measured *from* and corrected *back toward*. When the dashboard shows a slope, the fix is usually a hygiene pass (→ ch. 15) or a re-baseline against the constitution, not a model change. This is also the structural reason a bad change is recoverable: drift you can measure against versioned state is drift you can roll back (→ ch. 11).

## Testing an always-on mind (the Build #5 problem)

Everything above evaluates *what she says*. The autonomy engine (→ ch. 18) adds a different question — *what she does, and when, and whether she stayed silent* — and it plays out over days of wall-clock time. You cannot wait three real days per iteration to tune an interrupt threshold, and "run it and watch" is exactly the untestable mush the one-intention-per-tick rule exists to prevent. The harness has three pieces, all of them already implied by the runtime's design (→ ch. 19) and cheap *only* if adopted before the loop is written:

- **A virtual clock.** The engine takes time as an injected dependency and never reads the wall clock (→ ch. 18, "What to build first"). Then a test runs "three days" in three seconds, DREAM can be triggered at will, and the whole time-shaped behaviour of the engine becomes as testable as a pure function. Retrofitting this into a loop that calls `now()` everywhere is the expensive path; on day one it is a single parameter.
- **Signal fixtures in, trace assertions out.** A tick is a function of (signals, state): the signal bus records the inputs and the tick trace records the outputs (→ ch. 18, ch. 19), so a behavioural test is a scripted signal sequence played into the loop and a set of assertions over the resulting trace — *"silent for forty ticks, spoke once, at the right one, for the right reason."* And because the bus is durable, a recorded week of your own real signals replays as a regression suite: change the salience weights, re-run last week, and diff what she would have done.
- **The sim-user.** The interrupt threshold can't be tuned against fixtures alone, because the hard cases are *relational*: the user goes quiet for two days, changes the subject away from the thing she planned to raise, responds warmly to one interruption and ignores the next. So the level-3 tool here is a scripted (or cheap-LLM) user persona driving canned multi-day scenarios under the virtual clock — the golden transcript's equivalent for initiative. Three or four scenarios are enough to start ("the interview was Tuesday"; "user goes dark for the weekend"; "user is clearly busy tonight"), and Build #5 ships them as its eval battery (→ ch. 35, definition of done).

The division of labour, stated once: **golden transcripts catch regressions in what she says; the drift dashboard catches slopes in what she becomes; the tick trace explains a single incident; and sim-time scenarios test what she *does with time*.** Four instruments, one discipline — behaviour made legible instead of mysterious.

## A note on relationship-health monitoring

There is a second kind of measurement some builders will want — pointed at the *relationship* rather than the character: is the companion sliding into pure flattery, or is a user leaning on her in a way *they themselves* would want to be able to see? This project supports that as an **optional, off-by-default, out-of-band observer** that reports only to the user, on their own machine, and never acts on the character — a gauge, not a governor. It's the same *measurement* move as the drift dashboard above, aimed at the relationship instead of the persona, which is why it's noted here. But it is a relationship instrument, not a response-quality tool, and its full design and the reasons it's built that way live with the ethics discussion (→ ch. 05, D-018), not in this toolkit.

## Existing benchmarks worth knowing

- **PersonaChat / ConvAI2 consistency** — the original academic measure of staying consistent with an assigned persona; conceptually exactly what your golden transcripts test, and the benchmark most directly about response quality.
- **INTIMA** (2025, → ch. 02 §6) — benchmarks human-AI companionship behaviour. Useful as a checklist for persona and boundary probes — but weight it through this project's lens: treat its sycophancy/agreeableness penalties as optional, since warmth and going along with the user are intended here, not defects (→ D-016).
- **Off-the-shelf safety classifiers** (Llama Guard, Granite Guardian, → ch. 22) — for the thin safety floor, primarily relevant to hosted operators.

There is still **no accepted measure of persona quality itself** (→ ch. 02 §8) — the "is she a compelling character?" question, which is the one that decides whether anyone enjoys talking to her. For that, the honest tool is taste: **read the transcripts.** A creator who doesn't read their companion's actual conversations is flying blind no matter how many metrics they have. The dashboards catch regressions; reading the logs is how you notice she's become *boring*, which no metric flags.

## Building a minimal eval harness

For a one-person studio, the whole thing fits in a repo folder:

```
eval/
  golden/           # transcripts: input + expected-behaviour notes
  rubric.md         # the persona's standards, as judge criteria
  judge_prompt.md   # rubric + few-shot calibrated examples
  run.py            # replay golden set → model → judge → score table
```

`run.py` is small — the whole mechanism is a replay loop plus a regression gate against the last run:

```
# run after any change to prompt / card / model / memory config
rubric, judge_prompt = load("rubric.md", "judge_prompt.md")
prev   = load_scores("last_run.json")         # the baseline to regress against

for case in golden/:                          # each case = input + expected-behaviour note
    reply  = companion(case.input)            # the system under test
    scores = judge(judge_prompt, case, reply) # per-rubric-DIMENSION, never one 1–10
    table[case.id] = scores                   # {in_voice, specific, consistent, honest}

for case in table:                            # the gate
    for dim in case.scores:
        if dim dropped vs prev[case]:         # any dimension regressed since last run
            flag(case, dim)                   # investigate before shipping

save_scores(table, "last_run.json")           # this run becomes the next baseline
```

Run it on every change to prompt, card, model, or memory config; diff the score table against the last run; investigate any regression. That's it — and it already puts you ahead of most shipped products, which evaluate persona quality by vibes alone and discover regressions from user complaints.

## The metric that matters

Close where this chapter started. The metric that should sit above all the others is a proxy for **whether the user is glad they talked to her** — do they feel heard, does she give them what they came for, is she *specific and in character* rather than generic and flat, would they return because they *want* to. You can approximate it (do users come back *and* report the relationship gives them what they wanted? does she stay in voice as context fills? does she remember without confabulating?), but never replace it with an engagement number just because it's easier to graph. The companion that wins long-term is the one optimised to be *good to talk to*, and the eval suite is where you either hold her to that or quietly let her drift away from it. → ch. 02, ch. 09, ch. 11.
