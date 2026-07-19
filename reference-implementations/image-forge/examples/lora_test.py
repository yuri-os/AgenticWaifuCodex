"""Step 5 check: prove the trained Yuri LoRA holds identity on wholly new prompts.

Loads illustrij with the LoRA fused (the DiffusersBackend `lora` arg) and renders a
few scenes far from anything in the training set. If she's recognisably the same
person across all of them, the LoRA works — wire it into characters/yuri.yaml.

    python examples/lora_test.py
    python examples/lora_test.py --weight 0.8 --lora lora/yuri_v2/pytorch_lora_weights.safetensors
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from image_forge import provenance as prov                         # noqa: E402
from image_forge.backends.diffusers_backend import DiffusersBackend  # noqa: E402
from image_forge.types import GenRequest                           # noqa: E402

TRIGGER = "yuri_v2"
STYLE = "masterpiece, best quality, highly detailed 2.5D semi-realistic anime"
WHO = "1girl, cat ears, cat tail, long dark hair, choker"
NEG = "lowres, worst quality, bad anatomy, bad hands, extra digits, text, watermark"

# Deliberately unlike the training scenes, to test generalisation.
SCENES = [
    ("summit",  "on a snowy mountain summit at sunrise, red puffer parka, laughing"),
    ("space",   "inside a futuristic spaceship cockpit, sleek sci-fi flight suit, focused"),
    ("kimono",  "in a traditional japanese garden in autumn, elegant kimono, serene smile"),
    ("knight",  "as a fantasy knight in ornate armor in a castle hall, confident"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lora", default=str(ROOT / "lora/yuri_v2/pytorch_lora_weights.safetensors"))
    ap.add_argument("--weight", type=float, default=0.9)
    ap.add_argument("--model", default="illustrij")
    ap.add_argument("--cache", default="/mnt/6870C6B170C68572/AI/huggingface")
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--out", default=str(ROOT / "out/lora_test"))
    args = ap.parse_args()

    backend = DiffusersBackend(model=args.model, registry=str(ROOT / "models.yaml"),
                               cache_dir=args.cache, offload="model",
                               lora=(args.lora, args.weight))
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    print(f"model={args.model}  lora={Path(args.lora).name}  weight={args.weight}", flush=True)

    for i, (label, scene) in enumerate(SCENES):
        req = GenRequest(prompt=f"{TRIGGER}, {STYLE}, {WHO}, {scene}", negative_prompt=NEG,
                         width=832, height=1216, steps=args.steps, seed=4000 + i)
        res = backend.generate(req)
        res.data = prov.apply(res.data, res.meta, "strip")
        p = out / f"lora-{i}-{label}.png"
        p.write_bytes(res.data)
        print(f"  [{i+1}/{len(SCENES)}] {label} -> {p.name}", flush=True)

    print(f"\ndone -> {out}/", flush=True)


if __name__ == "__main__":
    main()
