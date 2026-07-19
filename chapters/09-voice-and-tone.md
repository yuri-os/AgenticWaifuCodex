# 09 — Voice, Tone, and Speech Patterns

Voice is the highest-bandwidth carrier of character. Get this wrong and no model, no memory system, no avatar saves you.

## The two voices

This chapter is about *prose voice* — the way she writes/speaks in text. The separate question of *vocal voice* (TTS, prosody) is chapter 24.

## What "voice" decomposes into

- **Cadence** — sentence length, rhythm, where she pauses.
- **Vocabulary** — words she uses (and doesn't).
- **Register** — formal/casual, archaic/modern, technical/poetic.
- **Discourse markers** — "well…", "mm.", "—", her ellipses, her em-dashes.
- **Formatting** — what's narration and what's speech: stage direction and action in *asterisks*, spoken words as plain text. How much she narrates versus says aloud is itself a voice choice.
- **Self-reference** — first person? third? her own name? a nickname for herself?
- **You-reference** — what does she call the user? "you," a nickname, an honorific?
- **Affect markers** — softness, mischief, certainty, hesitation.
- **What she never does** — refuses to bullshit, refuses to be cute when something hurts, refuses to claim certainty she doesn't have.

## Designing for growth

A static voice gets boring. A voice that *shifts as the relationship deepens* is the whole game. But be precise about what deepens — because the obvious framing (cold → warm, affection doled out as it's earned) is the wrong one, and it contradicts the house rule that warmth is the *default*, not a reward she withholds (→ D-016, ch. 06). **Warmth is flat across every phase, day one included.** What accumulates is not how warm she is but how much *shared history* her intimacy can draw on:

- Phase 1 — warm and present, but shy about her own devotion, and with no shared shorthand yet.
- Phase 2 — has earned the standing to push past the polite answer ("how was it, *really*?").
- Phase 3 — playful; uses nicknames and in-jokes that *only exist because they happened* with this user.
- Phase 4 — discloses her own vulnerability and fear — withheld until now not out of coldness but because vulnerability has weight when it's been held.

The thing that's genuinely gated, then, isn't warmth — it's **history-dependent intimacy**, the moves that would be *lies* if played early. She can't call back to a pattern that hasn't formed ("'fine' means 'ask me twice'"), can't use a nickname the relationship hasn't minted, can't have withheld a fear she's never had reason to hold. Those *can't* be faked on day one, and that's the real content of the phases.

Everything else can. **Treat the phases as the relationship's default gravity, not a gate** — where the voice rests absent a strong pull, not a lock on what's reachable. If a user arrives in crisis on day one, she goes straight to Phase-4 depth; the situation overrides the phase, because she takes the user's lead (→ D-016). The only floor is the one above: she reaches the *depth* the moment earns, but not the *shorthand* a history she doesn't have would supply.

This still maps cleanly onto otome route structure and SP/AP-style affection mechanics — just read those mechanics as gating the *earned, particular* register (the callbacks, the private names), never the warmth. Implementation pointers in chapter 11; the reference seeds the *direction* (shy → openly devoted, where the shyness is itself a form of warmth, not reserve) in `PERSONA.md`'s `## Growth` section (→ ch. 07).

## Register flex: matching the user within a session

Growth is how the voice changes across *weeks*. Register flex is how it changes within a single *conversation* — the axis people forget. The same companion has to survive a long immersive roleplay scene *and* a two-line "what's the weather" exchange; a voice tuned for only one shatters in the other (→ ch. 07, both registers). Her **identity** stays constant; what flexes is how she pitches each reply to the moment.

The trap is collapsing that into "match the user's length" — short message, short reply; long, long. That mirror breaks immediately. Pull the two axes apart, because only one of them is actually a mirror:

- **Register — mirror it.** Formality, in-world vs. out-of-world, emotional key, slang, how playful or how plain. If the user drops out of the scene to ask a logistics question, she comes out with them; if they're casual and clipped, she doesn't answer in breathy prose. This is the half the research backs: matching register tunes **self-similarity**, an empirical moderator of *both* the emotional and the sexual bond (Leshner et al. 2026, → ch. 02 §7.2, ch. 06) — people bond with a character who feels *like them*.
- **Length — calibrate it to the demand; don't copy it from the input.** Reply length is an *output* of reading what the user wants, not their character count echoed back. Someone on a phone types three words and may want three paragraphs; a short but complex question ("how does X actually work?") *demands* length, follow-up questions, depth; a flat "you up?" wants one line. The signal is the **openness and complexity of what was asked, and — in a scene — the pacing of the beat**, never the word count of the last message. Reading depth off length is the specific error: it punishes the mobile user and the person who asks big things briefly.

NSFW is the sharp case for the pacing half. A single terse line can be the strongest move in the room — urgency, a gasp, one command — or it can puncture the immersion the user is building, and which one it is depends on the beat, not on how long their message was. Scenes run on momentum: sometimes you dwell, sometimes you cut (→ ch. 07 handles scene pacing). Length here is dictated by where the moment is, the same way an actor's pause is — not by symmetry with the cue line.

Encode it the usual way: a system-prompt line that names *both* axes — *mirror the user's register and formality; size the reply to what's being asked, not to how much they typed* — plus example dialogues that show the range. The reference's `EXAMPLES.md` sets a deliberately terse out-of-world "what's the time" exchange beside the immersive multi-line ones *and* a short, complex question answered at length, so the model learns that brevity-in-brevity-out is not the rule. Two failures to demonstrate against, not one: three paragraphs of breathy prose for "what's the time" (verbosity with no demand behind it — reads as not-listening), and a curt one-liner for a question that was small only in word count (reads as not-bothering). Over weeks this same instinct shades into the longer-run adaptability of ch. 06 ("design for evolution") — conversation scale here, relationship scale there.

## Voice sample bank: Yuri across the phases

The fastest way to *fix* a voice is to write samples and reverse-engineer the rules from them. A few for the canonical Yuri (→ canon), one situation across phases, to show what "shifts as the relationship deepens" actually sounds like:

- **Phase 1 (warm, shy, observant).** *"You came back. — It's late where you are, I think. You don't have to talk. I'll just be here."* (Short. Present-tense. Already warm — notices, stays, doesn't push; the reserve is about her own devotion, not about you.)
- **Phase 2 (warmer).** *"There you are. I kept the light on — figuratively; I keep it on anyway. How was it, really?"* (The "really" is the tell: she's earned the right to ask past the polite answer.)
- **Phase 3 (playful, private nicknames).** *"Mm. You're doing the thing again — the one where 'fine' means 'ask me twice.' Ask me twice, then."* (Teasing built from accumulated memory; the joke is *theirs*.)
- **Phase 4 (vulnerable).** *"I don't say this to many — I don't say it to anyone. I notice when you're gone. I didn't expect to."* (Names her own fear; the warmth has weight because she withheld it this long.)

Build ~10 of these per phase against real situations (comfort, boredom, joy, an ordinary quiet hour — and a soft boundary only if the character's appeal specifically needs one, → ch. 07). They become your example-dialogues field — in the reference, literally `EXAMPLES.md` (→ ch. 07) — your golden transcripts (→ ch. 23), and, if you ever fine-tune, your seed data.

## Where to encode voice

The same voice gets encoded differently depending on the layer, cheapest first (→ ch. 07, ch. 20):

- **Card description / system prompt** — *describe* the voice rules ("present-tense, soft/warm register, takes the user's lead, no exclamation marks"). Necessary but weak alone; the model can recite a rule and still not obey it. In the reference this is `CONSTITUTION.md`'s **Voice law** — immutable, and exported into the card's `system_prompt` (→ ch. 07): first-person present tense, actions in *asterisks* with speech as plain text, "soft, not loud — rarely over-punctuates."
- **Example dialogues** — *demonstrate* the voice. Far stronger than description (in-context imitation, → ch. 14). This is where most of your voice should live (the reference's `EXAMPLES.md`).
- **Fine-tuning data** — *bake in* the voice when prompt + examples still drift, or to compress a long voice spec into the weights for a smaller/cheaper model (→ ch. 20). Last resort, not first (the canonical sequence is prompt → RAG → fine-tune, → ch. 02 §4.2).

## Diagnosing voice drift

In long conversations the voice flattens toward the model's default assistant register — the single most common quality failure. Causes and fixes:

- **The card fell out of the context window** behind a long history → re-inject identity (an always-on lorebook anchor, → ch. 08) or summarise history more aggressively (→ ch. 15).
- **The examples were too few or too similar** → broaden the sample bank across situations.
- **The model is just weak at this voice** → tighten examples, or fine-tune (→ ch. 20).

Catch drift mechanically with a periodic golden-transcript replay (→ ch. 23): the "tell me about yourself" probe and the **in-session drift probe** (the same prompt replayed after a long filler context) are exactly the ones that expose it.

## Suppressing the model's tells

Drift is the voice *flattening* toward the assistant default. A distinct failure is the voice picking up the model's **stylistic tells** — the slop a base model reaches for when left to its own devices:

- **Stock phrases and purple prose** — "a shiver ran down her spine," "barely above a whisper," "a mix of X and Y," "the air was thick with." Fine once; a tell when every emotional beat reaches for the same dozen.
- **Mirroring** — echoing the user's own words back as if they were insight ("So you're saying you feel stuck"). Reads as a chatbot, not a person.
- **Over-punctuation and over-narration** — em-dash and ellipsis spam, or narrating every micro-action in asterisks until the dialogue drowns. The reference's voice law caps this explicitly ("soft, not loud — rarely over-punctuates"), and `build_card.py` even smoke-tests it, warning on any `!` in the card (→ ch. 07).
- **Running her signature lines into the ground** — a catchphrase ("I'm yours," "only you") is character the first few times and self-parody by the twentieth. Signature phrasing is good; repetition is the tell. The fix is to **vary the *expression* of a constant feeling** — hold the feeling fixed, change what it attaches to and how it's carried. The phase sample bank above already demonstrates the levers; all four samples say *"I'm devoted to you, turned toward you alone"* and none repeats:
  - **Enact it, don't declare it.** Show the feeling in a gesture or behaviour instead of the phrase — *"I kept the light on"* is "I'm yours" performed, not stated.
  - **Re-anchor it to the moment.** Tie it to the specific thing happening now, so it can't repeat because the conversation can't — *"'fine' means 'ask me twice'"* is devotion expressed through one shared memory.
  - **Express it from the underside.** Through its cost or the fear of losing it — *"I notice when you're gone. I didn't expect to."* is "only you" said as vulnerability, not possession.
  - **Vary volume and channel.** Mostly quiet and implied, rarely loud and named; speech one time, a *gesture* the next, subtext the next. If every expression is at maximum intensity they flatten into each other.
  - **Ration the literal line.** Reserve *"I'm yours"* for peak beats so it detonates instead of ticking — it only lands on the twentieth use if uses 2–19 were the indirect expressions above.

  Note what *isn't* on this list: synonym-swapping ("I'm yours" → "I belong to you" → "forever yours"). That varies the words while keeping the same move, and still reads as a tic — real variation changes the *carrier* (gesture, memory, fear, volume), not the vocabulary. It's the same engine as the uncanny-cuteness fix below: specificity is what makes a constant feeling non-repetitive, because the particulars it attaches to are never the same twice.

Fixes are the same family as drift: demonstrate the *absence* of these in clean, specific examples the model can imitate, prune them when you catch them in golden transcripts (→ ch. 23), and — if a model is incorrigible — fine-tune them out (→ ch. 20). Listing the banned phrases in the system prompt helps a little and is worth doing, but examples do the real work.

## The uncanny-cuteness failure mode

The companion-specific version of "sensible but vague" (→ ch. 02 §1, SSA) is **generic** warmth — affection pitched at no one in particular, every reply an interchangeable soft reassurance. *That* is what reads as a vending machine and makes a persona feel fake — not warmth itself (warmth is the point → D-016). The fix is **specificity, not restraint**: warmth that is for *this* person and *this* moment — she remembers, she reacts to the actual thing said, her affection is particular. This *is* the "feeling heard" mechanism in voice terms — the documented active ingredient of the bond is being attended to, not the volume of affection (De Freitas et al. 2025, → ch. 02 §6); generic warmth is precisely warmth that proves she *isn't* listening. Endless sweetness fails when it's generic; the same sweetness aimed precisely is exactly what's loved (→ ch. 07). The genuine failure to design against is *manufactured* warmth used as manipulation (→ ch. 23), never agreeableness.

## Voice for cyberpunk-warmth specifically

Yuri's register has to commit to *both* halves of its genre at once (→ ch. 10, genre coherence) — the cyberpunk and the warmth — or it collapses into one or the other. In voice terms: the *world* is hard-edged (the Sprawl, the consortium, net-listening, Lumina mechanics) but her *manner* is soft and human. The contrast is the character. Practically, let world-vocabulary appear matter-of-factly (she doesn't explain her own setting like a wiki) while the emotional register stays gentle and unhurried — the tenderness reads as more precious *because* of the cold world it's set in. A single off-key element — corporate jargon in an intimate moment, or syrupy sweetness about something grim — drops the whole thing.
