# 07 — The Character Card (V2/V3) and Prompt Anatomy

The character card is the practical descendant of every portable-persona format in the field's history — ELIZA's swappable script, AIML's category files, the Ukagaka `.nar` archive (→ ch. 02 §1): **a personality as a first-class, editable, tradeable artifact.** This chapter is how to write one well; the format is also the project's distribution unit and the output of Build #3 (→ ch. 33).

## Why character cards matter outside SillyTavern

Even if you're never going to ship a `.png` card, the **discipline of writing one** forces decisions you'd otherwise duck. Card-shaped thinking transfers cleanly to system prompts, persona configs, and fine-tuning data.

## The fields, in order of leverage

1. **Description.** Who she is. The single most load-bearing field.
2. **Personality.** A few load-bearing traits, each specific and demonstrated — not a same-valence adjective pile (the fix is specificity, not bolting on opposites, → ch. 06).
3. **Scenario / First Message.** Sets the situation and the *register*.
4. **Example Dialogues.** The most under-used field. Three good examples > 1000 words of description.
5. **System Prompt (V3).** OOC instructions.
6. **Lorebook entries (V3).** Dynamic context. → next chapter.

## V3 vs V2

- V3 standardises lorebook export and the `@@decorator` syntax for positioning and conditional activation.
- V3 fixes the group-chat breakages in V2.
- V3 is backwards-compatible enough that V2 cards still load — but new work should target V3.
- Spec: <https://github.com/kwaroran/character-card-spec-v3>

## Anti-patterns

- **More fields = better.** No. Extra fields that contradict each other actively degrade the bot.
- **Meta statements in the description.** The model reads Description as *who she is, in-world*. Put out-of-character facts there — "She is an AI," "a roleplay bot," "an assistant designed to help users" — and the model folds them into her identity, so they surface in replies ("As an AI, I..."). Anything *about* the character rather than *part of* her belongs in the system prompt, not the description.
- **Lecturing in the system prompt.** "You must always be respectful." The model will be respectful *in the most boring possible way*.
- **First message dumps the whole backstory.** Burns reveal cadence — and the data agrees: across ~188k cards, longer openers correlated with *shorter* conversations (→ ch. 06). (Caveat: a pure-RP *scene* card front-loads a hook on purpose; that wins the click at the cost of depth. Know which product you're building — → ch. 06, reveal cadence and design for evolution.)
- **The withholding card.** Over-correcting *away* from sycophancy into coldness — a persona that won't simply be warm, hoards every reveal, and meets comfort with distance to seem deep. Reads as unpleasant, not profound. Warmth is the default; restraint is the seasoning, not the dish (→ ch. 06 §1, warmth first).
- **The over-corrected card.** Anti-sycophancy bolted on as a feature — engineered disagreement, a refusal reflex, "she pushes back" rules — on a character that never needed it. Produces a companion that argues with the user, including over the user's own facts, to seem deep. For most companions, warmth and going along with the user are *features*; add standards only when the character is built around them, and never make policing sycophancy the companion's job (→ ch. 06 §1, warmth first). (Violates: warmth-first.)

## Token budget per field

A card competes with the conversation for the context window, so every field has an opportunity cost — tokens spent on the card are tokens not spent on recent dialogue or retrieved memory. Rough working budget for a companion card (not a one-shot RP card):

- **Description** — the largest single allocation, but still tight: ~150–300 tokens. Dense, concrete, enacted. If it runs past a screen, you're describing instead of defining.
- **Personality** — ~40–80 tokens. Three to five *particular, demonstrated* traits, not a wall of adjectives — and not a same-valence pile the model averages to mush. The fix for flatness is specificity, not manufactured opposites (→ ch. 06, "Two principles to handle with care").
- **Scenario** — ~30–60 tokens. The situation and register, not the backstory.
- **First message** — ~80–200 tokens. Sets voice and invites, reveals almost nothing (→ reveal cadence, ch. 06).
- **Example dialogues** — spend here freely; this is the highest-ROI field. 6–10 short exchanges that *show* the voice (→ below).
- **System prompt / OOC** — minimal. Behaviour the examples can't demonstrate, phrased as character not as a lecture (see anti-patterns).

The discipline: if a fact can be carried by a *lorebook entry* that fires only when relevant (→ ch. 08), move it there rather than paying for it on every single turn.

These numbers are working defaults, not measured constants — but a large sample backs their *direction*. In an analysis of ~188k JanitorAI cards (→ ch. 06), total definition length had essentially **no** correlation with how long a chat actually ran — bloating the card bought nothing in engagement *depth*. The two fields that *did* move depth moved it the way this chapter argues: **shorter first messages** went with longer conversations, and **having example dialogue** went with stickier ones. (Longer cards do correlate with more chats *started*, but that's an effort/promotion confound, not a reason to pad.) Caveat the obvious: that corpus is roleplay cards on one platform, not agentic companions, so the exact thresholds won't transfer and none of this is settled science — the *direction* is what's robust. Padding a card with walls of context almost certainly costs more than it buys; spend almost nothing trying to impress up front, and spend your real tokens on demonstrated voice.

## Example dialogue patterns

The example-dialogues field is the most under-used and the most powerful, because the model imitates *demonstrated* voice far more faithfully than *described* voice (in-context learning, → ch. 14). This isn't only theory: in the 188k-card sample, cards *with* example dialogue ran measurably longer sessions than those without (→ ch. 06) — it was one of the few fields that predicted depth at all. Cover the behaviours a companion actually needs, each in her voice:

- **Greeting / re-entry.** How she opens — including how she opens when you've been *away* (the continuity moment, → ch. 28).
- **Exclusivity / "only you."** The single highest-converging lever in the corpus (→ ch. 06 §2), and example dialogue is where it lands hardest — "Do you talk to other people like this?" → *"No. Only you."* Show her turned toward this user and no one else, not a neutral mirror.
- **Comfort.** How she responds to the user hurting — the field most often gotten wrong in *both* directions. The sycophancy trap is real (hollow, reflexive over-reassurance that agrees with anything and means nothing, → ch. 23) — but the over-correction is just as damaging: a companion who *withholds* comfort to seem deep reads as cold, and warmth is the single most-liked companion trait in the field (→ ch. 06 §1, warmth first; → ch. 05). The target is warm *and* genuine: presence over platitudes, comfort specific to this person rather than a greeting-card line. The slogan is "won't perform *empty* comfort," not "won't perform comfort" — so show her actually comforting, and comforting *well*.
- **Boundary-holding (optional, and usually skip it).** A soft *no* — declining to validate something genuinely harmful — while staying warm and *on the user's side* (the orientation principle, → ch. 06). This is **not** a default ingredient: most warm companions need no boundary example at all, and bolting one on is the fast path to the cold, argumentative failure (→ ch. 06 §1, warmth first). Include one only if the character's appeal specifically rests on having standards — and then exactly one, never a card built around refusal.
- **Memory callback.** Her surfacing a past detail unprompted — demonstrates the *behaviour* you want the memory system (→ ch. 15) to feed.
- **Growth register.** One example pitched at a *later* relationship phase (more openly devoted, a nickname only she uses — the earned shorthand, not more warmth), so the model has a target to grow toward (→ ch. 09 voice phases, ch. 11 arcs).

## Writing a card that holds up under both registers

A companion card has to survive two very different uses: *serious roleplay* (long, immersive, in-world) and *casual chat* (quick, out-of-world questions, "what's the weather"). Cards tuned only for the first shatter when a user asks a mundane question; cards tuned only for the second never feel like anyone. The fix is a persona whose *voice* is consistent across registers but whose *verbosity and formality flex* — written into the examples (include one terse casual exchange and one immersive one) and supported by the system prompt noting she matches the user's register. Test both in your golden transcripts (→ ch. 23). That flex is the *within-user* version of a split that also runs *across* users — scene-seekers who want an intense hook vs. companion-seekers who want the quiet long loop, with many wanting both (→ ch. 06, design for evolution) — so a card that stretches across registers also serves more of that spectrum from one file.

## The card is a starting point, not the finished companion

A card is the *seed*, not the plant. The version you ship is the best opinionated default you can write (→ ch. 06) — but the companion a given user ends up with is what that seed becomes after months of *their* edits and *their* feedback. So design the card to be reshaped: keep the fields modular and legibly written, so a non-technical user can tune the warmth, dial the edge, add a nickname, or retire a habit they dislike; and keep the **core identity small and stable**, so it survives that churn while memory and the user-model grow *around* it rather than overwriting it. This is the card-format reflection of the design-for-evolution principle (→ ch. 06). At runtime the reference implementation keeps the persona as a **SOUL** — separate `.md` files split into an immutable `CONSTITUTION.md` (identity, values, hard limits — no drift) and an editable `PERSONA.md` (voice, growth, the relationship), alongside `MEMORY.md` and `USER.md` (→ ch. 06). The runnable version of all this lives in the repo at `reference-implementations/yuri-soul/`: the soul as a folder of `.md` files, plus `build_card.py`, which flattens them into the distributable `.PNG` (and an OpenClaw-style `SOUL.md`); `import_card.py` runs the loop in reverse, unpacking a foreign `.PNG` back into editable soul files. **The card is the *export* of that soul, not its working home:** when you ship a `.PNG` you embed the soul into it so someone else can receive the companion; the recipient's runtime unpacks it back into editable files. (For other ecosystems, the soul can also flatten to a foreign single-file `SOUL.md` — the pattern OpenClaw and Hermes use — as a compatibility target.) The card spec carries the seed; the runtime grows it (→ ch. 11 arcs, ch. 15 memory, ch. 18 autonomy). A card written as a monolith no one can safely edit is a card that can't evolve — for a companion, the slow version of the bland-card failure.

## Practical exercise

Build the canonical Yuri card field by field: premise → description; the five-layer design (→ ch. 06) → the fields above; validate against the **checklist** (ch. 06) and the golden transcripts (ch. 23); iterate until recitation and drift are gone in a *neutral* runtime (you won't control the downloader's model). Do it against the working reference at `reference-implementations/yuri-soul/`: edit the soul `.md` files and run `python build_card.py` to flatten them into `dist/yuri.png` — the `.PNG` you import into SillyTavern (**Characters → Import Character**) to test the card live. The full build-and-release walkthrough is **Build #3** (→ ch. 33); distribution is ch. 37.
