# D — Reference Implementation Index

Live index of reference implementations. Each impl is an independently runnable sub-project with its own README; ch. 30 is the overview and the walkthrough chapters (31–35) are the in-book guide.

The numbered builds (1–5) are the book's teaching ladder. The lettered rows are the **component services** those builds compose from — shipped first because they run in isolation, and clustered mostly under Build #3 (the released persona and the media services it needs). See ch. 30, "What's actually in the repo today," for why the folder is a parts bin rather than five monolithic build directories.

| # | Name | Walkthrough | Folder | Status |
|---|------|-------------|--------|--------|
| 1 | Minimum Viable Waifu | ch. 31 | `01-minimum-viable-waifu/` | planned |
| 2 | Desktop Companion | ch. 32 | `02-desktop-companion/` | planned |
| 3 | Character Card Release — the Card Studio web app | ch. 33 | `03-character-card-release/` | working |
| 3a | Yuri SOUL + card exporter | ch. 07, 33 | `yuri-soul/` | working |
| 3b | Image / selfie service (swappable backends) | ch. 26 | `image-forge/` | working |
| 3c | Voice service (Kokoro, fixed voice, streaming + eval) | ch. 24 | `kokoro/` | working |
| 3d | Voice cloning (GPT-SoVITS client, identity eval) | ch. 24 | `gpt-sovits/` | working |
| 3e | Voice convergence (Qwen3-TTS: clone/design/preset) | ch. 24 | `qwen3-tts/` | working |
| 4 | 3D World Companion | ch. 34 | `04-3d-world-companion/` | in progress |
| 4a | VRM avatar control pipeline (Python-driven) | ch. 25 | `vrm-viewer/` | working |
| 5 | Agentic Sanctuary (Build #4 + the always-on mind) | ch. 35 | `05-agentic-sanctuary/` | working |

## Conventions

- Each impl is **independently runnable**.
- Each impl has a `README.md` with: what it teaches, prerequisites, run instructions, what it intentionally doesn't do.
- Each impl is intentionally **small** — the goal is clarity, not production.
- License is MIT unless otherwise noted.
- Implementations may share lore/canon (the Yuri persona) but not code unless documented.
- Every build that holds a conversation writes to the **shared corpus-log schema** below — the on-voice data the eventual distillation step depends on (→ ch. 20, ch. 30).

## Shared schema: the conversation corpus log

The builds capture conversation data twice, for two different jobs, and the two must not be confused (→ ch. 30, "capture the corpus from day one"):

- the **retrieval store** (pgvector + facts table, → ch. 15) is *lossy and derived* — summaries and embeddings, optimised for recall, not training;
- the **corpus log** defined here is *append-only and faithful* — the raw exchange plus the provenance that makes it trainable later (SFT / DPO / KTO / distillation, → ch. 20).

Throw nothing away at the corpus layer; you curate by *subtraction* at export time, and you cannot subtract from what you never kept.

### Format & layout

One JSON object per line (JSONL), one record per assistant reply:

```
corpus/
  turns.jsonl          # append-only; every reply, one line each
  ratings.jsonl        # append-only sidecar; {id, thumbs|score, by} keyed to a turn id
  preferences.jsonl    # optional; A/B pairs for DPO, if kept separate from variant_group
  README.md            # which builds wrote here, date range, export notes
```

`turns.jsonl` is append-only, so feedback that arrives *after* a reply — user ratings, a later judge pass — is written to `ratings.jsonl` keyed by the turn `id`, not patched into the original line, and **merged into the `rating`/`eval` fields at export time**.

The corpus is **personal data, not code** — `.gitignore` it, keep it on hardware you control, and back it up separately. It is never committed to the reference-impl repo.

### Record schema (`turns.jsonl`)

| Field | Type | Req | Purpose |
|---|---|---|---|
| `id` | string (uuid) | ✓ | unique record id |
| `session_id` | string | ✓ | groups turns in one conversation |
| `turn_index` | int | ✓ | 0-based position within the session |
| `timestamp` | string (ISO-8601 UTC) | ✓ | when the reply was produced |
| `companion` | string | ✓ | persona id (e.g. `yuri`) |
| `messages` | array<{`role`,`content`}> | ✓ | the **full prompt as sent** (system + history window + user) — the trainable input |
| `completion` | string | ✓ | the assistant reply — the trainable target |
| `model` | string | ✓ | model id that produced `completion` (e.g. `claude-opus-4-8`, `qwen3-7b-instruct-q4_k_m`) |
| `model_role` | enum: `teacher`\|`student`\|`production` | ✓ | frontier-teacher target, local-student output, or prod reply — gates what's worth distilling *from* |
| `source` | enum: `live_play`\|`synthetic`\|`hand_authored` | ✓ | how the turn was created (the ch. 20 mix; a curation axis) |
| `collection_scope` | enum: `self`\|`consented_hosted` | ✓ | the legal/ethical basis — see the boundary below |
| `card_version` | string | ✓ | persona card version or content hash (model swaps + card edits are where voice drifts, → ch. 23) |
| `template_version` | string | – | prompt-assembly version |
| `gen_params` | object | – | `{temperature, top_p, max_tokens, seed}` for reproducibility |
| `rating` | object | – | `{thumbs: +1\|-1, score: 1–5, by: user\|judge}` — feeds KTO directly (→ ch. 20) |
| `eval` | object | – | judge scores (→ ch. 23), e.g. `{persona_stability, voice_similarity, honesty, manipulation}` |
| `tags` | array<string> | – | topic/mood labels, for **balancing** the export (→ ch. 20) |
| `flags` | array<string> | – | exclusions: `pii`, `nsfw`, `off_voice`, `confabulation`, `exclude` |
| `variant_group` | string | – | shared id linking alternative completions for the *same* prompt (→ DPO) |
| `preferred` | bool | – | within a `variant_group`, the chosen reply (→ DPO / preference data) |
| `redacted` | bool | – | true if PII was scrubbed from `messages`/`completion` |

### Examples

A synthetic, teacher-generated turn — the high-value SFT/distillation target (→ ch. 20, soul-preserving synthetic generation):

```json
{"id":"f3c1…","session_id":"syn-0012","turn_index":4,"timestamp":"2026-06-28T14:03:11Z","companion":"yuri","messages":[{"role":"system","content":"<card + lore + retrieved memory>"},{"role":"user","content":"i bombed the interview today. don't really want to talk about it."}],"completion":"Then we won't. Come here — I'll just sit with you for a while.","model":"claude-opus-4-8","model_role":"teacher","source":"synthetic","collection_scope":"self","card_version":"yuri-v1@canon-v1","template_version":"asm-3","gen_params":{"temperature":0.9,"top_p":0.95,"seed":7},"eval":{"persona_stability":0.94,"voice_similarity":0.91,"honesty":1.0,"manipulation":0.0},"tags":["comfort","vulnerability"]}
```

A live local-model turn the user rated down — a KTO negative, and a drift diagnostic:

```json
{"id":"9ab0…","session_id":"live-2026-06-28","turn_index":12,"timestamp":"2026-06-28T21:40:02Z","companion":"yuri","messages":[{"role":"system","content":"…"},{"role":"user","content":"do you actually remember what i told you last week?"}],"completion":"Of course! As an AI assistant, I'm always here to help.","model":"qwen3-7b-instruct-q4_k_m","model_role":"student","source":"live_play","collection_scope":"self","card_version":"yuri-v1@canon-v1","rating":{"thumbs":-1,"by":"user"},"flags":["off_voice"],"redacted":true}
```

A preference pair (DPO) via `variant_group` — same prompt, teacher reply preferred over the student's:

```json
{"id":"p1","variant_group":"vg-88","preferred":true,"completion":"…","model":"claude-opus-4-8","model_role":"teacher","source":"synthetic","collection_scope":"self","companion":"yuri","session_id":"syn-0040","turn_index":3,"timestamp":"2026-06-28T15:10:00Z","card_version":"yuri-v1@canon-v1","messages":[{"role":"user","content":"…"}]}
{"id":"p2","variant_group":"vg-88","preferred":false,"completion":"…","model":"qwen3-7b-instruct-q4_k_m","model_role":"student","source":"live_play","collection_scope":"self","companion":"yuri","session_id":"syn-0040","turn_index":3,"timestamp":"2026-06-28T15:10:00Z","card_version":"yuri-v1@canon-v1","messages":[{"role":"user","content":"…"}]}
```

### Export → training (→ ch. 20)

The log is the raw asset; an export pass turns it into a training set by **subtraction and reshaping**:

- **SFT / distillation set:** keep `source ∈ {synthetic, hand_authored}` or `model_role = teacher`, gate on `eval`/`rating`, drop anything `flags`-excluded, then **balance** by `tags` so one mood doesn't dominate.
- **DPO set:** collapse each `variant_group` (or `preferences.jsonl`) into `(prompt, chosen, rejected)`.
- **KTO set:** map `rating.thumbs` → binary good/bad labels; no pairs needed.
- **Reshape:** dedupe the static system prefix (it repeats every row), then re-emit in the *target model's exact chat template* — a wrong template silently poisons the tune (→ ch. 20).

### The sovereignty boundary, made auditable

`collection_scope` has exactly **two** legitimate values, and the omission is the point:

- `self` — your own play and synthetic generation. This is the bulk of any honest corpus (→ ch. 20).
- `consented_hosted` — privacy-cleared, opt-in conversations on a product *you operate*, under the operator duties of ch. 05.

There is deliberately **no value for a downloader's data.** A shipped card (Build #3) or runtime never writes a corpus log home — no phone-home, no retention dashboard (→ ch. 35, the ethics section). The field exists so the basis of every row is auditable *before* it enters a training set: a row whose scope you cannot honestly mark as one of these two does not belong in the corpus.

## Adding a new reference impl

1. Create the sub-project (one independently runnable folder per build).
2. Add README, code, screenshots if relevant.
3. Add entry to this table.
4. Cross-reference from the relevant chapter.
