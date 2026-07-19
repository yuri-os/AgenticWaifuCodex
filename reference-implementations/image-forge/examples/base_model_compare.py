"""Side-by-side base-model comparison for picking a higher-quality base.

Renders the SAME prompt + seed + Yuri LoRA across several SDXL bases (and,
optionally, Qwen-Image via ComfyUI) so you can choose the best look by eye —
the workflow this project has used throughout.

  - SDXL bases (illustrij + the Illustrious-lineage candidates) all load the
    trained Yuri LoRA (characters/yuri.yaml), since the LoRA transfers within
    the Illustrious family. Each runs through the normal diffusers path, so the
    full identity/register prompt + provenance log apply.
  - Qwen-Image is a DIFFERENT architecture: the SDXL LoRA does NOT apply, so its
    panel is prompt-only identity (no trained LoRA) rendered via the ComfyUI GGUF
    path. It's bigger/slower and included only as a quality yardstick (--qwen).

Models load one at a time and VRAM is freed between them, so this fits 16 GB.

    # the four SDXL bases (downloads ~6.6 GB each the first time):
    python examples/base_model_compare.py

    # add the Qwen yardstick (start ComfyUI first — see comfyui_qwen_test.py):
    python examples/base_model_compare.py --qwen

    # your own scene + seed:
    python examples/base_model_compare.py --prompt "on a neon rooftop at night, leather jacket" --seed 7
"""

from __future__ import annotations

import argparse
import gc
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from image_forge import Character, ImageForge, SelfieBook       # noqa: E402

# SDXL bases to compare — current default first, then the Illustrious candidates.
SDXL_MODELS = ["illustrij", "equinox", "nova-anime", "yesmix"]

CACHE_DIR = "/mnt/6870C6B170C68572/AI/huggingface"

# Qwen-specific register booster (same as comfyui_qwen_test.py — Qwen renders
# flatter/cooler than the SDXL anime tunes, so nudge it toward the locked look).
QWEN_STYLE = (
    "Dramatic neon rim lighting in vivid magenta and electric cyan, rich saturated "
    "cinematic color, ultra-detailed glossy reflective eyes with sharp catchlights, "
    "radiant skin with soft subsurface scattering, highly detailed painterly digital "
    "illustration, premium anime key visual, sharp focus, dramatic high contrast."
)
QWEN_NEG_STYLE = "flat dull lighting, plain flat cel shading, low detail, washed out colors, matte, amateur."


def _free_vram():
    try:
        import torch
        gc.collect()
        torch.cuda.empty_cache()
    except Exception:
        pass


def _render_sdxl(model, character, book, scene_prompt, seed, out_dir, w, h,
                 negative_extra="", steps=None, cfg=None):
    from image_forge.backends.diffusers_backend import DiffusersBackend
    print(f"\n=== {model} ===", flush=True)
    t = time.time()
    backend = DiffusersBackend(model=model, registry=str(ROOT / "models.yaml"),
                               cache_dir=CACHE_DIR, lora=character.lora, offload="model")
    forge = ImageForge(character, book, backend, out_dir=out_dir)
    over = {"width": w, "height": h}
    if steps is not None:
        over["steps"] = steps
    if cfg is not None:
        over["cfg"] = cfg
    res = forge.generate(scene_prompt, seed=seed, label=model,
                         negative_extra=negative_extra, **over)
    print(f"  -> {res.path.name}  ({time.time()-t:.0f}s)", flush=True)
    del forge, backend
    _free_vram()
    return res.path


def _render_qwen(character, book, scene_prompt, seed, out_dir, w, h, host, port, ckpt):
    from image_forge.backends.comfyui import ComfyUIBackend
    print(f"\n=== qwen (ComfyUI, no LoRA) ===", flush=True)
    backend = ComfyUIBackend(host=host, port=port,
                             workflow=str(ROOT / "comfy_workflows" / "qwen_image_gguf.json"),
                             checkpoint=ckpt, timeout=900.0)
    if not backend.health():
        print(f"  ! ComfyUI not reachable at http://{host}:{port} — skipping Qwen "
              "(start it: see comfyui_qwen_test.py).", flush=True)
        return None
    t = time.time()
    forge = ImageForge(character, book, backend, out_dir=out_dir)
    res = forge.generate(scene_prompt + " " + QWEN_STYLE, negative_extra=QWEN_NEG_STYLE,
                         label="qwen", seed=seed, width=w, height=h)
    print(f"  -> {res.path.name}  ({time.time()-t:.0f}s)", flush=True)
    return res.path


def _contact_sheet(panels, out_path):
    """panels: list of (label, image_path). Lay out in a row with a label bar."""
    from PIL import Image, ImageDraw, ImageFont
    if not panels:
        return None
    H = 1024
    bar = 36
    imgs = []
    for label, p in panels:
        im = Image.open(p).convert("RGB")
        w = int(im.width * H / im.height)
        imgs.append((label, im.resize((w, H))))
    total_w = sum(w for _, im in [(l, i) for l, i in imgs] for w in [im.width])
    sheet = Image.new("RGB", (total_w, H + bar), (15, 15, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    x = 0
    for label, im in imgs:
        sheet.paste(im, (x, bar))
        draw.text((x + 8, 7), label, fill=(255, 90, 210), font=font)
        x += im.width
    sheet.save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", default="cowboy shot framed from mid-thigh up, wearing a skimpy "
                    "black string bikini, slim toned hourglass figure, large bust, smooth flawless "
                    "bare skin, confident flirtatious pose, looking at the viewer with a seductive "
                    "smile, sunny tropical beach background",
                    help="the scene (identity + register are added automatically). Default is a "
                         "cowboy-framed appeal shot — shows figure AND a readable face for identity")
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--lora-weight", type=float, default=None,
                    help="override the LoRA weight from yuri.yaml just for this comparison "
                         "(e.g. 0.85 for a stronger face-identity lock at full/mid framing)")
    ap.add_argument("--quality", default=None,
                    help="override the character quality_preamble for this run (e.g. a "
                         "realistic/photoreal register instead of the locked 2.5D anime one)")
    ap.add_argument("--negative-extra", default="",
                    help="extra negatives appended to base+character negatives for this run")
    ap.add_argument("--steps", type=int, default=None, help="override num_inference_steps")
    ap.add_argument("--cfg", type=float, default=None, help="override guidance_scale")
    ap.add_argument("--models", nargs="+", default=SDXL_MODELS, help="SDXL keys from models.yaml")
    ap.add_argument("--qwen", action="store_true", help="also render the Qwen yardstick via ComfyUI")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--qwen-ckpt", default="qwen-image-Q4_K_M.gguf")
    ap.add_argument("--width", type=int, default=832)
    ap.add_argument("--height", type=int, default=1216)
    ap.add_argument("--out", default=str(ROOT / "out" / "compare"))
    args = ap.parse_args()

    out_dir = Path(args.out)
    character = Character.load(ROOT / "characters" / "yuri.yaml")
    book = SelfieBook.load(ROOT / "templates" / "selfie.yaml")
    if args.lora_weight is not None and character.lora:
        character.lora = (character.lora[0], args.lora_weight)   # comparison-only override
    if args.quality is not None:
        character.quality_preamble = args.quality               # comparison-only register swap
    print(f"prompt: {args.prompt}\nseed: {args.seed}\nLoRA: {character.lora}\n"
          f"quality: {character.quality_preamble[:80]}...\n"
          f"steps/cfg: {args.steps}/{args.cfg}", flush=True)

    panels = []
    for model in args.models:
        try:
            p = _render_sdxl(model, character, book, args.prompt, args.seed, out_dir,
                             args.width, args.height, negative_extra=args.negative_extra,
                             steps=args.steps, cfg=args.cfg)
            panels.append((model, p))
        except Exception as e:
            print(f"  ! {model} failed: {e}", flush=True)

    if args.qwen:
        p = _render_qwen(character, book, args.prompt, args.seed, out_dir,
                         args.width, args.height, args.host, args.port, args.qwen_ckpt)
        if p:
            panels.append(("qwen (no LoRA)", p))

    sheet = _contact_sheet(panels, out_dir / "compare_contact_sheet.png")
    print(f"\ndone — {len(panels)} panels in {out_dir}/", flush=True)
    if sheet:
        print(f"contact sheet: {sheet}", flush=True)


if __name__ == "__main__":
    main()
