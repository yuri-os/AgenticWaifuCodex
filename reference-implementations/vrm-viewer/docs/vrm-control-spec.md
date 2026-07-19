# Technical Specification — VRM Model Control & AI-Driven Animation

> **Purpose.** This document specifies, in implementation-independent terms, how Project AIRI loads,
> renders, and controls a `.vrm` avatar, and how an AI/LLM pipeline drives that avatar's expression,
> gaze, lip-sync, and full-body pose. It is written so the functionality can be **reproduced as a
> standalone application** without depending on the AIRI monorepo.
>
> Source of truth in this repo: `packages/stage-ui-three` (rendering + control), `packages/model-driver-mediapipe`
> (camera/body tracking), and `packages/stage-ui` (`components/scenes/Stage.vue`, `composables/queues.ts`,
> `constants/emotions.ts`) for the AI orchestration glue.

---

## 1. Scope & Glossary

### 1.1 What "controlling a `.vrm`" means here

A loaded VRM avatar is controlled through **seven independent channels**, each updated once per render
frame (~60 Hz). They are layered, not mutually exclusive — they all write into the same humanoid skeleton
and expression manager and are reconciled by update order (see §5).

| # | Channel | What it drives | Authoritative input |
|---|---------|----------------|---------------------|
| 1 | **Body animation** | Full skeleton (`.vrma` clip) | Idle/emotion animation clip via `AnimationMixer` |
| 2 | **Expression / emotion** | Face blendshapes (`happy`, `sad`, …) | AI token stream (`<\|ACT\|>` / `<\|EMOTE\|>`) |
| 3 | **Blink** | `blink` blendshape | Procedural timer |
| 4 | **Lip-sync** | Mouth visemes (`aa/ee/ih/oh/ou`) | TTS audio buffer (real-time analysis) |
| 5 | **Gaze / look-at** | Eye bones + saccades | Cursor / camera / idle saccade generator |
| 6 | **Live motion-capture pose** | Humanoid bones (arms/legs/torso) | Webcam → MediaPipe landmarks |
| 7 | **Transform & camera** | Model offset/rotation, orbit camera | UI / settings store |

### 1.2 Glossary

- **VRM**: glTF-based humanoid avatar format (VRM 0.x / 1.0) with a standardized humanoid bone map,
  blendshape/expression presets, spring bones (physics), look-at, and MToon (anime/NPR) materials.
- **`.vrma`**: VRM Animation file — a glTF animation retargetable onto any VRM humanoid.
- **Humanoid**: the normalized bone abstraction (`hips`, `spine`, `chest`, `head`, `leftUpperArm`, …)
  that lets one animation/pose drive any VRM regardless of its raw skeleton.
- **Expression Manager**: VRM subsystem mapping named expressions (`happy`, `aa`, `blink`) to
  weighted morph targets / material changes.
- **Spring bones**: secondary physics for hair/clothes, simulated per frame.
- **MToon**: toon/NPR material; needs a per-frame `material.update(delta)` for animated uniforms.
- **Special token**: an inline control marker emitted by the LLM inside its text stream
  (e.g. `<\|ACT\|>`, `<\|EMOTE\|>`, `<\|DELAY:1\|>`) that is parsed out of the text and turned into a command.

---

## 2. Dependencies & Runtime Assumptions

### 2.1 Core libraries (current implementation)

| Concern | Library | Notes |
|---------|---------|-------|
| WebGL renderer | `three` | Renderer, scene graph, cameras, raycasting, math |
| VRM load/runtime | `@pixiv/three-vrm` | `VRMLoaderPlugin`, `VRMUtils`, MToon material plugin |
| VRM animation | `@pixiv/three-vrm-animation` | `.vrma` loading + `createVRMAnimationClip`, `VRMLookAtQuaternionProxy` |
| VRM core types | `@pixiv/three-vrm-core` | `VRMCore`, expression manager types |
| Lip-sync DSP | `wlipsync` | Real-time viseme weights from an `AudioNode` |
| Body tracking | `@mediapipe/tasks-vision` | Pose/hand/face landmark detection |
| Vue binding (optional) | `@tresjs/core` | Declarative three.js for Vue; **not required** to reproduce |

> **Reproduction note.** The Vue/TresJS/Pinia layer is presentation glue. A standalone app can be built
> directly on `three` + `@pixiv/three-vrm` + `wlipsync` + `@mediapipe/tasks-vision`. Everything in §3–§6
> is expressible as plain TypeScript classes/functions driving a manual `requestAnimationFrame` loop.

### 2.2 Runtime environment

- Browser or Electron renderer with WebGL2 and Web Audio API.
- `AudioContext` (suspended until first user gesture — must be resumed on click/keydown/touch).
- Optional: webcam access (`getUserMedia`) for the motion-capture channel.
- A single shared `GLTFLoader` instance registered with the VRM + VRM-animation plugins
  (`composables/vrm/loader.ts`). The loader is a process-wide singleton.

---

## 3. Model Loading Pipeline

Reference: `composables/vrm/core.ts` (`loadVrm`), `composables/vrm/loader.ts` (`useVRMLoader`).

### 3.1 Loader construction

1. Create one `GLTFLoader`, `crossOrigin = 'anonymous'`.
2. Register a `VRMLoaderPlugin` with a custom `MToonMaterialLoaderPlugin` (AIRI subclass adds an optional
   "force outline on all materials" policy, default **off** via `AIRI_ALL_OUTLINE = false`).
3. Register a `VRMAnimationLoaderPlugin` so the same loader can also parse `.vrma` files.

### 3.2 `loadVrm(url, { lookAt, onProgress, scene? })`

1. `loader.loadAsync(url, onProgress)` → glTF; read `gltf.userData.vrm`. If absent, the file is not a VRM → bail.
2. **Performance passes** (critical, large FPS impact):
   - `VRMUtils.removeUnnecessaryVertices(vrm.scene)`
   - `VRMUtils.combineSkeletons(vrm.scene)`
3. Disable frustum culling on every object (avatar parts must never pop out at frame edges):
   `vrm.scene.traverse(o => o.frustumCulled = false)`.
4. **Look-at proxy**: if `lookAt`, attach a `VRMLookAtQuaternionProxy` named `lookAtQuaternionProxy`
   to `vrm.scene` (required for look-at to be animatable by clips).
5. Wrap `vrm.scene` in a parent `THREE.Group` (`_vrmGroup`). The **group** is the transform handle the
   app moves/rotates; the avatar scene stays at local origin.
6. **Facing normalization**: rotate `_vrmGroup` so the avatar's `lookAt.faceFront` aligns with world
   `-Z` (compute a quaternion `setFromUnitVectors(faceFront, (0,0,-1))` and premultiply).
7. `springBoneManager.reset()` and `updateMatrixWorld(true)`.
8. Compute a **bounding box** (skipping `VRMC_springBone_collider` meshes), deriving `modelSize`,
   `modelCenter` (pivot raised by `modelSize.y / 5` to put the chest near origin), and an initial camera
   offset so the upper ⅔ of the model is framed: `z = -(size.y/3) / tan(fov/2)`, `fov = 40°`.
9. Return `{ _vrm, _vrmGroup, modelCenter, modelSize, initialCameraOffset }`.

### 3.3 Scene-bootstrap output (consumed by camera/view)

After load, the renderer computes a `SceneBootstrap` payload (`VRMModel.vue → buildSceneBootstrap`):
`{ cameraPosition, cameraDistance, eyeHeight (world Y of head bone), lookAtTarget (default (0, eyeHeight, -100)),
modelOffset, modelOrigin, modelSize }`. A standalone app uses this to seat the camera and look-at default.

### 3.4 Material setup at load

Traverse `vrm.scene` meshes and, per material:
- `MeshStandardMaterial` / `MeshPhysicalMaterial`: set `envMapIntensity` and flag `needsUpdate`.
- **MToon** (`mat.isMToonMaterial`): set `toneMapped = false`; let three-vrm own its IBL/light-probe path
  (do **not** double-inject diffuse IBL).
- Custom `ShaderMaterial`: disable tone mapping, null out `envMap`, force sRGB on base color texture,
  inject diffuse IBL.

### 3.5 Lifecycle, caching & disposal

- **Load reasons**: `initial-load`, `model-reload` (same src), `model-switch` (different src),
  plus `component-unmount`, `manual-reload` (HMR).
- A **managed-instance cache** (`Model/vrm-instance-cache.ts`) can stash a fully-built instance
  (`{ vrm, group, mixer, emote }`) keyed by `(scopeKey = window.location.href, modelSrc)` so re-entry
  reuses it. Before reuse the instance is validated by calling `updateMatrixWorld` + `humanoid.update()`
  inside a try/catch.
- **Disposal policy**: `model-switch` → destroy resources; `component-unmount` → stash for reuse;
  destruction calls dispose hooks, `emote.dispose()`, `mixer.stopAllAction()`,
  `VRMUtils.deepDispose(vrm.scene)`, and removes the group from its parent.
- **Concurrency guard**: a monotonically increasing `loadSequence` invalidates in-flight loads; any await
  point re-checks `isLoadRequestCurrent(requestId)` and disposes orphaned partial loads. Essential to avoid
  leaks when the user switches models mid-load.

---

## 4. The Per-Frame Update Loop (heart of control)

Reference: `VRMModel.vue → bindManagedVrmInstanceRenderLoop`.

> **Why manual.** AIRI does **not** call `vrm.update(delta)`. It owns the render loop and updates each VRM
> subsystem explicitly so individual channels can be reordered, measured, paused, or replaced. A standalone
> app must replicate this exact ordering.

Each frame, with `delta` seconds since last frame, **in this order**:

```
1.  animationMixer.update(delta)          // body animation clip (channel 1)
2.  forEach material: material.update(delta)   // MToon/shader animated uniforms
3.  runVrmFrameHooks(ctx)                  // internal lifecycle hooks (outline, etc.)
4.  vrmFrameRuntimeHook?.(vrm, delta)      // EXTERNAL hook → live mocap pose (channel 6)
5.  vrm.humanoid.update()                  // flush normalized-bone → raw-bone
6.  vrm.lookAt.update(delta)               // gaze (channel 5)
7.  blink.update(vrm, delta)               // blink (channel 3)
8.  emote.update(delta)                    // emotion blendshape lerp (channel 2)
9.  lipSync.update(vrm, delta)             // visemes (channel 4)
10. vrm.expressionManager.update()         // commit all blendshape weights
11. vrm.nodeConstraintManager.update()     // VRM constraints
12. vrm.springBoneManager.update(delta)    // hair/cloth physics (must be last)
```

Key invariants:
- **`humanoid.update()` (5) must run after pose writes (4)** and before look-at/expression commit.
- **`expressionManager.update()` (10) must run after every blendshape writer** (blink, emote, lipsync) —
  those writers only *stage* values via `setValue`; (10) commits them.
- **Spring bones (12) run last** so secondary physics react to the final pose.
- Pausing = stop the loop (`useLoop().stop()`); resuming restarts it. Frame timing tracing is optional.

Transform watchers (outside the loop) update `group.position` from `modelOffset` and `group.rotation.y`
from `modelRotationY` (degrees→radians).

---

## 5. Control Channels — Detailed Specification

### 5.1 Channel 1 — Body Animation (`.vrma`)

Reference: `composables/vrm/animation.ts`.

1. `loadVRMAnimation(url)` → `gltf.userData.vrmAnimations[0]`.
2. `createVRMAnimationClip(animation, vrm)` → a `THREE.AnimationClip` retargeted to this avatar.
3. **Re-anchor root** (`reAnchorRootPositionTrack`): the clip's hips `.position` track is offset so the
   animation's first-frame hip position matches the model's rest hip world position — prevents the avatar
   from "jumping" to the animator's origin. Compute `delta = animFirstHipPos - restHipWorldPos` and
   subtract it from every `.position` track.
4. `new AnimationMixer(vrm.scene)`, `mixer.clipAction(clip).play()`.
5. Default idle clip ships as an asset: `assets/vrm/animations/idle_loop.vrma`.

> Emotion-specific body motions are namespaced in `constants/emotions.ts`
> (`EMOTION_SpineAnimationName_value`: happy→`celebrate`, sad→`sad`, …) for renderers that swap body
> clips per emotion (Live2D/Spine do; the VRM path currently drives emotion via **expressions**, not body
> clips — see §5.2). A standalone app may cross-fade emotion `.vrma` clips on the same mixer.

### 5.2 Channel 2 — Expression / Emotion (face)

Reference: `composables/vrm/expression.ts` (`useVRMEmote`).

State machine driving facial blendshapes with smooth blending:

- **Emotion catalog** (`emotionStates`): each emotion maps to a set of weighted expressions plus a
  `blendDuration`. Values are deliberately < 1.0 (0.7–0.8) to avoid an over-expressive face:
  - `happy` → `{happy:0.7, aa:0.2}`, blend 0.4s
  - `sad` → `{sad:0.7, oh:0.15}`, blend 0.4s
  - `angry` → `{angry:0.7, ee:0.3}`, blend 0.3s
  - `surprised` → `{surprised:0.8, oh:0.4}`, blend 0.15s
  - `neutral` → `{neutral:1.0}`, blend 0.6s
  - `think` → `{think:0.7}`, blend 0.5s
- **`setEmotion(name, intensity=1)`**: captures *current* values of all expressions as the lerp start
  (prevents snap-to-zero), sets targets to `value × clamp(intensity, 0..1)` for the emotion's expressions
  and `0` for all others.
- **`setEmotionWithResetAfter(name, ms, intensity)`**: applies, then auto-resets to `neutral` after `ms`
  (UI default is 3000 ms via `setExpression`).
- **`update(delta)`**: advances `transitionProgress += delta/blendDuration`, eases with
  `easeInOutCubic`, and `expressionManager.setValue(expr, lerp(start, target, eased))` for each tracked
  expression. Becomes idle once progress ≥ 1.
- Catalog is extensible at runtime (`addEmotionState` / `removeEmotionState`).

The public entry point on the renderer is `setExpression(name, intensity)` (exposed by `VRMModel.vue` →
`ThreeScene.vue`), which calls `setEmotionWithResetAfter(name, 3000, intensity)`.

### 5.3 Channel 3 — Blink

Reference: `useBlink` in `animation.ts`. Pure procedural:
- Random interval between blinks: `1–6 s`. Single blink duration `0.2 s`.
- During a blink, `blink` weight follows `sin(π · progress)` (0→1→0); reset to 0 and schedule next when done.
- Independent of emotion/lipsync; commits via `expressionManager.setValue('blink', …)`.

### 5.4 Channel 4 — Lip-sync (visemes from audio)

Reference: `composables/vrm/lip-sync.ts` (`useVRMLipSync`), plus `wlipsync` + a profile JSON
(`assets/lip-sync-profile.json`).

1. Create a `wlipsync` node bound to the `AudioContext` and the profile.
2. When a TTS `AudioBufferSourceNode` plays, connect it to the lipsync node (and to `destination` and an
   analyser). Disconnect prior source on change/unmount.
3. Per frame `update(vrm, delta)`:
   - Read node `volume` and per-phoneme `weights` for `A E I O U S`.
   - `amp = min(vol·0.9, 1)^0.7`; project `S`→`I`; map to VRM visemes `A→aa, E→ee, I→ih, O→oh, U→ou`.
   - **Winner+runner blend**: pick only the two highest visemes (mixing all five biases toward `aa`
     because of its large deformation). Cap winner at `0.7`, runner at `0.35`.
   - **Silence gating**: if `amp < 0.04` or top weight `< 0.05`, or idle > 160 ms, target all to 0.
   - **Attack/release smoothing**: exponential approach with `ATTACK=50`, `RELEASE=30`
     (`rate = 1 - exp(-k·delta)`); final weight scaled ×0.7 and floored to 0 below 0.01.
   - `expressionManager.setValue(viseme, weight)`.

> The audio source is the same buffer produced by the TTS pipeline (§6.3), so mouth motion is exactly
> synchronized to spoken output without phoneme timing metadata.

### 5.5 Channel 5 — Gaze / Look-at

Reference: `composables/eye-tracking.ts` (`useVRMEyeFocusFor`), `useIdleEyeSaccades` in `animation.ts`.

Three tracking modes (`TrackingMode = 'camera' | 'mouse' | 'none'`):
- **`camera`**: look-at target = camera position (avatar "makes eye contact" with viewer).
- **`mouse`**: normalize cursor to NDC against the canvas bounding box, raycast from camera, place the
  target ~8 units along the ray near-plane → world point the eyes follow.
- **`none`**: default target `(0, eyeHeight, -100)` (straight ahead).

**Idle saccades** (`useIdleEyeSaccades`): jitter the fixation target by `±0.25` on X/Y at random
intervals (`randomSaccadeInterval`, see `utils/eye-motions.ts`) to simulate natural micro-eye-movements;
`instantUpdate` snaps the look-at target when a new external focus arrives. A `VRMLookAt` target Object3D
is lazily created and `lerp`-ed toward the fixation point; `vrm.lookAt.update(delta)` applies it.

### 5.6 Channel 6 — Live Motion-Capture Pose

Reference: `packages/model-driver-mediapipe/src/three/{pose-to-vrm.ts,apply-pose-to-vrm.ts}` and
`src/types.ts`, `engine.ts`.

This is the most complex channel: webcam video → body landmarks → VRM bone rotations, applied through the
**external frame hook** (`setVrmFrameHook`, step 4 of §4).

**Stage A — Perception (`MocapEngine`/`MocapBackend`).**
A `FrameSource.getFrame()` supplies a `TexImageSource` (video frame). The MediaPipe backend runs
split tasks (`pose`, `hands`, `face`) at configurable Hz, emitting a `PerceptionState` with
`landmarks2d`, `worldLandmarks`, and quality (fps/latency/dropped). `maxPeople = 1`.

**Stage B — `poseToVrmTargets(pose, options)`** — landmarks → bone direction targets:
- Prefer `worldLandmarks`; gate each landmark by `visibility ≥ 0.5` (and optional `presence`). If
  visibility is missing, the landmark is rejected (no hallucinated motion).
- Build a torso basis from shoulders/hips: `up = shoulderCenter − hipCenter`,
  `right = rightShoulder − leftShoulder`, `forward = right × up` (sign-corrected and temporally stabilized
  against the previous frame to avoid 180° flips).
- Emit `VrmPoseTargets` — per-bone `{ dir, pole? }` for `hips, spine, chest, leftShoulder, rightShoulder,
  {left,right}{Upper,Lower}Arm, {left,right}{Upper,Lower}Leg`. Arm/leg **pole** vectors come from the
  elbow/knee bend plane (`cross(upper, lower)`). Legs require an ankle landmark to emit, reducing flips
  when the lower body is off-camera. Axis remap `{x,y,z} ∈ {±1}` adapts MediaPipe space to VRM space.

**Stage C — `createVrmPoseApplier().applyPoseTargetsToVrm(vrm, targets)`** — targets → bone quaternions:
- On first use, cache each bone's **rest direction** (bone→child vector in bone-local space) and, for
  pole bones, a **rest pole** (torso: world-forward in local; limbs: `cross(boneVec, childVec)`).
- Per bone: normalize target `dir`; **reject near-180° flips** when
  `prevTargetDir · newTargetDir < minDotBeforeReject (−0.2)`.
  - With pole: build orthonormal rest/target bases (`makeBasis(dir, y, pole)`), compute world rotation
    `R = targetBasis · restBasis⁻¹`, convert to local via parent world quaternion.
  - Without pole: `deltaQ = setFromUnitVectors(currentDirWorld, targetDirWorld)`; compose with bone world
    quaternion → local.
- Apply via `bone.quaternion.slerp(newLocal, alpha)` (`alpha = 0.35` default smoothing; `alpha ≥ 1` = snap).
- Pole flips likewise rejected via `minPoleDotBeforeReject (−0.2)`.

**Integration.** The app registers `setVrmFrameHook((vrm, delta) => applier.applyPoseTargetsToVrm(vrm, latestTargets))`.
Because this runs **before** `humanoid.update()` (§4 step 4→5), the mocap rotations are flushed into the raw
skeleton each frame and physically blend with the idle animation already on the mixer.

### 5.7 Channel 7 — Transform, Camera & Environment

- **Model transform**: `group.position` ← `modelOffset (x,y,z)`; `group.rotation.y` ← `modelRotationY`°.
- **Camera**: orbit controls + a Pinia/store-backed `cameraPosition`/`cameraDistance`/`cameraFOV`,
  seeded by the `SceneBootstrap` (§3.3). Camera mode also feeds gaze (§5.5).
- **Lighting/IBL**: hemisphere + ambient + directional lights, or an HDRI skybox producing spherical
  harmonics (`irrSH`) injected into MToon/shader materials (`composables/shader/ibl.ts`). Post-processing:
  hue/saturation pass. Not required for control, but part of faithful reproduction.

---

## 6. AI-Driven Control Pipeline

This section specifies **how an LLM + speech stack drives channels 2, 4, and 5**, and how the body/pose
channels can be AI-extended. References: `Stage.vue`, `composables/queues.ts`, `constants/emotions.ts`,
`constants/prompts/system-v2.ts`, `stores/llm-streaming-control.ts`.

### 6.1 Architecture overview

```
LLM stream ──► token splitter ──► { literal text , special tokens }
                                        │              │
                          literal ──────┘              └──► special: <|ACT|> / <|DELAY|> / plugin CALL
                                  │                                   │
                                  ▼                                   ▼
                         TTS session (text)                 streamingControl.dispatchWith()
                                  │                                   │
                                  ▼                          ┌────────┴───────────┐
                          audio buffer ──► playback          │  act → emotion     │  delay → sleep
                                  │                           ▼                    ▼
                                  ├──► wLipSync (channel 4)   emotionsQueue ──► setExpression() (channel 2)
                                  └──► analyser (caption/UI)        (per-renderer dispatch: VRM/Live2D/Spine)
```

### 6.2 Instructing the model (prompt contract)

`constants/prompts/system-v2.ts` injects a system message listing the available emotions
(from `EMOTION_VALUES`), each described by its motion name, so the model learns to emit emotion control
markers inline with its reply. The model interleaves natural language with **special tokens**:
- `<\|ACT\|>{ "emotion": "happy" }\|>` (or `{ "emotion": { "name": "happy", "intensity": 0.8 } }`)
- `<\|DELAY:1.5\|>` — pause speech/animation for N seconds.
- Plugin/tool `CALL` tokens (routed by `streamingControl`).

### 6.3 Stream processing & dispatch

1. **Token hooks** (`useChatOrchestratorStore` in `Stage.vue`): `onTokenLiteral` appends text to the
   current TTS session; `onTokenSpecial` appends special tokens; `onStreamEnd`/`onAssistantResponseEnd`
   finalize the session.
2. **TTS session** (`createStageTtsSession`): either a segmenter→REST adapter (non-streaming providers) or
   a bidirectional WebSocket adapter (streaming provider). It segments text, synthesizes audio, and emits
   `onSpecial` for any inline special token reaching playback.
3. **Special-token routing** (`streamingControl.dispatchWith` / `onSignal`): a special token becomes a
   typed signal:
   - `type: 'act'` → `normalizeActPayload` → if `emotion`, map to an `EmotionPayload` and
     `emotionsQueue.enqueue(...)`.
   - `type: 'delay'` → `await sleep(seconds·1000)` (paces emotion/speech with the narrative).
4. **Emotion parsing** (`composables/queues.ts → useEmotionsMessageQueue`): regex
   `/<\|ACT\s*(?::\s*)?(\{[\s\S]*\})\|>/i` extracts the JSON, normalizes the emotion name against the
   `Emotion` enum, clamps intensity to `0..1`, and enqueues.
5. **Emotion → model** (`emotionsQueue` handler in `Stage.vue`): dispatch per active renderer:
   - **VRM**: `EMOTION_VRMExpressionName_value[name]` → `vrmViewerRef.setExpression(expr, intensity)` (§5.2).
   - **Live2D**: set `currentMotion` to `EMOTION_EmotionMotionName_value[name]` (body/motion group).
   - **Spine**: `spineSceneRef.setEmotion(name, intensity)`.

   The queue serializes emotions so they don't stomp each other; each VRM expression auto-resets to
   neutral after 3 s.
6. **Lip-sync coupling**: the synthesized `AudioBufferSourceNode` is handed to the VRM renderer as
   `currentAudioSource`; channel 4 (§5.4) consumes it directly. No extra wiring — mouth follows audio.

### 6.4 AI-driving the remaining channels (extension surface)

- **Gaze**: an AI/agent can write the look-at target (`lookAtUpdate(target)` exposed by `VRMModel.vue`)
  to make the avatar glance at a subject of attention, or switch `TrackingMode` to `camera` during
  direct address.
- **Body pose / gesture**: two routes — (a) AI selects/cross-fades emotion `.vrma` clips on the mixer
  (clip names already enumerated in `EMOTION_SpineAnimationName_value`); (b) the **mocap frame hook**
  (§5.6) is generic — any source producing `VrmPoseTargets` (e.g. an AI motion model, not just MediaPipe)
  can drive the body through `applyPoseTargetsToVrm`. This is the intended seam for AI-generated motion.
- **Emotion intensity** can be modulated continuously (the model may emit `intensity`), enabling
  expression strength tied to sentiment.

---

## 7. Public Control API (what a host app calls)

Exposed by `ThreeScene.vue` (forwarded to `VRMModel.vue`). For a standalone app, mirror these as methods
on a `VrmStage` class:

| Method | Effect | Channel |
|--------|--------|---------|
| `setExpression(name, intensity=1)` | Trigger an emotion (auto-resets after 3 s) | 2 |
| `setVrmFrameHook(fn?)` | Install/replace the per-frame external pose hook | 6 |
| `lookAtUpdate(target: {x,y,z})` | Instantly aim gaze | 5 |
| `scene` / `camera()` / `renderer()` | Accessors for the three.js objects | 7 |
| `canvasElement()` | The `<canvas>` DOM node | — |
| `captureFrame()` | Render + `toBlob()` snapshot (optionally composited over a background) | — |
| `readRenderTargetRegionAtClientPoint(x,y,r)` | Read pixels (hit-testing) | — |
| props: `modelSrc`, `idleAnimation`, `paused`, `cursorPosition`, `currentAudioSource` | Load/swap model, idle clip, pause loop, feed cursor + TTS audio | 1,4,5,7 |

Lifecycle events to surface: `loadingProgress`, `loadStart(reason)`, `sceneBootstrap(payload)`,
`loaded(src)`, `error(e)`.

---

## 8. Reproduction Blueprint (standalone app)

Minimal module decomposition to rebuild this without the monorepo:

1. **`VrmLoader`** — singleton `GLTFLoader` + VRM/VRMA plugins; `loadVrm(url)` (§3).
2. **`VrmStage`** — owns `WebGLRenderer`, `Scene`, `PerspectiveCamera`, orbit controls, lights/IBL,
   and the **manual RAF loop with the exact update order of §4**. Holds the active `{ vrm, group, mixer }`.
3. **`EmoteController`** — port of `useVRMEmote` (§5.2): `setExpression`, `update(delta)`.
4. **`Blink`**, **`IdleSaccades`** — procedural (§5.3/§5.5).
5. **`LipSync`** — `wlipsync` node + viseme mapping/smoothing (§5.4); fed by the TTS audio source.
6. **`GazeController`** — tracking-mode → look-at target (§5.5).
7. **`MocapDriver`** (optional) — MediaPipe engine → `poseToVrmTargets` → `createVrmPoseApplier`; wired via
   `setVrmFrameHook` (§5.6).
8. **`AiOrchestrator`** — LLM stream → token splitter → TTS session (audio) + special-token parser →
   emotion queue → `VrmStage.setExpression`; couples TTS audio into `LipSync` (§6). Prompt must enumerate
   the emotion vocabulary (§6.2).

**Critical correctness checklist** (the non-obvious things that break reproductions):
- Do **not** call `vrm.update()`; run the §4 subsystem order manually.
- Call `expressionManager.update()` **after** blink/emote/lipsync `setValue`s.
- Run `humanoid.update()` **after** the external pose hook, **before** look-at/expression commit.
- Run `springBoneManager.update()` **last**.
- Run `material.update(delta)` for MToon every frame (alphaTest/cutout depends on it).
- `removeUnnecessaryVertices` + `combineSkeletons` at load (huge perf win).
- Disable `frustumCulled` on all avatar objects.
- Re-anchor `.vrma` hips `.position` track to rest pose to avoid teleport.
- Normalize avatar facing to `-Z` via the look-at `faceFront` quaternion at load.
- Guard concurrent model loads with a sequence id and dispose orphaned partial loads.
- Resume `AudioContext` on first user gesture before lipsync/TTS.

---

## 9. Source File Index

| Area | File |
|------|------|
| Model load + facing/bbox | `packages/stage-ui-three/src/composables/vrm/core.ts` |
| Loader + MToon plugin | `packages/stage-ui-three/src/composables/vrm/loader.ts` |
| Frame loop + lifecycle + public API | `packages/stage-ui-three/src/components/Model/VRMModel.vue` |
| Scene root, camera, lights, expose | `packages/stage-ui-three/src/components/ThreeScene.vue` |
| Animation clip + re-anchor + blink + saccades | `packages/stage-ui-three/src/composables/vrm/animation.ts` |
| Emotion blendshape state machine | `packages/stage-ui-three/src/composables/vrm/expression.ts` |
| Lip-sync | `packages/stage-ui-three/src/composables/vrm/lip-sync.ts` |
| Gaze mapping | `packages/stage-ui-three/src/composables/eye-tracking.ts` |
| Instance cache | `packages/stage-ui-three/src/components/Model/vrm-instance-cache.ts` |
| Model store (transform/camera/env) | `packages/stage-ui-three/src/stores/model-store.ts` |
| Mocap: landmarks → targets | `packages/model-driver-mediapipe/src/three/pose-to-vrm.ts` |
| Mocap: targets → bone quaternions | `packages/model-driver-mediapipe/src/three/apply-pose-to-vrm.ts` |
| Mocap types/engine | `packages/model-driver-mediapipe/src/types.ts`, `engine.ts` |
| AI orchestration (tokens→emotion→model, TTS, lipsync wiring) | `packages/stage-ui/src/components/scenes/Stage.vue` |
| Emotion/delay token parsing | `packages/stage-ui/src/composables/queues.ts` |
| Emotion vocabulary + mappings | `packages/stage-ui/src/constants/emotions.ts` |
| System prompt (emotion contract) | `packages/stage-ui/src/constants/prompts/system-v2.ts` |
| Streaming/special-token control | `packages/stage-ui/src/stores/llm-streaming-control.ts` |
