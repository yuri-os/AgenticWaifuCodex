# Training a character LoRA — the consistency pipeline

The hard requirement of ch. 26 is *the same character, a thousand times*. IP-Adapter
and reference/edit models get you "recognisably her" without training, but the
definitive answer — *any* prompt, any scene/pose/outfit, native quality, the character
unchanged — is a **character LoRA**. Once trained, consistency stops being a per-render
hack (an adapter fighting your prompt) and becomes a property of the model: you add a
trigger word and generate normally.

This is the full, reproducible pipeline we used to make `yuri_v2`, from a *single*
locked reference frame to a trained LoRA wired back into image-forge. Every step is a
script in `examples/` or `lora/`; run them in order.

```
 1. riverflow_variations.py         →  pick the canon frame (the "who")
 2. build_lora_dataset_openrouter.py →  ~28 varied, consistent images of her
 3. (curate)  +  make_lora_metadata.py  →  a trainable imagefolder
 4. train_yuri_lora.sh             →  yuri_v2/pytorch_lora_weights.safetensors
 5. wire into characters/yuri.yaml →  every render is her
```

Hardware here: RTX 5070 Ti (16 GB), the shared `yurios_env` (torch 2.10+cu128,
diffusers 0.37, accelerate, peft, bitsandbytes). No extra trainer install — the
diffusers DreamBooth-LoRA SDXL example does the job and keeps the env's pins intact.

---

## 1. Pick the canon frame

A LoRA can only be as consistent as what it's taught, so first lock *who she is* in one
high-quality frame. We generate with the **same model/API that made the register**
(`sourceful/riverflow-v2.5-pro` on OpenRouter, the exact manifest prompt), N times, and
pick the best sample:

```bash
OPENROUTER_TOKEN=... python examples/riverflow_variations.py --n 5
# review out/riverflow_variations/, choose one (we used variation-2.png)
```

Why riverflow and not a local model: it *is* the register. Bootstrapping from an
IP-Adapter render instead bakes that adapter's lower fidelity into everything
downstream — garbage in, garbage out.

## 2. Build the dataset (reference-editing via OpenRouter)

A character LoRA needs ~15–30 images of the **same** person across **varied**
outfits/scenes/poses/expressions. We feed the chosen frame back in as an identity anchor
to a hosted image-edit model and have it render new contexts at full quality — variety
**and** consistency **and** quality at once:

```bash
OPENROUTER_TOKEN=... python examples/build_lora_dataset_openrouter.py
```

**Choosing the edit model.** Any OpenRouter model that takes an input image and returns
one works — set it with `--model` (default `sourceful/riverflow-v2.5-pro`):

```bash
python examples/build_lora_dataset_openrouter.py --model google/gemini-2.5-flash-image
```

These hosted editors (riverflow, Nano Banana, FLUX/Qwen edit endpoints) differ in how
tightly they hold a character across a scene change. There's no universal winner — run a
small batch on two or three and **keep whichever keeps your character most consistent**;
that's the one to build the full set with. (Fidelity beats openness for this one-time,
throwaway bootstrap step; the trained LoRA you ship is fully local.)

Two phases, on purpose (see the script):

- **SCENES** — 19 new outfit/scene/pose shots from the primary anchor.
- **EXPRESSIONS** — 10 shots that *force* a different head angle + expression, rotated
  across 2–3 anchors (variation-2/3/4). This is the fix for a subtle but real failure:
  reference-editing from one frame **copies the source's head tilt and smile**, so a
  scenes-only set teaches the LoRA one tilt + one expression and it resists anything
  else. Forcing angle/expression — and varying the source anchor — keeps the LoRA
  flexible. (riverflow softens strong negative affect like crying/anger; expect good
  positive/neutral range, and lean on the base model at inference for extremes.)

Each image gets a `.txt` caption: the `yuri_v2` trigger + the *variable* content
(outfit/scene/expression), never the invariant identity — you want the trigger, not the
captions, to carry her face/hair/ears, and you want the words that vary to stay
steerable.

## 3. Curate, then make it trainable

Open `out/riverflow_dataset/contact_sheet.png` and **delete the off-model PNG + its
matching `.txt`** (drifted faces, bad hands, wrong eye colour). Keep ~15–25 of your
best. Quality and consistency beat count — 15 great images train a better LoRA than 40
mediocre ones.

Then build the imagefolder metadata:

```bash
python examples/make_lora_metadata.py        # writes metadata.jsonl, moves contact sheet aside
```

## 4. Train

```bash
bash lora/train_yuri_lora.sh
```

What it runs: the vendored `lora/train_dreambooth_lora_sdxl.py` (diffusers' example,
pinned to **v0.37.0** + a one-line patch so a local image folder loads via the
`imagefolder` builder, not as bare metadata). Settings tuned for 16 GB:

| Setting | Value | Why |
|---|---|---|
| base | `John6666/illustrij-v50-sdxl` | the register model — the LoRA lives in *its* look |
| VAE | `madebyollin/sdxl-vae-fp16-fix` | avoids fp16/bf16 VAE NaNs |
| precision | bf16 | stable on Blackwell; half the memory |
| optimizer | 8-bit Adam (bitsandbytes) | big VRAM saving |
| grad checkpointing | on | trades compute for memory |
| LoRA rank | 24 | plenty for one character |
| resolution | 1024, center-crop | SDXL-native; crop keeps the centred face |
| steps | 1400 (~50 epochs over 28 imgs) | enough to learn her, short of frying |
| text encoder | **not** trained | unet-only LoRA fits comfortably; trigger still binds |
| attention | PyTorch SDPA (no xformers) | xformers' kernel isn't built for this torch/GPU |

On a 5070 Ti this is ~9–10 GB and ~40 min. Output:
`lora/yuri_v2/pytorch_lora_weights.safetensors` (~tens of MB).

Tuning if results are off: **overfit** (every render is the rooftop pose / ignores the
prompt) → fewer steps (~900–1100) or lower rank (16). **Underfit** (doesn't look like
her) → more steps (~2000) or rank 32, or add a few more dataset images. Identity strong
but stiff expressions → that's the dataset-diversity lever in step 2, not training.

## 5. Wire it into image-forge

The `diffusers` backend loads a fused LoRA from the character file. In
`characters/yuri.yaml`:

```yaml
trigger: "yuri_v2"
lora:
  path: "../lora/yuri_v2/pytorch_lora_weights.safetensors"
  weight: 0.9
```

`Character.assemble` prepends the trigger to every prompt, and `DiffusersBackend`
`load_lora_weights` + `fuse_lora`s it into the base at load (before offload), so both
txt2img and img2img inherit it with no per-call scale. Then nothing special is needed —
just generate, and it's her:

```python
forge.set_backend("diffusers", model="illustrij",
                  cache_dir="/mnt/6870C6B170C68572/AI/huggingface")
forge.selfie(scene="cafe", wardrobe="cozy", mood="happy")   # consistent Yuri, new scene
forge.generate("yuri_v2, on a snowy mountat summit at sunrise, red parka, laughing")
```

Lower `weight` (~0.7) if the LoRA overpowers a prompt; raise (~1.0) if her identity
drifts. This is the no-adapter consistency path: the prompt determines everything; the
LoRA keeps *her* fixed.

## 6. Retraining on a different base

A LoRA lives in the look of the base it was trained on. It *transfers* across the
Illustrious lineage (illustrij ↔ equinox ↔ nova-anime) — it'll load and render her on a
sibling base — but her **face drifts** on a base it wasn't trained on: the body, skin and
hair hold, the identity loosens. If you settle on a different base as your daily driver,
retrain the LoRA on it. (We did exactly this when equinox-v5 became the default: the
illustrij-trained `yuri_v2` on equinox rendered a generic semi-real face; retraining on
equinox-v5 recovered her amber eyes, eye shape and knowing smile.)

It's the same trainer, dataset and hyperparams as step 4 — only the base differs. One
wrinkle: many community bases (e.g. Equinox v5.0) ship as a **single-file** Civitai
`.safetensors`, which the DreamBooth trainer's `from_pretrained` can't read. Convert it to
a diffusers folder first:

```bash
# 1. single-file checkpoint → diffusers-format folder (loads on CPU; ~6.5 GB out)
python examples/convert_single_file_to_diffusers.py \
    /path/to/base-v5.safetensors  /path/to/base-v5-diffusers

# 2. train on it → lora/yuri_v2_equinox/pytorch_lora_weights.safetensors
bash lora/train_yuri_lora_equinox.sh        # = train_yuri_lora.sh, base swapped

# 3. point characters/yuri.yaml at the new LoRA AND config.yaml at the matching base —
#    they're coupled; a mismatched pair renders her but drifts the face.
```

A diffusers-format base (an HF repo) skips step 1 — just set `--pretrained_model_name_or_path`.

---

### Notes / honesty

- **Single-reference bootstrap has a ceiling.** Everything descends from one frame, so
  the LoRA inherits whatever that frame (and riverflow's house style) can't vary. It's
  excellent for a consistent companion; it is not a substitute for a real multi-shot
  photoset of a real subject.
- **Cost.** Steps 1–2 are hosted/paid (~25 riverflow calls, a couple of dollars). Step
  4 is local/free. A re-train reuses the dataset — you only pay once.
- **Licensing.** `train_dreambooth_lora_sdxl.py` is vendored from diffusers
  (Apache-2.0). The base model and its license are your responsibility; the trained
  LoRA + Yuri's look are reserved brand IP.
