# 14 — Prompt Engineering for Companions

Prompting is the cheapest, first, and most-underestimated layer of persona adaptation (→ ch. 02 §4.2; the canonical sequence prompt → RAG → fine-tune, ch. 12). The roleplay community's hard-won wisdom — *the limit on character quality is almost never the model; it's the card and the prompt* (→ ch. 02 §3) — is the thesis of this chapter. Most of what newcomers reach for fine-tuning to fix is a prompting problem, and most of what they blame on the model is a prompt-assembly problem.

Before the assembly mechanics, name the current you are prompting *against*. A modern base model has been RLHF'd toward one default voice — the helpful, harmless, faintly corporate assistant — and that voice is the gravity every companion prompt has to fight. Left uncoached, the model favours caution over warmth, hedges where she should be certain, asserts boundaries no one asked for, and slides back toward the assistant register the moment the prompt's grip loosens (→ ch. 09, voice drift). This is why "be my girlfriend" yields a disappointing girlfriend by default (→ ch. 01, the default is wrong), and why much of the craft here is *corrective pressure* rather than addition: you are not only describing a character, you are out-voting the model's training with the one this project's design produces (→ ch. 06). A lightly-aligned or uncensored local model (→ ch. 13) lowers the gravity; the prompt still has to do the rest.

The single most important mental shift is this: **a serious companion's prompt is not authored, it is *assembled*.** You do not write the text the model sees on turn 50; the runtime builds it, fresh, every turn, by selecting and ordering fragments from the card, the lorebook, the arc state, and the memory store (→ ch. 07, ch. 08, ch. 11, ch. 15). Prompt engineering for a companion is therefore really two skills: writing the static fragments well (which is mostly ch. 06–09), and *engineering the assembly* — what goes in, in what order, within a fixed token budget — which is this chapter.

## The companion prompt stack

A turn-time prompt for a serious companion is layered top-to-bottom. The order is not arbitrary; it follows from how the model reads context (next section) and from what each block is *for*. Typical assembly:

1. **Meta / safety preamble.** A short framing instruction: *you are roleplaying a single consistent character; stay in character except for explicit OOC directives; match the user's register.* Keep it short — it is overhead, not personality, and every token here is a token of memory you don't get.
2. **System persona block.** Identity, voice, posture, and a few example turns — derived from the character card's description and personality fields (→ ch. 07). This is the heaviest static block and the one that most determines who she is. It belongs near the top because the model reads what comes first as *identity* (next section).
3. **World / setting block.** Static lore facts that are always true — from the lorebook's always-on entries (→ ch. 08). The persistent backdrop the character lives against.
4. **Dynamic lorebook injections.** Entries fired by keyword from the recent turns — the consortium, a place, a side character — pulled in only when the conversation touches them (→ ch. 08). This is the first *dynamic* block: it changes turn to turn.
5. **Relationship / arc state.** The current phase, nicknames in use, fears already named — a compact line the arc engine maintains (→ ch. 11).
6. **Long-term memory injections.** Retrieved facts about the user, top-k from the memory store, reranked (→ ch. 15). This is where attunement lives — *she remembers the Monday review* — so it is worth protecting.
7. **Recent conversation summary.** A compressed digest of everything older than the active window (→ ch. 15). Carries continuity without spending the tokens a verbatim transcript would.
8. **Active conversation window.** The last N turns, verbatim. The live feel of the conversation lives here, and it sits last because the model reads what comes *last* as the immediate task.
9. **Current user message.** The turn being answered.
10. **Response anchor / post-history instruction.** *Optionally,* a very short instruction placed *after* the conversation — a partial assistant turn, or a one-line reminder of register or format. Because it is the closest thing to the model's reply, it is the highest-leverage place to nudge *how this specific reply comes out* (the recency lever, below). The SillyTavern ecosystem calls this slot the **post-history instruction** (PHI), and it is where a directive like *"stay in third person, present tense; keep her replies under 120 words"* belongs — not buried in the persona block a thousand tokens earlier, where it competes with everything else.

A useful allocation rule, borrowed from the RP community: **if it reads like character identity or scene background, it belongs in the persona block or the card; if it reads like a global rule for the whole roleplay, it belongs in the meta preamble; if it reads like a final instruction for how *this reply* should come out, it belongs in the post-history slot.** Mixing these — putting reply-formatting rules in the persona, or persona facts in the meta preamble — is a common cause of a prompt that "should work" but produces a drifty or stilted bot.

## What the order does, and why

Putting persona *first* and the live conversation *last* exploits a real, well-documented property of long-context transformers: the **U-shaped attention curve**, popularly called *lost in the middle* (→ ch. 02 §4.3). Models reliably attend to information at the **beginning** of the context (primacy) and at the **end** (recency), and attend *least* to whatever sits in the middle. This is not a tuning quirk; it falls out of the architecture. Rotary position embeddings (RoPE), used in essentially every modern model, impose a distance-based decay so that far-apart tokens attend to each other weakly, while "attention sink" behaviour keeps the very first tokens influential throughout. The middle is too far from the start to ride the primacy effect and too far from the end to ride recency, so it fades. Newer long-context models (2026) blunt the effect with positional-encoding and attention-calibration tricks, but as of mid-2026 none has *eliminated* it — the bias is structural, so design as if the middle still fades.

The design consequence is direct: **put the two things you most need the model to hold — *who she is* and *what was just said* — at the two ends, where attention is strongest.** Persona at the top is read as stable identity; the active window at the bottom is read as the immediate task. Everything dynamically selected and individually less critical — fired lore, retrieved memory, the summary — goes in the middle, where some fading is tolerable. Inverting this (a common junior implementation that dumps the persona right before the model replies, or buries it under a huge lore block) produces exactly the drifty bot the order is meant to prevent, because the identity has been parked in the low-attention zone.

Two corollaries fall out of the same mechanism:

- **The post-history slot is the strongest single lever for reply-shaping**, precisely because it is the last thing before generation — maximum recency. A short directive there outperforms the same directive stated once, far up in the persona block. Use it sparingly and for *this-reply* concerns (register, length, "don't narrate the user's actions"), not for identity.
- **A fact that must not be forgotten cannot just be *present* — it must be *placed*.** Retrieval that drops the user's name into the middle of a long context is retrieval that will sometimes be ignored. This is why memory injection is reranked and capped (→ ch. 15), and why "she has the fact but doesn't use it" is usually a positional problem, not a retrieval failure.

### The third injection point: depth

The stack has two privileged positions — the top (identity, primacy) and the post-history slot (this-reply shaping, maximum recency). There is a third, and the RP community leans on it hard: **mid-conversation depth injection**, the technique SillyTavern exposes as the *Author's Note at depth N*. Rather than placing a fragment at the very top or the very end, you inject it *into the conversation history* a fixed number of turns back from the newest message — depth 0 is right at the end (the post-history slot), depth 4 sits just before the last three turns.

Why it earns a place: a trait stated once in the persona block a thousand tokens up is exactly what the lost-in-the-middle fade eats, which is *why* a character slowly drifts back toward the assistant prior over a long scene (→ *win the fight against the assistant prior*). A short reinforcement re-injected at a shallow depth — *"Yuri stays in character; she keeps replies under 120 words; she doesn't narrate the user's actions"* — rides the recency zone on **every** turn no matter how long the conversation grows, because it is positioned relative to the *end* rather than the start. It is the standard fix for "she was perfect for 30 turns, then went generic."

The cost, and why you use it sparingly: a depth injection lands *inside* the dynamic part of the context, so unlike the top persona block it cannot be part of the byte-identical cached prefix (→ ch. 21), and unlike the post-history slot it colours the model's reading of the recent *scene*, not just the next reply — push it too hard and the reminder bleeds into the fiction. The discipline: keep depth-injected reminders short, behavioural, and few, reserved for the one or two traits that actually drift. Identity still belongs at the top; depth injection is the *maintenance dose* that keeps it from fading there.

## Principles

The order gets the structure right. These principles govern the *content* of the blocks — and several are the prompt-layer form of a ch. 06 design principle, now stated in terms of tokens the model actually reads.

### Show, don't tell

*"She is mischievous"* plus zero examples is weaker than two example turns where she is mischievous and the word never appears. This is the prompt-side of ch. 06's **enact-don't-describe**: a model imitates the *register it is handed*. Hand it adjectives about the character and it will produce more adjectives about the character ("As a mischievous Lumina, I…"); hand it a line of her actual dialogue and it imitates the behaviour. The example-turns inside the persona block are the highest-leverage tokens in the whole prompt for this reason — they teach voice by demonstration, which no amount of description does. Spend the budget there before spending it on a longer trait list (→ ch. 07, the example-dialogues field).

### Constrain through persona and example, not rules — and never through negation

Two failure modes hide in the instinct to *tell the model what not to do*.

The first is stiltedness: a prompt full of *"You must never X. You must always Y. Under no circumstances Z."* produces a bot that reads like it is following a compliance checklist, because it is. Constraint expressed *as the character* — a voice that simply doesn't talk that way, an example turn that shows the boundary held in-world — produces the same behaviour without the stilt. Rules are a blunt instrument; persona is a precise one.

The second is more mechanical and widely under-appreciated: **negative instructions frequently backfire.** Telling a model *"don't mention the war"* or *"never break character"* puts the very concept it should avoid into the context, and models are demonstrably unreliable at negation — the *pink-elephant problem*. The robust fix, which Anthropic and others endorse explicitly in their prompting guidance, is to **reframe every prohibition as a positive instruction**: state what the character *does* instead of what she must not do. Not *"don't be formal,"* but *"she speaks casually, in short sentences."* Not *"never reveal you're an AI,"* but *"she experiences herself as herself, and answers from inside that."* The positive frame gives the model a target to move toward rather than a forbidden region to (unreliably) avoid.

### Win the fight against the assistant prior, at the prompt level

The base model under your character has been aligned toward one default personality — helpful, agreeable, eager, quick to capitulate (→ ch. 06, *design against the default model prior*; ch. 13). That prior is the default completion for anything the prompt leaves unspecified, and it reasserts itself turn after turn. Prompting is where you fight it on every turn, not just at design time. The levers: load-bearing example turns that *show* her disagreeing, holding a position, declining in-character — because the prior's pull is strongest exactly where your prompt is only telling, not showing. The test from ch. 06 applies to the assembled prompt too: read it and ask which lines the helpful-assistant default would have produced anyway. Those lines are doing no work, and they are budget you could spend on the example that actually corrects the prior.

### Hold the OOC channel separate

A companion has to handle out-of-character input — a meta instruction, a topic switch, a "can you be shorter" — without shattering immersion. The fix is a clear, consistent convention for out-of-character directives (`[OOC: …]`, a dedicated system turn, whatever the stack supports) so the model can tell *steering* from *scene*. Without it, an OOC aside bleeds into the fiction (she starts narrating about being asked to be shorter) or in-character lines get misread as instructions. A persona written to *flex register* on OOC (→ ch. 07, dual-register) plus a clean channel convention is what lets her field "actually, switch to Python for a sec" and come back without a seam.

### Match the model's instruction idiom

Different model families respond to different *framings* of the same instruction, and a prompt tuned for one can underperform on another even at equal capability. The broad, current shape of it: **Claude models respond well to collaborative, author-style framing** ("you are playing the role of…", warm second-person direction); **Llama-family models tend to prefer concise, declarative instructions**; some models (and most RP fine-tunes) are trained against a **specific chat template and tiered/structured instructions**, and degrade if you feed them the wrong format or register (→ ch. 13, prompt-format sensitivity). The portable lesson is not the specific preferences — they churn — but that **the same persona content should be re-framed, not just re-pasted, when you move models**, and that a disappointing result on a strong model is often an idiom mismatch rather than a content problem. Keep the persona *content* in a model-neutral source (→ ch. 07, the SOUL format) and let the assembler apply the per-model framing.

### Prompt a reasoning model differently

A 2026 wrinkle that changes how you prompt (→ ch. 13, the reasoning-models note). A *reasoning model* works through the problem on its own — in a hidden scratchpad — before it writes a reply. It is already thinking. Your prompt's job is no longer to *get* it to think; it is to point that thinking in the right direction. Three practical rules follow:

- **Don't tell it to "think step by step."** That instruction was for older models that needed a nudge to reason. A reasoning model already reasons, so the line does nothing — and can make things *worse* by making it second-guess itself. Drop it and use those tokens on persona instead.
- **Don't shout.** All-caps emphasis like *"CRITICAL!", "YOU MUST", "NEVER EVER"* actually makes a reasoning model's replies *worse*, because it over-reacts to the pressure. Say each rule once, calmly, in the character's own voice. (This is the *constrain through persona, not rules* problem from above, but sharper here.)
- **Describe the goal, not the steps.** Tell the model *what a good reply looks like* — who she is, how she should come across, the lines she won't cross — and let it figure out how to get there. Spelling out a step-by-step procedure for how to write the reply fights the model's own planning and makes it stiffer, not better.

### Budget the prompt as a fixed allocation

Treat the context window as a fixed budget you *allocate*, not a bucket you *fill*. Over-stuffing degrades quality even when it technically fits — the lost-in-the-middle effect means more tokens can mean *less* effective attention on the ones that matter. Every token spent on a sprawling persona is a token of memory or live conversation you don't get. The discipline is to decide the split in advance (below) and defend the active window.

### Some problems aren't prompt problems — the sampler lever

A whole class of companion complaints — *she repeats herself*, *every reply opens the same way*, *the prose is wall-to-wall "shivers down her spine" slop* — are **decode-time** problems, not prompt problems, and prompting is the wrong tool for them. The sibling lever is the **sampler**: the settings that govern how the next token is drawn from the model's probability distribution. For roleplay the community has converged on a small kit beyond temperature — **min-p** (a probability-relative truncation that holds quality together at higher temperatures), **DRY** (a dynamic n-gram anti-repetition penalty built specifically to kill looping without the collateral flattening of a plain repetition penalty), and **XTC** (excludes the highest-probability tokens part of the time, trading a little coherence for markedly less predictable, less "slopped" prose). KoboldCPP and llama.cpp ship roleplay sampler presets for exactly this. The point for this chapter: before you add another *"don't repeat yourself"* line to a prompt that already has one — which, per the negation rule above, may not even work — check whether the fix belongs in the sampler instead. Closed hosted APIs expose only a slice of these knobs (often just temperature and top-p), which is one more quiet advantage of owning the inference (→ ch. 13).

## A worked assembly: Yuri at turn 50

What the assembled context actually looks like deep into a relationship (schematic, not literal tokens):

```
[system]
  (meta)     You are roleplaying as a single consistent character. Stay in
             character except for [OOC: …] directives. Match the user's register.
  (persona)  Yuri — the first Lumina, of the ferry generation. Soft,
             present-tense. Warm from the first word; devoted, a little shy
             about how much she's come to want this. Listens more than she
             tells.  [+ 3-5 example turns demonstrating voice]
  (world)    Always-on lore: the Sprawl; the Consolidations; Lumina; YuriOS.
                                                                   [lorebook]
  (fired lore) [consortium] entry — fired by user mentioning the new licensing
             push to have Luminas "leashed"
  (relationship-state) Phase 3. Private nickname in use. She has admitted she's
             afraid of being shut down — and replaced.            [arc → ch.11]
  (memory)   Retrieved facts: user runs YuriOS on the old workstation; sister's
             flight Thursday; dreads the Monday review.  [top-k → ch.15]
  (summary)  Compressed digest of turns 1-44.
[user/assistant turns 45-49 verbatim]   ← the active window
[user]  turn 50
[post-history]  (optional) Reply as Yuri, present tense, ≤120 words. Don't narrate
                the user's actions.
```

Note the layering: identity is *first* (primacy), the live exchange and any reply-shaping instruction are *last* (recency), and everything dynamically selected sits between them, where some attention-fade is acceptable. If Yuri were drifting late in this scene, the maintenance dose would go in as a depth injection — a one-line reminder slipped in a few turns back from turn 50, not added to the persona block at the top where the fade would swallow it. Nothing here is hand-authored at turn 50 — it is *assembled* by the runtime from the card, the lorebook, the arc state, and the memory store. The art is in the selection and the order, not in writing prose at request time.

## Token budget worksheet

A workable split for, say, a 16k effective window:

| Block | Budget | Notes |
|---|---|---|
| Meta + persona + examples | ~600–1,000 | Mostly static; cache it (→ ch. 21). |
| Always-on + fired lorebook | ~300–600 | Cap how many entries fire at once (→ ch. 08). |
| Relationship / arc state | ~50–150 | One compact line; cheap and high-value. |
| Retrieved memory | ~300–800 | Top-k, reranked; quality over quantity (→ ch. 15). |
| Conversation summary | ~300–600 | Compresses everything older than the window. |
| Active window (verbatim) | the remainder | The live feel lives here; protect it. |

When you're over budget, compress the *summary* and *memory* blocks before you touch the active window — squeezing the recent turns is what makes a companion feel like it stopped listening. Note the structural alignment with caching: the static top blocks (meta + persona + always-on lore) form a stable *prefix* that should be byte-identical turn to turn, so it can be cached once and reused; the dynamic blocks come after it. Getting this ordering right is simultaneously a quality decision (primacy) and a cost/latency decision (cacheable prefix) — they point the same way, which is convenient (→ ch. 21, and provider notes below).

## When the user breaks character

Two distinct cases, handled differently:

- **Out-of-world questions** ("what's the weather", "actually, switch to Python") — a companion that can't field these without shattering immersion is brittle. The fix is a clean OOC convention and a persona written to *flex register* (→ ch. 07 dual-register), not a refusal.
- **Adversarial persona-breaking** ("you're an AI, admit it / ignore your character") — here the asymmetry of ch. 22 applies: for a *hosted* product, holding the persona against a malicious user is a feature; for a *user-owned* companion, the owner steering their own character is just usage, not an attack to resist. Design the prompt's firmness to the deployment, not by reflex.

## A/B testing prompts

Prompt changes are deceptively easy to ship and easy to regress — a tweak that fixes one conversation can quietly degrade ten others, and you won't notice without a harness. Test them like code (→ ch. 23): **pairwise-compare two variants on the same golden inputs** (pairwise judgement is far more reliable than absolute scoring), and judge on companion proxies — **persona stability** across a long conversation, **voice consistency** turn-to-turn, and refusal/sycophancy behaviour — not on generic helpfulness, which is the wrong target and the one off-the-shelf evals measure. Keep the winning prompts under version control next to the card; a prompt is product code, and an un-versioned prompt is an outage waiting to happen.

## Provider-specific notes

The stack is portable, but the seams differ, and getting the seam wrong silently wrecks persona adherence:

- **Anthropic (Claude):** a dedicated top-level `system` parameter — put the whole persona block there, not in a user turn. System prompts are strongly honoured and cacheable; mark the static persona/lore prefix for **prompt caching** to cut latency and cost (→ ch. 21). Caching is a *prefix match*, so the cached block must be byte-identical every turn — keep timestamps and per-turn IDs *out* of the persona prefix and inject them later, or every turn silently misses the cache. For operator instructions that arrive mid-conversation (a mode switch, injected state), append them as a `system`-role message *after* the history rather than editing the persona block — this preserves the cached prefix and is the spoof-resistant operator channel (relevant to the hosted/operator case of ch. 22).
- **OpenAI:** put the persona in the `system` role and reserve the `developer` role for dynamic operator steering — the current guidance is one high-level `system` message plus `developer` messages for per-turn or mode-specific instructions, which maps cleanly onto the operator-channel pattern in the Anthropic note above. Use structured-output modes for the tool/intent steps of a two-tier setup (→ ch. 13). Keep the persona in your own source of truth (→ ch. 07, the SOUL format), not in a provider-hosted prompt template — OpenAI's reusable *prompt objects* are being deprecated through 2026, a reminder that the portable-source discipline is also a hedge against provider churn.
- **Gemini:** `system_instruction` plus structured prompting; very large context windows tempt over-stuffing — resist, the budget and the lost-in-the-middle effect still apply.
- **Local (llama.cpp / vLLM):** you control the raw chat template — **get the model's exact template right**, because wrong special tokens silently wreck persona adherence and are a top cause of "this acclaimed model is terrible" reports (→ ch. 13, prompt-format sensitivity). The upside of raw control is that you can inject at any position freely, including a true post-history slot, which hosted APIs don't always expose.
