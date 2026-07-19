"""Render Yuri through ComfyUI + Qwen-Image (GGUF) via image-forge.

This is the path for running a flagship DiT (Qwen-Image 20B) locally on 16 GB VRAM:
ComfyUI loads a pre-quantized GGUF incrementally (no quantize-on-load spike that
OOMs the diffusers bnb path — see models.yaml). image-forge just talks HTTP to a
running ComfyUI and substitutes %TOKENS% into comfy_workflows/qwen_image_gguf.json.

Prereqs (already set up on this box):
  - ComfyUI at /mnt/6870C6B170C68572/AI/CompfyUI/ComfyUI with the city96/ComfyUI-GGUF node
  - models/diffusion_models/qwen-image-Q4_K_M.gguf
  - models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors
  - models/vae/qwen_image_vae.safetensors
  - ComfyUI server running:  python main.py  (default 127.0.0.1:8188)

    python examples/comfyui_qwen_test.py
    python examples/comfyui_qwen_test.py --n 2 --width 1024 --height 1328
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from image_forge import Character, ImageForge, SelfieBook       # noqa: E402
from image_forge.backends.comfyui import ComfyUIBackend          # noqa: E402

SCENES = [
    ("portrait", "signature", "waiting"),
    ("window", "signature", "happy"),
    ("sanctuary", "everyday", "playful"),
]

# Qwen-Image renders "anime" flatter/cooler than illustrij (which made the locked
# reference). These cues push it back toward the riverflow register — dramatic
# neon rim-light, painterly micro-detail, high contrast. Kept here (not in
# yuri.yaml) because it's Qwen-specific prompting, not part of the locked register.
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--ckpt", default="qwen-image-Q4_K_M.gguf",
                    help="GGUF in ComfyUI/models/diffusion_models")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1328)
    ap.add_argument("--out", default=str(ROOT / "out" / "comfyui_qwen"))
    args = ap.parse_args()

    backend = ComfyUIBackend(
        host=args.host, port=args.port,
        workflow=str(ROOT / "comfy_workflows" / "qwen_image_gguf.json"),
        checkpoint=args.ckpt, timeout=600.0,
    )
    if not backend.health():
        sys.exit(f"ComfyUI not reachable at http://{args.host}:{args.port} — start it first.")

    forge = ImageForge(Character.load(ROOT / "characters" / "yuri.yaml"),
                       SelfieBook.load(ROOT / "templates" / "selfie.yaml"),
                       backend, out_dir=args.out)
    print(f"caps: {forge.capabilities()}", flush=True)

    t0 = time.time()
    for i, (scene, wardrobe, mood) in enumerate(SCENES[:args.n]):
        t = time.time()
        # Compose the scene from the book, then render via generate() so we can
        # append the Qwen style booster + negative (selfie() doesn't expose those).
        scene_prompt, chosen = forge.book.compose(
            scene=scene, wardrobe=wardrobe, mood=mood, seed=100 + i)
        res = forge.generate(scene_prompt + " " + QWEN_STYLE, negative_extra=QWEN_NEG_STYLE,
                             label=f"selfie-{scene}-{wardrobe}", seed=100 + i,
                             width=args.width, height=args.height)
        print(f"  [{i+1}/{args.n}] {scene} -> {res.path.name}  ({time.time()-t:.0f}s)", flush=True)

    print(f"\ndone -> {forge.out_dir}/  (total {time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
