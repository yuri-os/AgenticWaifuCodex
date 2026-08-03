# 34 — Build #4: The 3D World Companion

**Goal:** a browser-based 3D companion — a VRM avatar in the canonical sanctuary scene, with a chat transcript beside her, the real-time voice loop, a handful of real tools (one of them her camera — selfies that land in the chat), and *ambient behaviour* when idle. This is the richest *reactive* body: she has a 3D presence, a place, and hands — standing on the same backbone as the YuriOS runtime it grows into: **one event bus** carrying everything the host tells a frontend. And Build #2's desktop mode survives the upgrade: one flag floats her on the desktop instead — the VRM body with the room set aside, or the Live2D body itself, served by this build's server.

**What it teaches:** agentic patterns and tool use (→ ch. 17), avatars (→ ch. 25), 3D worlds (→ ch. 29), and how to compose the previous builds instead of rewriting them.

**Property added (→ ch. 03):** deepens property 4 (a full 3D body in a place) and introduces **property 3a** — *hands*: reactive tool-use, the capability half of owned agency (the always-on initiative half, 3b, is Build #5). Still reactive; the ambient idle behaviour is a teaser of initiative, not the real thing — and the build is loud about that.

The reference implementation lives in `reference-implementations/04-3d-world-companion/`, built to its own normative `SPEC.md`. As with Builds #1 and #2, this chapter is the reading guide — a map of where the load-bearing ideas are in the code — not a transcript. Section numbers (§n) point into that build's `SPEC.md`; `CS §n` points into the VRM control spec vendored with the `vrm-viewer/` component; file paths are relative to the build's root.

## The one-sentence architecture

```
 python -m world — one process, one origin (:8767)
 ┌────────────────────────────────────────────────────────────────────────────────────┐
 │  Build #1 brain (vendored) ◄── ToolBrain: the §7 tool loop                         │
 │          │ reply tokens…   [[set_timer {…}]]   …continuation                       │
 │          ▼                             │                                           │
 │  Build #2 voice loop (vendored)        guard ─► MCP server (stdio)                 │
 │          │ OutEvents                   └─► bounded audit/latency JSONL             │
 │          ▼                             ├─► SelfieLab ─► forge (vendored)           │
 │  /ws/voice             TimerBoard ─► IdleMachine ─► VrmController                  │
 │    (audio-only wire,     (injected clock)                          │               │
 │     marked fork)  message · draft · avatar events                  ▼               │
 │          │             └─────────► EventHub ──► /api/events (SSE)                  │
 └──────────┼─────────────────────────────────────────────────────────┼───────────────┘
            ▼ browser (no-build ES modules; three.js + three-vrm committed)
   VrmStage (CS §4 order) · SanctuaryScene + Rain · viseme.js · voice.js
   chat.js — the chat column beside her, fed by the one bus
```

The whole thing is: **Builds #1 and #2, unchanged, now standing in a room with hands — on the runtime backbone of ch. 35.** The brain is the vendored Build #1 `app/`; the voice loop is the vendored Build #2 `desktop/` — called, not copied (§2.2). The genuinely new work is six things: the **event bus** (`world/hub.py` — the YuriOS host's `EventHub`, ported, with sticky scene replay), the **VRM stage** in the browser (`web/js/stage/`), the **puppet strings** from Python (`world/avatar/controller.py` → `avatar` events on the bus), the **chat surface** (`web/js/chat.js` + the host's transcript ring, §2.6), the **tool loop** wrapped around the brain (`world/brain.py` + `world/tools/`, now four hands including `take_selfie` → `world/selfies.py`), and the **idle machine** (`world/idle.py`) — plus one small seventh that keeps the others honest: the **situation block** (`world/situation.py`), the present tense every prompt carries. Everything below is one of those, looked at closely.

The single idea to internalise before reading a line: **the body is a puppet, and the brain holds the strings.** The browser is a render-and-control client; every decision lives in Python. That split — proven first in the `vrm-viewer/` component this build's stage was ported from — is the whole point: the body is "solved enough" to be a dumb renderer you drive, and the mind that drives it is ordinary, portable Python (→ ch. 02 §4.6). Build #5 doesn't touch the body at all; it just takes the strings.

## The vendoring chain, and the one fork

Build #4 composes *three* predecessors, so the reuse discipline gets its stress test. `app/` is Build #1 (via Build #2's copy), `desktop/` is Build #2, `forge/` is the image-forge slice (her camera, mock + OpenRouter backends only — the GPU paths stay behind) — each resync-able with commands documented in its `VENDORED.md`. The brain seam is a **subclass**, not an edit: `ToolBrain(BrainAdapter)` changes exactly one behaviour — how a reply streams — and everything else (prompt assembly, recall, the greeting, the corpus line, one-commit-per-turn) is inherited. Build #2 is in fact vendored twice: its Python as the voice loop, and — for the second body (§6.6) — its *web client* under `web/live2d/`.

Two files could not be reused by subclass or call, and both are **documented forks** with every departure marked `FORK(B2 …)` in the source and a docstring saying exactly how to re-diff when Build #2 changes. `world/routes/voice_ws.py` needed the idle machine's engagement notifications, the ambient-speech injector, the transcript tee, and the expression re-route *inside* its connection scope. The Live2D client's fork is exactly the bus adaptation: a chat column and one new adapter file (`events.js`); its body, voice, and settings scripts stay byte-identical. A documented fork beats a dozen silent drifts — the same honesty rule as `/api/health`.

The topology also simplifies against the `vrm-viewer` component: the controller runs **in-process** on the FastAPI event loop instead of owning a second WebSocket server, and the frontend is a **no-build port** of the viewer's TypeScript to plain ES modules — three.js and three-vrm are committed MIT artifacts in `web/vendor/`, resolved by an import map. No npm, no bundler, no second port: copy the folder, `python -m world`, done.

## Reading the code: follow the strings

| Read this to understand… | …in this file |
|---|---|
| **the one event bus** (the YuriOS backbone, §10) | `world/hub.py` + `world/routes/events.py` — attach, sticky replay, SSE ordering |
| **the chat surface** beside her (§2.6) | `web/js/chat.js` + `Runtime.post_message` in `world/main.py` |
| **the boot log** while her voice stack warms (§6.4) | `world/boot.py` + `web/js/boot.js` + `tests/test_boot.py` |
| **her camera**: start-don't-await selfies (§7.6) | `world/selfies.py` + `forge/` + `tests/test_selfie.py` |
| **the puppet strings** (the §4 command union) | `world/avatar/controller.py` + `web/js/bridge.js` |
| **the CS §4 update order** (springbones LAST) | `web/js/stage/VrmStage.js` — `update()` |
| the B2 palette on a VRM face | `web/js/stage/EmoteController.js` + `tests/test_palette_map.py` |
| real lip-sync, amplitude tier | `web/js/viseme.js` |
| the sanctuary, procedural | `web/js/stage/SanctuaryScene.js`, `Rain.js`, `music.js` |
| **the tool loop** (the spine of §7) | `world/brain.py` — `ToolBrain._stream_with_tools` |
| the in-stream marker parser | `world/tooltags.py` + `tests/test_tool_tags.py` |
| the MCP server and client | `world/tools/server.py`, `client.py` |
| guardrails: allowlist · rates · canonical per-turn idempotency · audit | `world/tools/guard.py` |
| **the situation block** (she knows when/where she is) | `world/situation.py` + `tests/test_situation.py` |
| host-side realisation (timers, music) | `world/tools/timers.py` + `ToolBrain._realise` |
| **the idle machine** | `world/idle.py` + `tests/test_idle_machine.py` |
| ambient speech through a live connection | `world/routes/voice_ws.py` (the fork) |
| injected time (the test story) | `world/clock.py` — `Clock` / `VirtualClock` |
| **the desktop window** (§6.5) | `world/window.py` + the `DESKTOP` branch in `web/js/main.js` — pywebview, or a Windows-browser handoff under WSL |
| the second body: B2's client, served (§6.6) | `web/live2d/` (vendored) + `world/routes/live2d.py` |

And here is the same map as a wiring diagram — every box is a file you can open, every arrow is a string being pulled. `world/main.py`'s `create_app()` builds one FastAPI app on one origin (`:8767`) and one `Runtime` that owns every seam below; the browser is a pure render-and-control client reached over **one event stream and one audio socket**.

```
python -m world → world/main.py : create_app() + Runtime — one process, :8767

 BROWSER  ── web/  (no-build ES modules; three.js + three-vrm in web/vendor/)
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │ web/js/main.js boots the room + stage + the bus after the enter gesture          │
 │   web/js/stage/SanctuaryScene.js · Rain.js · music.js   (the place, §6)          │
 │   web/js/stage/VrmStage.js  (CS §4 update order; spring bones LAST)              │
 │   web/js/stage/EmoteController.js · Blink.js · GazeController.js                 │
 │   web/js/viseme.js  (mouth follows the played audio, §5)                         │
 │                                                                                  │
 │   web/js/chat.js ◄── /api/events (SSE) ─┐   ┌── /ws/voice ──► voice.js           │
 │   (the chat column + the bus consumer;  │   │  (mic ⇄ audio, the                 │
 │    every event re-dispatched as         │   │   audio-only wire)                 │
 │    `world-ev` → bridge.js realises      │   │                                    │
 │    the `avatar` ops on the stage)       │   │                                    │
 └─────────────────────────────────────────┼───┼────────────────────────────────────┘
  PYTHON  ── world/                        │   │
 ┌─────────────────────────────────────────┼───┼────────────────────────────────────┐
 │ routes/events.py ◄── hub.py : EventHub ─┘   └─► routes/voice_ws.py               │
 │   (SSE: attach → hello →    ▲ ▲ ▲            (FORK B2 §10, marked:               │
 │    sticky flush → live;     │ │ │             + transcript tee →                 │
 │    history sidecar)         │ │ │             message/draft events,              │
 │                             │ │ └─ post_message │ + expressions → the            │
 │ avatar/controller.py :──────┘ │    (the ring,   │   controller lane)             │
 │   VrmController — every       │     §2.6)       │ turn i/o                       │
 │   method = one `avatar` op    │                 ▼                                │
 │      ▲          ▲             │       brain.py : ToolBrain                       │
 │      │ gaze/pose│ set_rain    │       (vendored desktop/ adapter                 │
 │      │          │ / music     │        + §7 tool loop; emits                     │
 │      │          │             │        [[take_selfie {…}]] in-stream)            │
 │ idle.py : IdleMachine         │                 │                                │
 │   §8 state machine ─ speak_ambient ─┐ tooltags.py (junk-proof parse)             │
 │      │ announce ▲                   │           ▼                                │
 │      ▼          │ timer fires       └► tools/guard.py  allowlist ·               │
 │ tools/timers.py : TimerBoard ───────┘  rate buckets · calls.jsonl audit          │
 │   host owns the countdown (§7.5)                │ allowed                        │
 │                                                 ▼                                │
 │ selfies.py : SelfieLab ◄── _realise ── tools/client.py : McpToolRunner           │
 │   start-don't-await (§7.6):                     │ stdio (MCP)                    │
 │   forge render off-turn → PNG →                 ▼                                │
 │   message{image_url} on the bus       tools/server.py  (FastMCP):                │
 │                                       set_timer · play_music ·                   │
 │ clock.py : Clock / VirtualClock       get_weather · take_selfie                  │
 │   injected into idle, timers, guard, lab — never the wall clock (§8.2)           │
 └──────────────────────────────────────────────────────────────────────────────────┘
 VENDORED:  app/ = Build #1 brain · desktop/ = Build #2 voice ·
            forge/ = image-forge slice · web/live2d/ = Build #2 client (fork)
```

Read it as two lanes meeting at the hub. The **left lane is the body and everything visible**: `controller.py`'s `VrmController` is the single Python surface that holds every string, and each method is one `avatar` event on `hub.py`'s `EventHub` — the same bus that carries the chat's `message` and `draft` events — drained to every page by `routes/events.py`'s SSE stream. Attaching first registers a bounded queue preloaded with sticky scene state; the stream then sends `hello`, flushes that queue, and only then waits for live events. Nothing on the left decides anything — `idle.py` pulls those same strings when you're quiet, and Build #5 will swap `idle.py` for a real mind without touching one line below it. The **right lane is the turn**: `voice_ws.py` (the fork) runs `brain.py`'s `ToolBrain`, whose reply stream carries `[[…]]` tool markers that `tooltags.py` parses, `guard.py` polices, and `client.py`→`server.py` execute over stdio — with `timers.py` keeping the countdown and `selfies.py` rendering the photos on the host. `clock.py` sits under everything timed. The lanes cross where they always did, plus once more: the brain's expressions land on the controller (one lane for the face), a fired timer travels `timers.py → idle.py → voice_ws.py` to become a spoken line, and a finished selfie travels `selfies.py → post_message → the bus` to become a photo in the chat.

## The bus: one lane for everything the host says

`world/hub.py`, `world/routes/events.py`, `web/js/chat.js` (§10, §2.6). Build #4 originally spoke to the browser over two WebSockets with two contracts — the voice wire carrying the turn, the avatar wire carrying the puppet. That worked, and then the first new surface arrived and exposed the flaw: a selfie is neither a voice event nor a puppet command, and every future surface (a dashboard, a diary, a notification) would have posed the same question — *which socket does this ride?* The runtime this build grows into answered it years ahead: the YuriOS host has **one `EventHub`**, every host→frontend fact is one typed JSON event on it, and frontends subscribe once. So Build #4 adopts the backbone early: `world/hub.py` is that hub, ported, plus this build's sticky replay (rain, music, tints re-arrive on every fresh page), and `GET /api/events` is its wire — SSE, one `data:` line per event, self-terminating on shutdown so an open tab never holds Ctrl+C hostage. The puppet strings didn't change their method surface; `VrmController`'s methods now each publish one `avatar` event instead of owning queues of their own. Only sound keeps a socket, because audio is the one flow that is bidirectional, binary, and latency-critical; everything else is a broadcastable fact about the world, and facts ride the bus.

The first thing the bus paid for is the surface this build was missing: **the chat**. Both browser pages now carry a chat column beside the body (`web/js/chat.js` — one shared, classic script; the same renderer the YuriOS sanctuary uses), fed entirely by bus events: your turns as `message`s (typed *and spoken* — the forked voice route tees the STT transcript into the chat, so a voice conversation finally reads back), her reply as an accumulating `draft` that commits on `done`, a `proactive` tag on lines she spoke unprompted, and an inline image when a message carries `image_url`. The host keeps a two-hundred-entry transcript ring and `/api/history` returns its latest hundred. The client opens SSE first, buffers arriving `message`s while that history request completes, then renders history before flushing the buffer; message IDs de-duplicate the overlap. The rules mirror the memory rules exactly: a barged-in turn drops its draft and commits nothing (a turn that didn't happen leaves no trace), ambient lines appear in the chat but never persist. The chat is what was *said*; the Vault is what is *remembered*. Typing in the composer still rides the voice socket as a `text` turn, deliberately: a typed turn gets the full `TurnController` treatment — TTS, barge-in, latency masking — not a separate code path.

One consequence worth savouring: expressions moved onto the bus too (the fork re-routes a turn's expression events through the controller), which means her face has **one lane** whether the emotion came from a reply tag or the idle machine — and every open page sees it. Open the VRM room and the Live2D page side by side and both faces change together; the previous build's body now receives the idle machine's expression pulses it never had before.

## The stage: why the update loop is manual

`web/js/stage/VrmStage.js`. A VRM body is driven by several systems at once — an animation clip, bone overrides, gaze, blink, emotion, the mouth, constraints, spring-bone physics — and they all write to the same skeleton and the same blendshapes. The control spec's answer (CS §4) is a **manual per-frame update in a fixed order**, with `vrm.update()` never called: mixer → materials → bone overrides → `humanoid.update()` → gaze → blink → emote → viseme → commit expressions → constraints → **spring bones last**. Get the order wrong and physics fights expressions — hair jitters, the face flickers. The stage pins the order with numbered comments, and the two known foot-guns from the YuriOS port are carried as law: the emote sweep must never stage `blink` or `aa` (or it fights the blink controller and the mouth), and a `.vrma` clip's hips track must be re-anchored to the model's rest pose or she teleports to the animator's origin.

One deliberate deviation from the viewer it was ported from: **no orbit controls**. The camera is fixed and cinematic — framed from her head and hips at load, drifting a few centimetres with the mouse and always re-aiming at her. A model viewer invites you to inspect an asset; a fixed camera with parallax puts you *in a room with someone* (§6.3). The distinction is the entire register of the build.

**Expressions cross a mapping boundary, by design.** The brain still emits Build #2's eight palette *names* (`[happy]`, `[shy]`, `[thinking]`…); the stage's catalog realises each as VRM preset weights — the six standard presets directly, the non-preset names as blended composites (shy ≈ sad + happy + relaxed at low weights). The map lives in the frontend, exactly as ch. 32 promised it would, which is why the brain needed zero changes to move from a Live2D face to a VRM one. `test_palette_map.py` scans both sources and fails the build if either side renames — a face that silently falls back to neutral is the kind of bug you *feel* before you find.

## Visemes: the mouth follows the actual audio

`web/js/viseme.js` (§5). Build #2 drove the mouth from audio RMS in the Live2D layer; Build #4 does the same one tier up the control spec: an `AnalyserNode` sits between every queued TTS buffer and the speakers, and its RMS — shaped by a perceptual `amp^0.7` curve, attack/release smoothing, a silence gate, a weight cap — stages the `aa` blendshape *inside loop step 9*, in CS §4 order. Because the analyser reads the very samples the speaker plays, mouth and voice cannot drift; there is nothing to synchronise. The full phoneme tier (CS §5.4's wlipsync winner/runner blending onto `aa/ee/ih/oh/ou`) adds mouth *shape* at the cost of an unvendorable dependency — the seam is documented and deliberately not built.

## The sanctuary: a place, not a void

`web/js/stage/SanctuaryScene.js` (§6). The room is canon (→ ch. 28) and its elements are normative in the SPEC: a small room, low warm light from a lamp, a window with rain, a window seat, a single plant. She must not stand in a default grey three.js void — the place is part of the character. Everything is **procedural**: the room is generated geometry, the rain is a pane-streak shader plus a falling-drop point cloud (occluded by a real hole in the wall, no masking tricks), and the sound is synthesized client-side — a filtered-noise rain bed whose gain follows the same `rain` command the visuals do, plus two generative ambience "tracks" for the music tool. Zero binary scene assets in git; the whole room is readable code.

Two small things carry disproportionate weight. The **enter gesture** (§6.4): the page gates on one click before connecting the sockets, because autoplay policy would otherwise silence her greeting — the single most important moment of presence (she speaks first, from memory). While that gate waits, a **kernel-style boot log** (`world/boot.py` → `GET /api/boot`, *polled* — not the bus, which only opens after the click) shows the local voice stack warming service by service (`pending → loading → ready | failed | skipped`, with timings), so a cold start where Kokoro and faster-whisper take a minute on CPU is a wake-up sequence, not a dead screen. And **sticky scene state** (§4): rain intensity, music, material tints are remembered by the controller and replayed to every newly attached viewer, so a page reload doesn't reset the weather.

## The desktop mode: the room, set aside

`world/window.py` (§6.5). Build #2 ended with her floating on the desktop, and Build #4 doesn't take that away: `python -m world --window` runs the same server behind Build #2's frame — a frameless, transparent, always-on-top pywebview window pointed at `?desktop=1` on native hosts. Under WSL it instead rebinds the server for Windows reachability and asks Windows to open that URL in its browser; it is a browser handoff, not a Linux pywebview window. The launcher is the reuse discipline in miniature: the readiness probe, WSL helpers, and the Qt-versus-GTK engine pick are *imported from the vendored `desktop/window.py`* (with their war stories — the 30fps WebKitGTK cap, the NVIDIA DMA-BUF smear, the private-mode localStorage trap), and `test_window.py` pins that they are B2's actual functions, not lookalikes.

What the flag *means* is the page's decision, not Python's (`web/js/main.js`). In desktop mode the sanctuary is never built — no walls, no fog, no lamp; **the desktop is the room.** The renderer clears to alpha 0, a neutral two-light rig stands in for the lamp (an unlit MToon face shades toward black), and the camera framing switches from head-and-torso-in-a-room to the full body, feet at the window's bottom edge. The §6.4 autoplay gate goes too — a native window's engines don't demand the gesture, so she greets the moment the socket opens (a first-click resume stays as insurance, so a stricter engine means a quiet greeting, never a dead one). Nothing on the wire changes: both sockets, every puppet command, the tools, the idle machine. Rain follows her as sound only — the synthesized bed tracking the same sticky `rain` state — and when the idle machine sends her rain-gazing she looks off to where the window would be, which on a desk reads exactly right.

**And the previous body still works — served by this build** (§6.6). Build #2's web client — the Live2D body, its expression map, its edge-VAD voice client, even its settings panel — runs against Build #4's server as a *documented fork* under `web/live2d/`, served at `/live2d/`: audio still arrives over the voice socket exactly as it did in Build #2, and the fork is precisely the bus adaptation — a chat column beside the body, plus one new adapter file (`events.js`, ~25 lines) mapping `avatar`/`expression` events from `/api/events` onto the untouched pixi body. Its API needs are met by the vendored B2 settings router (included as-is; it edits this build's `.env`) and a re-aimed copy of the rig-registry route. `DESKTOP_BODY=vrm|live2d` (or `--window --body live2d`) picks which body the window floats. The honest asymmetry: the adapter realises only the `expression` op, so the idle machine's other body acts (gaze drift, posture) don't reach the Live2D body — but everything audible does, and now everything *visible in the chat* does too. Ask her for a selfie while she wears the Hiyori rig and the whole §7 loop runs; the photo lands in the chat beside a face two builds old.

That asymmetry is the lesson, not a bug to apologise for. The seam between mind and body is *the wire*, and there are two wires with two contracts: `/ws/voice` carries the sound (any client that speaks the audio wire gets all of her conversation), `/api/events` carries the facts — the chat and the puppet (any client that renders the ops it cares about gets exactly that much of her). The Live2D page realises one op and gets one op's worth of body; the VRM page realises the full §4 union and gets everything. Swap the renderer, keep the wire — the same claim ch. 32 made when it promised the palette names would survive the jump to VRM, now demonstrated in the other direction, with a whole legacy body plugging into a newer runtime.

## The hands: tools via MCP, without touching the brain

`world/brain.py`, `world/tools/` (§7). Four tools — a timer, the room's music, a weather lookup, and her camera — because four is enough to teach the entire pattern (→ ch. 17): **build the capability behind MCP once, and the same client talks to any server.** The in-repo server (`world/tools/server.py`, FastMCP over stdio) validates arguments and returns structured results; the host spawns it, discovers the tools with `list_tools`, and builds the model's `## TOOLS` directive *from the discovery*, not from constants. Point the runner at a different command line and she has different hands; the brain doesn't change.

**The call protocol is in the token stream.** Build #1's provider seam is text in, text out — and it stays byte-identical — so tool calls ride the reply as `[[set_timer {"minutes": 10, "label": "tea"}]]` markers: double brackets because single brackets are already the emotion channel, parsed by a streaming, junk-proof parser *upstream* of the emotion parser (split markers, malformed JSON, oversized or unclosed markers are dropped and never spoken — a 12B local model will eventually emit a broken one). The loop is multi-pass: her partial reply plus the tool result go back to the model as a continuation cue in the *same* turn, so she weaves what her hands found into the sentence she was already saying.

The property that matters most is temporal: **the directive asks for a natural lead-in sentence before the marker, so her first audio is at the speaker while the tool is still running.** A slow tool cannot blow the latency budget ch. 32 fought for — `tests/test_turn_tools.py` pins it with a runner that deliberately blocks until the first audio event has been observed. And barge-in still reaches everything: cancelling mid-continuation tears down TTS, the generation pass, and persists nothing.

**Guardrails are policy, not intelligence** (§7.3, → ch. 02 §1's game-NPC lesson). She can be *asked* anything; a `Guard` decides what her hands do: an allowlist that is exactly the discovered tools, per-tool token-bucket rate limits on the injected clock, a per-turn call cap, a timeout, result truncation, and canonical per-turn idempotency — the same tool plus sorted JSON arguments is denied if the model repeats it in the reply's continuation. Each allowed, denied, or failed call gets a JSONL audit line with its latency. That audit, like the voice latency trace, is bounded operational diagnostics (rotated to one previous generation), not the permanent Vault or corpus record.

**The server validates; the host realises** (§7.5). `set_timer`'s MCP call returns the contract (`seconds`, `due`) — but the actual countdown lives on the host's `TimerBoard`, on the injected clock, because only the host owns her voice and her room. The same split survives into Build #5 when the tools move behind a broker. One honest note for the permanent corpus: `persist` records the *model-verbatim* stream — markers and results included — because the training log should reflect what the model actually did, not just what was spoken (→ ch. 20).

**The camera teaches the fourth lesson: a slow tool must not sit inside the turn** (§7.6). The first three tools return in milliseconds; a hosted image render takes ten to thirty seconds, and no timeout knob makes that pleasant — her lead-in sentence would trail into dead air. So `take_selfie` follows the rule the YuriOS effectors live by — *ACT starts work; it never awaits it*. The MCP server is the contract point only: it validates `scene`/`mood` against the vendored template library (the tool description the model reads is *built from* the library, so the options can never drift from the yaml) and returns `{"status": "started"}`; the turn continues and ends on budget. The host's `SelfieLab` (`world/selfies.py`) renders off-turn through the vendored forge (`./forge` — image-forge's locked register, anti-collapse selfie templates, provenance stripping; → ch. 26), saves the PNG and its provenance sidecar, posts an `image_url` message onto the bus — the photo simply appears in the chat — and offers one spoken line about it through the ambient seam, *dropped* if she's busy: unlike a timer, which is a promise and queues, the photo already delivered itself, and she never talks over you. The backends are GPU-free on purpose — OpenRouter by default on a deliberately cheap image model (her voice keeps the local GPU; one config knob points `SELFIE_MODEL` at riverflow, the repo's brand-art register, when the shot should match the canon set) with the mock's deterministic placeholder cards when there's no key, one loud WARNING naming the fix — and a failed render becomes a quiet line in the chat, never a crash and never silence about something she said she'd do.

## She knows when and where she is: the situation block

`world/situation.py` (§2.5). The smallest file in the build fixes the strangest failure in it. Without this block the build was honest to a fault: Build #1's honesty constraint rightly forbids inventing facts, and no block carried the clock — so a companion whose host runs her timers to the second would answer "what time is it?" with *I don't know*. Worse, asked to blink, a safety-aligned base model reaches for its reflex — *"I'm an AI, I have no body"* — which is cold, and here simply false: her body is rendered on screen that instant, blinking on the idle machine's clock. The model wasn't refusing; it genuinely had no way to know it was embodied. Ch. 19 names the missing organ: the **world model**, the present tense that memory (the past) and knowledge (the documents) never cover.

Build #4's answer is that organ at reactive scale: one `## THE SITUATION RIGHT NOW` block, appended by `ToolBrain._assemble` so every prompt — reply, greeting, ambient self-talk — gets it, rendered fresh each time from surfaces the host already owns. The date and time come from the **injected clock** (never the wall clock, so sim-time tests can move the stated hour); the weather and music come from the controller's sticky scene state — the same state a page reload replays, now also what *she* believes about her room; the pending timers come off the timer board with time remaining, so "how long on the tea?" is a fact she holds rather than a tool call. And the block states the embodiment truth outright, pinned verbatim by the tests: she may know she runs as an AI; that never means bodiless. *Never say you have no body, no eyes, or no surroundings.* The no-narration rule (§6) forbids stage directions, not the truth about herself.

The block is deliberately a *rendering*, not a store — no beliefs, no expectations, no "what was true when" (§12 names the omission). Build #5's `WorldModelStore` replaces the rendering with `situation()` over real observed state; the block's *place* in the prompt is the seam that survives the swap, the same way the palette names survived the jump from Live2D to VRM.

## Alive when you're quiet: scripted, and proud of it

`world/idle.py` (§8). Leave her alone and the room keeps living: her gaze drifts, her posture shifts, sometimes she turns to watch the rain on the window (the gaze target is the same world-space point the scene builds the window at — scene canon and behaviour canon are one constant). Every few minutes, one soft line said half to herself. When your tea timer lands, she perks up and tells you. This is the Ukagaka idle-talk timer reborn (→ ch. 02 §1, Ukagaka) — a **state machine** (engaged / resting / rain_gazing / self_talk / announce), and the build names honestly what it is not: no goals, no salience, no deciding to reach out. Build #5's whole job is to replace this one file with the cognitive tick loop (→ ch. 18) holding the exact same strings.

Three disciplines inside it are worth reading closely. **She never talks over you:** engagement (turns in flight, or within a settle window after one) silences all ambient life, and ambient *speech* runs through the same per-connection `TurnController` as a real reply — so a barge-in kills a self-talk line exactly the way it kills a turn, and none of it persists (an opener she gave herself is not a turn you took). **A timer is a promise, idle chatter is not:** an announcement that finds no one connected stays queued and delivers on reconnect; a self-talk line that finds no one is dropped. And **everything timed runs on an injected clock** (§8.2): the idle machine, the timer board, the guard's rate buckets — no wall-clock reads, no bare sleeps — which is the entire test story: `test_idle_machine.py` runs hours of idleness in milliseconds on a `VirtualClock` with a seeded RNG, deterministically, on any machine.

## Definition of done

In a browser, she stands in her room with the conversation readable beside her, looks at you, talks in real time with natural turn-taking, *does* the four tool things when asked — with her first word landing before the tool returns, and a selfie landing in the chat half a minute after she says she'll take one — and feels alive when you're quiet, without being genuinely proactive. Your spoken words appear in the chat as they're transcribed; her reply streams as a draft and commits when she finishes; barge in and the draft vanishes like it was never said. Ask her the time and she says it; ask her to blink and she knows the eyes on screen are hers — she never claims to have no body (§2.5). With `--window` the browser disappears: the same server floats her on the desktop, chat hidden, as the VRM body alone on transparency or as Build #2's Live2D body, whichever you configured. Pull the network cable and everything but the weather lookup and the real camera still works. And it's **tested** — `pytest` ships and is green from the build root, entirely offline: the marker parser (split/junk/oversized/unclosed), the tool loop end-to-end (guard consulted, result in the continuation, cap enforced, errors survivable), first-audio-before-tool and barge-in-mid-continuation under a real `TurnController`, the guard's allowlist/rates/audit (the selfie's price included), the real MCP server's contract over an **in-memory session** (four tools — three with selfies off; template-key validation), the selfie lab in sim time (a started contract becomes a PNG + provenance sidecar and an `image_url` message; the announce drops when she's busy; a broken forge is a quiet message; no key degrades to mock loudly), timers and the idle machine's states in sim time, every §4 op's event shape with the hub's sticky replay, N-subscriber fan-out, and never-block drop, the SSE route honouring the stop flag with `/api/history` backfilling a bounded ring, the boot board's `pending→loading→ready|failed|skipped` state machine and `/api/boot` snapshot over the real Runtime, the forked `/ws/voice` route (greeting-once, noise-drop, ambient injection reaching the client and never persisting, the transcript tee — typed and spoken turns committed, drafts dropping on barge-in, `proactive` flags, expressions on the bus and off the wire), the source-scanned palette map, the situation block (the stated time is the virtual clock's and moves with it, the embodiment law verbatim, weather and timers tracking live state), the desktop launcher (imports without a GUI stack, the URL carries the flag for whichever body, an occupied port is refused, the reused helpers are B2's actual functions) with both pages honouring the flag and the forked Live2D client served with its config and settings routes answering, and an end-to-end tool-bearing turn over the real vendored brain proving one corpus line and one Vault commit.

## What it deliberately omits

The idle behaviour is a state machine, not a mind — no always-on loop, no goals, no deciding to reach out (→ Build #5, ch. 18). The situation block is a rendering, not a world-model *store* — no beliefs, no expectations, no point-in-time queries (→ ch. 19, `WorldModelStore`; Build #5). Only the *outbound* half of the YuriOS split is adopted: the inbound `SignalBus` inbox and the broker/effector gate are named next rungs, taken when the tick loop gives them a consumer — until then user input keeps the voice socket's turn semantics. Her tools are the *small reactive* surface — a timer, music, weather, a camera, called when asked; the heavy sandboxed hands (running code, the research-and-build workshop) are a runtime capability deferred to Build #5 and beyond (→ ch. 17, "the heavy hands"; ch. 19). No selfie *editing* and no local-GPU image backends — the vendored forge slice is mock + OpenRouter only; the diffusers path stays in `image-forge/`. Phoneme-level visemes and webcam mocap are specced seams (CS §5.4, §5.6), not built. The body ships one register; `load_model` is the user's own-`.vrm` slot (→ ch. 25 licensing), not a wardrobe. The Live2D body is a served guest, not a second puppet — it realises exactly one op off the bus, deliberately (§6.6). VR proper is sketched in ch. 29, not built here.

## Extends to

This is the cleanest seam in the whole book, and now it's load-bearing — and the wires it leads to are already YuriOS's. The body exposes one Python control surface (`VrmController`) and one tool seam (`ToolRunner`); every visible fact rides the same `EventHub` the YuriOS host runs; the selfie lab already obeys its effectors' start-don't-await rule; and Build #4's "mind between turns" is a scripted caller of all of it. **Build #5 swaps the callers, one publisher at a time**: the cognitive tick loop (→ ch. 18) — an always-on brain that decides, on its own clock, when to look up, change expression, gesture, speak, or use a tool — replaces the idle machine behind the same methods; the inbound `SignalBus` lands with it, turning user input into signals the loop consumes; the Guard grows into the broker (→ ch. 19). Give the MCP tools to that autonomy engine and the sanctuary becomes the front-end body of the agentic sanctuary. Nothing in the body or the frontends changes; the strings just get a real puppeteer.
