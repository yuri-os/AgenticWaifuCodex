"""Local Yuri asset pipeline #2: IP-Adapter "same Yuri, brand-new scenes".

The contrast to local_variations.py. Instead of re-rendering one image (img2img),
this generates *fresh* scenes/poses/outfits with txt2img, while an IP-Adapter holds
her identity from a reference image (here the locked register). This is the
"different things, different clothes, recognisably her" tool (→ ch. 26).

    python examples/local_ipadapter_scenes.py

Runs on the local `diffusers` backend (yurios_env python). First run downloads the
IP-Adapter weights + image encoder (~4 GB) to the HF cache.

Note on prompts: with IP-Adapter the *image* carries the identity, so the text is
kept SHORT (concise SDXL tags). That is also what avoids the long-prompt encoder
(sd_embed) — whose manual embeds don't compose with IP-Adapter's attention. Short
prompt + IP-Adapter is the clean local-consistency recipe.
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
from image_forge.types import GenRequest                        # noqa: E402

REF = ROOT.parents[1] / "artworks/registers/anime-25d-riverflow.png"

# IP-Adapter variants, low→high fidelity. "plus" (vit-h, 16 image tokens) is much
# sharper/more faithful than "base" (bigG, 4 tokens); "plus-face" focuses on the face.
ADAPTERS = {
    "base":      {"weight_name": "ip-adapter_sdxl.bin"},   # bigG encoder, auto-loaded
    "plus":      {"weight_name": "ip-adapter-plus_sdxl_vit-h.safetensors",
                  "image_encoder_subfolder": "models/image_encoder"},
    "plus-face": {"weight_name": "ip-adapter-plus-face_sdxl_vit-h.safetensors",
                  "image_encoder_subfolder": "models/image_encoder"},
}

# Concise register + identity tags (IP-Adapter reinforces the look from the anchor).
STYLE = "masterpiece, best quality, highly detailed 2.5D semi-realistic anime, dreamy volumetric lighting"
WHO = "1girl, cat ears, cat tail, long dark hair, choker"
NEG = "lowres, worst quality, bad anatomy, bad hands, extra digits, text, watermark, signature, logo, ui"

# Deliberately far from the neon-ledge reference, to show identity transfer.
SCENES = [
    ("kitchen",   "in a cozy kitchen at night, holding a warm mug, soft warm light, gentle happy smile, casual sweater"),
    ("rooftop",   "on a rooftop garden at dusk, string lights, playful grin, light breeze, casual clothes"),
    ("desk",      "at a desk with glowing computer monitors, looking back over her shoulder, shy soft smile"),
    ("bedroom",   "lying among soft blankets in a dim cozy bedroom, propped on one elbow, tender expression, oversized hoodie"),
    ("cafe",      "sitting by a rainy cafe window in the daytime, cup of coffee, calm and content, knit cardigan"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=str(REF))
    ap.add_argument("--model", default="illustrij")
    ap.add_argument("--cache", default="/mnt/6870C6B170C68572/AI/huggingface")
    ap.add_argument("--scale", type=float, default=0.5,
                    help="IP-Adapter strength: 0.4 looser identity / 0.8 stronger")
    # plus-face is the default: base/plus transfer the anchor's WHOLE-image palette
    # (riverflow's neon drowns every scene). plus-face isolates the face, so new
    # scenes keep their own natural colours while Yuri stays recognisable.
    ap.add_argument("--adapter", default="plus-face", choices=list(ADAPTERS),
                    help="base | plus (sharp but bleeds palette) | plus-face (default)")
    ap.add_argument("--steps", type=int, default=36)
    ap.add_argument("--out", default=str(ROOT / "out" / "ipadapter"))
    args = ap.parse_args()

    adapter = dict(ADAPTERS[args.adapter])
    backend = DiffusersBackend(
        model=args.model, registry=str(ROOT / "models.yaml"),
        # offload="none": all on GPU. Model CPU-offload's device hooks conflict with
        # IP-Adapter's image-encoder path here; illustrij + encoder fits 16 GB.
        cache_dir=args.cache, offload="none",
        ip_adapter={"repo": "h94/IP-Adapter", "subfolder": "sdxl_models",
                    "scale": args.scale, **adapter},
    )
    char = Character.load(ROOT / "characters" / "yuri.yaml")
    char.reference_images = [Path(args.ref)]        # the identity anchor for IP-Adapter
    forge = ImageForge(char, SelfieBook.load(ROOT / "templates" / "selfie.yaml"),
                       backend, out_dir=args.out)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    print(f"model={args.model}  adapter={args.adapter}  scale={args.scale}  "
          f"steps={args.steps}  ip-anchor={Path(args.ref).name}", flush=True)

    for i, (label, scene) in enumerate(SCENES):
        req = GenRequest(prompt=f"{STYLE}, {WHO}, {scene}", negative_prompt=NEG,
                         width=832, height=1216, steps=args.steps, seed=2000 + i,
                         reference_images=char.reference_images)
        res = backend.generate(req)
        res.data = prov.apply(res.data, res.meta, "strip")
        path = out / f"ipadapter-{args.adapter}-{i+1}-{label}-{2000+i}.png"
        path.write_bytes(res.data)
        print(f"  [{i+1}/{len(SCENES)}] {label} -> {path.name}", flush=True)

    print(f"\ndone -> {out}/", flush=True)


if __name__ == "__main__":
    main()
