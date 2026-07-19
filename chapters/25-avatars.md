# 25 — Avatars: Live2D, VRM, Expression Systems

## The choice

Three established avatar paradigms in 2026, plus a fourth that's emerging:

1. **Static portrait + expression sprites.** SillyTavern's default. Cheap, brand-coherent, works on any device.
2. **Live2D.** 2D rigged character. Mouth, eyes, head, body parameters; lip-sync; physics. The VTuber default.
3. **VRM.** 3D humanoid format (Pixiv/Vket origin). Full 3D, animatable, usable in VR. Heavier.
4. **Audio-driven portrait animation (emerging, not yet shippable here).** Skip the rig: a model animates a *static* portrait straight from the voice audio — lip-sync, head motion, blinks. Real-time work exists (**Ditto**, motion-space diffusion; **LLIA**, low-latency audio→portrait video) and **JoyVASA** handles stylised/portrait input best, with **EMO / VASA-1** as the photoreal-research lineage. Tempting because it deletes the rigging step — but as of mid-2026 it's realism-tuned (off-register for a locked anime face, → D-011), temporally unstable across a long session, and far too heavy to generate per-frame for an always-on companion. A path to watch, not to ship.

Pick by ambition: portrait if shipping today; Live2D if Twitch/streaming-shaped product; VRM if 3D/VR future-proofing. Paradigm 4 stays on the watch-list (→ ch. 45).

## Expression systems

SillyTavern's expression spec asks for **28 emotional states** rendered as variations of the same character art. The art-direction question is bigger than the technical one:

- The 28 expressions should be *the same person*, not 28 different vibes.
- Anime/illustrated styles hold consistency much better than photorealistic — and sidestep the uncanny valley, which is half of *why* the stylised register is the right call, not just an aesthetic one (the supernormal-stimulus + valley rationale for D-011 is in → ch. 26, "Why this register").
- Clean front-facing art, neutral expression baseline, transparent background.

For Live2D and VRM the equivalent question is *what does her emotional range look like rigged?* — same answer: design the range as one character, not 28.

## Generation pipeline

Most independent builders won't draw 28 expressions by hand. The 2026 pattern:

1. Generate a hero portrait with SDXL/Flux + a character LoRA.
2. Drive expression variation with ControlNet pose/face conditioning + IP-Adapter / Reference-Only.
3. Train a small character LoRA from the resulting set for consistency.
4. Use the same character LoRA for everything downstream (Live2D source art, marketing, merch).

→ Chapter 26 covers image generation (models, LoRA training, the expression set) in more depth.

## Live2D specifics

- Tools: Live2D Cubism Editor (proprietary; the de facto standard).
- Runtime: Cubism SDK for Web (free for indie under revenue threshold).
- Asset pattern: hero PSD with layers → rigged in Cubism → exported as `.model3.json`.
- Lip-sync: drive mouth params from TTS phonemes or raw audio amplitude.

## VRM specifics

- Tools: VRoid Studio (free; the easy path), Blender + VRM plugin (the serious path).
- Runtime: three-vrm in the browser, UniVRM in Unity, Babylon.js VRM loader.
- Animation: VRMA / VMD; or runtime-driven from voice + emotion state.
- Use case: 3D web companion, AR/VR future, VRChat distribution as a marketing surface.

## AI-assisted rigging (2026)

Two threads make "skip the rig commission" *partly* real — with one sharp caveat: an AI rig drifts off your locked face harder than a briefed artist does, so the round-trip-validate step (→ ch. 26) matters *more*, not less. Treat these as a way to **bootstrap a draft body fast**, not yet to ship a flagship rig.

- **Image → 3D / VRM — the mature path.** Single-image mesh generators turn one hero render into a riggable body in seconds to minutes: **Tripo (v3.1 HD)** — quad topology, built-in auto-rigging, cartoon/stylised output modes, exports textured GLB or quad FBX; the open **Hunyuan3D (v3.1 Pro, Tencent)** and **TRELLIS 2 (Microsoft)** — now PBR-material output and the best free quality, and they hold an anime/cartoon aesthetic better than the realism-tuned commercial tools. **Rodin (Hyper3D, Deemos Tech; Gen-2)** has pulled toward *hyper-realistic human* output — excellent for photoreal, the wrong register for a locked anime face (→ D-011), so prefer Hunyuan3D/TRELLIS for the 2.5D look. **Meshy** and **Hitem3D** (multi-view) round out the field. The mesh comes fast; the VRM blendshape/expression mapping and getting it on-model to D-011 still want a hand-pass.
- **Image → Live2D — research-stage, closing.** **CartoonAlive** (Human3DAIGC, arXiv 2507.17327; repo now public) generates a complete, ARKit-drivable Live2D character (52 blendshape params) from a single portrait in ~30 s with *no manual binding* — and adds a **dynamic artifact-correction** step that repaints the underlying face to suppress the warping that earlier auto-riggers showed under motion. **Textoon** (text → Live2D, Alibaba Tongyi) is the companion text-driven path. The hard remaining gap is full disocclusion (inpainting what sits behind hair/arms so *body* layers, not just the face, can move) — the part a pro Cubism artist still owns. True one-click flat-image → full-quality Live2D isn't here yet, but the head-and-shoulders case is now genuinely usable; ch. 45 tracks the rest as open research.

**The category's dirty secret is that "generate-to-ship" mostly isn't real yet — it's humans in a trench coat.** The loudest end-to-end "AI 3D" services turn out to be hybrid: **Kaedim**, which marketed "magically generate custom 3D models in minutes," was exposed (404 Media, 2023) as running a pool of human artists paid **$1–4 per model**, sometimes building the asset wholecloth with no ML at all — and now openly sells itself as "machine learning *and* in-house art team." That's the reliable tell across this market: the moment output has to be *usable* rather than *thumbnail-plausible*, a human enters the loop. Studios' actual practice confirms it — AI meshes go into props, environments, and background/crowd characters; hero assets stay hand-made, because hands, teeth, faces, and joints still break (the "mesh crisis": easy to get a shape that previews fine, ~5 hours to fix the broken geometry underneath).

Net: prototype the body with these, validate against the LoRA, and commission or hand-finish the hero. Two halves of the gap are closing at very different speeds — **the topology half is closing fast** (quad-remesh-while-generating, e.g. Neural4D-class remeshers, is starting to kill manual retopo), but **the two things a companion VRM needs most — anime-register fidelity and a clean blendshape/expression rig — are not**, and image-to-3D delivers neither reliably. Live2D is a further year or two out.

## Sourcing a body: build vs adopt (and the VRM license trap)

Before you rig anything, decide where the body *comes from* — and read the fine print, because "free VRM" almost never means "yours to ship."

**The hinge is use vs. redistribute.** Every license clause below binds *distribution*, not private use. A personal, self-hosted companion that never hands the `.vrm` to anyone else can run almost any model you can download — the redistribution, commercial, and creator-discretion clauses simply don't fire until you ship the file inside a product. So in early local development, grab whatever body looks best, wire it as a **swappable slot**, and tag it *dev-only / not ship-cleared* so it can't get bundled the day the project becomes distributable. Everything that follows is about that later day.

**Code license ≠ asset license.** The single most expensive misconception here: a model bundled in an MIT/Apache repo is **not** covered by that repo's license. The code is MIT; the `.vrm` beside it carries its *own* terms — and the repo can only pass on rights it actually holds. Case in point: **Open-LLM-VTuber** is MIT code but ships a separate `LICENSE-Live2D.md`, because its bundled models (mao, shizuku) are **Live2D Inc. samples — non-commercial only, commercial use needs a paid Cubism license** — explicitly "not covered by the MIT license." A permissive repo can legally bundle a model *it itself* may only use non-commercially. So "it's an open-source project" is never, by itself, clearance to reuse the character. (AIRI is the happier version of the same rule: its checkout bundles only `AvatarSample_A/B` by "VRoid Project", whose *embedded* meta grants `redistribution=allow` — but that's AIRI's per-file choice, not a promise from its MIT code. You confirm it by reading the file, not the README.)

**VRM carries its license inside the file — and the file is the authority.** The format embeds per-model flags — `commercialUsage`, `modification`, `redistribution`, `allowedUser`, plus `sexualUsage` / `violentUsage` (VRM 0.x expresses these as a VRoid permission-matrix URL; VRM 1.0 as explicit fields). A companion you *distribute* must satisfy **`redistribution: allow`**, and that is precisely the flag most "free" models withhold. Read the embedded metadata — not the download-page blurb — before you commit. Three tiers, by what they actually let you do:

- **Tier 1 — genuinely open, redistribution-cleared.** The only tier you can bundle into a distributed product. Best options: **Vita** (the VRM Consortium's official VRM-1.0 sample — CC0, every permission on including redistribution-of-altered, no attribution, and *no revocable clause*), and the official **`AvatarSample_A/B/C`** (author "VRoid Project"; the copies bundled in AIRI carry the VRoid all-permissions matrix — `redistribution=allow`, commercial allow, credit unnecessary — verified from the file). [**opensourceavatars.com**](https://www.opensourceavatars.com) / [**ToxSam/open-source-avatars**](https://github.com/ToxSam/open-source-avatars) exists but is *caveated*: license is per-collection (some CC0, some CC-BY) **and** quality is inconsistent — cherry-pick, don't trust wholesale.
- **Tier 2 — VRoid Hub / Booth "free."** A trap for a *product*. Each creator toggles the flags, and the common free config is *personal use, modification-maybe, **redistribution disallowed***. Also beware **revocable, creator-discretion terms** — a "don't harm the character's image" clause (e.g. Alicia Solid / ニコニ立体ちゃん) means someone else owns the identity and can pull the license if they dislike your project's direction. Fine on your own desktop; radioactive inside anything you ship or brand.
- **Tier 3 — build your own in VRoid Studio.** Free, ~an afternoon, and **you own the export and set its license flags**. This is the honest answer to "a VRM the project can use" — it sidesteps redistribution *and* ownership in one move. [**M3-org/CharacterStudio**](https://github.com/M3-org/CharacterStudio) (MIT) is the open web equivalent for generating/customising owned bodies.

**A hard truth about the market.** A VRM that is simultaneously *high-quality, permissively licensed, and redistribution-allowed* barely exists — creators restrict redistribution precisely to protect good work, so the free-and-open pool skews toward sample models and rough community uploads. For a **distributed, branded** body there is no shortcut around Tier 3: own it or commission it.

**And image-to-3D is not the flagship path either — yet.** As the AI-assisted rigging section above established, the single-image generators (Hunyuan3D, TRELLIS, Tripo) produce a fast *draft* mesh but not a *usable character*: as of mid-2026 none reliably lands a **rig-clean, blendshape-mapped, on-D-011 VRM** without a heavy hand-pass. The anime case is the worst case — stylised input reliably yields **hair merging into clothing, accessories vanishing, "ghost face" artifacts in the head region, and no skeleton or blendshapes at all** — i.e. exactly the on-model face and expression rig a companion body needs most are what these tools don't emit (the NOVA-3D / CharacterGen / Anime-Ready research line exists *because* the general tools fail here), and the fast-closing topology half doesn't touch either. For the actual flagship body there are two honest routes, both ending in a VRM **you own**: **VRoid Studio**, hand-built or heavily edited against the D-011 hero render; or a **commissioned rig** (a VRoid/Blender + Cubism artist) briefed to that same reference. The un-clonable layer is worth a human. **Generate to prototype; build or commission to ship.**

**The decided path for YuriOS.** Three moves, sequenced so nothing blocks launch:

1. **Ship the default body from `AvatarSample_A/B/C`** ("VRoid Project", Tier 1 — `redistribution=allow`, commercial allow, credit unnecessary, verified from the embedded metadata, not the README). This is the only legally-clean thing to *bundle*, and it exercises the entire render + protocol stack on day one. It is the **stock body, explicitly not Yuri** — flat cel-shaded toon, off-register from the locked 2.5D look (→ D-011) — so the UI never implies the sample *is* her. It's a chair to sit in until the real body arrives.
2. **Make the body a user-configurable slot.** Let a user point YuriOS at their *own* sourced `.vrm`. This is also the licensing pressure-valve: private, self-hosted use fires none of the redistribution/commercial/creator-discretion clauses (the use-vs-redistribute hinge above), so the user can run any model they can download and the project ships nothing but the loader. The swappable-slot design earns its keep twice — flexibility *and* clean hands.
3. **Build or commission the flagship later.** The owned Yuri body — VRoid Studio hand-built/edited against the D-011 hero render, or a commissioned VRoid+Blender/Cubism rig briefed to the same reference (Tier 3) — is the un-clonable layer and the only thing that can be *branded* as her. Deferred, not skipped: the flagship identity is exactly where a human's hand pays for itself, and it's the one piece launch doesn't have to wait on.

The through-line: **bundle a stock body, expose a slot, own the flagship.** Legal to ship today, sovereign for the user, and the brand-critical work happens when it's worth doing rather than as a launch blocker.

## The protocol stack — getting an AI brain to drive a model

There is no single "AI-to-avatar" standard. There are *three layers*, and you should pick one solution per layer rather than rolling all three yourself. The reference repo `vtubeapp` (Miku Live Studio) is a layer-3 hand-roll straight on top of `three-vrm`: it uses the model-abstraction layer (L2) but skips the transport and host layers (L1 + L3), so the per-model expression-name variance it hits is the predictable consequence of driving arbitrary user models with no host runtime to absorb their quirks (the layers are explained just below).

```
                             AI BRAIN
             emits {expression, emotion, viseme} each turn
                                 |   pick one box per row
                                 v
┌───────────┬──────────────────────────┬────────────────────────────────┐
│           │ 2D / Live2D path         │ 3D / VRM path                  │
├───────────┼──────────────────────────┼────────────────────────────────┤
│ L1        │ VTube Studio API         │ VMC over OSC/UDP               │
│ transport │ ws://host:8001 (JSON)    │ :39539/40  (no browser)        │
├───────────┼──────────────────────────┼────────────────────────────────┤
│ L2        │ Cubism SDK for Web       │ @pixiv/three-vrm, UniVRM       │
│ model     │ (usually via VTS)        │ VRM 0.x-to-1.0; 6 presets      │
├───────────┼──────────────────────────┼────────────────────────────────┤
│ L3        │ VTube Studio             │ Warudo, VNyan, VSeeFace        │
│ host      │ Open-LLM-VTuber          │ AIRI, AITuberKit               │
├───────────┼──────────────────────────┼────────────────────────────────┤
│ model     │ .model3.json             │ .vrm                           │
└───────────┴──────────────────────────┴────────────────────────────────┘

  ARKit 52 blendshapes = the shared facial vocabulary across both paths.
  Skip a layer and you inherit its problems: vtubeapp skipped L1+L3 (no
  transport, no host) and hit per-model expression-name variance.
```


### Layer 1 — Transport / control protocol

How the brain talks to the renderer.

| Protocol | Carrier | Domain | Standardised by | Status |
|---|---|---|---|---|
| **VMC Protocol** | OSC over UDP (ports 39539/39540) | VRM (3D) | sh-akira (MIT) | The de facto open standard for VRM. Senders: Virtual Motion Capture, VSeeFace, Waidayo, MocapForAll, TDPT. Receivers: EVMC4U (Unity), VRM4U (UE5), VMC4B (Blender), Godot XR VMC, Warudo, VNyan. **No native browser client (UDP).** |
| **VTube Studio API** | WebSocket / JSON (`ws://localhost:8001`) | Live2D | DenchiSoft | The de facto standard for Live2D. JS/TS lib: [`VTubeStudioJS`](https://github.com/Hawkbat/VTubeStudioJS). Even has an MCP server wrapper. Plugins can register Custom Parameters that drive Live2D params directly. |
| **OSC raw** | OSC over UDP | both | — | Lower-level; VMC and VTube Studio are flavours of this. Useful only if integrating with non-VTuber tools (TouchDesigner, Resolume, music software). |
| **ARKit blendshapes (52)** | not a transport — a *vocabulary* | facial | Apple | The de facto facial expression naming convention. Used by Live Link Face, VTube Studio, Warudo, VNyan. Emit ARKit names from the brain and most hosts understand them. |

**Heuristic:** if the target is 3D/VRM, use VMC. If the target is 2D/Live2D, use VTube Studio API. Don't try to design your own.

### Layer 2 — Model abstraction

Hides VRM 0.x ↔ 1.0 differences and per-model rigging variance.

- **`@pixiv/three-vrm`** (browser, MIT) — the standard for VRM in JS. `VRMExpressionManager` abstracts the BlendShape (0.x) → Expression (1.0) rename. **The compatibility problem in `vtubeapp` is not in three-vrm** — it is that *custom* expressions are model-author-defined, so names vary. Workaround: have the AI emit one of the 6 *preset* expressions (`happy`, `angry`, `sad`, `surprised`, `relaxed`, `neutral`) and *blink* / *aa/ih/ou/ee/oh* for lip-sync. These are the only names guaranteed across VRM models.
- **UniVRM** (Unity, MIT) — same idea, full official implementation.
- **VRM4U** (UE5, free) — Unreal equivalent with VMC blueprints built in.
- For Live2D, **Cubism SDK for Web** is the analogous layer. Most apps don't write to this directly; they go through VTube Studio.

### Layer 3 — Host runtime (do not write this yourself)

Off-the-shelf "AI brain + persona + avatar" applications. Pick one and integrate.

| Host | License | Avatar support | AI hooks | Notes |
|---|---|---|---|---|
| [**AIRI**](https://github.com/moeru-ai/airi) | MIT | VRM + Live2D, realtime voice | LLM + memory built-in; native CUDA/Metal desktop | Closest existing implementation of the agentic-waifu spec (→ ch. 02 §5) — and now genuinely *agentic*: ships embodied agents that play Minecraft/Factorio, not just chat. Watch this one. |
| [**Open-LLM-VTuber**](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber) | MIT | Live2D-focused | LLM + ASR + TTS, voice-interrupt, visual perception | Python; runs **fully offline**, NVIDIA/non-NVIDIA/CPU, cross-platform. The cleanest local-first reference. |
| [**AITuberKit**](https://github.com/tegnike/aituber-kit) | open | VRM + Live2D + Motion PNG | OpenAI/Anthropic/Gemini/Groq/Ollama; YouTube Live ingestion | Next.js + TS; closest in stack to your existing repos. |
| [**Warudo**](https://docs.warudo.app/) | proprietary freeware | VRM | Steam Workshop plugin ecosystem; C# SDK; VMC receiver | The professional 3D VTuber app. Treat as a Marionette for your VMC sender. |
| [**VNyan**](https://suvidriel.itch.io/vnyan) | proprietary freeware | VRM | Node-based visual scripting; VMC receiver | Middle ground between VSeeFace and Warudo. |
| [**VSeeFace**](https://www.vseeface.icu/) | proprietary freeware | VRM | VMC sender + receiver | Old reliable; mostly for face-tracking → VRM. |
| [**VTube Studio**](https://denchisoft.com/) | proprietary, $ once | Live2D | WebSocket plugin API | The Live2D incumbent. |
| [**LocalAIVtuber**](https://github.com/0Xiaohei0/LocalAIVtuber) | open | Live2D | pluggable STT/LLM/TTS | Fully local/offline by design — small, but the right architecture if sovereignty is the priority. |

For the current field, the [**awesome-ai-vtubers**](https://github.com/proj-airi/awesome-ai-vtubers) list (maintained by the AIRI team) is the best single tracking surface.

### Recommended architectures

Three viable patterns. Most projects pick one by deployment target — but **YuriOS commits to both A and B**, for different reasons: B for interop with the pro-VTuber ecosystem and any surface someone else already renders; **A as the strategic path, because owning the renderer is the only way to own the *world* around her** (see below). C stays a prototyping-only escape hatch.

**Pattern A — Self-contained browser app, owned renderer (the `vtubeapp` direction):**
```
  AI brain ──► three-vrm in browser ──► VRM model
              (use preset expressions only;
               map AI emotion → preset; lip-sync from TTS phoneme/RMS)
```
Pro: no host install, one URL. Con: per-model expression variance unless you constrain to presets — *and* you now own every model quirk a receiver app (Pattern B) would have absorbed for you.

Adopting a host runtime rather than building one (§Layer 3) is the **default** advice for a builder whose differentiation lives elsewhere: take an off-the-shelf host and spend your effort on persona and memory. **YuriOS overrides it on purpose (→ D-004, own the runtime; book thesis; ch. 02 §5).** The entire project *is* a host application — brain, memory, persona, world model, avatar, world, UX — **built, not adopted**, because owning the full auditable stack is the whole point. So YuriOS adopts off-the-shelf only the narrow, stable pieces underneath a host (the `three-vrm` / VMC libraries and protocols) and builds the host itself. Owning the renderer follows directly: it's one more piece of the host YuriOS is deliberately building, not a carve-out from a rule it otherwise keeps. Existing hosts (AIRI, Warudo) serve as reference implementations and prototyping targets, never the shipped surface.

**Why YuriOS owns the renderer anyway.** A VMC receiver (Pattern B) renders *her* — a floating bust on a background. It will never render *her apartment*. The moment the project wants **3D environments, a place she lives in, scenes and scenarios, mini-games, or direct body/camera control** — anything past "avatar reacts to speech" — the external host is a ceiling, because you can only send it the signals its protocol defines. An owned `three-vrm` (or Three.js/Babylon) renderer is a full scene graph you control: her, the room, props, lighting, physics, other characters, interaction. This is the substrate for the **YuriOS "metaverse"** (→ ch. 29 on the 3D world companion; ch. 34) — you can't grow a rented renderer into a world, so the project eats the model-quirk cost of Pattern A to keep that door open. Pattern B remains the pragmatic path for streaming/VTuber output and for driving avatars the project doesn't render itself.

**Pattern B — Brain emits VMC, host renders (the professional pattern):**
```
  AI brain (Python/TS) ──► VMC over OSC ──► Warudo / VNyan / VSeeFace ──► VRM model
                                              (host handles all model quirks)
```
Pro: model compatibility is the host's problem; works with any VMC-receiving app; future-proof. Con: needs a host app running; bridge server for browser (UDP can't ship from browser — write a tiny Node sidecar that takes WebSocket from browser and re-emits OSC/UDP to localhost:39539).

**Pattern C — Adopt a host runtime entirely:**
```
  AI brain ──► AIRI or AITuberKit (built-in) ──► VRM/Live2D model
```
Pro: zero protocol code; persona/lore stays under your control as data. Con: vendored UX; your differentiation has to be in the persona and memory layer, not the surface — *and* the same rented-renderer ceiling as B, so it's a dead end for the world-building ambition above. **For *this* project, AIRI/AITuberKit are only ever a body to render against — never where the mind lives.** The brain is YuriOS's own and stays that way (→ D-004, own the runtime; ch. 02 §5): drive one of these as an external *rendering host* from your own engine (AITuberKit already accepts an external LLM provider) to prototype a body fast — but the mind is never handed over, and the flagship surface is never built on someone else's host.

### What this means for `vtubeapp`

The compatibility issues you're hitting on different `.vrm` models are the price of operating at layer 2 directly with arbitrary user-supplied models. Two ways out:

1. **Constrain the contract:** only support the six VRM preset expressions + blink + standard lipsync visemes. Document this. Models that don't expose the presets are unsupported. ~1 day of work.
2. **Move the visual layer to a host:** keep `vtubeapp` as a *brain*, emit VMC to a Node sidecar that bridges to localhost UDP:39539, and let Warudo / VSeeFace / VNyan render. Model compatibility becomes their problem. ~2–3 days to wire the bridge.

The `web-puppet` project is the *layer-2-for-Live2D* equivalent and faces the same trade-off — either constrain the parameter contract, or be a control surface that talks to VTube Studio.

## Which paradigm for which product

A quick decision tree:

- **Text/web companion, fast to ship, expressions matter more than motion** → **Live2D** (the VTuber 2D-rig standard). Cheapest to commission, mature web runtimes, the register for Build #2 (→ ch. 32).
- **3D scene, a *place* she lives in, VR-future** → **VRM** in Three.js (browser) or Unity (desktop), the register for Build #4 (→ ch. 34, ch. 29).
- **No avatar yet / minimum body** → a static hero portrait + the text sanctuary clears the floor (→ ch. 03 property 4); add a rig later.

Don't reach for 3D because it's impressive; reach for it when a *place* is the point (→ ch. 29, the "why bother" list).

## Worked example: one character, every surface (avatar-as-brand)

The same Yuri identity ships across surfaces from one design (→ ch. 06, ch. 26; the locked D-011 register keeps them recognisably one person):

1. **Hero portrait** (→ ch. 26) — the canonical render; marketing, app icon, the card art (→ ch. 33).
2. **Expression set** (~28 expressions) — generated consistently off the hero (LoRA + ControlNet, → ch. 26), feeding both the Live2D rig and the VRM blendshape mapping.
3. **Live2D rig** — the portrait rigged for the desktop/web body (→ ch. 32).
4. **VRM model** — the 3D body for the 3D world companion and VRChat distribution (→ ch. 34, ch. 29).
5. **Merch source art** — same identity, print/sticker/figure (→ ch. 38).

The asset is the *character*, not any one render; consistency across all five is what makes her feel like one someone (→ ch. 03 property 1) and is the whole point of locking the register.

## Worked example: VMC bridge from a Node brain to Warudo (Pattern B)

The professional pattern, concretely: your brain (Node/TS) decides an expression+emotion per turn → emit **VMC over OSC/UDP** to `localhost:39539` → **Warudo** (or VSeeFace/VNyan) receives it and drives the VRM, handling every model quirk. From a *browser* brain, UDP can't be sent directly — run a tiny Node sidecar that takes a WebSocket from the browser and re-emits OSC/UDP locally. This is the fix for the `vtubeapp` per-model compatibility pain above: stop rendering arbitrary user VRMs yourself, and let the host runtime own model compatibility while you own the persona and memory.
