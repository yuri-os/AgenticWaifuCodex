# Build #4 — The 3D World Companion — SPEC

Normative specification for the reference implementation of **book ch. 34**. Keywords
**MUST**, **SHOULD**, **MAY** are used in the RFC-2119 sense. Section numbers (§n) are cited
from the code and the README. Where this build reuses Build #1 or Build #2 it cites those
builds' SPECs as **B1 §n** / **B2 §n** rather than restating them; where it implements the
vendored VRM control spec it cites **CS §n** (`../vrm-viewer/docs/vrm-control-spec.md`).

---

## §1 — Goal and properties

A browser-based 3D companion: a VRM body in the canonical sanctuary — a small quiet room,
low warm light, rain outside a window, a window seat, a single plant (→ ch. 28) — with a
**chat transcript beside her** (§2.6), the Build #2 voice loop, four real tools over MCP
(one of them her camera, §7.6), and scripted ambient life between turns. The same server
can also float her on the desktop instead of a browser tab — the VRM body with the room
set aside, or Build #2's Live2D body served as a second client (§6.5–§6.6).

- It **MUST** deepen **property 4** (a full 3D body *in a place*, not a floating bust) and
  add **property 3a — hands**: reactive tool use, the capability half of owned agency
  (→ ch. 03). The initiative half (3b) is Build #5.
- It **MUST** remain **reactive**: the ambient behaviour is a state machine, not a mind
  (§8.5) — no goals, no deciding to reach out. That is Build #5 (→ ch. 18).
- It **MUST** be **standalone** (§2.1) and **MUST** preserve Build #2's latency budget:
  ≤ **1200 ms** end-of-speech → first audio (B2 §4.2), including on turns that call a tool
  (§7.4).
- It **MUST** be shaped like the runtime it grows into: **one outbound event bus** (§10 —
  the YuriOS `EventHub`, ported) carrying every host→frontend event as typed JSON, so each
  step toward Build #5 swaps a publisher, never the wires.

```
 mic ──► /ws/voice ──► vendored voice loop (B2 §4) ──► ToolBrain ──► vendored B1 brain
 (audio-only wire)        │  TurnController · fillers      │ [[tool]] markers
                          │  emotion tags · barge-in       ▼
                          │                          MCP client ──► in-repo MCP server
                          │                           (guardrails)   timer·music·weather·selfie
                          ▼                                │ take_selfie: start-don't-await
 browser ◄── audio (pcm) ── /ws/voice                      ▼
    ▲                                              SelfieLab (§7.6) ──► vendored forge
    │                                                      │ message{image_url}
    └── /api/events (SSE) ◄── EventHub (§10) ◄─────────────┤
         hello · message · draft · avatar          VrmController (§4) ◄── idle machine
         (chat panel + puppet strings, one bus)            ▲              + timers (§8)
  VrmStage: sanctuary · VRM body · visemes · blink · gaze  (CS §4 loop) · chat column (§2.6)
```

The control model is ch. 34's: **the body is a puppet, the brain holds the strings.** All
decisions live in Python; the browser is a render-and-control client. The Python control
surface (`VrmController`, §4) is the seam Build #5's tick loop will hold.

## §2 — The brain and the voice are Builds #1 + #2, reused

- §2.1 **Standalone.** The Build #1 brain **MUST** be vendored into `./app`, the Build #2
  voice stack into `./desktop`, and the image-forge slice into `./forge` (§7.6), each with
  a `VENDORED.md` documenting provenance, what was left behind, and the re-sync command.
  The SOUL source **MUST** be vendored (`./soul-src`). Nothing points at a sibling build.
- §2.2 **Unchanged, with documented forks.** No file under `app/`, `desktop/`, or `forge/`
  **MAY** be edited to make Build #4 work, beyond deviations its `VENDORED.md` names. All
  new behaviour lives under `world/`, with one exception: `world/routes/voice_ws.py` is a
  fork of `desktop/routes/voice_ws.py` that adds the ambient-speech seam (§8.4), the
  transcript tee (§2.6), and the expression re-route (§10) — a route cannot speak
  unprompted, feed a chat, or publish to a bus it predates. Every divergence from the
  vendored original **MUST** be confined and marked (`FORK(B2 §10)`) so a re-vendor diff
  is mechanical. The vendored Live2D *client* is a fork under the same discipline (§6.6).
- §2.3 **The tool loop wraps the brain.** `world/brain.py`'s `ToolBrain` **MUST** subclass
  the vendored `desktop.brain.BrainAdapter`, overriding reply streaming (§7.4) and
  extending prompt assembly with exactly one appended block (§2.5); `persist` and the
  greeting are inherited. Build #1's provider seam (text tokens in, text tokens out —
  B1 §3.1) stays untouched: tools ride *in* the token stream, the same discipline as
  B2 §6's emotion tags.
- §2.4 **Identity and models by citation.** Her identity is the SOUL (B2 §2.3); `VAULT_DIR`
  **MUST** allow continuing an existing Build #1/#2 Vault. Local-first model defaults, the
  reasoning switches, and the embedder rules are inherited (B2 §2.4–§2.6).
- §2.5 **The situation block — she knows when and where she is.** Every assembled prompt —
  reply, greeting, and ambient speech alike — **MUST** carry one appended
  `## THE SITUATION RIGHT NOW` block (`world/situation.py`), rendered fresh per prompt
  from surfaces the host already owns: the current date and time read from the
  **injected clock** (§8.2, never the wall clock), the room's sticky scene state (§4:
  rain, music), and the timer board's pending timers with time remaining. The block
  **MUST** state the embodiment truth: her body is rendered live — eyes that blink, a
  face that shows feeling, a mouth that moves with her voice — in her room or on the
  desktop (§6.5). She **MAY** know she runs as an AI; the block **MUST** direct that
  this never means bodiless — she **MUST NOT** claim to have no body, no eyes, or no
  surroundings, and asked about them she answers plainly (B2 §6's no-narration rule
  forbids stage directions, not the truth). This is ch. 19's world model at reactive
  scale: a rendered snapshot, not a `WorldModelStore` — Build #5 replaces the rendering,
  the block's place in the prompt is the seam that survives (§14).
- §2.6 **The chat surface — her words, visible, beside her.** Both browser pages (`/` and
  `/live2d/`) **MUST** show a chat column next to the body: a scrolling transcript with
  the user's turns (typed *and* spoken — the STT transcript joins the chat), her committed
  replies, an accumulating **draft** while she speaks, a `proactive` tag on lines she
  spoke unprompted (the greeting, ambient self-talk, a finished selfie — YuriOS's flag,
  same meaning), and inline images when a message carries `image_url` (§7.6). The host
  owns the transcript: an in-memory ring (~200 entries) on the Runtime, appended by
  `post_message` and published as `message` events on the bus (§10); `GET /api/history`
  backfills a fresh page. The chat is the *visible* conversation, not her memory — the
  Vault stays the only durable record (B1 §5), and the rules match: a barged-in turn
  drops its draft and commits nothing (B2 §4.4 — a turn that didn't happen leaves no
  trace), ambient lines appear in the chat but still never persist (§8.3). Typing in the
  chat composer **MUST** ride `/ws/voice` as a `text` turn (unchanged wire), so a typed
  turn keeps full TurnController semantics — TTS, barge-in, latency masking. Desktop-pet
  windows (§6.5) hide the chat column; the composer moves to the hover bar.

## §3 — The body: the VRM stage

- §3.1 **No build step.** The frontend **MUST** be one static page served by the app (B2
  §8.1): plain ES modules with an import map; three.js + `@pixiv/three-vrm` (+ `-animation`)
  vendored as committed `.module.min.js` files (MIT — unlike B2 §8.2's fetched proprietary
  runtime, this body ships in git). No npm, no bundler.
- §3.2 **The per-frame update loop** **MUST** follow CS §4's manual order exactly and
  **MUST NOT** call `vrm.update()`: animation mixer → animated material uniforms → bone
  overrides → `humanoid.update()` → gaze → blink → emote → viseme →
  `expressionManager.update()` (commit) → constraints → **spring bones last**. Getting this
  order wrong is the classic failure mode (physics and expressions fight); CS §8 is the
  correctness checklist.
- §3.3 **Load passes** (CS §3): `removeUnnecessaryVertices`, `combineSkeletons`,
  `frustumCulled = false` on every node, the look-at quaternion proxy, facing normalized to
  −Z, and `.vrma` clips re-anchored at the hips so she doesn't teleport to the animator's
  origin.
- §3.4 **The expression catalog.** The brain emits the B2 §6 palette *names*
  (`neutral, happy, sad, surprised, shy, thinking, playful, tender`); the map from name →
  VRM expression weights **MUST** live in the frontend (`web/js/stage/EmoteController.js`),
  so the brain stays renderer-agnostic — this is the exact seam B2 promised Build #4 would
  swap. Every palette name **MUST** resolve to a composite of the six VRM preset expressions
  (`happy, angry, sad, surprised, relaxed, neutral` — the only names guaranteed across VRM
  models, → ch. 25), and the six preset names **MUST** also work directly (they are
  `VrmController.set_expression`'s catalog, §4). The emote blender **MUST NOT** stage
  `blink` or `aa` — those channels are owned by the blink controller and the viseme driver.
- §3.5 **Cheap aliveness** (→ ch. 25): procedural blink on a random timer, gaze that tracks
  the camera by default with idle saccades, and a looping idle `.vrma`. These run
  client-side, unconditionally — she is never a statue, even with the server gone.
- §3.6 **Degrade gracefully.** Without WebGL (or with the model missing) the page **MUST**
  still run the voice loop (B2 §8.2's rule, ported to 3D).

## §4 — The control channel (`avatar` events on the bus)

The Python-side **`VrmController` method surface is canonical** — it is ch. 34's "cleanest
seam in the book," the strings Build #5's tick loop will hold. It **MUST** expose at least:
`set_expression, set_expression_raw, look_at_camera, look_forward, look_at, set_bone,
reset_bone, set_mouth, set_material_color, play_animation, load_model` (vrm-viewer's
surface) plus Build #4's scene channels `set_rain` and `music`. It runs in-process on the
app's event loop; every method publishes **one `avatar` event on the EventHub** (§10),
fanned out to every attached frontend over `/api/events` — the YuriOS avatar-effector
shape, with a command's old wire `type` carried as the event's `op`.

Command shapes are vrm-viewer's `types.ts` union verbatim, extended, under the envelope
`{"type":"avatar", "op": …}`:

```jsonc
{"type":"expression",     "name":"happy", "intensity":0.8}   // §3.4 catalog
{"type":"expression_raw", "values":{"blink":1.0}}
{"type":"look_at",        "mode":"camera"|"none"}
{"type":"look_at",        "target":{"x":0,"y":1.2,"z":-1}}
{"type":"bone",           "name":"rightUpperArm", "euler":{"x":0,"y":0,"z":-75}}
{"type":"bone_reset",     "name":"rightUpperArm"}             // name optional
{"type":"mouth",          "value":0.5}                        // manual override (§5)
{"type":"material_color", "material":"Tops_01_CLOTH", "color":"#223"}
{"type":"animation",      "url":"/models/idle.vrma", "loop":true, "fadeIn":0.3}
{"type":"load_model",     "url":"/models/avatar.vrm"}
{"type":"rain",           "intensity":0.6}                    // scene channel (§6)
{"type":"music",          "action":"play"|"stop", "track":"warm_pad", "volume":0.4}  // (§7)
```

Turn expressions ride this channel too (§10): the voice route realises an expression
OutEvent as `set_expression(name, reset_ms=0)` — hold semantics (B2 §6) — so one lane
carries the face for every body and every open page, scripted or spoken. The frontend
**MUST** auto-reconnect (`EventSource` does). Events arriving before the model loads
**MAY** be dropped, except persistent appearance state (material colors, rain intensity,
music), which the hub keeps **sticky** and **MUST** replay to every new subscriber before
its first live event. Malformed JSON is logged and dropped.

## §5 — Visemes: real lip-sync, amplitude tier

- §5.1 The mouth **MUST** be driven from the **RMS amplitude of the audio actually
  playing** — a WebAudio `AnalyserNode` on the playback graph (`web/js/viseme.js`) staging
  the `aa` expression in loop step 9. Because the analyser reads the same buffers the
  speaker plays, mouth and voice cannot drift (CS §5.4's core property, achieved one tier
  down).
- §5.2 The driver **MUST** apply attack/release smoothing and a silence gate (constants
  adapted from CS §5.4: perceptual `amp^0.7` curve, fast attack ≈ 50, slower release ≈ 30,
  gate below ≈ 0.04, weight cap ≈ 0.7) so the mouth doesn't chatter on noise or freeze open
  between sentences.
- §5.3 When audio is present the `say()` wiggle and any text-length flap **MUST NOT** drive
  the mouth. The `mouth` command (§4) remains as the puppet-channel override for scripted
  use. The full phoneme tier (wlipsync winner/runner blending onto `aa/ee/ih/oh/ou`,
  CS §5.4) is the documented upgrade seam, deliberately not built: amplitude-on-real-audio
  already gives exact sync; phonemes add mouth *shape*, at the cost of an unvendorable
  dependency.

## §6 — The sanctuary scene

- §6.1 The room is canon (→ ch. 28, ch. 29) and its elements are normative: a **small
  room** with **low warm light** (a lamp), a **window with rain** on it, a **window seat**,
  and a **single plant**. She **MUST NOT** stand in a void or a default grey three.js
  scene.
- §6.2 The set **MUST** be procedural three.js geometry and shader work — no binary scene
  assets in git. Rain **MUST** respond to the `rain` command (§4): a window-pane streak
  shader plus falling drops outside, and a synthesized rain-noise bed (filtered noise,
  client-side) whose gain follows intensity.
- §6.3 The page chrome carries the dark-sanctuary brand (Build #1's tokens: JetBrains Mono,
  magenta/cyan/amber accents on near-black). The camera is fixed and cinematic — framing
  her in the room, with subtle mouse parallax — not an orbit-controls model viewer: this is
  a place, not an asset inspector.
- §6.4 **The enter gesture.** The page **MUST** gate on one click ("enter the sanctuary")
  before connecting the sockets, so the `AudioContext` is user-activated and the greeting
  (B2 §7) is audible. Without it, autoplay policy silences her first words. Desktop mode
  (§6.5) is the one exception: a native window's engines don't enforce a gesture, so the
  page auto-enters — and **MUST** still resume a suspended context on the first click, so
  the worst case on a stricter engine is a quiet greeting, never a dead one.
- §6.5 **Desktop presence — the room, set aside.** `python -m world --window` **MAY** host
  the served page in a frameless, transparent, always-on-top native window (pywebview;
  `world/window.py`) pointed at `?desktop=1`, so she floats on the desktop as B2 §9's pet
  did. The launcher **MUST** reuse the vendored B2 launcher's helpers (readiness probe,
  engine pick) rather than copy them, and the frame reuses B2 §9's `WINDOW_*` knobs
  (inherited config). What the flag *means* is the page's decision, not Python's: in
  desktop mode the page **MUST NOT** build the sanctuary (no room, no fog — the desktop is
  the room), the renderer **MUST** clear to alpha 0, a neutral light rig **MUST** replace
  the lamp (an unlit MToon face shades toward black), and the camera frames the full body.
  Both sockets, every §4 command, the tools, and the idle machine are unchanged; `rain`
  arrives as sound only (the §6.2 noise bed). Not required for the DoD.
- §6.6 **The second body.** Build #2's web client **MUST** be vendored under `web/live2d/`
  as a *documented fork* (a `VENDORED.md` naming every departure, each marked `FORK(B2)`
  in-file; runtime + rigs fetched by `scripts/fetch_live2d.py`, never committed — B2 §8.2)
  and served at `/live2d/`, with its API needs answered — the vendored B2 settings router
  included as-is, and `/api/config` re-aimed at `web/live2d/` (`world/routes/live2d.py`,
  over the vendored rig registry). The fork is exactly the bus adaptation: the page gains
  the §2.6 chat column (loading the shared `/js/chat.js`) and one new file, `events.js`,
  that maps `avatar`/`expression` events from `/api/events` onto the untouched pixi body
  (`avatar.js`, `voice.js`, `settings.js` stay byte-identical to B2's). Audio still rides
  `/ws/voice` unchanged. `DESKTOP_BODY=vrm|live2d` (or `--window --body …`) picks which
  body the §6.5 window floats. The Live2D body realises only the `expression` op, so the
  idle machine's other *body* acts (gaze, posture) don't reach it — it remains a guest,
  not a second puppet; wiring pixi to the rest of the puppet ops is the reader exercise
  it always was, with the events now already arriving on the page. One page, one flag,
  zero brain changes: the proof that the seam is the bus, not the renderer.

## §7 — Tools via MCP: the hands

- §7.1 **Four tools, real MCP.** The build ships an in-repo MCP server
  (`world/tools/server.py`, FastMCP over stdio) exposing exactly:

  | tool | args | returns | side effect |
  |---|---|---|---|
  | `set_timer` | `minutes` (0 < m ≤ `TIMER_MAX_MINUTES`), `label?` | `{id, label, seconds, due}` | host schedules the announcement (§7.5) |
  | `play_music` | `action: "play"\|"stop"`, `track?`, `volume?` | `{playing, track}` | `music` event to the stage (§4) |
  | `get_weather` | `city?` (default `WEATHER_CITY`) | `{city, temp_c, condition, wind_kmh}` | none |
  | `take_selfie` | `scene?`, `mood?` (template-library keys; empty = her choice) | `{id, scene, mood, status:"started"}` | host renders off-turn, posts the photo to the chat (§7.6) |

  Four is enough to teach the whole pattern (→ ch. 17) — including the one lesson three
  couldn't (§7.6: a slow tool). The surface **MUST NOT** grow a shell — the heavy,
  sandboxed hands are Build #5's (§12). With `SELFIE_BACKEND=off` the fourth tool **MUST
  NOT** be advertised at all: no hand, not a dead one.
- §7.2 **A genuine MCP client.** The brain side **MUST** connect over MCP
  (`world/tools/client.py`, stdio transport spawning `sys.executable -m world.tools.server`),
  discover the tools with `list_tools`, and build the §7.4 directive from the discovered
  schemas — build the capability behind MCP once, stay portable (→ ch. 17). If the SDK or
  server fails, the build **MUST** degrade to tools-off and keep talking (B2 §3's
  graceful-backend rule); `/api/health` reports the truth.
- §7.3 **Guardrails** (→ ch. 17; the game-NPC lesson, ch. 02 §1). Every call **MUST** pass
  `world/tools/guard.py`: an **allowlist** (exactly the discovered tools; anything else is
  denied, never forwarded), **per-tool rate limits** (token bucket on the injected clock),
  a **per-turn call cap** (`TOOL_MAX_CALLS_PER_TURN`), a **per-call timeout**, and **result
  truncation**. Every call — allowed or denied — **MUST** append one JSONL audit line
  (`ts, tool, args, verdict, duration_ms, result`) to `TOOL_LOG_DIR`. She can be *asked*
  anything; the guard decides what her hands actually do.
- §7.4 **The in-stream call protocol.** A `## TOOLS` block appended to the system prompt
  (the same one-append pattern as B2 §6.1) instructs the model: speak a short lead-in
  sentence first, then emit `[[tool_name {"arg": value}]]`. The streaming parser
  (`world/tooltags.py`) **MUST** strip markers from speech, tolerate token-boundary splits,
  and drop unclosed, unknown, or oversized markers silently (mirrors B2 §6.2). On a closed
  marker: guard-check → MCP call → a **continuation stream** (original messages + the
  partial reply + a `((tool result: …))` cue) that the model finishes as the same turn —
  the result returns to context, so she *speaks to* what her hands found. First audio
  **MUST NOT** wait on a tool: the lead-in sentence reaches TTS before the call runs, so
  the §1 budget holds. Barge-in (B2 §4.3) **MUST** cancel the continuation, and a barged-in
  tool turn persists nothing (B2 §4.4).
- §7.5 **Semantics.** The MCP server is the *contract and audit point* for `set_timer` —
  it validates and records — but the **host** schedules the wake (`world/tools/timers.py`,
  on the injected clock), because only the host owns her voice; when a timer elapses she
  **MUST** announce it aloud through the ambient seam (§8.4), queued until deliverable.
  `get_weather` **MUST** be a real HTTP lookup (Open-Meteo, keyless) behind a
  `WeatherProvider` seam with an offline fake. `play_music` drives the browser-side
  synthesized ambience (§6.2) — honest note: "music" is a generative pad, not a media
  library; the seam is the point.
- §7.6 **Her camera: `take_selfie`, start-don't-await.** The fourth hand teaches the one
  tool lesson the other three can't: **a slow tool must not sit inside the turn.** A
  hosted render takes 10–30 s; the §7.3 timeout is tuned for weather lookups, and dead
  air after her lead-in sentence would read as a hang. So the tool follows the YuriOS
  `spawn` rule (*ACT starts work; it never awaits it*): the MCP server is the contract
  point only — it validates `scene`/`mood` against the vendored template library (its
  tool description **MUST** be built *from* the library, so the choices the model reads
  can never drift from the yaml) and returns `{status:"started"}` immediately; the turn
  continues and ends on the §1 budget. The **host** realises the shot (§7.5's split):
  `world/selfies.py`'s `SelfieLab` renders off-turn through the vendored forge
  (`./forge` — the image-forge slice: the locked register, the selfie template
  library, provenance stripping; → ch. 26), saves the PNG + its provenance sidecar under
  `SELFIE_DIR` (served at `/selfies/`), posts an `image_url` `message` to the chat
  (§2.6, `proactive`), and offers one spoken line about it through the ambient seam
  (§8.4) — dropped if she's busy, because unlike a timer (§8.3's promise) the photo
  itself already landed. Backends are GPU-free by construction: `openrouter` — default
  model `bytedance-seed/seedream-4.5`, cheap enough for casual selfies; point
  `SELFIE_MODEL` at `sourceful/riverflow-v2.5-pro` for the brand-art register — or `mock`
  (deterministic placeholder cards; the tests). Her voice keeps the local GPU either
  way. A configured `openrouter` with no key
  **MUST** degrade to `mock` with one loud WARNING naming the fix (B2 §3's rule);
  `/api/health` reports which camera she actually has. A failed render **MUST** become a
  quiet chat message, never a crash and never silence.

## §8 — The idle machine: alive when you're quiet

- §8.1 **States** (`world/idle.py`), all on the Python side, all through the §4 controller:

  | state | entered | behaviour |
  |---|---|---|
  | `engaged` | a turn in flight, or < `IDLE_SETTLE_S` since one ended | gaze to camera; no ambient acts |
  | `resting` | the settle timer expires | micro-acts every `IDLE_ACT_MIN..MAX_S`: gaze drift, a small expression pulse, a posture shift (bone nudge) |
  | `rain_gazing` | occasionally from `resting` | look-at the window for a few seconds, `relaxed` |
  | `self_talk` | the Ukagaka idle timer (`IDLE_TALK_MIN..MAX_S` of quiet) | one short in-character spoken line about the room, the rain, or a memory (§8.3) |
  | `announce` | a timer elapses | speak the timer's label; preempts any non-engaged state, queues while `engaged` or clientless |

- §8.2 **Sim-time testable.** The machine **MUST** take an injected clock
  (`world/clock.py`; `VirtualClock` in tests — the YuriOS discipline: never read the wall
  clock, never bare-`sleep`) and a seedable RNG, so tests run hours of idleness in
  milliseconds (§13).
- §8.3 **Ambient speech is a real turn, minus the memory.** Self-talk and announcements
  **MUST** go through the same turn pipeline (voice, face, barge-in-able), cued like the
  greeting (B2 §7), and **MUST NOT** persist — no corpus line, no Vault commit. They
  **do** appear in the visible chat (§2.6), flagged `proactive` — the chat is what was
  said, the Vault is what is remembered, and only the second is memory. Announcements
  queue until deliverable; missed self-talk is simply dropped.
- §8.4 **The ambient seam.** The forked route (§2.2) registers a per-connection injector;
  ambient turns run on that connection's own `TurnController`, so one barge-in path kills
  everything she says, scripted or replied.
- §8.5 **This is not a mind** (normative). No goals, no salience, no deciding to reach out,
  no world model — the idle machine is the Ukagaka idle-talk timer reborn (→ ch. 02 §1),
  and it is *scripted* on purpose. Build #5 replaces this exact caller with the cognitive
  tick loop (→ ch. 18) holding the same `VrmController`.

## §9 — The voice loop, preserved

B2 §3 (seams and fakes), §4 (the real-time loop; barge-in-as-cancel; no-trace), §5 (filler
masking), §6 (emotion tags), and §7 (the greeting) are inherited **by citation** — the
vendored code *is* the implementation. The suite **MUST** re-prove barge-in and
no-trace-on-cancel *through `ToolBrain`* (§13), since the tool loop adds a second
generation pass that must also die on cancel.

## §10 — Topology: one event bus + one audio socket

The YuriOS shape, adopted: **everything the host tells a frontend is one typed event on
one bus.** The only thing that keeps a socket of its own is sound.

- **`EventHub`** (`world/hub.py`) — the single outbound fan-out, ported from the YuriOS
  host (`http_api.EventHub`) plus this build's sticky replay. Every host→frontend event
  is one typed JSON dict: `hello` (her name), `message` (§2.6 — chat entries, including
  `image_url` selfies), `draft` / `draft_cancel` (§2.6), and `avatar` (§4 — the puppet
  strings, scene channels included). Publishes are non-blocking (a stalled client loses
  events, never blocks the publisher) and thread-safe (the TTS thread publishes).
- **`GET /api/events`** — the bus's wire: SSE, one `data:` line per event. On attach:
  `hello`, then the sticky replay (§4), then live events. The stream **MUST** end itself
  on shutdown (a stop flag polled every second — an open tab must never hold Ctrl+C
  hostage) and ping (`: ping`) while idle. `GET /api/history` backfills the chat (§2.6).
- **`/ws/voice`** — the audio-only socket: binary mic PCM up, `hello`/`endpoint`/
  `bargein`/`text` control up; `session`, `filler`/`audio` (base64 PCM + the sentence
  text for the §5 viseme path), `done`, `cancelled`, `error` down. This is B2 §10's wire
  *minus* `expression` — turn expressions are re-routed onto the bus by the forked route
  (§4), so the face has one lane. PCM keeps a websocket because audio is the one flow
  that is bidirectional, binary, and latency-critical; everything else is a broadcastable
  fact about the world, and facts ride the bus.

One bus is the convergence path (§14): YuriOS's frontends already speak exactly this
`/api/events` shape, so each Build-#5 step swaps a publisher behind the hub — the tick
loop for the idle machine, the broker for the guard — and no frontend changes. The
inbound mirror (YuriOS's `SignalBus`) is **deliberately not ported yet**: it has no
consumer until the tick loop exists, so user input stays on the voice socket's turn
semantics (§2.6).

## §11 — Config

Typed (`world/config.py`), extending Build #2's config (which extends Build #1's); read
once from env/`.env`. Every knob in `.env.example` **MUST** have a default and the default
stack **MUST** need no key (`SELFIE_BACKEND=openrouter` without a key degrades to mock —
§7.6 — so the no-key rule survives it). New knobs: `PORT=8767`; `COMPANION_NAME`;
`TOOLS_BACKEND=mcp|fake|off`; `TOOL_MAX_CALLS_PER_TURN`, `TOOL_TIMEOUT_S`, `TOOL_LOG_DIR`,
per-tool rate limits (incl. `TOOL_RATE_SELFIE`); `WEATHER_BACKEND=open_meteo|fake`,
`WEATHER_CITY`; `TIMER_MAX_MINUTES`; `SELFIE_BACKEND=openrouter|mock|off`, `SELFIE_MODEL`,
`SELFIE_DIR` (§7.6); `IDLE_ENABLED`, `IDLE_SETTLE_S`, `IDLE_ACT_MIN_S/MAX_S`,
`IDLE_TALK_MIN_S/MAX_S`, `IDLE_SEED`; `RAIN_INTENSITY`; `DESKTOP_BODY=vrm|live2d` (§6.6).
The desktop window inherits B2 §9's `WINDOW_WIDTH/HEIGHT/ON_TOP/GUI` and the Live2D body
inherits B2 §6's `AVATAR_MODEL`, all via the vendored config.

## §12 — Omissions (normative)

No autonomy/tick loop, no goals, no salience gates (→ Build #5, ch. 18). No world-model
*store*: the §2.5 situation block is a per-prompt rendering of host state, not a
`WorldModelStore` with beliefs, expectations, or point-in-time queries (→ ch. 19; Build #5).
No inbound `SignalBus` and no broker — the outbound half of the YuriOS split is here (§10);
the inbound inbox and the broker/effector gate are the named next rungs, taken when the
tick loop gives them a consumer (§14). No heavy sandboxed hands — no code execution, no
shell, no workshop (→ ch. 17 "the heavy hands", ch. 19): the reactive MCP surface
is deliberately small. No selfie *editing* and no local-GPU image backends — the vendored
forge slice ships `mock` + `openrouter` only (§7.6; the diffusers/ComfyUI paths live in
`../image-forge`). No phoneme-tier visemes and no webcam mocap (CS §5.4/§5.6 — the seams
are in place). No VR (→ ch. 29; the body is VRM-standard and the stack transport-agnostic,
so the door stays open). No outfit changes — VRM clothing is baked; `material_color` is a
tint (→ ch. 29). The Live2D body realises only the `expression` op off the bus (§6.6) —
the second body is a guest, not a second puppet. Single room, single register. The bundled
avatar is the VRoid Project's **AvatarSample_B** — the same stock body the YuriOS
sanctuary ships, redistributable under its VRoid Hub license (everyone / commercial /
redistribution allowed) — explicitly not Yuri (→ ch. 25's license trap; `load_model` is
the user's `.vrm` slot).

## §13 — Tests (the hard gate)

`pytest` **MUST** ship and be green from the project root, entirely offline — fakes for
STT/TTS/VAD/brain (B2 §3), a fake tool runner, `httpx.MockTransport` for weather, an
**in-memory MCP session** (never a subprocess) for the contract tests, and `VirtualClock`
for everything timed. It **MUST** pin at least: tool-tag parsing (whole, split across
tokens, unknown/unclosed/oversized dropped, never spoken); the tool loop end-to-end over a
scripted fake stream (guard consulted, result reaches the continuation, call cap enforced,
tool error still completes the turn); **barge-in mid-continuation cancels and persists
nothing** (§7.4, §9); guard allowlist/rate-limit/audit-line behaviour (the selfie's rate
included); the real MCP server's contract (`list_tools` = exactly four — three with
selfies off; schema, bounds, and template-key validation) over an in-memory session; the
§7.6 lab (a started contract becomes a PNG + provenance sidecar on disk and an
`image_url` `message` on the bus in sim time; the announce cue is offered and dropped
when she's busy; a broken forge becomes a quiet message; no key degrades openrouter →
mock loudly; the tool loop hands the contract to the lab and the turn ends first); timer
scheduling and queued announcements in sim time; the idle machine's states, windows, and
preemption in sim time (seeded RNG, silent while `engaged`, self-talk via the ambient
seam with `persist=False`); every §4 op's event shape including `rain`/`music`; the hub
(typed fan-out to N subscribers, sticky recorded before any subscriber and replayed
last-write-wins, a full queue drops without blocking, thread-safe publish); the SSE route
(hello + sticky replay, honours the stop flag, transcript backfill via `/api/history`,
the ring bounded); the forked `/ws/voice` route (greeting-once, noise-drop, barge-in,
**ambient injection reaches the client and is not persisted**, the transcript tee —
typed and spoken user turns committed, drafts commit on done and drop on barge-in,
greeting/ambient flagged `proactive`, expressions on the bus and off the wire); first
audio precedes tool execution on a tool turn (§7.4's ordering, from the OutEvent
stream); the §3.4 palette map (every brain palette name has a frontend catalog
entry — source-scanned); the §2.5 situation block (the stated time is the injected
clock's and moves when it advances, the embodiment truth is present verbatim — never
"no body" — weather and music lines follow the sticky scene state, pending timers are
listed with time remaining and leave when they land, and the real-brain e2e prompt
carries the block); the §6.5 launcher (imports without pywebview, the URL carries
`?desktop=1` for whichever body and never targets 0.0.0.0, an occupied port is refused,
the vendored helpers are B2's actual functions) and both pages honouring the flag
(source-scanned); the §6.6 second body (the vendored client served at `/live2d/`,
`/api/config` resolving and falling back over the re-aimed registry, the vendored settings
router answering); and an end-to-end turn over the **real vendored brain** (seeded
Vault, injected fake models) proving a tool-bearing turn writes one corpus line and one
Vault commit.

## §14 — Extends to

This build is now **YuriOS-shaped where it counts**: the `EventHub` is literally the
YuriOS host's (§10), the chat surface is the sanctuary frontend's (§2.6), and the selfie
follows the effectors' start-don't-await rule (§7.6). Build #5 swaps the scripted callers
for the mind, one publisher at a time, behind wires that don't move: the cognitive tick
loop (→ ch. 18) replaces `world/idle.py` and decides, on its own clock, when to look,
gesture, speak, or reach for a tool — calling the exact same `VrmController` methods onto
the exact same bus; the inbound `SignalBus` lands with it (user input becomes a signal the
loop consumes — §10's deliberate omission); the Guard grows into the broker/effector gate
(→ ch. 19) holding the same MCP client and the same `SelfieLab`. Nothing in the body or
the frontends changes; the strings get a real puppeteer.
