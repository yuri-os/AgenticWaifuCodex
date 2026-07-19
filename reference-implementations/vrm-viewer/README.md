# VRM Viewer — Python-controlled reference implementation

A minimal, standalone implementation of the AIRI VRM control pipeline (see the vendored
[`docs/vrm-control-spec.md`](docs/vrm-control-spec.md) — the implementation-independent spec this
build follows). A browser renders and animates a `.vrm` avatar; a **Python API drives it**
over WebSocket — expressions, gaze, body pose, mouth/speech, and animation.

```
  Python (server/)                          Browser (web/)
  ┌────────────────┐   WebSocket :8765   ┌──────────────────────────┐
  │ VrmController   │ ──── JSON cmds ───► │ ControlBridge → VrmStage  │
  │  .set_expression│                     │  • manual §4 update loop  │
  │  .look_at       │                     │  • EmoteController (face) │
  │  .set_bone      │                     │  • Blink / Gaze / mouth   │
  │  .say           │                     │  • three.js + three-vrm   │
  └────────────────┘                     └──────────────────────────┘
```

The viewer is the WebSocket **client** and auto-reconnects, so you can start either side first.

## What's included

- `web/` — the viewer (TypeScript + three.js + `@pixiv/three-vrm`). No framework.
- `web/public/models/avatar.vrm` — a sample VRM 1.0 avatar (pixiv three-vrm sample).
- `web/public/models/idle.vrma` — a looping idle animation.
- `server/` — the Python control bridge (`websockets`) and a `demo.py`.

## Quick start

**1. Run the viewer**

```bash
cd web
npm install
npm run dev          # serves http://127.0.0.1:5173
```

Open <http://127.0.0.1:5173>. You should see the avatar idling, blinking, and tracking the camera.
The status overlay (top-left) shows model + bridge state.

**2. Drive it from Python**

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python examples/demo.py
```

The demo waits for the browser tab, then cycles emotions, waves, and "talks".

## Python API

```python
from vrm_control import VrmController

vrm = VrmController(host="127.0.0.1", port=8765).start()
vrm.wait_for_viewer()                      # block until the browser connects

# Channel 2 — facial emotion (auto-resets to neutral after 3s in the viewer)
vrm.set_expression("happy", intensity=0.8) # happy|sad|angry|surprised|neutral|relaxed
vrm.set_expression_raw({"blink": 1.0})     # raw blendshape weights

# Channel 5 — gaze
vrm.look_at_camera()                       # eye contact
vrm.look_at(0.5, 1.4, -1.0)                # explicit world point
vrm.look_forward()

# Channel 6 — body pose (direct humanoid-bone override, Euler degrees)
vrm.set_bone("rightUpperArm", z=-75)       # lift the arm
vrm.reset_bone("rightUpperArm")            # release (back to animation)
vrm.reset_bone()                           # release all

# Channel 4 — mouth / speech
vrm.set_mouth(0.6)
vrm.say(2.0)                               # pseudo-speech mouth wiggle for 2s

# Appearance — tint a material by name (texture is multiplied by the color)
vrm.set_shirt_color("#2b3a67")             # recolor the bundled avatar's t-shirt
vrm.set_material_color("Hair_00_HAIR", "#5a3825")

# Channel 1 — body animation / model swap
vrm.play_animation("/models/idle.vrma", loop=True)
vrm.load_model("/models/avatar.vrm")
```

`vrm_control.EMOTIONS`, `vrm_control.HUMANOID_BONES`, and `vrm_control.MATERIALS`
(shirt/pants/shoes/skin/hair → material names) enumerate valid names. For any other model,
run `stage.materialNames()` in the browser console to list its materials.

> **Recoloring vs. new clothing.** VRM clothing is baked into the mesh + textures at authoring
> time — there's no runtime "change outfit". `set_material_color` multiplies the existing texture
> by a tint (great for the bundled avatar's near-white t-shirt). To change a garment's *design*,
> swap the whole `.vrm` (drop a file in `web/public/models/` and `vrm.load_model(...)`) or author
> a new outfit in **VRoid Studio**. Note each `.vrm` embeds an avatar usage license — pick models
> whose license fits your use.

## Hooking up your own AI loop

`VrmController` is plain blocking Python, so any agent loop can call it directly. The natural
mapping to the spec's AI pipeline (§6):

- Parse your LLM's emotion intent (e.g. an `<|ACT|>{"emotion":"happy"}|>` token, or a tool call)
  → `vrm.set_expression(name, intensity)`.
- While your TTS plays audio, sample its amplitude per frame → `vrm.set_mouth(level)` (or call
  `vrm.say(duration)` for a quick stand-in). For real viseme lip-sync, feed the TTS `AudioNode`
  into a `wlipsync` graph in the browser as described in spec §5.4.
- For AI-generated gestures, compute bone rotations and stream them via `vrm.set_bone(...)`
  each tick — this is the same "generic pose seam" the spec uses for MediaPipe mocap (§5.6).

## How it maps to the spec

| Spec section | Where |
|---|---|
| §3 model loading (perf passes, facing, framing) | `web/src/stage/VrmLoader.ts` |
| §4 manual per-frame update order | `web/src/stage/VrmStage.ts` → `update()` |
| §5.1 `.vrma` load + hips re-anchor | `VrmStage.playAnimation` / `reAnchorHips` |
| §5.2 emotion state machine | `web/src/stage/EmoteController.ts` |
| §5.3 blink | `web/src/stage/Blink.ts` |
| §5.5 gaze + idle saccades | `web/src/stage/GazeController.ts` |
| §5.6 generic pose seam | `VrmStage.setBone` (bone overrides applied pre-`humanoid.update()`) |
| §6 AI control bridge | `web/src/bridge/ControlBridge.ts` + `server/vrm_control/` |

## Reference material (for AI coders improving this)

The single most important document is the vendored spec — read it before changing the update loop or
adding a channel:

- **[`docs/vrm-control-spec.md`](docs/vrm-control-spec.md)** — the full AIRI VRM control spec this build
  implements: the seven control channels (§1), the **exact per-frame update order** (§4 — get this wrong
  and spring bones/expressions/pose fight each other), per-channel detail (§5), the AI-driven pipeline
  (§6), and a "critical correctness checklist" of the non-obvious things that break reproductions (§8).
  The README's *How it maps to the spec* table above ties each `web/src/` file to a spec section.

External library docs an agent will need to extend this faithfully:

| Concern | Library / doc |
|---|---|
| VRM in three.js (loader, MToon, expressions, look-at, spring bones) | `@pixiv/three-vrm` — <https://github.com/pixiv/three-vrm>, API docs <https://pixiv.github.io/three-vrm/> |
| `.vrma` animation loading + retargeting | `@pixiv/three-vrm-animation` (same repo) |
| The VRM format itself (humanoid bones, expression presets, license block) | VRM spec — <https://github.com/vrm-c/vrm-specification>, <https://vrm.dev/en/> |
| Real-time visemes from audio (full lip-sync, spec §5.4) | `wlipsync` — <https://www.npmjs.com/package/wlipsync> |
| Webcam → body landmarks (mocap pose, spec §5.6) | `@mediapipe/tasks-vision` — <https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker> |
| three.js core (render loop, math, raycasting) | <https://threejs.org/docs/> |

The features deliberately omitted here (full viseme lip-sync, MediaPipe mocap, MToon/IBL shader injection)
are each fully specified in the noted spec sections — the bridge command shape already leaves room to add
them, so they're the natural first improvements.

## Limitations (intentional, to stay minimal)

- Lip-sync is a single mouth-open value, not full audio-driven visemes (spec §5.4 uses `wlipsync`).
- Pose control is direct per-bone Euler rotation, not the full MediaPipe landmark → quaternion
  solver (spec §5.6). The bridge command shape leaves room to add it.
- MToon/IBL shader injection and post-processing from the full app are omitted.
