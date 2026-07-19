# Build #4 — The 3D World Companion

The reference implementation for **book ch. 34**, built to **[SPEC.md](SPEC.md)** (normative).
A browser-based 3D companion: a **VRM avatar in the canonical sanctuary** — a small room,
low warm light, rain on the window — with a **chat transcript beside her**, the Build #2
**voice loop**, four real **tools over MCP** (a timer, the room's music, a weather lookup,
and **her camera** — selfies that land in the chat), and **scripted ambient life** when
you're quiet. Rung 4 of the ladder (→ ch. 30): the richest *reactive* body — a presence, a
place, and hands.

**She is Build #1's brain and Build #2's voice, now with a 3D body, a room, hands — and
the YuriOS backbone.** The brain (persona, memory, corpus, the Vault-git spine) and the
voice stack (STT/TTS/VAD, turn controller, barge-in) are vendored unchanged; the new work
is the **event bus** (`world/hub.py` — the YuriOS `EventHub`, ported: every host→frontend
event is one typed JSON object on one SSE stream), the **VRM stage** (`web/js/stage/`),
the **puppet strings** (`world/avatar/controller.py` → `avatar` events on the bus), the
**chat surface** (`web/js/chat.js` + the transcript ring), the **tool loop**
(`world/brain.py` + `world/tools/`), the **selfie lab** (`world/selfies.py` over the
vendored `./forge`), and the **idle machine** (`world/idle.py`).

> **Standalone.** This folder runs on its own — copy it to another machine, follow the
> quickstart, and it works. Build #1 is vendored into `./app`, Build #2 into `./desktop`,
> the image-forge slice into `./forge` (see the three `VENDORED.md`s); nothing points back
> at `../01-…`, `../02-…`, or `../image-forge`. The frontend is **no-build**: three.js +
> three-vrm are committed ES modules in `web/vendor/` — no npm, no bundler, one process.

## Quickstart

```bash
cd 04-3d-world-companion
python3 -m venv .venv && source .venv/bin/activate
sudo apt-get install espeak-ng     # for the kokoro voice (macOS: brew install espeak-ng)
pip install -e ".[all,test]"       # brain + MCP + the real voice stack:
                                   #   faster-whisper (ears) · kokoro (voice) · silero (VAD)
ollama pull qwen3:8b               # her thinking, local (any LiteLLM route works)
ollama pull nomic-embed-text       # local embeddings for memory

python scripts/seed_vault.py       # once: her mind, from the vendored SOUL (./soul-src)
cp .env.example .env               # defaults are local-first; edit if you like
python -m world                    # → http://localhost:8767
```

Open it, click **enter the sanctuary** (one click, so the browser lets her speak —
autoplay policy), then **start listening** and talk — or type in the **chat column beside
the room**, which carries the whole conversation: your turns (spoken ones included, via
STT), her replies as they stream, and her selfies (*"take a selfie by the window"* — the
photo appears in the chat a few moments later; set `OPENROUTER_API_KEY` in `.env` for
real pixels, placeholder cards otherwise). The voice stack warms in the background — the
room and her body render in seconds, and the first run downloads the kokoro/whisper
weights, so give her voice a minute; `curl localhost:8767/api/health` reports what's
actually wired (voice, tools, selfies, idle, attached viewers) and when it's ready.

### The four ways to run her

One server, two frames (browser tab / native desktop window), two bodies (the VRM stage /
Build #2's Live2D client). Every combination works, off the same brain, voice loop, tools,
and idle machine:

| | frame | body | how |
|---|---|---|---|
| **1** | browser | VRM sanctuary (default) | `python -m world` → open `http://localhost:8767` |
| **2** | browser | Live2D (B2's client, §6.6) | same server → open `http://localhost:8767/live2d/` |
| **3** | desktop window | VRM, room set aside (§6.5) | `python -m world --window` |
| **4** | desktop window | Live2D desktop pet | `python -m world --window --body live2d` |

Two one-time setups gate the non-default modes:

```bash
# Live2D body (modes 2 + 4): fetch the runtime + rigs — third-party, never in git
python scripts/fetch_live2d.py           # then pick the rig with AVATAR_MODEL in .env

# desktop window (modes 3 + 4): the pywebview frame + the Qt/Chromium engine
pip install -e ".[desktop]"
```

The window's default body comes from `DESKTOP_BODY` in `.env` (`vrm` | `live2d`); `--body`
overrides it per launch. Size / always-on-top / engine are the `WINDOW_*` knobs. The two
browser pages are both live all the time — you can even open them side by side; they share
the session (same someone), and whichever page is free carries her ambient speech.

**No GPU, no models, no install beyond the basics?** She still boots: with just
`pip install -e ".[test]"` every voice backend degrades gracefully to a fake (one loud
`WARNING` each, naming the extra that upgrades it) — the room renders, rain runs down the
window, tools and the idle machine work; she's present but silent. That fakes-only mode is
also exactly what the test suite runs against.

Just want to see the body move? The puppet demo drives every control channel —
expressions, gaze, bones, rain, music — with fakes everywhere else:

```bash
python scripts/demo_avatar.py      # open the printed URL, click to enter, watch
```

```bash
pytest                             # the §13 suite — the hard gate; must be green
```

The suite runs **entirely offline**: fake voice backends, a fake tool runner, the real MCP
server over an **in-memory session** (no subprocess), `httpx.MockTransport` weather, and a
`VirtualClock` for everything timed — hours of idleness run in milliseconds.

## The shape of it (one process, one bus, one audio socket)

```
 python -m world  (FastAPI on :8767)
 ├── EventHub — the one outbound bus (§10; the YuriOS host's, ported)
 │     └── /api/events (SSE) — hello · message · draft · avatar, typed JSON;
 │         sticky rain/music/colors replay to every new subscriber
 ├── the brain: ToolBrain(BrainAdapter) over the vendored Build #1 AppState
 │     └── the tool loop (§7): [[tool {json}]] markers → guard → MCP → continue
 ├── the voice loop: vendored Build #2 (TurnController, barge-in, fillers)
 │     └── /ws/voice — audio only now: mic PCM up, her voice down (marked fork:
 │         + the transcript tee → `message`/`draft` events; expressions → the bus)
 ├── VrmController — the puppet strings (§4), each method one `avatar` event
 ├── SelfieLab — take_selfie's start-don't-await realisation (§7.6) over ./forge
 │     └── renders off-turn → /selfies/…png → a `message` with image_url in the chat
 ├── TimerBoard + IdleMachine on an injected clock (§7.5, §8)
 ├── /live2d/ — Build #2's web client, vendored as a documented fork (§6.6)
 └── spawns: python -m world.tools.server   (MCP over stdio — her hands, §7.2)

 browser (no-build ES modules) — or a pywebview desktop window (--window, §6.5)
 ├── chat.js — the chat column beside her + the SSE consumer (one per page);
 │     every event re-dispatched as a `world-ev` for the stage adapters
 ├── VrmStage — CS §4 manual update order; fixed cinematic camera + parallax
 │     (desktop mode: alpha-clear renderer, full-body framing, no room, no chat)
 ├── SanctuaryScene + Rain — procedural room, pane-streak shader, drops, noise bed
 ├── viseme.js — mouth follows the RMS of the audio actually playing (§5)
 └── voice.js — B2's edge VAD / barge-in client, audio-only wire
```

## Where the book lives in the code

| Book / SPEC | Code |
|---|---|
| The one event bus (ch. 35's shape, adopted · §10) | `world/hub.py` + `world/routes/events.py` + `web/js/chat.js` |
| The chat surface, beside her (§2.6) | `web/js/chat.js` + `Runtime.post_message` + the `#chat-col` in both pages |
| Her camera: selfies into the chat (ch. 26 · §7.6) | `world/selfies.py` + `forge/` (vendored image-forge) |
| The puppet control model (ch. 34 · §4) | `world/avatar/controller.py` + `web/js/bridge.js` |
| CS §4 update order, springbones LAST (ch. 25/29 · §3) | `web/js/stage/VrmStage.js` — `update()` |
| The B2 palette on a VRM face (ch. 25 · §3.4) | `web/js/stage/EmoteController.js` + `test_palette_map.py` |
| Real lip-sync, amplitude tier (ch. 24 · §5) | `web/js/viseme.js` (analyser → `aa` in loop step 9) |
| The sanctuary, procedural (ch. 28 · §6) | `web/js/stage/SanctuaryScene.js`, `Rain.js`, `music.js` |
| Tools via MCP, discovered not hardcoded (ch. 17 · §7.2) | `world/tools/server.py` (FastMCP) + `client.py` |
| In-stream tool calls; first audio never waits (§7.4) | `world/tooltags.py` + `world/brain.py` — `_stream_with_tools` |
| Guardrails: allowlist, rates, audit (ch. 17 · §7.3) | `world/tools/guard.py` → `tool-logs/calls.jsonl` |
| The host schedules, the server validates (§7.5) | `world/tools/timers.py` + `ToolBrain._realise` |
| The idle machine — Ukagaka reborn (ch. 02 §1 · §8) | `world/idle.py` (+ `test_idle_machine.py`, sim time) |
| Ambient speech through the live connection (§8.3–8.4) | `world/routes/voice_ws.py` — the one marked fork |
| The voice loop, preserved (ch. 32 · §9) | vendored `desktop/voice/` — called, not copied |
| Injected time everywhere (§8.2) | `world/clock.py` — `Clock` / `VirtualClock` |
| The desktop window, both bodies (ch. 32→34 · §6.5–§6.6) | `world/window.py` + the `DESKTOP` branch in `web/js/main.js`; `web/live2d/` (vendored) + `world/routes/live2d.py` |

## The hands (→ ch. 17)

Four tools, deliberately small — a timer, the room's music, a weather lookup, and her
camera — because four is enough to teach the whole pattern: **build the capability behind
MCP once and the same client talks to any server.** `world/tools/server.py` is a genuine MCP server
(`python -m world.tools.server`, stdio); the host spawns it, `initialize`s, discovers the
tools with `list_tools`, and builds the model's `## TOOLS` directive *from the discovery* —
point `McpToolRunner` at a different command line and she has different hands, no brain
changes.

The call protocol is **in the token stream** — `[[set_timer {"minutes": 10, "label":
"tea"}]]`, the same discipline as Build #2's `[happy]` emotion tags, one channel up
(double brackets, parsed upstream of the emotion parser). That is the price of keeping the
vendored brain byte-identical, and it buys the property that matters: she says a natural
lead-in sentence *first*, so her first audio is at the speaker while the tool is still
running — a slow tool can never blow the §1 latency budget (`test_turn_tools.py` pins this
with a deliberately-blocked runner).

And the game-NPC lesson (→ ch. 02 §1): she can be *asked* anything, so a `Guard` decides
what her hands actually do — an allowlist (exactly the discovered tools), per-tool
token-bucket rate limits, a per-turn call cap, a timeout, result truncation, and one JSONL
audit line for every call, allowed or denied. "What did she do while I was away" is a file
you can read (`tool-logs/calls.jsonl`), not a vibe.

**The camera teaches the lesson the other three can't: a slow tool must not sit inside
the turn.** Ask for a selfie and she answers on the normal latency budget — the MCP server
only *validates* the ask (scene/mood against the vendored template library) and returns
`{"status": "started"}`; the host's `SelfieLab` renders off-turn (the YuriOS
start-don't-await rule), saves the PNG + provenance under `selfies/`, posts it into the
chat as an `image_url` message, and offers one spoken line about it if she's free. The
generator is the vendored **image-forge** slice (`./forge`, → ch. 26): the locked 2.5D
register + the anti-collapse selfie template library, behind a swappable backend —
**OpenRouter by default, on the cheap seedream model** (set `OPENROUTER_API_KEY` in
`.env`; the local GPU stays free for her voice; `SELFIE_MODEL=sourceful/riverflow-v2.5-pro`
buys the brand-art register), a deterministic `mock` with no key (one loud WARNING names
the fix), `SELFIE_BACKEND=off` and the tool isn't even advertised.

## Alive when you're quiet (→ ch. 02 §1, ch. 18)

Leave her alone and the room keeps living: gaze drifts, posture shifts, sometimes she turns
to watch the rain; every few minutes, one soft line said half to herself; when your tea
timer lands, she perks up and tells you. This is `world/idle.py` — a **state machine**
(engaged / resting / rain_gazing / self_talk / announce), and the build is loud about what
it is *not*: no goals, no salience, no deciding to reach out. It is the Ukagaka idle-talk
timer reborn, scripted on purpose — Build #5's whole job is to replace this one file with
the cognitive tick loop holding the exact same strings.

Two honest rules inside it: she **never talks over you** (announcements wait out the
engagement window; a barge-in kills ambient speech exactly like a reply, because ambient
speech runs through the same TurnController), and **a timer is a promise** — an
announcement that finds no one connected stays queued; idle chatter that finds no one is
dropped.

## The desktop mode: two bodies, one flag (§6.5–§6.6)

Build #2 ended with her floating on the desktop; Build #4 keeps that door open — twice.
`python -m world --window` runs the same server behind a frameless, transparent,
always-on-top pywebview window (`world/window.py`, reusing the vendored B2 launcher's
readiness probe and engine pick — `test_window.py` pins that they're B2's actual
functions), and `DESKTOP_BODY` / `--body` picks who stands in it:

- **`vrm`** (default): the 3D body with **the room set aside** — `?desktop=1` is decided
  entirely by the page (`web/js/main.js`): no sanctuary, no fog, an alpha-clear renderer,
  a neutral light rig where the lamp was, full-body framing, no enter gate (native engines
  don't demand the autoplay gesture). Rain follows her as sound only; drag her by the body.
- **`live2d`**: Build #2's **web client, vendored as a documented fork** under
  `web/live2d/` and served at `/live2d/` — audio (greeting, barge-in, ambient speech)
  still arrives over the voice socket exactly as in Build #2, while the fork is precisely
  the bus adaptation: a chat column beside the body, and a 25-line `events.js` adapter
  that maps `avatar`/`expression` events from `/api/events` onto the untouched pixi body
  (`avatar.js`/`voice.js`/`settings.js` stay byte-identical; see
  `web/live2d/VENDORED.md`). Fetch the runtime + rigs once with
  `python scripts/fetch_live2d.py`; pick the rig with `AVATAR_MODEL`.

## Honest notes (where this build makes a call the spec leaves open)

- **Tool calling is a text protocol, not native function-calling.** Build #1's provider seam
  is text tokens in/out, and it stays byte-identical — so the markers ride the stream. The
  parser is junk-proof (split markers, bad JSON, oversized, unclosed → dropped, never
  spoken), because a 12B local model *will* eventually emit a broken one. Native
  function-calling slots in behind the same `ToolRunner` seam later.
- **Visemes are the amplitude tier** of the control spec's §5.4: an `AnalyserNode` on the
  playback graph drives `aa`, so mouth and voice read the same samples and cannot drift.
  The full phoneme tier (wlipsync onto `aa/ee/ih/oh/ou`) adds mouth *shape* at the cost of
  an unvendorable dependency — documented seam, deliberately not built.
- **The "music" is generative ambience** (a detuned pad, sparse pentatonic plucks, a
  filtered-noise rain bed — all synthesized client-side, zero audio assets), honest
  scare-quotes included. A real library is the obvious swap behind the same `play()/stop()`.
- **The corpus records the model verbatim** — markers and tool results included. The
  training log should reflect what the model actually did in the turn, not just what was
  spoken; the spoken stream is what gets the markers stripped.
- **The forks are documented, not hidden.** `world/routes/voice_ws.py` is a copy of B2's
  route with a small set of additions, each marked `FORK(B2 §10)` (turn notifications,
  the ambient injector + its cleanup, the transcript tee, the expression re-route);
  `web/live2d/` is B2's client with each departure marked `FORK(B2)`. Everything else
  vendored is called, never edited — if B2 changes, re-diff the marked files against it.
- **The selfie arrives after the turn, on purpose.** A hosted render takes 10–30 s;
  parking the tool loop on it would mean dead air after her lead-in sentence. So
  `take_selfie` is start-don't-await (§7.6): she acknowledges on-budget, the photo lands
  in the chat when it's done, and she mentions it aloud only if she's free. A timer is a
  promise and stays queued; a selfie already delivered itself, so the spoken line is
  droppable.
- **The Live2D body is a guest, not a second puppet.** It realises only the `expression`
  op off the bus (`web/live2d/events.js`), so the idle machine's other body acts (gaze
  drift, posture) don't reach it — everything audible does, over `/ws/voice`. Wiring pixi
  to the rest of the puppet ops is a reader exercise with a clean seam, and the events
  already arrive on the page.
- **The sanctuary is procedural geometry and shaders** — no binary scene assets in git. It
  reads as a place (lamp, window, seat, plant, rain) rather than a showcase; the fixed
  cinematic camera with mouse parallax is the point — this is a room she lives in, not a
  model viewer with orbit controls.

## What it deliberately omits (§12)

Still **reactive** — the idle machine is scripted life, not a mind (→ Build #5, ch. 18).
Tools are the *small reactive* surface; the heavy sandboxed hands (code execution, the
workshop) are Build #5+ (→ ch. 17, ch. 19). The **inbound half of the YuriOS
split** — the `SignalBus` inbox and the broker/effector gate — is a named next rung, not
built: it has no consumer until the tick loop exists, so user input keeps the voice
socket's turn semantics. Selfie *editing* and the local-GPU image backends stay in
`../image-forge` (the vendored slice is mock + openrouter only). Phoneme visemes, webcam
mocap, and VR proper are specced seams, not built. Single body register; `load_model` is
the user's own-`.vrm` slot (→ ch. 25 licensing), not a wardrobe.

## How it extends (§14)

**Build #5 swaps the callers, not the wires — and the wires are already YuriOS's.** The
`EventHub` is the YuriOS host's fan-out, ported; the chat column is its sanctuary
frontend's; the selfie lab already obeys its effectors' start-don't-await rule. The tick
loop (→ ch. 18) replaces `world/idle.py` and holds the exact same `VrmController` methods
and the same `ToolRunner`; the `SignalBus` lands with it (user input becomes a signal the
loop consumes); the Guard grows into the broker; the sanctuary becomes the front-end body
of the agentic sanctuary. Nothing in the body or the frontends changes — the strings just
get a real puppeteer.
