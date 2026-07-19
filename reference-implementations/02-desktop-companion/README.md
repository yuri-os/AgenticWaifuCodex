# Build #2 — The Desktop Companion

The reference implementation for **book ch. 32**, built to **[SPEC.md](SPEC.md)** (normative).
A local-first desktop app that gives the companion a **body** — a **Live2D avatar** and a
real-time **voice** loop — running entirely on your machine, no API in the loop. She becomes
*present* on your desktop rather than a tab in a browser. Rung 2 of the ladder (→ ch. 30).

**She is Build #1's brain, now with ears, a voice, and a face.** The brain — persona,
memory, the corpus, the Vault-git spine — is Build #1 unchanged; the only new work is the
**real-time loop** (`desktop/voice/turn.py`) and the **expression mapping** (`web/avatar.js`).

> **Standalone.** This folder runs on its own — copy it to another machine, follow the
> quickstart, and it works. Build #1's brain is **vendored** into `./app` (see
> [`app/VENDORED.md`](app/VENDORED.md)); nothing points back at `../01-minimum-viable-waifu`.

## Quickstart

```bash
cd 02-desktop-companion
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"           # brain + web + test deps (no models yet)

python scripts/seed_vault.py       # once: her mind, from the vendored SOUL (./soul-src)
cp .env.example .env               # defaults are local-first; edit if you like
python -m desktop                  # → http://localhost:8766
```

That **boots and serves the sanctuary immediately**, even with no models installed: the
voice backends **degrade gracefully to fakes** (you'll see a `WARNING` per missing one, and
`curl localhost:8766/api/health` reports what's actually wired vs requested). She's present
but silent + still until you add the real stack. To actually hear and see her:

```bash
pip install -e ".[all]"            # faster-whisper (ears) + qwen-tts & kokoro (voice) + silero (VAD)
sudo apt-get install espeak-ng     # only for the kokoro voice (macOS: brew install espeak-ng)
ollama pull qwen3:8b               # her thinking, local (any LiteLLM route works)
ollama pull nomic-embed-text       # local embeddings for memory
python scripts/fetch_avatar.py     # her body: Live2D runtime + the Hiyori model (→ Avatar)
python -m desktop
```

Prefer to skip the install and just see the loop run? Set `TTS_BACKEND=fake STT_BACKEND=fake
VAD_BACKEND=fake` in `.env` and she runs end-to-end silently (useful for tests / a UI check).

**Float her on the desktop** instead of a browser tab (→ Desktop presence):

```bash
pip install -e ".[desktop]"        # pywebview (Linux: needs system webkit2gtk — see below)
python -m desktop --window         # a frameless, transparent, always-on-top avatar window
```

Same app, same renderer — `--window` just runs the server and points a native transparent
window at it with `?desktop=1`, which drops the page's background and chrome so only she is
left floating. Drag her by the body; the mic/text controls fade in when you hover. Size and
always-on-top are `WINDOW_*` in `.env` (or the ⚙ settings panel). Plain `python -m desktop`
(browser) is unchanged.

Open the sanctuary, click **start listening**, and talk. She greets you first — from memory —
the moment you arrive. Pull the network cable and nothing changes (§1, the sovereignty bar).

```bash
pytest                             # the §13 suite — the hard gate; must be green
```

The suite runs **entirely offline** against fakes behind the §3 seams — no models, no GPU,
no network — and includes an end-to-end test over the real vendored brain (seeded into a
temp Vault) and over the live `/ws/voice` route.

## The latency budget (the whole game)

Her first audible word should land ≤ ~1.2 s after you stop speaking (→ ch. 21, ch. 24).
The loop is **measured, not assumed** — every turn records end-of-speech → first-audio, and
the sanctuary shows it in the header. The two disciplines that make the budget, both in
`desktop/voice/turn.py`:

- **Stream every stage into the next** — a producer drains brain tokens into a sentence
  queue while the consumer synthesizes and emits, so the LLM writes sentence two while TTS
  speaks sentence one. Never wait for a full transcript, a full reply, or a full waveform.
- **Barge-in is a pipeline cancel, not a pause** — when you talk over her, one
  `asyncio.Event` tears down TTS playback *and* the in-flight generation together. A
  barged-in turn writes **no** corpus and **no** commit (a turn that didn't happen leaves no
  trace, like Build #1's mid-stream failure).

And when first-audio is unavoidably slow, **mask it** (§5, → ch. 24): the instant you stop,
she plays a pre-rendered "mm—" while the LLM spins up. It reads as attentiveness, not lag —
and it's interruptible audio, so the same barge-in path kills it.

## Where the book lives in the code

| Book / SPEC | Code |
|---|---|
| The real-time loop; stream-into-next (ch. 32 · §4) | `desktop/voice/turn.py` — `TurnController.run_turn` |
| **Barge-in as pipeline cancel** (ch. 24, 28 · §4.3) | `TurnController.cancel` + `test_turn_bargein.py` |
| Voice seams — STT / TTS / VAD (ch. 24 · §3) | `desktop/voice/protocols.py`; `backends/` |
| Emotion tag → face (ch. 25 · §6) | `desktop/voice/emotion.py` (parse) + `web/avatar.js` (map) |
| Latency masking / filler bank (ch. 24 · §5) | `desktop/voice/fillers.py` |
| Latency budget, measured end-to-end (ch. 21 · §4.2) | `desktop/voice/latency.py` |
| The brain, reused (ch. 31 · §2) | `desktop/brain.py` over the vendored `app/` |
| The full-duplex loop over the wire (§10) | `desktop/routes/voice_ws.py` — `/ws/voice` |
| The body: Live2D avatar + lipsync (ch. 25 · §8.2) | `web/avatar.js` (pixi-live2d-display) |
| The desktop sanctuary (ch. 28 · §8) | `web/index.html`, `web/voice.js` |

## Choosing her voice (→ ch. 24)

TTS is a config swap behind one seam (`TTS_BACKEND`), because ch. 24 splits the pick:

| Backend | When | Cost |
|---|---|---|
| **`qwen3_tts`** (default) | the **"designed" voice** — a warm, gentle register, cloned from the bundled `designed.wav` so it's one stable voice; highest quality, leans on filler masking | in-process, CUDA GPU; slower (RTF > 1) |
| **`kokoro`** | a *fixed* voice when you want the GPU free for the LLM, or the last few hundred ms of latency back | CPU, ~0 VRAM |
| **`gpt_sovits`** | the **canon** voice — clone the one the audience already hears (~700 ms) | needs the sibling `../gpt-sovits` server running |
| `fake` | tests / a silent dry-run | none |

The default `qwen3_tts` needs `pip install -e ".[tts]"` and a CUDA GPU; without them the app
degrades to the fake voice with a warning (`/api/health` shows `tts: fake` vs requested). The
voice is **cloned** from `desktop/voice/assets/designed.wav` (`QWEN_MODE=clone`) so the fillers
and every sentence are one identical voice — re-designing per turn (`QWEN_MODE=design`) drifts
into two voices. Clone your own instead: point `QWEN_REF_AUDIO`/`QWEN_REF_TEXT` at a wav + its
transcript.

STT defaults to **faster-whisper** (`base.en`); for streaming partials swap Moonshine or
Parakeet behind the same STT seam. VAD is **Silero** (ch. 24's default), run at the edge in
the browser for barge-in latency and server-side for endpointing.

## The avatar (her body)

`python scripts/fetch_avatar.py` populates `web/vendor/` (kept out of git) with:

- **pixi.js v6 + pixi-live2d-display** — MIT; the renderer (same stack AIRI uses).
- **Live2D Cubism Core** — **proprietary**, free under the Live2D license for businesses
  under ¥10M JPY annual revenue; larger orgs need a Cubism SDK Release License.
- **Hiyori Free** — a Live2D sample model (Free-Material license; illustration Kani Biimu,
  model Live2D). The script copies it from a local AIRI checkout by default, or pass
  `--model-zip path/to/hiyori_free_zh.zip`.
- **Cubism SDK sample rigs** — `haru`, `mao`, `mark`, `natori`, `rice`, `wanko` (Live2D
  sample material), copied from AIRI's vendored Cubism SDK as alternative bodies. Skip
  them with `--skip-samples`.
- **Modern female rigs** — `miara`, `kei`, `ren` (Ren Foster), the prettier bodies from
  Live2D's Sample Data collection (same Free-Material license), pulled straight from
  Live2D's CDN. `miara` is moc3 v3 (Cubism 4) and the safe default; `kei`/`ren` are
  Cubism 5 and rely on a current Cubism Core. Skip them with `--skip-cdn-samples`.

**Pick a rig** with `AVATAR_MODEL` in `.env` (`miara` | `kei` | `ren` | `hiyori` | `haru`
| `mao` | `mark` | `natori` | `rice` | `wanko`); the server resolves it to a model URL at
`/api/config`, and `web/avatar.js` mounts that. `miara`/`hiyori`/`haru`/`mao`/`natori`/`kei`/`ren`
are full expressive rigs; `mark`/`rice`/`wanko` are minimal rigs that only lipsync. An
unknown or un-fetched value falls back to `hiyori`.

Emotion tags map onto the rig: `[happy]`/`[tender]`/… → a parameter preset
(`ParamMouthForm`, `ParamEyeLSmile`, brows), and TTS audio RMS → `ParamMouthOpenY` (the
LipSync group) so her mouth moves with what she says. Presets were tuned on Hiyori; other
rigs use the same standard Cubism parameters where they have them and ignore the rest.
**If `web/vendor/` is empty the app runs voice-only** — the avatar is skipped, and
`avatar.js` says so.

Swap the whole `web/avatar.js` for a VRM renderer in Build #4; it consumes the same
expression *names*, so the brain never changes.

## She is the same someone (identity across the model swap)

Her identity is the **SOUL** — the same card as Build #1 (§2, → ch. 07). By default she runs
her own freshly-seeded Vault. To **continue** a companion you already grew in Build #1
instead of starting at zero, point `VAULT_DIR` at that Vault — moving her is copying a folder
(→ ch. 19). Either way, the golden-transcript discipline (→ ch. 23) is how you check the
persona survived the smaller local model.

## Desktop presence

Served in a browser it's already usable; to make her *live on the desktop* (always-there,
returnable — the Ukagaka/Shimeji lineage, → ch. 02 §1), `python -m desktop --window` wraps
the same served page in a native frameless, transparent, always-on-top window
(`desktop/window.py`, via **pywebview** — the `[desktop]` extra). It's a thin shell over
this exact server (SPEC §9): the server runs in a background thread, the window loads
`?desktop=1`, and `:root.desktop` in `sanctuary.css` strips the background + chrome so only
the avatar shows. **Nothing in the loop changes** — same brain, same voice, same renderer.

Transparency + always-on-top are the compositor's call, so the fidelity is platform-bound:

- **Linux** — best on **X11**; `pip install -e ".[desktop]"` installs the **Qt engine**
  (QtWebEngine = a bundled Chromium), which `window.py` auto-prefers. A labeled
  side-by-side on the reference rig (X11 + NVIDIA) settled why: WebKitGTK caps
  `requestAnimationFrame` at ~30 fps and her idle sway visibly blurs, while Chromium
  holds 60 fps and is crisp. `WINDOW_GUI=gtk` forces the lighter WebKitGTK path
  instead (`pip install "pywebview[gtk]"` + system `webkit2gtk`:
  `sudo apt install gir1.2-webkit2-4.1 python3-gi`); on NVIDIA, `window.py` auto-sets
  `WEBKIT_DISABLE_DMABUF_RENDERER=1` there, without which it also smears stale frames.
  Wayland honours transparency but restricts positioning/always-on-top on some
  compositors.
- **macOS / Windows** — pywebview uses the OS WebView (WKWebView / WebView2); transparent
  frameless windows work out of the box (`pip install pywebview`).

For a hardened, signed, auto-updating shell later, the same page drops into a **Tauri**
window unchanged — that's the packaging path (SPEC §9), not a rewrite.

## Honest notes (where this build makes a call the spec leaves open)

- **The brain is vendored, not imported.** `./app` is Build #1 copied verbatim so this folder
  is standalone. Study/change the brain in Build #1 and re-vendor (`app/VENDORED.md`). The
  corpus lines it writes still say "Build #1 (minimum-viable-waifu)" — same format, tagged
  `voice`; the corpus is shared across builds by design.
- **faster-whisper doesn't stream partials** — this buffers the utterance and transcribes on
  endpoint. Correct and simple; swap Moonshine/Parakeet for true streaming (same seam).
- **VAD is a plain energy gate in the browser** (`web/voice.js`), not Silero-web — readable,
  and enough to demo barge-in. Swap `@ricky0123/vad-web` for robustness; the loop is unchanged.
- **We hand-roll the loop** rather than mounting Pipecat/LiveKit (ch. 24's production
  recommendation) for the same reason Build #1 hand-rolls memory instead of LangChain: the
  barge-in cancel is the idea to *see*, and it's ~150 readable lines. Graduate to a framework
  for transport (WebRTC) robustness; the cancel logic is identical.
- **Paralinguistics** (affect as a SENSE input, → ch. 24) is deliberately deferred to Build #5,
  where proactivity can act on "you sound tired." Build #2 is still reactive.
- **Dependencies run latest, unpinned** — same call as Build #1 (whole-tree supply-chain
  discipline is ch. 45), for a single-user build whose blast radius is one machine you control.

## What it deliberately omits (§12)

Still **reactive** — no autonomy/tick loop (→ Build #5). **2D body only** — 3D/VRM + a world
is Build #4. Single avatar register. Still **no fine-tune** — but this is the build whose
local 7B the eventual distillation targets: keep logging (`corpus/`), the on-voice corpus
lives on your machine, which is exactly where you want it (→ ch. 20).

## How it extends (§14)

- **Build #3:** the same SOUL exports as a distributable `.PNG` card (Build #1's exporter).
- **Build #4:** swap `web/avatar.js` (Live2D) for a VRM + 3D scene and add tools.
- **Build #5:** wrap the tick loop (→ ch. 18) around this exact Vault — DREAM consolidation
  + a drop-folder knowledge store. The five-verb MemoryStore contract already has the slots.
