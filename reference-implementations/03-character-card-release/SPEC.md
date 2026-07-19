# Card Studio — SPEC

Normative spec for the Build #3 Card Studio. Section numbers (§n) are referenced
from book ch. 33.

## §1 Goal & non-goals

**Goal.** A single-user local web app that turns character design into a fast,
enjoyable loop and ends in a SillyTavern-ready `.PNG` character card. It layers
authoring, AI assistance, art selection, and live testing on top of the existing
soul ⇄ card converter.

**Non-goals.** Not a runtime (no memory/knowledge/autonomy). No constitution
signing (Build #5). No multi-user auth or hosting. Not a general image editor.

## §2 Architecture

- **Backend:** FastAPI (`studio/app.py`), a factory `create_app(openrouter=...)`
  so the OpenRouter seam can be faked in tests. Sync route handlers; the two
  network calls run in a threadpool.
- **Converter:** `studio/soulkit/` — `build_card.py` + `import_card.py` **vendored**
  from `yuri-soul/` (VENDORED.md). The studio never reimplements PNG embedding,
  self-verification, or the importer.
- **Card model:** `studio/cardmodel.py` — the working draft ⇄ the `build_card`
  `data` dict, the token report, voice-law warnings, the placeholder portrait,
  the build, the soul-folder `.zip` export, and the card import.
- **Frontend:** `web/` — a no-build vanilla-JS SPA in the locked dark brand
  palette (`web/styles.css`).
- **Working state:** `workspace/` (gitignored) holds `draft.json`, `portrait.png`,
  `settings.json`, and `dist/` (built cards).

## §3 The draft (editable state)

The browser owns a **draft** — a friendly dict, not the card JSON:
`name, personality, description, scenario, first_mes, examples[],
alternate_greetings[], system_prompt, post_history_instructions, creator_notes,
creator, character_version, tags[], lorebook{scan_depth, token_budget,
recursive_scanning, entries[{keys[], content}]}`. `cardmodel.to_card_data`
maps it 1:1 to the card `data` dict; `from_card_data` is the inverse (used on
import). Editing card fields — not soul files — is the right altitude for a studio.

## §4 OpenRouter seam (§ ch. 33)

`studio/openrouter.py` exposes exactly two methods, `chat()` and `image()`:

- **chat** → `POST {base_url}/chat/completions`, reads `choices[0].message.content`.
- **image** → `POST {base_url}/images` with `{model, prompt}`, reads
  `data[].b64_json` (with a fallback for the chat-style `message.images[]` shape).
  Called `n` times to offer `n` candidates.

Key resolution order: `settings.json` → `OPENROUTER_API_KEY` env → sibling
`02-desktop-companion/.env`. The key is never returned to the browser unmasked.
A single retry covers a transient upstream 429. `CARD_STUDIO_FAKE_OR=1` swaps a
canned offline client (`_DemoOpenRouter`) for keyless demos and UI tests.

## §5 AI assist (grounded in ch. 06)

`studio/principles.py` encodes the ten ch. 06 principles and a field→principles
map. `studio/prompts.assist_messages` injects the relevant principles into the
assist model's system prompt so suggestions follow the book's recipe, and marks
the model uncensored so it won't refuse companion/NSFW writing. Modes: `improve`
(rewrite), `draft` (from scratch), `suggest` (advice only).

## §6 Test chat

`prompts.chat_messages` assembles the draft into a single system prompt the way a
V2/V3 runtime would (system_prompt + description + personality + scenario +
example dialogue + hard limits), then appends history + the new user turn — so
"test the card" exercises the card that will ship.

## §7 Build & verify (§ ch. 07)

`cardmodel.build` assembles the `data` dict, embeds it via `build_card.embed_png`
(V2 `chara` chunk always; V3 `ccv3` chunk when `spec=v3`), and **self-verifies**
with `build_card.verify_png` — the build fails if SillyTavern couldn't read it. It
returns the structured **token report** (per-field estimate vs the ch. 07 budgets),
voice-law warnings (any `!`), the verified chunks, and a placeholder-portrait flag.
It also writes `SOUL.md` (the OpenClaw single-file flattening).

## §8 Round trip

`GET /api/download/soul` exports the current draft as an editable soul folder
(`.zip`) via `import_card.write_soul`. `POST /api/import` unpacks an uploaded V2/V3
`.png`/`.json` back into a draft (and adopts the PNG image as the portrait) — the
same soul ⇄ card symmetry the chapter describes.

## §9 API surface

`GET /api/state`, `GET|POST /api/draft`, `POST /api/draft/reset`,
`POST /api/assist`, `POST /api/chat`, `POST /api/image`,
`GET|POST|DELETE /api/portrait`, `GET|POST /api/settings`, `POST /api/build`,
`GET /api/download/card`, `GET /api/download/soul`, `POST /api/import`,
`GET /api/health`. The SPA is served from `web/` (mounted last so `/api` wins).

## §10 Tests

Offline by default (faked OpenRouter). Unit (`test_converter.py`), endpoint
(`test_api.py`), end-to-end journey (`test_e2e_api.py`), and an optional Playwright
UI test (`test_e2e_playwright.py`) that skips unless Playwright + a browser are
installed. Target: green with `python -m pytest`, no network.
