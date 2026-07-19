"""Local Yuri asset pipeline: make N on-register img2img variations of a reference.

A reusable loop for generating local Yuri assets from an existing image (e.g. the
locked register `assets/register-anime-25d.png`). It keeps the
reference's composition and identity (img2img) while varying expression, lighting,
and seed — the practical "give me a set, same character, slightly different" pipeline.

    python examples/local_variations.py                       # 5 variations of riverflow
    python examples/local_variations.py --ref path.png -n 8 --strength 0.6 --model illustrij

Runs on the local `diffusers` backend (your GPU, uncensored). Use the yurios_env
python. Needs sd_embed for the full-length register prompt (see README).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from image_forge import Character, ImageForge, SelfieBook       # noqa: E402
from image_forge import provenance as prov                      # noqa: E402
from image_forge.backends.diffusers_backend import DiffusersBackend  # noqa: E402
from image_forge.types import EditRequest                       # noqa: E402

# A scene line matching the reference (neon megacity, seated) so img2img stays
# coherent; mood + lighting rotate per variation for visible variety.
SCENE = ("She sits on a rooftop ledge high above a neon cyberpunk megacity at night, "
         "the glowing skyline reduced to magenta and cyan bokeh behind her")
MOODS = ["happy", "shy", "playful", "tender", "sleepy", "waiting"]
LIGHTING = ["neon", "lamplit", "golden", "screenglow", "neon", "daylight"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=str(ROOT / "assets/register-anime-25d.png"))
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--strength", type=float, default=0.5,
                    help="0.4 stays close to the reference / 0.7 diverges more")
    ap.add_argument("--model", default="illustrij")
    ap.add_argument("--cache", default="/mnt/6870C6B170C68572/AI/huggingface")
    ap.add_argument("--out", default=str(ROOT / "out" / "variations"))
    ap.add_argument("--seed0", type=int, default=1000)
    args = ap.parse_args()

    backend = DiffusersBackend(model=args.model, registry=str(ROOT / "models.yaml"),
                               cache_dir=args.cache, offload="model")
    forge = ImageForge(Character.load(ROOT / "characters" / "yuri.yaml"),
                       SelfieBook.load(ROOT / "templates" / "selfie.yaml"),
                       backend, out_dir=args.out)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f"model={args.model}  ref={Path(args.ref).name}  strength={args.strength}  n={args.n}", flush=True)

    for i in range(args.n):
        seed = args.seed0 + i
        mood, light = MOODS[i % len(MOODS)], LIGHTING[i % len(LIGHTING)]
        # On-register prompt: locked register + identity + scene + this variation's mood/light.
        scene = f"{SCENE}. {forge.book.moods[mood]} {forge.book.lighting[light]}"
        positive, negative = forge.character.assemble(scene, include_character=True)
        req = EditRequest(image=Path(args.ref), instruction=positive,
                          negative_prompt=negative, strength=args.strength, seed=seed)
        res = backend.edit(req)
        res.data = prov.apply(res.data, res.meta, "strip")
        path = out / f"riverflow-var-{i+1}-{mood}-{light}-{seed}.png"
        path.write_bytes(res.data)
        print(f"  [{i+1}/{args.n}] {path.name}", flush=True)

    print(f"\ndone -> {out}/", flush=True)


if __name__ == "__main__":
    main()
