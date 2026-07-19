"""Quality test for any local base model in models.yaml (esp. big quantized DiTs).

Generates a couple of on-register Yuri selfies with the chosen model so you can
compare quality across base models (illustrij vs Qwen-Image vs FLUX.2 ...).

    python examples/local_model_test.py --model qwen-image
    python examples/local_model_test.py --model flux2-dev --n 1

Big models (qwen-image, flux2-dev) download tens of GB on first run and load 4-bit
quantized (see models.yaml). Use the yurios_env python. Slow — minutes per image.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from image_forge import Character, ImageForge, SelfieBook       # noqa: E402
from image_forge.backends.diffusers_backend import DiffusersBackend  # noqa: E402

SCENES = [
    ("portrait", "signature", "waiting"),
    ("window", "signature", "happy"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="a key in models.yaml")
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--offload", default="model", choices=["model", "sequential", "none"])
    ap.add_argument("--cache", default="/mnt/6870C6B170C68572/AI/huggingface")
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1280)
    ap.add_argument("--steps", type=int)
    ap.add_argument("--out", default=str(ROOT / "out" / "modeltest"))
    args = ap.parse_args()

    t0 = time.time()
    backend = DiffusersBackend(model=args.model, registry=str(ROOT / "models.yaml"),
                               cache_dir=args.cache, offload=args.offload)
    forge = ImageForge(Character.load(ROOT / "characters" / "yuri.yaml"),
                       SelfieBook.load(ROOT / "templates" / "selfie.yaml"),
                       backend, out_dir=args.out)
    print(f"caps: {forge.capabilities()}", flush=True)

    for i, (scene, wardrobe, mood) in enumerate(SCENES[:args.n]):
        t = time.time()
        over = {"width": args.width, "height": args.height}
        if args.steps:
            over["steps"] = args.steps
        res = forge.selfie(scene=scene, wardrobe=wardrobe, mood=mood, seed=100 + i, **over)
        print(f"  [{i+1}/{args.n}] {scene} -> {res.path.name}  ({time.time()-t:.0f}s)", flush=True)

    print(f"\ndone -> {forge.out_dir}/  (total {time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
