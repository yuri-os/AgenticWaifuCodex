"""CLI: python -m image_forge <command>

    python -m image_forge generate "on a snowy mountain at sunrise, red parka, laughing"
    python -m image_forge selfie --scene window --mood happy --seed 1
    python -m image_forge portrait
    python -m image_forge scenery "rainy neon megacity skyline at night"
    python -m image_forge edit out/some.png "her in the rain, looking back"
    python -m image_forge caps           # show the active backend's capabilities

Reads ./config.yaml unless --config is given. The selfie/portrait subcommands
are the calls a YuriOS agent loop makes; this CLI is just a thin wrapper on them.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import ImageForge


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="image_forge")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--backend", help="override the configured backend name")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("selfie", help="render an image 'of her'")
    for slot in ("scene", "framing", "lighting", "mood", "wardrobe"):
        s.add_argument(f"--{slot}")
    s.add_argument("--seed", type=int)

    sub.add_parser("portrait", help="render the canonical hero portrait")

    g = sub.add_parser("generate", help="render HER from a free-text prompt (uses the LoRA)")
    g.add_argument("prompt")
    g.add_argument("--seed", type=int)

    sc = sub.add_parser("scenery", help="render a worldbuilding atlas image (no figure)")
    sc.add_argument("prompt")

    e = sub.add_parser("edit", help="reference-driven re-render of an existing image")
    e.add_argument("image")
    e.add_argument("instruction")
    e.add_argument("--seed", type=int)

    sub.add_parser("caps", help="print the active backend's capabilities")

    args = ap.parse_args(argv)
    forge = ImageForge.from_config(Path(args.config))
    if args.backend:
        forge.set_backend(args.backend)

    if args.cmd == "caps":
        c = forge.capabilities()
        print(f"backend={c.name} edit={c.supports_edit} refs={c.supports_reference_images}"
              f" lora={c.supports_lora} uncensored={c.uncensored}\n  {c.notes}")
        return

    if args.cmd == "selfie":
        r = forge.selfie(scene=args.scene, framing=args.framing, lighting=args.lighting,
                         mood=args.mood, wardrobe=args.wardrobe or "everyday", seed=args.seed)
        print(r.path, "  template:", r.meta.get("template"))
    elif args.cmd == "portrait":
        print(forge.portrait().path)
    elif args.cmd == "generate":
        print(forge.generate(args.prompt, seed=args.seed).path)
    elif args.cmd == "scenery":
        print(forge.scenery(args.prompt).path)
    elif args.cmd == "edit":
        print(forge.edit(args.image, args.instruction, seed=args.seed).path)


if __name__ == "__main__":
    main()
