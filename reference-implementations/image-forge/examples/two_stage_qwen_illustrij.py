"""Two-stage render: Qwen-Image composition -> illustrij surface refine.

Why two stages (→ ch. 26, the right tool per job):
  - Qwen-Image (20B DiT, via ComfyUI) has the best prompt adherence and structure
    but renders the D-011 "anime" register a touch flat/clean.
  - illustrij (SDXL) *is* the model that made the riverflow reference — its painterly
    2.5D surface is exactly the look we want, but on its own it's weaker at composition
    and identity from a cold prompt.
So: let Qwen lay down pose/scene/lighting, then run a LOW-denoise img2img pass with
illustrij to repaint the surface in-register. Best of both.

CUSTOM PROMPTS — pass your own scene with --prompt (it gets wrapped in Yuri's
identity + the locked register automatically); add --raw to send the prompt verbatim:

    # the three preset scenes (portrait / window / sanctuary)
    python examples/two_stage_qwen_illustrij.py --n 3

    # your own scene — "she" is Yuri, identity + register added for you
    python examples/two_stage_qwen_illustrij.py \
        --prompt "she sits on a neon-lit rooftop at night, city rain, holding an umbrella"

    # push the painterly refine harder / softer (0.30 subtle .. 0.60 strong)
    python examples/two_stage_qwen_illustrij.py --prompt "..." --strength 0.60

    # a specific seed, and Qwen-only (skip the illustrij refine to compare)
    python examples/two_stage_qwen_illustrij.py --prompt "..." --seed 7 --no-refine

    # full manual control — your text IS the whole positive prompt, no identity wrap
    python examples/two_stage_qwen_illustrij.py --raw \
        --prompt "2.5D anime, a black cat curled on a windowsill, neon city behind"

NSFW: Qwen-Image is censored and cannot generate explicit content (and a low-denoise
refine can't add back what the base omitted). For intimate work, run the base on an
uncensored local model instead of Qwen — this needs no ComfyUI at all:

    # single uncensored stage (illustrij makes the base AND is the register surface)
    python examples/two_stage_qwen_illustrij.py --stage1 diffusers \
        --prompt "she lies on soft sheets in delicate lingerie, warm lamplight"

    # or use a stronger NSFW base model, then refine its surface with illustrij
    python examples/two_stage_qwen_illustrij.py --stage1 diffusers \
        --stage1-model some_nsfw_sdxl --refiner illustrij --prompt "..."

Two ways to keep Qwen's composition for NSFW (both via --stage1 qwen):
  --qwen-nsfw : load the Qwen-Image NSFW LoRA on the base GGUF (slow first run).
  --qwen-aio  : swap to Phr00t's distilled Qwen-Rapid-AIO-NSFW GGUF (fast, ~8 steps).

    python examples/two_stage_qwen_illustrij.py --stage1 qwen --qwen-aio \
        --prompt "she reclines on soft sheets in delicate lingerie" --no-refine

Needs: a running ComfyUI with the Qwen GGUF set up (see comfyui_qwen_test.py) AND
the diffusers env (yurios_env python) for the illustrij stage. The two models do not
sit in VRAM together — after stage 1 we ask ComfyUI to free its VRAM, then load
illustrij. Use the yurios_env python.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from image_forge import Character, SelfieBook                     # noqa: E402
from image_forge.types import EditRequest, GenRequest             # noqa: E402
from image_forge.backends.comfyui import ComfyUIBackend           # noqa: E402
from image_forge.backends.diffusers_backend import DiffusersBackend  # noqa: E402

# Stage-1 booster — push Qwen toward the riverflow lighting/composition. The
# painterly *surface* is illustrij's job in stage 2.
QWEN_STYLE = (
    "Dramatic neon rim lighting in vivid magenta and electric cyan, glowing purple "
    "and hot-pink light catching her long dark hair, rich saturated cinematic color "
    "grade, luminous volumetric haze, ultra-detailed glossy reflective eyes with sharp "
    "catchlights, radiant skin with soft subsurface scattering, highly detailed "
    "painterly digital illustration, premium anime key visual, intricate fine detail, "
    "sharp focus, dramatic high contrast."
)
QWEN_NEG_STYLE = (
    "flat dull lighting, plain flat cel shading, low detail, simple cartoon, washed "
    "out colors, matte, soft even lighting, amateur."
)

PRESET_SCENES = [
    ("portrait", "signature", "waiting"),
    ("window", "signature", "happy"),
    ("sanctuary", "everyday", "playful"),
]


def comfy_free(host: str, port: int) -> None:
    """Ask ComfyUI to unload models + free VRAM so illustrij has room."""
    try:
        req = urllib.request.Request(
            f"http://{host}:{port}/free",
            data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=60).read()
    except Exception as e:
        print(f"  (warn: could not free ComfyUI VRAM: {e})", flush=True)


def build_prompts(character: Character, scene_prompt: str, *, raw: bool, style: bool):
    """Return (s1_pos, s1_neg, s2_pos, s2_neg) for the two stages.

    raw=False: scene_prompt is wrapped in the register + Yuri identity (recommended).
    raw=True:  scene_prompt is used verbatim as the positive prompt.
    """
    booster = (" " + QWEN_STYLE) if style else ""
    if raw:
        s1_pos = scene_prompt + booster
        s1_neg = (character.base_negative + " " + QWEN_NEG_STYLE).strip()
        s2_pos = scene_prompt
        s2_neg = character.base_negative
    else:
        s1_pos, s1_neg = character.assemble(scene_prompt + booster, negative_extra=QWEN_NEG_STYLE)
        s2_pos, s2_neg = character.assemble(scene_prompt)
    return s1_pos, s1_neg, s2_pos, s2_neg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", help="custom scene (wrapped in Yuri's identity + register)")
    ap.add_argument("--raw", action="store_true", help="use --prompt verbatim, no identity/register wrap")
    ap.add_argument("--stage1", choices=["qwen", "diffusers"], default="qwen",
                    help="base generator. 'qwen' = ComfyUI Qwen-Image (best composition, but "
                         "SFW-only — it's censored). 'diffusers' = a local uncensored model "
                         "(--stage1-model) for NSFW work.")
    ap.add_argument("--stage1-model", default="illustrij",
                    help="diffusers model key for --stage1 diffusers (uncensored, e.g. illustrij)")
    ap.add_argument("--qwen-nsfw", action="store_true",
                    help="with --stage1 qwen: load the Qwen-Image NSFW LoRA so the base can do "
                         "intimate composition (uses comfy_workflows/qwen_image_gguf_nsfw.json)")
    ap.add_argument("--lora-strength", type=float, default=0.85,
                    help="strength of the Qwen NSFW LoRA (~0.7 .. 1.0) when --qwen-nsfw")
    ap.add_argument("--qwen-aio", action="store_true",
                    help="with --stage1 qwen: use Phr00t's Qwen-Rapid-AIO-NSFW GGUF instead "
                         "(distilled, NSFW baked in; uses comfy_workflows/qwen_rapid_aio.json)")
    ap.add_argument("--aio-ckpt", default="qwen-rapid-nsfw-v9.0-Q4_K_M.gguf",
                    help="the Rapid-AIO GGUF in models/diffusion_models (for --qwen-aio)")
    ap.add_argument("--aio-steps", type=int, default=8, help="steps for --qwen-aio (distilled: 4..8)")
    ap.add_argument("--aio-cfg", type=float, default=1.0, help="cfg for --qwen-aio (distilled: ~1.0)")
    ap.add_argument("--no-style", dest="style", action="store_false", help="skip the stage-1 Qwen style booster")
    ap.add_argument("--no-refine", dest="refine", action="store_false", help="stage 1 only, skip the refine pass")
    ap.add_argument("--seed", type=int, default=100, help="seed for --prompt mode")
    ap.add_argument("--strength", type=float, default=0.50,
                    help="img2img denoise for the refine pass (0.30 subtle .. 0.60 strong)")
    ap.add_argument("--n", type=int, default=1, help="how many preset scenes (ignored with --prompt)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--ckpt", default="qwen-image-Q4_K_M.gguf")
    ap.add_argument("--refiner", default="illustrij", help="diffusers model key for stage 2")
    ap.add_argument("--cache", default="/mnt/6870C6B170C68572/AI/huggingface")
    ap.add_argument("--width", type=int, default=832)
    ap.add_argument("--height", type=int, default=1216)
    ap.add_argument("--out", default=str(ROOT / "out" / "two_stage"))
    args = ap.parse_args()

    # Refining illustrij with illustrij is pointless — collapse to a single
    # uncensored stage when stage 1 already is the refiner model. This is the
    # NSFW path: Qwen is censored, so its base can't carry explicit content and a
    # low-denoise refine can't add it back; an uncensored diffusers base can.
    refine = args.refine
    if args.stage1 == "diffusers" and args.stage1_model == args.refiner:
        if refine:
            print(f"  (stage 1 is already '{args.refiner}' — single uncensored stage, "
                  f"skipping the redundant refine)", flush=True)
        refine = False

    # Fail fast: any diffusers stage needs diffusers (the yurios_env python). The
    # Qwen stage is pure stdlib HTTP and would otherwise run for minutes under the
    # wrong interpreter before crashing. Check up front so no render is wasted.
    if (refine or args.stage1 == "diffusers") and importlib.util.find_spec("diffusers") is None:
        sys.exit(
            "diffusers not found — the local model stage needs it.\n"
            "Run with the diffusers env, e.g.:\n"
            "  /mnt/6870C6B170C68572/AI/yurios_env/bin/python "
            "examples/two_stage_qwen_illustrij.py ...")

    character = Character.load(ROOT / "characters" / "yuri.yaml")
    book = SelfieBook.load(ROOT / "templates" / "selfie.yaml")
    out = Path(args.out)
    base_dir = out / "stage1"
    base_dir.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    # Build the job list: a single custom prompt, or the preset scenes.
    jobs = []  # (label, scene_prompt, seed)
    if args.prompt:
        jobs.append(("custom", args.prompt, args.seed))
    else:
        for i, (scene, wardrobe, mood) in enumerate(PRESET_SCENES[:args.n]):
            scene_prompt, _ = book.compose(scene=scene, wardrobe=wardrobe, mood=mood, seed=100 + i)
            jobs.append((f"{scene}-{wardrobe}", scene_prompt, 100 + i))

    # ---- Stage 1: the base generator ----
    stage1_backend = None
    bases = []  # (label, base_path, s2_pos, s2_neg, seed)
    t0 = time.time()
    if args.stage1 == "qwen":
        if args.qwen_aio:
            # Distilled NSFW AIO: low steps, cfg 1.0, its own GGUF. Negatives are
            # inert at cfg 1.0 (classifier-free guidance off) — that's expected.
            wf, ckpt = "qwen_rapid_aio.json", args.aio_ckpt
            extra = {"%STEPS%": args.aio_steps, "%CFG%": args.aio_cfg}
            timeout = 900.0
        elif args.qwen_nsfw:
            # Applying a LoRA to a Q4 GGUF dequantizes hundreds of tensors on the
            # first run (minutes, on top of sampling), so allow much longer.
            wf, ckpt = "qwen_image_gguf_nsfw.json", args.ckpt
            extra = {"%LORA_STRENGTH%": args.lora_strength}
            timeout = 1800.0
        else:
            wf, ckpt, extra, timeout = "qwen_image_gguf.json", args.ckpt, None, 600.0
        comfy = ComfyUIBackend(
            host=args.host, port=args.port,
            workflow=str(ROOT / "comfy_workflows" / wf),
            checkpoint=ckpt, extra_tokens=extra, timeout=timeout)
        if not comfy.health():
            sys.exit(f"ComfyUI not reachable at http://{args.host}:{args.port} — start it first.")
    else:
        # Uncensored local base (NSFW-capable). No Qwen booster — illustrij does
        # the register surface natively; use the plain assembled register prompt.
        stage1_backend = DiffusersBackend(model=args.stage1_model, registry=str(ROOT / "models.yaml"),
                                          cache_dir=args.cache, offload="model")

    for i, (label, scene_prompt, seed) in enumerate(jobs):
        t = time.time()
        s1_pos, s1_neg, s2_pos, s2_neg = build_prompts(
            character, scene_prompt, raw=args.raw, style=args.style)
        if args.stage1 == "qwen":
            res = comfy.generate(GenRequest(
                prompt=s1_pos, negative_prompt=s1_neg, seed=seed,
                width=args.width, height=args.height))
        else:
            res = stage1_backend.generate(GenRequest(
                prompt=s2_pos, negative_prompt=s2_neg, seed=seed,
                width=args.width, height=args.height))
        base_path = base_dir / f"{time.strftime('%Y%m%d-%H%M%S')}-base-{label}-{seed}.png"
        base_path.write_bytes(res.data)
        bases.append((label, base_path, s2_pos, s2_neg, seed))
        print(f"  stage1 [{i+1}/{len(jobs)}] {label} -> {base_path.name}  ({time.time()-t:.0f}s)", flush=True)

    if not refine:
        print(f"\ndone (single stage) -> {base_dir}/  (total {time.time()-t0:.0f}s)", flush=True)
        return

    # ---- free the stage-1 model from VRAM, then load the refiner ----
    if args.stage1 == "qwen":
        print("  freeing ComfyUI VRAM for the refiner ...", flush=True)
        comfy_free(args.host, args.port)
    else:
        print("  freeing the stage-1 model from VRAM for the refiner ...", flush=True)
        stage1_backend = None
        import gc
        import torch
        gc.collect()
        torch.cuda.empty_cache()
    # Stage 2 carries the character LoRA: Qwen (stage 1) can't use the SDXL LoRA, so the
    # refine is what restores *her* trained identity (not just the base model's generic
    # face) while repainting in-register. Fuses at load like any other LoRA render.
    refiner = DiffusersBackend(model=args.refiner, registry=str(ROOT / "models.yaml"),
                               cache_dir=args.cache, lora=character.lora, offload="model")

    # ---- Stage 2: illustrij low-denoise img2img refine ----
    for i, (label, base_path, s2_pos, s2_neg, seed) in enumerate(bases):
        t = time.time()
        result = refiner.edit(EditRequest(
            image=base_path, instruction=s2_pos, negative_prompt=s2_neg,
            strength=args.strength, seed=seed))
        final = out / f"{time.strftime('%Y%m%d-%H%M%S')}-twostage-{label}-s{args.strength:.2f}.png"
        final.write_bytes(result.data)
        print(f"  stage2 [{i+1}/{len(bases)}] {label} -> {final.name}  ({time.time()-t:.0f}s)", flush=True)

    print(f"\ndone -> {out}/  (bases in {base_dir}/, total {time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
