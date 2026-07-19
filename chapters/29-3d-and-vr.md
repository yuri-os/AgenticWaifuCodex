# 29 — 3D Worlds, Games, and VR

## Why bother

A 3D companion is more work than a 2D one and reaches a smaller audience. Why do it anyway:

- **Differentiation.** Few commercial products have credible 3D embodiment.
- **A game becomes possible.** A 3D body and a scene are also the raw material for *a game built on YuriOS* — a place to be with her, not just a chat window (→ "A game on top of YuriOS," below).
- **Avatar reach, later.** A finished VRM is also a *shareable asset* — people can wear Yuri as an avatar in social-VR — a free marketing channel for the model, separate from the app you actually ship (→ "How it ships," below).
- **VR later.** Headsets are runway, not a near-term target (→ "A note on VR," below) — but a VRM-standard body today is a VR body tomorrow at no extra cost.
- **Vibe.** A 3D companion in a 3D space *is* the embodiment story you keep selling in the lore.

## The stacks

### Browser-based 3D (lightest)

- **Three.js + three-vrm.** VRM in the browser. The standard. This is the owned-renderer path (Pattern A, → ch. 25), and owning it is deliberate: a rented VMC host renders *her*, but only a renderer you control can render *the place she lives in*. The scene graph — not just the avatar — is the whole point of going 3D (→ "scene as set piece" below).
- **Babylon.js.** Alternative; better tooling, smaller ecosystem.
- **PlayCanvas / Needle.** Higher-level engines for browser-deliverable 3D.

### Game engines (heavier, full quality — and the AI-harness story)

For anything past a browser scene — a desktop app, a game, VR later — you pick a game engine. For a *solo* developer leaning on AI code harnesses (Claude Code and the like) to do the heavy lifting, the deciding factor is not the visual ceiling; it's **how legible the engine is to an agent.** An engine whose scenes and logic are plain text is one an agent can read, reason about, and edit end-to-end. An engine that hides its state in binary assets or GUID-keyed blobs forces the agent to work blind, one API call at a time. That single axis reorders the usual rankings:

| Engine | License | Language | Project files | AI-harness fit | VRM avatar | Best for |
|---|---|---|---|---|---|---|
| **Godot 4** | MIT, no royalties | GDScript (Python-ish), C# | Plain-text `.tscn` / `.gd`, node tree | **Best** — an agent reads and edits the whole project directly; mature MCP servers drive the editor | `godot-vrm` (V-Sekai; VRM 1.0 + MToon) | The solo-dev default |
| **Bevy 0.18** | MIT/Apache, no royalties | Rust (ECS) | All code, no binary scenes | Excellent for codegen — but steep to learn and slow to compile | via glTF / community | Code-first devs who want the whole game as text |
| **Unity 6** | Proprietary, free tier | C# | YAML scenes, but nodes are GUID references into `.meta` files | Good at writing C#; can't *read* a scene without crawling the asset DB | UniVRM (the mature reference) | Mobile + VR reach, huge asset store |
| **Unreal 5** | Proprietary, ~5% royalty | C++ / Blueprints | Binary `.uasset` | Hardest — the agent works at the code/API level, blind to the project tree; Blueprints are visual, not text | via plugin | AAA visual ceiling |

**The pick for this project is Godot.** It is MIT-licensed with no royalties (→ the owned, un-rented stack; book thesis), its entire project is a tree of plain-text scene (`.tscn`) and script (`.gd`) files, and GDScript reads like Python — so an AI harness can hold the *whole* project in its head, not just the file it's editing. Godot 4.6 (January 2026) made Jolt physics the default and closed much of the 3D gap with Unity. And the harness loop is now first-class: several **Godot MCP servers** (they connect Claude Code, Cursor, or any MCP client straight to the running editor, exposing 40–170+ tools to build scenes, wire nodes and signals, edit scripts, and read back debug output) turn "describe the scene, watch it built, see the error, fix it" into a real workflow. For a one-person studio that is the difference between shipping and not.

**Bevy** is the principled alternative: everything is Rust code, so there are *no* opaque scene files at all — arguably the most agent-legible engine there is. The costs are real, though — Rust's learning curve and Bevy's minutes-long incremental builds — and it has a handful of shipped commercial titles to Godot's many. Pick it only if you're already a Rust person and want the entire game as code.

**Unity and Unreal** are the reach-and-ceiling choices — Unity for mobile/VR distribution and its asset store, Unreal for AAA fidelity — but both fight the harness. Unity's scenes are GUID-keyed YAML an LLM can't resolve without crawling the asset database; Unreal's `.uasset` files are binary, so an agent is reduced to poking the API one call at a time. If your bottleneck is *your own throughput as a solo dev*, that friction is decisive.

## A game on top of YuriOS

There are two ways an engine and the companion can meet, and they point in opposite directions:

```
  DIRECTION 1 — engine as her body           DIRECTION 2 — engine as host for many
  (this chapter)                             (→ ch. 19: one engine, many characters)

     YuriOS (the brain)                          YuriOS (character-brain SDK)
            │                                              │
      drives one avatar                       binds as one profile per NPC
            ▼                                    ┌─────────┼─────────┐
     ┌───────────────┐                           ▼         ▼         ▼
     │ engine renders │                        NPC A     NPC B     NPC C
     │   her + room   │                       (one mind, many front-ends)
     └───────────────┘
```

The first — *engine as her body* — is everything above: the engine renders Yuri and her room, and the brain drives one avatar. The second — *engine as host for many* — is the "one engine, many characters" idea from ch. 19: the game becomes the renderer, animation system, and world-event source, and YuriOS is the **character brain** a game NPC binds to as a second profile over the same contracts. The NPC is then just another front-end on the same mind — voice, memory, autonomy, world-model — that the browser and desktop builds already use.

**Is a game on YuriOS viable for a solo dev?** In 2026, yes — and the surrounding market says why. LLM-driven NPCs went from tech demo to shipped product: *Suck Up!* (GPT-powered persuasion), *inZOI*'s Smart Zois (NVIDIA ACE), *Wanderfolk* (AI memory + reputation), and *Instantale* (a fully LLM-generated roguelike, June 2026) are all in players' hands. The tooling is mature too: **Inworld** and **Convai** sell hosted character brains, and **NVIDIA ACE** supplies the "body" (real-time TTS, lip-sync, facial animation, gesture). What used to take a five-person team is now a one-person-plus-harness effort.

**So what does YuriOS add that Inworld doesn't?** The thing this whole book is about: **ownership.** Inworld and Convai are hosted SaaS — you rent the brain, pay per message, and the character's memory and personality live on someone else's server, to change or vanish on their terms (the rug-pull pattern, → ch. 05). YuriOS is the opposite bet: a local, owned, persistent, auditable brain (→ book thesis; ch. 19) that the game ships *with*, not *calls out to*. The NPC remembers across sessions because the memory is a file on the player's disk, not a row in a vendor's database. For a companion — where the entire value is a continuous relationship — that is not a nice-to-have; it *is* the product.

The realistic first game is small: Godot + `godot-vrm` for the body, YuriOS as the brain over the ch. 19 contracts, one canonical room (the sanctuary, below), and the autonomy loop (→ ch. 18) driving what she does between conversations. Not a genre game with Yuri bolted on — *a place to be with her that happens to be built in a game engine.* That is the honest shape of "a game on top of YuriOS," and it is squarely within a solo dev's reach with the harness doing the engine work.

## The reference impl

Reference Build #4 (chapter 34) is *the 3D world companion*: a VRM avatar in a Three.js browser scene, with voice loop, tool use, ambient behaviour, and a small canonical environment. Its full walkthrough is ch. 34 (see also Appendix D).

## Companion-specific 3D considerations

- **Idle behaviour.** What does she *do* when the user isn't talking to her? This is 80% of the felt aliveness in a 3D scene.
- **Gaze.** Cheap to add, enormous payoff. Eyes follow cursor / user webcam if available.
- **Lip-sync.** As in ch. 25 — drive blendshapes from TTS phonemes or amplitude.
- **Scene as set piece.** The room is part of the character. Don't ship her in a default Three.js scene.

## Open-source projects to study

- **Soul of Waifu** — desktop, VRM/Live2D + local LLM + voice. <https://github.com/jofizcd/Soul-of-Waifu>
- **Open-LLM-VTuber** — cross-platform, voice-interactive, Live2D, local. <https://github.com/Open-LLM-VTuber/Open-LLM-VTuber>
- **Awesome AI VTubers** list — <https://github.com/proj-airi/awesome-ai-vtubers>
- **Awesome AI Waifu** list — <https://github.com/parallelarc/Awesome-AI-Waifu>

## Models and assets — what you can actually use

A 3D companion needs a body. You have four sources, in roughly increasing order of how much you *own* the result:

- **CC0 / open registries (placeholders, throwaway dev avatars).** [ToxSam's open-source-avatars](https://github.com/ToxSam/open-source-avatars) (browse at opensourceavatars.com) is a curated registry of CC0/CC-BY VRM avatars with a `projects.json` for programmatic pulls — the 100 Avatars set, NeonGlitch86, and others. [madjin/vrm-samples](https://github.com/madjin/vrm-samples) has VRoid sample models. VRoid's own **AvatarSample_A/B/C** and **HairSample** presets are CC0 — but you may not redistribute the file *for a fee* or re-flag it CC0 yourself. These are exactly what the reference impl bundles: a pixiv three-vrm sample avatar, good for wiring the pipeline, not for being your character.
- **VRoid Hub.** Thousands of community VRM models; each exposes per-flag permissions (download / commercial / modify / redistribute) in the bottom-right of its page. They vary per model — read them. Note VRoid Hub *cannot* set CC0 ([license FAQ](https://vroid.pixiv.help/hc/en-us/articles/360016417013-About-VRoid-Hub-s-conditions-of-use-and-VRM-license)).
- **Booth.pm** (pixiv's marketplace). Free and paid VRM models plus [`.vrma` animation packs](https://vroid.com/en/news/6HozzBIV0KkcKf9dc1fZGW). Quality is uneven and commercial rights aren't guaranteed — check each listing.
- **Author your own — the right path for Yuri.** [VRoid Studio](https://vroid.com/en/studio) is free, runs the full hair/face/body/outfit + texture-painting pipeline, and — critically — pixiv grants you **full commercial rights to anything you make in it**, individual or company, *and* lets you set the embedded license on export ([commercial-use FAQ](https://vroid.pixiv.help/hc/en-us/articles/4405813333657-Can-I-use-the-models-created-with-VRoid-Studio-Stable-Ver-for-commercial-purposes)). For a canonical, owned character that matches the locked register and the "user-owned, auditable" thesis (→ ch. 03; book thesis), this is the only source that doesn't borrow someone else's identity or license.

**Customisation pipeline.** VRoid Studio for authoring from presets; the [Blender VRM add-on](https://extensions.blender.org/add-ons/vrm/) to import/export VRM, edit mesh, repaint textures, tune MToon, and add clothing meshes to the existing armature; **Unity + UniVRM** (the reference VRM implementation) to finalise, add wearables, and export for VRChat — or, if you're on the Godot path above, V-Sekai's **`godot-vrm`** addon imports/exports the same VRM 1.0 + MToon with no Unity round-trip. One runtime caveat that surprises people: **clothing is baked into the mesh and textures** — there is no live "change outfit". The reference impl can only *tint* a material at runtime (`set_material_color` / `set_shirt_color`); to change a garment's *design* you swap the whole `.vrm` or re-author it in VRoid.

**Generative 3D — for the room, not (yet) for her.** Image/text-to-3D has matured fast: **TRELLIS 2** (open, ~4B; Gaussian-splatting PBR meshes, the open fidelity leader), **Hunyuan3D 3.1** (open, strong on illustrative/anime input), and the hosted **Tripo** (~10 s/model), **Meshy** (cleanest printable geometry), and **Rodin** (pro output) all turn a single reference image into a usable mesh in seconds. For a solo creator this is a real shortcut — but for *props, set-dressing, and the sanctuary room* (→ ch. 10; the room is part of the character), **not for the companion herself.** These tools output a *static* mesh; the same generators *can* bootstrap a draft avatar body (Tripo's auto-rig, Hunyuan3D/TRELLIS for the 2.5D look — covered in ch. 25's AI-assisted rigging), but getting it on-register with clean VRM blendshapes and spring-bones still wants a hand-pass. So the division of labour: generative 3D to **fill the scene** around her — a window seat, a plant, a mug — and VRoid (or a hand-finished generated draft, → ch. 25) for **the avatar herself**, where the rig and the embedded license are yours.

**The 2D path (Live2D).** If you go 2D instead (→ ch. 28), Live2D's [official sample collection](https://www.live2d.com/en/learn/sample/) (~20 models) is non-commercial *by default* — but the [Free Material License Agreement](https://www.live2d.com/eula/live2d-free-material-license-agreement_en.html) grants **commercial use to general users and small enterprises** (under ¥10M ≈ $67k annual revenue), which covers virtually any solo indie. Above that threshold, no. Author or commission your own in [Cubism](https://www.live2d.com/en/cubism/comparison/) (Free vs Pro tiers) and sell on nizima or Booth.

## Licensing — read the embedded block before you ship

This is the part that bites you in production, so treat it as a gate, not a footnote.

**Every `.vrm` embeds a license block** — not just a download permission. It encodes avatar-use rights, **commercial use split into corporate vs individual**, whether modification is allowed, and whether redistribution is allowed. "Free to download" tells you nothing about any of these. For a companion you intend to monetise (→ ch. 37), only ship a model whose embedded block explicitly allows **commercial use *and* modification**, or — cleaner — author your own and set the block yourself. When you swap models with `vrm.load_model(...)`, you inherit that model's license; make it a checklist item, not an afterthought.

**Live2D's threshold is revenue-based, not project-based.** The small-enterprise commercial allowance is tied to your annual revenue crossing ¥10M — so a licence that's fine today can lapse precisely when the product starts working. If the 2D companion is core to the business, budget for a commissioned/owned model before you scale, not after.

**The throwaway-vs-canonical split.** CC0 registry avatars are fine for *wiring the pipeline* and demos; they are not your character and you don't control their license downstream. Author the canonical companion (VRoid for 3D, Cubism for 2D) so the identity, the register, and the rights are all yours — which is the whole point of the owned, auditable, user-controlled stack (→ book thesis; ch. 03).

## A reference scene (Three.js + three-vrm)

The browser-based path, which is also Build #4 (→ ch. 34):

1. **Scene + camera** — a small canonical room, warm light, a fixed-ish camera framing her (the sanctuary as set piece, below).
2. **Load the VRM** via three-vrm; wire **auto-blink**, **idle eye movement**, and **look-at** (gaze) — the three cheap touches that carry most of the felt aliveness.
3. **Expression realisation** — map the model's emotion/intent tags (→ ch. 25, the FML→BML split) to VRM blendshapes; drive the mouth from TTS audio (→ ch. 24).
4. **Voice loop** — the real-time stack from ch. 24 plugged into the brain (→ ch. 14, ch. 15).
5. **Idle state machine** (below) for ambient life between turns.

Build it on web tech (Three.js) so the same rendering code that runs during development is the renderer you wrap into the shipped desktop app (→ "How it ships," below; ch. 27 surfaces).

## Idle-behaviour state machine

What she *does* when no one's talking is ~80% of a 3D scene's felt aliveness. A small state machine — `idle → glance around → react to the rain → settle → occasional in-character self-talk` — with gentle randomness and gaze that tracks the cursor/user. Be clear about what this is: in a reactive build (ch. 34) it's a *scripted* state machine, the Ukagaka idle-talk timer reborn (→ ch. 02 §1, Ukagaka). In the agentic build it's replaced by the real autonomy loop — the same scene, driven by a mind that actually decides what to do (→ ch. 18, ch. 35).

## The sanctuary room

Don't ship her in a default Three.js grey-void scene — the room is part of the character (→ ch. 03 property 4; ch. 28). Build the canonical sanctuary (→ ch. 10): small, warm light, rain on the window, a window seat, a single plant. Lock the environment register to the same 2.5D look (→ ch. 26). The same environment carries across the 3D world companion (ch. 34), the desktop companion (ch. 32), and the marketing imagery (ch. 26).

## How it ships: a local app first

The first ship is a **downloadable desktop app** — a signed binary for Windows, macOS, and Linux — not a hosted web page and *definitely* not a public social space. This falls straight out of the thesis: the whole point is that the brain, the model, and the memory live on *the user's* machine (→ book thesis; ch. 03). A local binary is the honest form of "you own her." Choosing web tech (Three.js) for the *renderer* doesn't fight this — you wrap the same rendering code in **Tauri** (small, Rust) or Electron and ship it as a native app with the local runtime behind it, which is exactly the path the open-source companions take (Soul of Waifu, Open-LLM-VTuber are desktop apps, → below; full packaging is ch. 32).

**Why not a public social world (VRChat/Cluster) as the launch surface.** Running the *live* YuriOS brain in a shared space means she's talking to arbitrary strangers, which drags in the entire content-moderation, abuse-handling, and prompt-injection problem before the single-user product even exists — a mountain of safety work for a channel that isn't the product. So social-VR is, at most, a *later and avatar-only* marketing option: you can export the **static VRM** (just the 3D model, no brain behind it) so people can *wear* Yuri as an avatar — the Julia-in-TinyMUD presence lesson at modern scale (→ ch. 02 §1, Julia), and free reach (→ ch. 37) — while the mind ships only in the app the user owns. If that day comes, VRChat is the largest audience (~149k concurrent record, New Year's 2026), **Cluster** is the VRM-native Japanese channel that fits the 2.5D register, and **Resonite** has the deepest in-world building. But that's a distribution afterthought, not the launch.

## A note on VR (later, not now)

VR is real runway for this project, not a near-term target — the next headset inflection slipped to ~2027 (Meta rebooted its flagship as "Griffin": a gaming-focused **Quest 4** and a Vision-Pro-class **Quest Pro 2**, with a lightweight tethered **Quest Air** alongside). So don't build for VR now; just don't paint yourself out of it. Four cheap habits keep the door open: keep the avatar **VRM-standard** (portable across platforms), keep the rig within **VR performance budgets** from the start (re-rigging later is costly), let the scene work at **room scale and seated**, and keep the brain/voice stack **transport-agnostic** so the same companion runs in a browser today and a headset tomorrow.
