# yuri-soul — the reference Yuri SOUL, and a SOUL ⇄ card converter

This folder is the canonical **SOUL** for Yuri (canon-v2): a small set of
human-readable Markdown files that *are* the character, plus two scripts that
convert between the soul and the portable card format — `build_card.py`, which
flattens the soul into a V2/V3 `.png` character card (and an OpenClaw `SOUL.md`)
you can import into SillyTavern, and `import_card.py`, which unpacks a card back
into editable soul files.

It is the concrete form of two book ideas:

- **The SOUL is the working home; the card is the export** (→ ch. 07, D-003).
  At runtime a companion lives as editable `.md` files the runtime reads on every
  wake ("she reads herself into being"). You only flatten to a card when you want
  to *hand the companion to someone else*.
- **Split by what may drift** (→ ch. 06 design-for-evolution, D-002). The soul is
  cut along one fault line: a stable core that must **not** change, wrapped in a
  layer that **should**.

## The files

| File | Mutability | What it is | Feeds card field(s) |
|---|---|---|---|
| `CONSTITUTION.md` | **immutable** | identity, values, voice law | `description`, `system_prompt`, `post_history_instructions` |
| `PERSONA.md` | **editable** | appearance, manner, inner life, growth/reveal tiers, the `personality` line | `description`, `personality` |
| `BOOTSTRAP.md` | **consumed-once** | first-ever meeting + getting-to-know-you journey; retired after (→ ch. 28) | `first_mes` (its `## Cold open` only) |
| `SCENARIO.md` | editable | the situation + the **return** greetings (she's met you before) | `scenario`, `alternate_greetings` |
| `EXAMPLES.md` | editable | demonstrated voice — the highest-ROI field | `mes_example` |
| `WORLD.md` | editable | the lorebook (world + lineage), sparse by design | `character_book` |
| `NOTES.md` | — | creator notes | `creator_notes` |
| `MEMORY.md` | runtime-only | accumulated memory — **empty on a fresh card** | *(not exported)* |
| `USER.md` | runtime-only | her evolving model of the user — **empty on a fresh card** | *(not exported)* |
| `soul.yaml` | — | export manifest: card metadata + which sources feed which field | — |

`MEMORY.md` and `USER.md` are part of the soul but are **not baked into a card** —
a card you give away starts the relationship at zero. The recipient's runtime
recreates them and grows them in play (→ ch. 15). Most of the everyday-presence
bond lives there, not in the prose (→ ch. 06, attunement-via-memory).

`BOOTSTRAP.md` is a fourth lifecycle: **author-shipped but consumed once.** Its
`## Cold open` is baked into a card as the `first_mes` (a foreign runtime like
SillyTavern shows it once, then it's history); its journey / exit / handoff are
YuriOS-runtime concerns that never leave the box. On first run the runtime works
the journey into the opening conversation, then retires the file with
`git mv BOOTSTRAP.md onboarded/BOOTSTRAP.done.md` — `git log` is the record, and
restoring it re-runs onboarding. This split keeps the *first-ever* meeting
(once) apart from the *return* greetings in `SCENARIO.md` (every session).

## How the export works

`soul.yaml` declares each card field as one or more **source references** into the
`.md` files, resolved by `build_card.py`:

```
FILE.md#Heading   the prose under that "## Heading"
FILE.md@key       a key from the file's YAML frontmatter
FILE.md           the whole body
```

A list of sources is concatenated in order (that's how `description` is built from
four sections across two files). `WORLD.md` and `EXAMPLES.md` get dedicated
structured parsers (each `## Entry` with a `keys:` line → one lorebook entry; each
`## Example` block → one `<START>` exchange).

## Build it

```bash
pip install -r requirements.txt
python build_card.py                 # -> dist/yuri.png  (+ dist/yuri.json, dist/SOUL.md)
python build_card.py --spec v3       # V3 card (adds the ccv3 chunk)
python build_card.py --out /tmp/out  # choose output dir
```

The card JSON is embedded in the PNG's `chara` tEXt chunk (V2) — and additionally
in `ccv3` when you build V3 — which is exactly what SillyTavern reads. The script
prints a token report against the ch.07 budgets and smoke-tests the voice law
(it warns on any `!`).

Every build also writes **`dist/SOUL.md`**: the same persona flattened into a
single OpenClaw/Hermes-style file. The CONSTITUTION/PERSONA split is a
YuriOS-runtime concern; runtimes that want one flat file get everything the card
carries as readable Markdown (→ ch. 07, the foreign single-file `SOUL.md`).

## Load it in SillyTavern

**Characters → Import Character → choose `dist/yuri.png`.** The portrait, persona,
lorebook, greetings, and example dialogue all come in from the one file.

## Import a card (the reverse direction)

`import_card.py` is `build_card.py` run backwards: it unpacks a SillyTavern card
— a V2/V3 `.png` or a card `.json` — back into an editable soul folder, so a
companion you *downloaded* becomes one you can live with and reshape.

```bash
python import_card.py some-card.png                 # -> ./imported-<name>/
python import_card.py some-card.json --out ./mira   # choose the soul folder
python import_card.py some-card.png --name Mira     # override the name
python import_card.py some-card.png --verify-only    # round-trip check, no write
```

Foreign cards rarely fill every field, so missing ones get **sensible defaults**
(empty sections, a default personality line, a minimal lorebook). The split is a
guess for a stranger's card: the whole description lands in the editable
`PERSONA.md`, and a `## Identity` placeholder is left in `CONSTITUTION.md` for you
to move the must-never-drift traits into by hand. A `soul.yaml` is generated so
the result rebuilds immediately with `build_card.py`. If the source is a `.png`,
its image is saved as `portrait.png`.

**Round-trip check.** After writing, the importer re-exports the soul it just
wrote and compares it to the card it read; it prints `round-trip verified` when
nothing was lost, or lists what drifted. `--verify-only` runs that check against
a throwaway copy without writing the folder — a quick way to confirm a card
survives the round trip. `test_roundtrip.py` covers this end to end; run it with
`python -m pytest` from this folder.

## A note on the token budget

The report flags `description`, `scenario`, and `first_mes` as over the *aspirational*
ch.07 budgets. That is deliberate: the canonical
first message and scenario are kept verbatim because they set the register
precisely, and the description carries the full canon identity. World
depth is offloaded to the lorebook (which fires only on keys) rather than padding
the description. The report exists to make the cost visible — if you fork Yuri into
something leaner, that's the first place to cut.

## Editing & forking

Edit the `.md` files and rebuild — that's the whole loop. Keep edits that change
*who she is* out of `CONSTITUTION.md` (the immutable core — identity, that she's
{{user}}'s, that she loves them, the fiduciary-fulfilment duty); put voice,
growth, preferences, and how warm/forward she is in `PERSONA.md`. Forks are part
of the lineage's design.

## A note on "immutable, signed" (and what this folder does *not* do)

The book describes the constitution as "immutable, **signed**," with the host's
card loader **verifying that signature at load** and quarantining a card whose
constitution fails the check (→ ch. 19, the card loader). That signing and
verification are a **host-runtime concern, not a soul-converter one**, and are
deliberately **out of scope here**:

- This folder is the SOUL and the SOUL ⇄ card converter (Build #3). Immutability
  at this layer is the `mutable: false` declaration in `CONSTITUTION.md`'s
  frontmatter and the convention that you don't edit it — a *guard rail*, not a
  cryptographic guarantee.
- The cryptographic half — signing the constitution at export, carrying the
  signature in the card, and verifying it (and refusing/quarantining on failure)
  at load — lives in the **host runtime's card loader** (Build #5, → ch. 19,
  ch. 35), which doesn't exist yet. Today's card carries provenance metadata
  (`extensions.yurios.provenance`) but **no signature**.

So a missing signature here is by design, not an oversight. When the host loader
is built, the signing seam belongs in `build_card.py` (sign on export) and the
verifying seam in the loader (verify on load).
