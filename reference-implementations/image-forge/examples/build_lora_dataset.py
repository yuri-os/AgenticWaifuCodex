"""Bootstrap a Yuri character-LoRA training set from the one locked reference.

A character LoRA needs many varied images of the *same* person. We have one canon
frame (the riverflow register), so we synthesise a varied set with IP-Adapter
(plus-face) holding her identity from that frame while txt2img drives wholly new
scenes/outfits/poses/expressions — then you curate the on-model ones and train.

Outputs, per image, a `.txt` caption (trigger + the variable content) ready for the
diffusers DreamBooth-LoRA trainer, plus a `contact_sheet.png` so you can eyeball
consistency at a glance and delete the drifters before training.

    python examples/build_lora_dataset.py                 # ~20 candidates + sheet
    python examples/build_lora_dataset.py --scale 0.7     # stronger identity lock

Run with the yurios_env python. Free other GPU users first (illustrij + the IP-Adapter
encoder want ~10 GB). Curate: open out/lora_dataset/contact_sheet.png, delete bad
PNG+TXT pairs, then point the trainer at the folder.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from image_forge import Character                              # noqa: E402
from image_forge import provenance as prov                     # noqa: E402
from image_forge.backends.diffusers_backend import DiffusersBackend  # noqa: E402
from image_forge.types import GenRequest                       # noqa: E402

REF = ROOT / "assets/register-anime-25d.png"

TRIGGER = "yuri_v2"
STYLE = "masterpiece, best quality, highly detailed 2.5D semi-realistic anime, dreamy volumetric lighting"
WHO = "1girl, cat ears, cat tail, long dark hair, choker"
NEG = ("lowres, worst quality, bad anatomy, bad hands, extra digits, deformed, "
       "text, watermark, signature, logo, ui, multiple views")

# Wide variety on purpose — scenes/outfits/poses/expressions far from the neon-ledge
# anchor, so the LoRA learns *her* (face/hair/ears) and lets the prompt drive the rest.
# (label, "outfit, scene, pose, expression")
SCENES = [
    ("cafe",      "cream knit sweater, sitting at a sunny cafe table, hands around a latte, gentle smile"),
    ("rooftop",   "techwear jacket, standing on a neon rooftop at night, hand on hip, confident look"),
    ("beach",     "light summer sundress, walking on a sunny beach, hair in the wind, happy laugh"),
    ("library",   "pleated skirt and blouse, reading a book in a quiet library, focused expression"),
    ("kitchen",   "casual tee under an apron, cooking at a stove, steam rising, cheerful smile"),
    ("park",      "long coat and scarf, walking through an autumn park, looking back over shoulder, soft smile"),
    ("bedroom",   "oversized hoodie, lying among blankets in a cozy bedroom, propped on elbow, relaxed"),
    ("rain",      "yellow raincoat, holding a clear umbrella on a rainy street, calm content expression"),
    ("gym",       "sporty crop top and leggings, stretching in a gym, determined expression"),
    ("office",    "smart blouse, seated at an office desk with a laptop, professional poised look"),
    ("forest",    "flowing fantasy dress, standing in a sunlit forest clearing, serene expression"),
    ("arcade",    "graphic hoodie, playing a glowing arcade machine, excited grin"),
    ("snow",      "padded winter coat, on a snowy street, breath visible, soft warm smile"),
    ("garden",    "floral dress, kneeling in a flower garden holding a bouquet, content expression"),
    ("car",       "casual jacket, sitting in a car passenger seat, looking out the window, thoughtful"),
    ("bookstore", "soft cardigan, browsing shelves in a warm bookstore, curious expression"),
    ("balcony",   "elegant evening dress, leaning on a balcony railing at sunset, wistful expression"),
    ("studio",    "simple fitted top, clean studio headshot on grey backdrop, neutral calm expression"),
    ("pool",      "one-piece swimsuit, sitting at the edge of a pool, feet in the water, playful smile"),
    ("street",    "denim jacket and jeans, walking a busy daytime city street, bright cheerful smile"),
]


def contact_sheet(paths, out_path, cols=5, thumb=320):
    from PIL import Image
    if not paths:
        return
    rows = math.ceil(len(paths) / cols)
    cell_w, cell_h = thumb, int(thumb * 1216 / 832)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (20, 20, 24))
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((cell_w, cell_h))
        sheet.paste(im, ((i % cols) * cell_w, (i // cols) * cell_h))
    sheet.save(out_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=str(REF))
    ap.add_argument("--model", default="illustrij")
    ap.add_argument("--cache", default="/mnt/6870C6B170C68572/AI/huggingface")
    ap.add_argument("--scale", type=float, default=0.65,
                    help="IP-Adapter identity strength (0.5 looser .. 0.8 stronger)")
    ap.add_argument("--steps", type=int, default=36)
    ap.add_argument("--seed0", type=int, default=3000)
    ap.add_argument("--out", default=str(ROOT / "out" / "lora_dataset"))
    args = ap.parse_args()

    backend = DiffusersBackend(
        model=args.model, registry=str(ROOT / "models.yaml"),
        cache_dir=args.cache, offload="none",
        ip_adapter={"repo": "h94/IP-Adapter", "subfolder": "sdxl_models",
                    "scale": args.scale,
                    "weight_name": "ip-adapter-plus-face_sdxl_vit-h.safetensors",
                    "image_encoder_subfolder": "models/image_encoder"})
    char = Character.load(ROOT / "characters" / "yuri.yaml")
    refs = [Path(args.ref)]
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    print(f"model={args.model}  scale={args.scale}  steps={args.steps}  ref={Path(args.ref).name}", flush=True)

    made = []
    for i, (label, scene) in enumerate(SCENES):
        seed = args.seed0 + i
        req = GenRequest(prompt=f"{STYLE}, {WHO}, {scene}", negative_prompt=NEG,
                         width=832, height=1216, steps=args.steps, seed=seed,
                         reference_images=refs)
        res = backend.generate(req)
        res.data = prov.apply(res.data, res.meta, "strip")
        stem = f"{i:02d}-{label}-{seed}"
        (out / f"{stem}.png").write_bytes(res.data)
        # Caption: trigger + class + the variable content (NOT the anchor's neon scene).
        (out / f"{stem}.txt").write_text(f"{TRIGGER}, {WHO}, {scene}\n")
        made.append(out / f"{stem}.png")
        print(f"  [{i+1}/{len(SCENES)}] {label} -> {stem}.png", flush=True)

    contact_sheet(made, out / "contact_sheet.png")
    print(f"\ndone -> {out}/  ({len(made)} candidates + contact_sheet.png)", flush=True)
    print("Curate: open contact_sheet.png, delete off-model PNG+TXT pairs, then train.", flush=True)


if __name__ == "__main__":
    main()
