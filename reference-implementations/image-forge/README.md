# image-forge — a swappable image service for YuriOS

The companion's **image capability behind one stable API, with interchangeable
generator backends** (→ book ch. 26, *Generated Imagery and Selfies*). It renders
the things the project needs pixels for — the hero portrait, in-conversation
selfies "of her", worldbuilding art, branding, and reference-driven edits — and it
does so *on-register* (the locked 2.5D anime look) regardless of which
generator is plugged in behind it.

This is the live, on-demand counterpart to an offline batch art pipeline:
same locked register, same proven OpenRouter path,
but reshaped into the **service a runtime calls** rather than a one-shot script —
and made provider-agnostic so you can swap a hosted API for your own GPU (or for an
uncensored local model) without the rest of YuriOS noticing.

```
  YuriOS runtime / agent loop
        │  forge.selfie(scene="window", mood="happy")
        ▼
  ┌──────────────────────────────────────────────┐
  │ ImageForge (service.py)                        │
  │  • Character  — the locked 2.5D anime register  │
  │  • SelfieBook — scene × framing × … templates  │
  │  • provenance — strip / embed metadata          │
  └───────────────────────┬────────────────────────┘
                          │ GenRequest / EditRequest      ← the one narrow seam
        ┌─────────────┬────┴────┬──────────────┐
        ▼             ▼         ▼              ▼
     mock         openrouter  comfyui       replicate     ← swap at runtime
  (no deps)      (riverflow) (local GPU)  (hosted GPU)
```

Swapping the generator is swapping the object behind that seam — the image-side of
the model-agnostic runtime (→ ch. 07). Everything above the seam (who she is, what
to render, what leaves the building) stays put.

## Quick start

```bash
pip install -r requirements.txt          # Pillow + PyYAML — that's all the mock backend needs
python examples/demo.py                  # writes a portrait, selfies, scenery, an edit → out/
```

The demo runs on the **mock backend**: a deterministic placeholder renderer, so
the whole pipeline — register assembly, the selfie template library, provenance,
saving, a runtime backend swap — runs on a laptop with no GPU, no API key, and no
network. Swap in a real backend (below) to get real pixels; nothing else changes.

The shipped **`config.yaml` defaults to the real path**: local diffusers on equinox-v5
with Yuri's trained hero LoRA (`characters/yuri.yaml`), so `ImageForge.from_config()`
renders the actual consistent character — *any* prompt, same Yuri (→ `lora/TRAINING.md`).
That needs a CUDA GPU + the trained LoRA; flip `backend.name` to `mock` for a no-GPU run.

> **Base ↔ LoRA are coupled.** The default pairs equinox-v5 with the LoRA *trained on
> equinox-v5* (`lora/yuri_v2_equinox/`, → `lora/train_yuri_lora_equinox.sh`), which locks
> her face tightest. A LoRA transfers across the Illustrious lineage (illustrij ↔ equinox ↔
> nova) but her face drifts on a base it wasn't trained on — so if you change `backend.model`,
> switch `lora:` to the sibling trained on that base (the original `lora/yuri_v2/` is the
> illustrij one). Retraining on a new base is one script + a single-file→diffusers convert.

Tests (also fully offline — mock backend + offline checks):

```bash
python -m pytest          # 55 tests: assembly, templates, provenance, backends, diffusers, service
```

CLI for the same calls:

```bash
python -m image_forge portrait
python -m image_forge selfie --scene window --mood happy --seed 1
python -m image_forge scenery "rainy neon megacity skyline at night"
python -m image_forge edit out/some.png "her in the rain, looking back"
python -m image_forge caps               # what the active backend can do
```

## Using it from YuriOS

`ImageForge` is plain blocking Python; an agent loop calls it directly — the
selfie/portrait/edit methods *are* the integration surface.

```python
from image_forge import ImageForge

forge = ImageForge.from_config("config.yaml")   # default: equinox-v5 + Yuri's LoRA

# When the model decides to send a selfie (a tool call, a token, your own trigger):
result = forge.selfie(scene="window", mood="happy", wardrobe="cozy")
send_to_user(result.path)                # consistent Yuri (LoRA), saved + provenance-stamped

# Hold her identity, change the scene (reference-driven editing, → ch. 26):
forge.edit(result.path, "her, out in the rain at night, looking back")

# Swap the generator live — e.g. move to a local uncensored model for intimacy:
forge.set_backend("comfyui", port=8188, checkpoint="myAnimeModel.safetensors")
```

## The backends

Choose one in `config.yaml` (`backend.name` + its options). All implement the same
`ImageBackend` interface (`generate` / `edit` / `capabilities` / `health`).

| Backend | Needs | `generate` | `edit` | Notes |
|---|---|---|---|---|
| `mock` | Pillow only | ✓ placeholder | ✓ | wire-up / tests; renders the prompt onto a card |
| `openrouter` | `$OPENROUTER_TOKEN` | ✓ | model-dependent | the repo's proven path — default `sourceful/riverflow-v2.5-pro`, matches the brand art |
| `diffusers` | `torch`+`diffusers`, a GPU | ✓ txt2img | ✓ img2img (+IP-Adapter) | **fully yours, NSFW-capable** — any HF model in-process, no refusals |
| `comfyui` | a running local ComfyUI | ✓ | with an edit workflow | **fully yours** — your GPU, checkpoint, LoRA, no refusals |
| `replicate` | `pip install replicate` + `$REPLICATE_API_TOKEN` | ✓ FLUX/Qwen | ✓ FLUX.1 Kontext | hosted GPUs without owning hardware |

Adding a provider (Fal, Modal, NovelAI…) is one `ImageBackend` subclass registered
in `image_forge/backends/__init__.py`. The seam is identical.

### The diffusers path (local HF models, owned, uncensored)

Runs any Hugging Face model **in-process on your own GPU** — the strongest privacy
and the NSFW-capable path (SDXL anime fine-tunes have no safety checker). It takes the
usual batch-generator shape: a model registry plus
16 GB-VRAM offload settings (sequential CPU offload, attention slicing, VAE
tiling, xformers). On an RTX 5070 Ti, illustrij renders 832×1216 in ~1 minute.

- **Models** live in `models.yaml` (`repo` + diffusers `pipeline` + `defaults`). Add
  any HF repo — e.g. `John6666/illustrij-v50-sdxl`. Select with `backend.model`.
- **Download/cache location** is `cache_dir` (sets `$HF_HOME`), e.g.
  `/mnt/6870C6B170C68572/AI/huggingface` — weights download there once, reused.
- **Long prompts.** SDXL's CLIP truncates at 77 tokens, which would silently drop most
  of the rich register+identity+scene prompt (and its negatives). The backend detects
  this and, if `sd_embed` is installed, encodes the *full* prompt via SDXL's two text
  encoders — install it without disturbing your other pins:
  `pip install --no-deps git+https://github.com/xhinker/sd_embed.git`. Without it, the
  backend warns once and lets the pipeline truncate.
- **Editing for consistency.** `edit()` uses **img2img** (keep the composition,
  change clothes/scene via `strength`). Both `generate()` and `edit()` can also hold
  *her* identity with an **IP-Adapter** fed the character's `reference_images` — put
  Yuri in entirely new scenes/outfits while she stays recognisably herself, no LoRA
  training (→ ch. 26, reference-driven consistency). Enable it under `ip_adapter:`
  in `config.yaml` and set `reference_images:` in `characters/yuri.yaml`.

```python
forge.set_backend("diffusers", model="illustrij",
                  cache_dir="/mnt/6870C6B170C68572/AI/huggingface")
forge.selfie(scene="bed", wardrobe="intimate", mood="tender")     # local, uncensored
forge.edit("out/her.png", "her in an elegant red dress", strength=0.5)  # change the outfit
```

- **Face detailer (small-face fix).** SDXL works in a 1/8-resolution latent, so a small
  or distant face — a full-body or overhead shot — gets only a handful of latent pixels
  and its **eyes degrade** (soft, asymmetric, malformed). This is a *resolution* problem,
  not an identity one, so no LoRA or negative can fix it. The detailer (ADetailer-style)
  detects each face with `facexlib`'s RetinaFace, and for any face below `max_face_ratio`
  of the frame height it **crops, upscales the crop to full resolution, redraws it with
  the same fused LoRA** (so identity carries), then feathers it back in — one short extra
  img2img pass per starved face, no seam. It's **on by default** in `config.yaml`
  (`face_detailer: {enabled: true}`); tune `strength` (redraw distance), `max_face_ratio`
  (set to `1.0` to detail every face), or drop `enabled: false` to skip it. Each render's
  provenance records `faces_detailed`. A big, close-up face already has enough pixels, so
  it's left untouched.
- **Hi-res fix (whole-image crispness).** Upscales the finished frame and runs a second
  low-denoise pass over the *whole* image, so global detail (skin, hair, fabric) is
  rendered at a resolution the base pass never had — the complement to the face detailer
  (that fixes small faces; this lifts everything). Runs *before* the detailer so the
  detailer works on the larger image. **Off by default** (`hires_fix: {enabled: false}`)
  because it roughly doubles render time — flip it on for hero shots. At `scale: 1.3`
  (832×1216 → 1080×1584 — 1.5× OOMs SDXL img2img on 16 GB; raise with more VRAM);
  `strength` is the second-pass denoise. Provenance records the `hires` output size.

### The ComfyUI path (local, owned, uncensored)

ComfyUI is the power-user default in ch. 26 and the only fully-owned option. The
backend talks to a running ComfyUI over its HTTP API and injects your prompt into a
**workflow graph** by placeholder substitution: your exported workflow (ComfyUI →
*Save (API Format)*) contains the tokens `%POSITIVE%`, `%NEGATIVE%`, `%SEED%`,
`%WIDTH%`, `%HEIGHT%`, `%CKPT%`. A ready-to-run SD/SDXL graph ships in
`comfy_workflows/txt2img.json` — point `checkpoint:` at a model you have installed.
For identity-preserving edits, add an `edit_workflow:` (a FLUX.1 Kontext /
Qwen-Image-Edit graph with a `LoadImage` node fed `%IMAGE%`).

**Running a flagship DiT on 16 GB — Qwen-Image via GGUF.** The big DiTs
(Qwen-Image 20B, FLUX.2 32B) out-render SDXL on prompt adherence and structure but
**don't fit 16 GB through the diffusers path** — on-the-fly bitsandbytes loads the
full model to the GPU to quantize it and OOMs (see the note in `models.yaml`).
ComfyUI sidesteps this by loading a **pre-quantized GGUF** incrementally. A
ready-to-run graph ships in `comfy_workflows/qwen_image_gguf.json` (uses the
`city96/ComfyUI-GGUF` node: `UnetLoaderGGUF` + `CLIPLoader` type `qwen_image` +
`VAELoader`). Point the backend's `checkpoint` at the GGUF and go — Qwen honours the
negative prompt (true CFG) and has no 77-token cap, so the full register prompt is
used as-is. `examples/comfyui_qwen_test.py` renders on-register Yuri selfies through it.

### Opt-in hero-shot path: the two-stage Qwen → illustrij pass

> **Not the default — an opt-in for the occasional hero still.** We built and
> evaluated this and decided against it for everyday use (→ ch. 26): the quality lift
> is real but marginal once the face detailer and a well-tuned single-model path are
> in place, and it costs ~25× the render time (minutes per image), a looser identity
> from the hand-off, and a warmer skin tone to fight. The everyday path stays one
> uncensored SDXL + the character LoRA (the diffusers default above) — fast, and good
> enough. Reach for this only when you want to spend minutes on a single showcase image.

The idea is to use **each model for what it's best at** (→ ch. 26, the right tool per
job). Qwen-Image has the best composition and prompt adherence but renders the register
a touch flat; illustrij (the SDXL model that *made* the riverflow reference) has exactly
the painterly 2.5D surface we want but is weaker at composition from a cold prompt. So:

1. **Stage 1** — Qwen lays down pose / scene / lighting (with a neon-rim style booster).
2. **Stage 2** — a *low-denoise* illustrij img2img pass repaints the surface in-register.

`examples/two_stage_qwen_illustrij.py` runs both (the two models don't co-reside on
16 GB, so it POSTs ComfyUI `/free` between stages, then loads illustrij). It takes
**your own prompt** — by default the scene is wrapped in Yuri's identity + the locked
register for you, so you just describe what she's doing:

```bash
# your own scene — "she" is Yuri; identity + register added automatically
python examples/two_stage_qwen_illustrij.py \
    --prompt "she sits on a neon-lit rooftop at night in the rain, holding a clear umbrella"

# the painterly refine dial: 0.30 subtle .. 0.50 default .. 0.60 strong
python examples/two_stage_qwen_illustrij.py --prompt "..." --strength 0.60

# pin a seed; or compare the Qwen base alone (skip the illustrij refine)
python examples/two_stage_qwen_illustrij.py --prompt "..." --seed 7 --no-refine

# the three preset scenes instead of a custom prompt
python examples/two_stage_qwen_illustrij.py --n 3

# full manual control — your text IS the whole positive prompt, no identity wrap
python examples/two_stage_qwen_illustrij.py --raw \
    --prompt "2.5D anime, a black cat curled on a windowsill, neon city behind"
```

Stage-1 bases land in `out/two_stage/stage1/`, finals in `out/two_stage/`.
`--strength` is the main knob (img2img denoise): low keeps Qwen's composition almost
intact with a light illustrij polish; high lets illustrij's painterly surface take
over (richer, but drifts further from Qwen's exact features). Run it with the
`yurios_env` python, against a ComfyUI that has the Qwen GGUF set up.

**NSFW — don't use Qwen for the base.** Qwen-Image is trained with NSFW filtered out;
it sanitises or refuses explicit content no matter the prompt, and a *low*-denoise
refine can't add back anatomy the base never drew (only a near-total
`--strength` ~0.85+ could, which throws the base away). For intimate work the base
must come from an **uncensored** model — pass `--stage1 diffusers`, which runs the
base on a local no-safety-checker model (default illustrij, the Illustrious-based
model that made the reference and handles anime NSFW natively). No ComfyUI needed:

```bash
# single uncensored stage (illustrij is both the base and the register surface)
python examples/two_stage_qwen_illustrij.py --stage1 diffusers \
    --prompt "she lies on soft sheets in delicate lingerie, warm lamplight"
```

When `--stage1-model` equals `--refiner` (both illustrij by default) the redundant
refine is skipped automatically — it's one clean uncensored pass. Use a different
`--stage1-model` (a dedicated NSFW SDXL) with `--refiner illustrij` if you want a
stronger NSFW base composition repainted into the register. This is the ch. 11
posture in practice: uncensoredness is **backend/model selection**, not engine
policy — the intimate wardrobe tier lives in `templates/selfie.yaml`, and what
actually renders is decided by the model you point at.

**Keeping Qwen's composition for NSFW — the Qwen NSFW LoRA.** If you want Qwen's
superior composition *and* NSFW, add the `--qwen-nsfw` flag to the `--stage1 qwen`
path. It swaps in `comfy_workflows/qwen_image_gguf_nsfw.json`, which loads the
[`starsfriday/Qwen-Image-NSFW`](https://huggingface.co/starsfriday/Qwen-Image-NSFW)
LoRA (`ComfyUI/models/loras/qwen_image_nsfw.safetensors`, ~189 MB) on top of your GGUF
so the otherwise-filtered base can lay down intimate composition — then illustrij
refines the surface as usual:

```bash
python examples/two_stage_qwen_illustrij.py --stage1 qwen --qwen-nsfw \
    --lora-strength 0.85 --prompt "she reclines on soft sheets in delicate lingerie"
```

`--lora-strength` (~0.7–1.0) tunes how strongly the LoRA pushes. Note the **first**
run is slow: applying a LoRA to a Q4 GGUF dequantizes hundreds of tensors (minutes
on top of sampling), so the backend allows up to 30 min on this path. The LoRA is
loaded by the workflow via a `LoraLoaderModelOnly` node and its strength comes from
the `%LORA_STRENGTH%` token (the ComfyUI backend gained an `extra_tokens` option for
workflow-specific knobs like this).

**Or a purpose-built NSFW model — `--qwen-aio`.** Instead of the LoRA, swap to
[Phr00t's Qwen-Rapid-AIO-NSFW](https://huggingface.co/Phil2Sat/Qwen-Image-Edit-Rapid-AIO-GGUF)
(a Qwen-Image-Edit merge with NSFW LoRAs baked in, **distilled** for ~8-step speed).
Drop `qwen-rapid-nsfw-v9.0-Q4_K_M.gguf` into `models/diffusion_models` (it reuses the
same text-encoder + VAE) and add `--qwen-aio`:

```bash
python examples/two_stage_qwen_illustrij.py --stage1 qwen --qwen-aio \
    --prompt "she reclines on soft sheets in delicate lingerie" --no-refine
```

It runs `comfy_workflows/qwen_rapid_aio.json` at `--aio-steps` (8) / `--aio-cfg` (1.0)
— distilled, so cfg is ~1.0 and the **negative prompt is inert** (classifier-free
guidance off). Faster than the LoRA path (no per-run dequant) and NSFW out of the box;
the trade-off is it's Edit/AIO-flavored rather than the pristine base Qwen-Image.

## How the look is kept consistent

The hard requirement of ch. 26 is *the same character, a thousand times*. Three
mechanisms, layered, all driven from `characters/yuri.yaml`:

1. **The locked register, as prompt text.** `quality_preamble` (the locked 2.5D look)
   and `identity` (her face/build/marks) are pinned in
   `characters/yuri.yaml`, so a runtime selfie reads as the *same person* as the
   batch-generated brand set — the "one source of truth" discipline (→ ch. 26).
   Assembly is strictly ordered — `preamble + identity + scene` — with the
   clothing/anatomy guard appended only when a figure is in frame.
2. **Durable identity (a trained LoRA).** The definitive path: train a character LoRA
   once, then *any* prompt renders her in any scene/pose/outfit at native quality, with
   no adapter fighting the prompt. Set `trigger` + `lora` in `characters/yuri.yaml`;
   `DiffusersBackend` fuses the LoRA into the base at load. The full reproducible
   pipeline — pick a canon frame, synthesise a varied+consistent dataset by
   reference-editing it with a hosted OpenRouter edit model (`--model`, default riverflow;
   try a few and keep whichever holds the character best), curate, train on illustrij
   (16 GB), wire it back — is in **[`lora/TRAINING.md`](lora/TRAINING.md)** (scripts:
   `examples/riverflow_variations.py`, `examples/build_lora_dataset_openrouter.py`,
   `examples/make_lora_metadata.py`, `lora/train_yuri_lora.sh`).
3. **Reference-driven consistency without training.** For quick results or to *bootstrap
   the LoRA's dataset*: an **IP-Adapter** on the diffusers backend (`reference_images` in
   the character file, `examples/local_ipadapter_scenes.py`), or reference/edit models
   (riverflow image-input, FLUX.1 Kontext, Qwen-Image-Edit) that re-render her into a new
   scene via `edit()`. Lower fidelity / less prompt freedom than a LoRA, but no train step.

## Selfies that don't collapse

ch. 26's named failure is every selfie resolving to the same five poses. The fix is
`templates/selfie.yaml` — a rotated library of **scene × framing × lighting × mood ×
wardrobe**. Name a slot to pin it, leave it out to rotate one in (seeded, so a seed
reproduces a shot). Settings and palette stay inside the canon (the sanctuary above
a rainy neon megacity → `brand_system`) so every shot reads as one world. Add rows
freely; more variety is the entire point.

## Intimacy is a tier, not a gate

The intimate register (spicy selfies, lingerie/swimwear) is a normal `wardrobe`
value, available from day one — **user-initiated, never gated**, because withholding
warmth is the failure this project refuses (→ ch. 11). This service refuses nothing.

Whether a given request *actually renders* is decided by the **backend you point
at**, not by this code: a hosted frontier model refuses the register; a local
uncensored / abliterated model does not. That is exactly the ch. 11 "model
requirement" — uncensoredness is backend selection (`capabilities().uncensored`),
not engine policy. The shipped `character_negative` keeps the *default* register at
"alluring but no nudity" (the taste guard); loosen or remove that line for
your own build. The engine takes **no enforcement posture** on what gets generated
(→ ch. 26); the user is sovereign (→ ch. 05). The explicit *craft* of the register
is out of scope here — left to the separate optional course (→ ch. 11, ch. 39).

## Provenance & opsec

`provenance:` in `config.yaml` controls what metadata leaves with an image:

- `strip` (default) — round-trip through Pillow, dropping **all** upstream metadata.
  This is the opsec posture the batch pipeline uses: nothing
  about the generator travels with the file.
- `embed` — strip, then write a small `content_credentials` record (the C2PA idea
  from ch. 26, minus cryptographic signing). A hosted operator's duty-of-care build
  would sign these; a user-owned build ships them as a sensible, removable default,
  not a control it can enforce downstream (→ ch. 03, user-owned).
- `raw` — pass bytes through untouched.

### Reproducibility log (how each image was made)

Distinct from the provenance *stamp* above (which governs what metadata leaves
*with* an outbound file — `strip` by default for opsec): every **saved** image
also writes a local record of exactly how it was generated, so any render is
reproducible and auditable.

- `out/<name>.json` — a per-image sidecar next to the PNG: backend, model
  (`diffusers:illustrij`, the HF repo, *and the LoRA path + fused weight* — or the
  remote API model id), full prompt + negative, seed, steps, guidance, dimensions,
  provenance mode, character, request id, timestamp.
- `out/generations.jsonl` — the same record appended as one line per render: a
  scannable ledger of everything you've generated (`jq` / grep it).

These stay local (the `out/` folder is gitignored) and are written for **all**
backends. They are not stamped into the outbound image, so the opsec posture is
unchanged — a `strip`-mode file you send still carries nothing.

## Files

```
config.yaml              live config: which character, which templates, which backend
models.yaml              local diffusers model registry (repo + pipeline + defaults)
characters/yuri.yaml     the locked look as prompt parts (source of truth)
templates/selfie.yaml    the scene × framing × lighting × mood × wardrobe library
comfy_workflows/         ComfyUI API-format graphs with %TOKENS% (txt2img, qwen_image_gguf[_nsfw], qwen_rapid_aio)
image_forge/
  service.py             ImageForge — the high-level asks + the runtime backend swap
  character.py           Character.load + register/identity prompt assembly
  templates.py           SelfieBook.compose — the anti-collapse rotation
  provenance.py          strip / embed metadata
  types.py               GenRequest / EditRequest / ImageResult / Capabilities
  backends/
    base.py              ImageBackend — the one interface (the swap seam)
    mock.py  openrouter.py  comfyui.py  replicate_backend.py  diffusers_backend.py
    __init__.py          the registry: make_backend(name, **opts)
examples/
  demo.py                end-to-end on the mock backend (no GPU/key/network)
  comfyui_qwen_test.py   on-register Yuri via ComfyUI + Qwen-Image GGUF
  two_stage_qwen_illustrij.py   Qwen compose → illustrij refine (custom --prompt)
  local_variations.py    img2img variations of one image (diffusers)
  local_ipadapter_scenes.py     same Yuri, new scenes via IP-Adapter (diffusers)
  local_model_test.py    quality-test any model in models.yaml
  riverflow_variations.py       LoRA step 1: canon-frame candidates via riverflow
  build_lora_dataset_openrouter.py  LoRA step 2: dataset via reference-editing (--model, any OpenRouter editor)
  make_lora_metadata.py         LoRA step 3: curated folder → trainable imagefolder
lora/
  TRAINING.md            the full character-LoRA pipeline (replicable, → ch. 26)
  train_yuri_lora.sh     LoRA step 4: train on illustrij (16 GB-tuned)
  accelerate_config.yaml single-GPU bf16 launch config
  train_dreambooth_lora_sdxl.py  vendored diffusers trainer (v0.37.0 + imagefolder patch)
test_image_forge.py      53 offline tests
```

## How it maps to ch. 26

| Chapter idea | Where |
|---|---|
| The use cases (portrait, selfie, worldbuilding, merch source) | `ImageForge.portrait/selfie/scenery/edit` |
| Why this register (supernormal stimulus, uncanny valley) | `characters/yuri.yaml` `quality_preamble`/`identity` |
| Consistency: LoRA / reference-editing / IP-Adapter | **`lora/TRAINING.md`** (full LoRA pipeline), `character.py` (trigger/lora/refs), `edit()`, diffusers IP-Adapter, the comfyui/replicate edit models |
| Tooling: ComfyUI, diffusers, base generators, hosted inference | the five backends |
| One source of truth (selfie ⇄ rig read as same person) | register lifted from `manifest.json`; the canonical portrait |
| Selfie prompts that don't collapse | `templates/selfie.yaml` + `SelfieBook.compose` |
| Worldbuilding atlas | `scenery()` (no figure in frame) |
| Provenance & watermarking | `provenance.py` |
| (intimacy posture) | ch. 11 — the intimate wardrobe tier + backend-selected uncensoredness |

## Limitations (intentional, to stay minimal)

- **LoRA training is included** (`lora/TRAINING.md`) but kept deliberately minimal: a
  single-reference bootstrap via the vendored diffusers SDXL trainer, unet-only, no
  aspect-ratio bucketing or multi-subject support. For production datasets use kohya /
  ai-toolkit; this is the replicable reference path, not a full training rig.
- **No queue / batching / cost accounting.** One image per call, synchronous. The
  batch concerns belong to the offline art pipeline, not here; a service would add a
  job queue and the token-economy metering of ch. 39.
- **ComfyUI workflows are bundled only for SDXL txt2img and Qwen-Image GGUF** —
  anything else depends on your installed models. Export your own and add the `%TOKENS%`.
- **No expression-set generator.** The ~28-expression sheet for the avatar rig
  (→ ch. 25) is a natural next addition on top of `edit()` + a pose ControlNet.
- **`embed` provenance isn't signed C2PA** — it's the metadata record without the
  cryptographic manifest a hosted duty-of-care build would attach.

License: MIT (per `../README.md`). Yuri's look/canon is reserved brand IP.
