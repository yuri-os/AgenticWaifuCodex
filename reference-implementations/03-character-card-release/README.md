# 03 — Card Studio (Build #3: The Character Card Release)

A local web app that makes character design **fun, easier, and streamlined**, and
ends in one click: **Generate** → a SillyTavern-ready `.PNG` character card.

It is the interactive front-end for Build #3. The card-format machinery (PNG
embedding, self-verification, the soul importer) is reused verbatim from the
sibling [`yuri-soul/`](../yuri-soul/) converter — see
[`studio/soulkit/VENDORED.md`](studio/soulkit/VENDORED.md).

## What it teaches

- **Character cards** as a build artifact (→ book ch. 07) and the soul ⇄ card
  round trip (→ ch. 33) — including importing an existing card to edit it.
- **The ch. 06 design principles put to work**: the AI-assist grounds every
  suggestion in the book's recipe (specificity, enact-don't-describe, orientation)
  instead of the generic-assistant default.
- Wiring an app to **OpenRouter** for both text (writing help + a live test chat)
  and **image generation** (candidate art you review and pick from).

## The five tabs

| Tab | What it does |
|---|---|
| **Design** | Edit every card field. Each field has ✎ *improve* / ✦ *draft* / ? *suggest* buttons that call an OpenRouter model grounded in the ch. 06 principles. Autosaves. |
| **Art** | Describe the look, **generate candidates through OpenRouter**, and click one to make it the card's portrait (or upload your own). |
| **Test** | **Chat with the card** exactly as a runtime would assemble it, before you ship — using your OpenRouter chat model. |
| **Generate** | Build the `.PNG`, self-verify it parses the way SillyTavern parses it, read the **token report** (→ ch. 07 budgets), and download the card **and** an editable soul folder (`.zip`). Also **imports** an existing V2/V3 card to edit. |
| **Settings** | OpenRouter config — key, base URL, models, temperature. Model presets included. |

## Run it

```bash
cd reference-implementations/03-character-card-release
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run.py          # → http://127.0.0.1:8777
```

Open the URL, edit the starter character, click **Generate**, download your card.

### The OpenRouter key

The AI features (assist, test-chat, art) call OpenRouter. The key is resolved at
call time, in this order:

1. a key saved in the **Settings** tab (`workspace/settings.json`),
2. the `OPENROUTER_API_KEY` environment variable,
3. the **sibling Build #2 `.env`** (`../02-desktop-companion/.env`).

So if you already put your key in Build #2, the studio finds it automatically —
the header shows `key ✓` and its source. Get a key at
[openrouter.ai/keys](https://openrouter.ai/keys).

**No key?** Run in offline **demo mode** to explore the UI (canned replies, no
network, still builds real cards):

```bash
CARD_STUDIO_FAKE_OR=1 python scripts/run.py
```

### Default models (all editable in Settings — model ids drift)

- **Text (assist + test-chat):** `z-ai/glm-5.2` — a strong, current model. It is a
  *reasoning* model, so `max_tokens` defaults to a generous 2048 (its thinking
  shares the budget). If you want an uncensored writer that won't hesitate on adult
  personas, switch to a preset: `venice/uncensored` (free), `thedrummer/cydonia-24b-v4.1`,
  `neversleep/llama-3-lumimaid-70b`.
- **Image:** `google/gemini-2.5-flash-image` (Nano Banana). Presets:
  `google/gemini-3.1-flash-image-preview`, `bytedance-seed/seedream-4.5`.

## Tests

```bash
python -m pytest            # 23 tests, offline (faked OpenRouter)
```

- `test_converter.py` — the card model + vendored converter reuse: a draft builds
  a `.PNG` that self-verifies, reads back as the same character, and round-trips.
- `test_api.py` — every endpoint against a fake OpenRouter (no network).
- `test_e2e_api.py` — the whole journey: load → edit → assist → art → portrait →
  test-chat → build → download → verify the emitted `.PNG` imports.
- `test_e2e_playwright.py` — optional browser UI test; **skips** unless you
  `pip install playwright && playwright install chromium`.

## What it intentionally doesn't do

- It is **not** a runtime — no memory, knowledge, or autonomy (those are Builds
  #1/#2/#5). It authors, tests, and exports the *card* (→ ch. 33, "what it omits").
- It does **not** sign the constitution — signing/verification is a host-loader
  concern deferred to Build #5 (→ ch. 33, "the honest deferral").
- Image generation is via **OpenRouter (cloud)**. For a local diffusers pipeline,
  see the sibling [`image-forge/`](../image-forge/) service.
