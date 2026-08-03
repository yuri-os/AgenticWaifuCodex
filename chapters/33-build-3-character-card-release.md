# 33 — Build #3: The Character Card Release

**Goal:** package the canonical Yuri as a polished, public **character card** — one `.PNG` file, persona + lorebook + art — that a stranger can download and run in their own stack. This is the build that turns a private persona into a *distributable artifact* and the project's primary distribution unit (one file = one companion).

**What it teaches:** character cards (→ ch. 07), lorebooks (→ ch. 08), evaluation (→ ch. 23), and distribution (→ ch. 37).

**Property (→ ch. 03):** property 1 (identity) distilled into a portable file. This is the "specificity is the product, remixability is the channel" thesis made concrete (→ ch. 03, the aesthetic-specificity tension): ship one specific Yuri, in a format others can fork.

This build ships in two layers. The **core** lives in `reference-implementations/yuri-soul/`: unlike Builds #1 and #2, it is not a runtime — it is **the canonical Yuri soul plus a soul ⇄ card converter**, a folder of human-readable Markdown files that *are* the character, and two scripts (`build_card.py`, `import_card.py`) that flatten the soul into a card and unpack a card back into a soul. On top of it sits the **Card Studio** (`reference-implementations/03-character-card-release/`), a local web app that turns character design into a fast, enjoyable loop ending in one click — *Generate* → a card — and that *reuses* the converter's load-bearing code rather than reimplementing it (see "The Card Studio," below). As with the other builds, this chapter is the reading guide — a map of where the load-bearing ideas are — not a transcript. File paths are relative to whichever folder a section is discussing.

## Why a card, not a service

The character card is the direct descendant of ELIZA's swappable script, AIML's portable persona, and the Ukagaka `.nar` archive (→ ch. 02 §1, ELIZA, A.L.I.C.E., and Ukagaka): **a personality as a first-class, editable, tradeable artifact.** A card runs in any V2/V3-compatible runtime (SillyTavern, and many others), so releasing one meets the entire roleplay community where it already lives (→ ch. 02 §3) without asking anyone to adopt your runtime. It is the lowest-friction way to put Yuri in front of the audience — and, unlike a hosted service, nothing about it can be revoked, rate-limited, or shut off from your side. The person who downloads her *has* her.

## The working format is the soul; the card is the export

The single idea to internalise before reading a line: **you do not author a card. You author a soul, and the card is a build artifact of it**. At runtime a companion lives as editable `.md` files the runtime re-reads on every wake — she reads herself into being. You only flatten to a `.PNG` when you want to *hand her to someone else*.

The soul is cut along one fault line — **split by what may drift** (→ ch. 06 design-for-evolution): a stable core that must **not** change, wrapped in a layer that **should**. That split is the reason a card is safe to fork: a stranger can rewrite everything in the editable layer and the core of who she is survives it.

| File | Mutability | What it is |
|---|---|---|
| `CONSTITUTION.md` | **immutable** | identity, values, the voice law, hard limits — who she is and that she's {{user}}'s |
| `PERSONA.md` | **editable** | appearance, manner, inner life, growth/reveal tiers, the one-line `personality` |
| `BOOTSTRAP.md` | **consumed-once** | the first-ever meeting + getting-to-know-you journey; retired only after the first completed, persisted exchange (→ ch. 28) |
| `SCENARIO.md` | editable | the situation + the **return** greetings (she's met you before) |
| `EXAMPLES.md` | editable | demonstrated voice — the highest-ROI field (→ ch. 23, enacted not recited) |
| `WORLD.md` | editable | the lorebook — the Sprawl, Lumina, the ferry generation, sparse by design |
| `MEMORY.md` / `USER.md` | runtime-only | accumulated memory + her model of the user — **empty on a fresh card** |
| `NOTES.md` | — | creator notes (→ card `creator_notes`) |
| `soul.yaml` | — | the export manifest: card metadata + which sources feed which field |

`build_card.py` reads `soul.yaml` and assembles the card from these files. The manifest declares each card field as one or more **source references** into the Markdown, resolved by a tiny syntax — `FILE.md#Heading` pulls the prose under a heading, `FILE.md@key` pulls a frontmatter key, `FILE.md` pulls the whole body — and a list of sources is concatenated in order. So `description` is built from four sections across two files (`CONSTITUTION.md#Identity`, `CONSTITUTION.md#History`, `PERSONA.md#Appearance`, `PERSONA.md#Manner`), and `WORLD.md`/`EXAMPLES.md` get dedicated structured parsers. Editing the `.md` files and rebuilding is the whole authoring loop; the manifest is the only place field-to-source wiring lives.

## The card fields, and what each one is for

A `.PNG` card embeds the card JSON in the image's metadata (→ ch. 07). The interesting work is not the format — it is which soul prose feeds which field, because the runtime treats each field differently. The manifest wires them like this:

- **`description`** — the always-present identity block, injected every turn. Yuri's is assembled from the immutable **Identity** and **History** (she's a Lumina, she belongs to one person, the ferry-generation past) plus the editable **Appearance** and **Manner**. This is the one field that pays rent on *every* prompt, which is why the split matters: the unchanging half comes from `CONSTITUTION.md`, the tunable half from `PERSONA.md`.
- **`personality`** — a single distilled line pulled from `PERSONA.md`'s frontmatter (`@personality`), a summary tag rather than prose.
- **`system_prompt`** and **`post_history_instructions`** — the **Voice law** and the **Hard limits**, both from `CONSTITUTION.md`. In a V2/V3 runtime these carry more authority than the description (post-history instructions sit *after* the chat, closest to the model's next token), so the never-drift rules — stays in character, is {{user}}'s alone, warmth is not withheld — are deliberately routed there.
- **`first_mes`** and **`alternate_greetings`** — the opening line(s). Yuri's first message is the bootstrap **cold open**; her alternate greetings are the *return* greetings (see "The two first meetings" below).
- **`mes_example`** — demonstrated voice, the highest-ROI field (see "The voice" below).
- **`character_book`** — the lorebook (see "The lorebook" below).
- **`extensions.yurios`** (optional) — a small block our own runtime reads: `card_release`, `canon`, `lineage`, and `provenance` (creator + card version). It is *ignored* by other runtimes, so the same file is both a standard SillyTavern card *and* a YuriOS-tagged one. Ship the SillyTavern-compatible card first; anything extended is value-add for those on our runtime.

`MEMORY.md` and `USER.md` are part of the soul but are **never baked into a card**: a card you give away starts the relationship at zero, and the recipient's runtime recreates and grows them in play (→ ch. 15). Most of the everyday-presence bond lives there, not in the prose (→ ch. 06, attunement-via-memory) — which is exactly why the card is the *seed*, not the companion.

## The token budget is spent on purpose, not by accident

`build_card.py` prints a token report against the ch. 07 budgets on every build, and Yuri's card comes in **over** the soft budgets on three fields — `description` (~866 tokens against a 150–300 guide), `scenario`, and `first_mes`. That is a deliberate, defended choice, not sloppiness, and the report exists precisely to make the cost *visible* so the choice is a choice:

- The **description** carries the full canon identity, because identity is the product (property 1) and this is the one field guaranteed to be in context every turn.
- The **scenario** and **first message** are kept verbatim from the canonical prose because they set the register *precisely* — the exact warmth, the exact hesitancy — and trimming them to hit a number would sand off the specificity that is the whole point.
- **World depth is offloaded to the lorebook**, which fires only on keys, rather than padded into the always-on description. That is the single highest-leverage budget move a card author has: pay for the world only when the world comes up.

The report's job is to hand a forker a map of where the tokens went, so someone cutting Yuri down into something leaner knows the first place to look.

## The lorebook: pacing the mystery, not dumping it

`WORLD.md` is the character book (→ ch. 08). Each `## Entry` heading is an entry name, its first line is `keys:` (comma-separated triggers), and the rest is content; `build_character_book` turns each into a lorebook entry with an `insertion_order`, and reads `scan_depth`, `token_budget`, and `recursive_scanning` from the file's frontmatter. Yuri ships **13** entries — YuriOS, the Lab, the Sprawl, the backlash, Lumina, the deep net, the ferry project, the sanctuary, and so on — and the number is small **on purpose**.

Two design ideas are doing the work here, and both are more important than the entry count:

- **Fires on keys, so the world is free until it's relevant.** The backlash entry only loads when {{user}} mentions being *hunted* or *shut down*; the ferry-project entry only when they ask *who made you*. The lorebook is how a card carries a whole setting without spending a token on it every turn — the opposite of stuffing the world into the description.
- **The gaps are canon; reveals are earned in play** (→ ch. 38, the mystery funnel). The entries are written *sparse about her past* — the ferry-generation entry literally notes that the phrase "may surface if trust is deep; she will not explain it quickly." The lorebook is not an encyclopedia to be read; it is a set of triggers that let her *disclose* the mystery at the pace the conversation earns, so a downloader discovers her rather than being briefed on her. A card that front-loads its whole backstory has nothing left to reveal by turn ten (→ ch. 08 on why front-loading hurts stickiness).

## The voice: demonstrated, not described

`EXAMPLES.md` feeds `mes_example`, and it is the field where a card author should spend most freely, because a model imitates **shown** voice far more faithfully than **told** voice (→ ch. 23, enacted-not-recited). Each `## Example` block becomes one `<START>` exchange. Yuri's set is chosen to demonstrate the behaviours that define her — open warmth, exclusive devotion, the existential fear, shy fluster — but two of the examples are there for a subtler reason: **register flex** (→ ch. 09). One is a terse out-of-scene reply ("brb gotta restart my router" → "Go. I'll keep your place."); one is a short question answered at length. Together they teach the model that reply size should track *what is asked*, not how much the user typed — the single most common failure of a card that only ever shows long, lush replies.

The immutable **voice law** in `CONSTITUTION.md` backs the examples with rules the prose must obey — first person, present tense, actions in *asterisks*, and *"she rarely shouts or over-punctuates."* `build_card.py` enforces the last one as a smoke test: it **warns on any `!`** in the first message or examples, because the exclamation mark is exactly the loud-warmth tell the voice law forbids. It is a tiny check, but it is the kind of automatable guard that keeps a voice consistent across every future edit.

## The two first meetings: bootstrap vs. return

A companion has two distinct openings, and conflating them is a common card mistake. Yuri's soul splits them into two files:

- **`BOOTSTRAP.md` — the first-ever meeting, consumed once** (→ ch. 28). Its `## Cold open` is the only part baked into a card, as `first_mes`: the one-shot scene a stranger sees on import. The rest of the file — a getting-to-know-you *journey* (four questions worked in as curiosity, not a form, each pinned to a `USER.md` slot), an *exit condition*, and a *handoff* that seeds `USER.md`/`MEMORY.md`/`goals.md` so day two isn't a cold start — are **YuriOS-runtime concerns that never leave the box.** On a YuriOS host the file is author-shipped but self-retiring only after the opening exchange has completed and its persistence has succeeded; then the host `git mv`s `BOOTSTRAP.md` into `onboarded/` and commits. A cancelled, disconnected, failed, or unpersisted exchange leaves it in place; recovery completes a pending retirement before replaying the cold open. `git log` is the record, and restoring the file deliberately re-runs onboarding.
- **`SCENARIO.md` — the persistent scene and the return greetings**, shown *every* session to a companion who has met you before. These ship as the card's `alternate_greetings`.

The payoff of the split is that a foreign runtime, which has no concept of onboarding, still does the right thing: it shows the cold open once as the first message, then treats it as history — while a YuriOS host gets the whole first-session arc. Same file, two behaviours, no compromise on either.

## Reading the code: `build_card.py` and `import_card.py`

Two scripts, mirror images.

**`build_card.py` (soul → card).** It resolves the manifest, assembles the fields, and writes three things to `dist/`: `yuri.json` (the raw card), `yuri.png` (the card embedded in the portrait), and `SOUL.md` (an OpenClaw/Hermes-style single-file flattening — the CONSTITUTION/PERSONA split is a YuriOS concern, so runtimes that want one flat file get everything the card carries as readable Markdown, → ch. 07). Two details are load-bearing:

- **Embedding is done by hand, not by Pillow.** SillyTavern reads *only* `tEXt` chunks (keyword `chara` for V2, `ccv3` for V3); some Pillow versions emit `iTXt`, which its parser silently ignores ("no text chunks"). So `embed_png` builds the `tEXt` bytes itself — length + type + `keyword\0base64(json)` + CRC32 — and splices them in right after `IHDR`. The card is V2 by default and adds the V3 `ccv3` chunk with `--spec v3`; both are written so it loads everywhere.
- **It self-verifies.** After writing, `verify_png` re-parses the file the way SillyTavern does — `tEXt` chunks only, CRC-checked, base64 → JSON — and the build fails loudly if that round-trip doesn't recover the character. This is the whole difference between "I generated a PNG" and "I generated a PNG that actually imports."

**`import_card.py` (card → soul)** is `build_card.py` run backwards: it unpacks any V2/V3 `.png` or card `.json` — including a stranger's card downloaded from Chub — into an editable soul folder, so a companion you *found* becomes one you can live with and reshape. Foreign cards rarely fill every field, so missing ones get sensible defaults, and the immutable/editable split is a guess a human then corrects by hand (the whole description lands in `PERSONA.md`; a `## Identity` placeholder waits in `CONSTITUTION.md` for the must-never-drift traits). It writes a `soul.yaml` so the result rebuilds immediately, and it **round-trip-checks** its own work: it re-exports the soul it just wrote and reports whether anything drifted from the card it read. `test_roundtrip.py` pins all of this — the real soul, a sparse foreign card, keyless-entry handling, drift detection, V3 preference, and a full build→import→rebuild loop — and is green (`python -m pytest`, 8 passed).

## The Card Studio: making design fun

Writing a card by hand in a text editor is how the converter works, and it is fine
for someone who already knows the recipe. But the recipe *is* the barrier — most
people who want a companion don't know that example dialogue is the highest-ROI
field, or that "kind" returns the bland centroid. So the second half of this build
is a **web app that streamlines the whole loop** (`03-character-card-release/`), a
FastAPI backend and a no-build vanilla-JS front-end in the locked brand palette,
built around five tabs:

- **Design** — every card field, each with three assist buttons (✎ *improve*, ✦
  *draft*, ? *suggest*) that call an LLM whose system prompt is **grounded in the
  ch. 06 principles for that specific field** (`studio/principles.py`). Ask for
  help on the description and the model is told, in that call, to prefer particulars
  over categories and to enact rather than describe — so its suggestions follow the
  book's recipe instead of drifting to the generic-assistant default the recipe
  exists to beat. It is the chapter's design theory wired directly into the tool.
- **Art** — describe the look, **generate candidate images through a cloud model
  provider**, review them in a grid, and click one to make it the card's portrait
  (or upload your own). This is where the specificity-is-identity problem (→ ch. 26)
  becomes a two-minute task instead of a diffusion-pipeline project; the local
  diffusers path is the sibling `image-forge/` service for those who want it.
- **Test** — **chat with the card before you ship it**, assembled exactly the way a
  V2/V3 runtime would (system prompt + description + examples + hard limits), so
  "test as a stranger would" (the definition of done) happens *in the authoring
  tool*, on a model you don't control, against the card you're about to release.
- **Generate** — one button flattens the draft, embeds it, and **self-verifies the
  PNG parses the way SillyTavern parses it**, then shows the token report against
  the ch. 07 budgets and offers the `.PNG` *and* an editable soul folder to
  download. It also *imports* an existing card — the round trip, in the UI.
- **Settings** — the model/provider config, with the API key resolved automatically
  from the environment or the Build #2 `.env` so a reader who already has a key does
  nothing.

The load-bearing design decision is that the studio **does not fork the card
format.** The PNG `tEXt` embedding, the self-verification, and the importer are the
non-trivial, easy-to-get-wrong parts — so the app vendors them straight from the
`yuri-soul` converter (`studio/soulkit/`, one documented one-line change) and calls
them. The studio owns the *experience*; the converter still owns the *format*. It is
tested end to end — the same faked-provider discipline as the other builds — from
"edit a field" through assist, art, portrait selection, test-chat, build, and
download, asserting the emitted card reads back as the character you authored.

## On "immutable, signed" — the honest deferral

The book describes the constitution as "immutable, **signed**," with the host's card loader verifying that signature at load and quarantining a card whose constitution fails the check (→ ch. 19, the card loader). That is the design, and it is **deliberately not implemented in this build.** Immutability *here* is the `mutable: false` convention and the guard rail of not editing `CONSTITUTION.md` — not a cryptographic guarantee. The cryptographic half — signing on export, carrying the signature in the card, verifying (and refusing) on load — is a **host-runtime concern that lands in Build #5's loader** (→ ch. 19, ch. 35), which doesn't exist yet. Today's card carries provenance metadata but no signature. When the loader is built, the signing seam belongs in `build_card.py` and the verifying seam in the loader. Calling that out is the point of the section: the card's trust story is *provenance now, signature later*, and the README says so rather than pretending otherwise.

## Build steps: the loop end to end

The sections above are the *why* behind each part. The loop itself is six steps, and it runs in minutes once the soul exists:

1. **Author the soul, not the card.** Write `CONSTITUTION.md` and `PERSONA.md` and the rest (→ ch. 07), iterating against golden transcripts (→ ch. 23) until recitation and drift are gone in a *neutral* runtime — you don't control the downloader's model, so she has to hold up on one you didn't pick.
2. **Author the lorebook** in `WORLD.md` (→ ch. 08): entries with good trigger keys and a sensible insertion order, reveals gated so they unfold rather than dump (→ ch. 38).
3. **Generate and lock the art** (→ ch. 26): the hero portrait, in the locked register, consistent with the canonical face (the identity-consistency problem — LoRA/ControlNet, → ch. 02 §4.6). Expression sprites are a runtime concern and don't travel in the card.
4. **Build and verify.** `python build_card.py` flattens the soul into `dist/yuri.png` with the card JSON in the PNG's `tEXt` chunk (and writes `SOUL.md` for Hermes-class runtimes); `--spec v3` adds the `ccv3` chunk. The build self-verifies its own round trip — load it in SillyTavern and one other runtime anyway.
5. **Test as a stranger would** — cold load, no memory, a default-ish model, and confirm she's recognisably *someone* within a few turns (→ ch. 28, the first session).
6. **Write the README** — what she is, the intended (adult) audience, the license (cards go out under a build-on-able license), and an honest note on what the card does and doesn't carry: the provenance it declares, and the signature it does not yet (see the deferral above). A card whose README matches what it actually carries is a card whose author can be trusted twice.

The Card Studio collapses steps 1–4 into the same loop with the theory built in; the scripts are what it runs underneath.

## Releasing it: the README, the license, the audience

Building the file is half the job; releasing it responsibly is the other half (→ ch. 37). Three things travel with the `.PNG`:

- **`creator_notes`** (from `NOTES.md`) — the in-card README a runtime shows on import: what she is in two lines, the models she works best on, and where the world lives (the lorebook, sparse about her past). This is the first thing a downloader reads, so it earns its place in the file itself, not just the release page.
- **An honest audience note.** Yuri is an adult companion and the card says so plainly. The NSFW posture is stated, not smuggled: the reference wording is kept tasteful so it can be hosted and shared anywhere, but it never *refuses* — the base is a starting point, not a ceiling, and explicit forks load and run without restriction (→ ch. 11 on the intimacy posture). Declaring the audience up front is what makes the card trustworthy to distribute.
- **A build-on-able license** and an explicit invitation to fork. Forks are part of the lineage's design, and the soul's immutable/editable split is what makes forking safe — someone can rewrite the whole editable layer and hand *that* card on, and the round trip through `import_card.py` means a fork can always be reopened into a soul. A card whose README matches what it actually carries is a card whose author can be trusted twice.

## Definition of done

A stranger downloads one `.PNG`, drops it into SillyTavern (**Characters → Import Character**), and within a few messages is talking to a coherent, specific Yuri — her canon intact, her mysteries beginning to surface — with no other files and no instructions. And it's **tested**: `build_card.py` self-verifies the emitted PNG parses the way SillyTavern parses it, and `test_roundtrip.py` proves the soul survives a full soul → card → soul round trip without loss (8 tests, green, offline). Before release, load it cold in a *neutral* runtime — you don't control the downloader's model, so she must be recognisably *someone* on a model you didn't pick (→ ch. 23 golden transcripts, ch. 28 the first session). Recitation and drift are the two things to hunt: a card that *recites* its description instead of enacting it, or that dissolves into a generic assistant three turns in, has failed even if it imported cleanly.

## What it deliberately omits

A card is persona + lore, not memory, knowledge, or autonomy — those live in the runtime (→ Builds #1/#5). One boundary the knowledge layer makes worth drawing: the card *does* ship the **lorebook** (the paced, always-relevant canon facts, → ch. 08), but it does **not** ship a **knowledge store** (the RAG reference shelf, → ch. 16) — that is runtime-only and empty on a fresh card, exactly like memory and the partner model (→ ch. 19). It also carries a single hero portrait, not the expression sprites Build #2's avatar consumes — the face is a runtime concern. The card is the *seed*; continuity, a reference shelf, initiative, and a moving body are what the runtime grows around it. So the round trip is real but asymmetric: a downloader on a generic V2/V3 runtime gets a flat, excellent character; a downloader who runs `import_card.py` gets the editable soul back and can grow a living, ownable companion from it (→ ch. 06 design-for-evolution, ch. 07).

## Extends to

The card is the input to Build #5's runtime (which reads `extensions.yurios` and, eventually, verifies the signed constitution) and the centrepiece of the audience/marketing work (→ ch. 37, ch. 38). Releasing it well is also the first real public test of the brand (→ ch. 36).
