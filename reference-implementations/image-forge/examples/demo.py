"""End-to-end demo. Runs on the mock backend, so it needs nothing but Pillow.

    python examples/demo.py

Writes a handful of PNGs to out/ — a portrait, a few rotated selfies, a
worldbuilding render, an edit, and the same selfie generated on a swapped
backend — exercising the whole pipeline without a GPU or an API key.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))   # so `python examples/demo.py` finds the package

from image_forge import ImageForge  # noqa: E402


def main() -> None:
    forge = ImageForge.from_config(HERE / "config.yaml")
    print(f"backend: {forge.capabilities().name}  ({forge.capabilities().notes})")

    # 1. The canonical hero portrait — the source of truth (→ ch. 26).
    r = forge.portrait(seed=7)
    print("portrait      ->", r.path.name)

    # 2. A few selfies. Pin some slots; let the rest rotate (seeded).
    print("selfie        ->", forge.selfie(scene="window", mood="happy", seed=1).path.name)
    print("selfie        ->", forge.selfie(scene="kitchen", mood="shy", wardrobe="cozy", seed=2).path.name)
    print("selfie (auto) ->", forge.selfie(seed=3).path.name, "  <- everything rotated")

    # 3. The intimate tier is just another wardrobe value — never gated here;
    #    on a real run it renders only if the backend permits it (→ ch. 11).
    print("selfie (int.) ->", forge.selfie(scene="bed", wardrobe="intimate", mood="tender", seed=4).path.name)

    # 4. Worldbuilding atlas — no figure in frame (→ ch. 26).
    print("scenery       ->",
          forge.scenery("Wide establishing shot of the rainy neon megacity at night, "
                        "the sanctuary tower lit warm among cold towers.").path.name)

    # 5. Reference-driven edit: hold identity, change the scene.
    print("edit          ->", forge.edit(r.path, "her, out in the rain, looking back over her shoulder").path.name)

    # 6. Swap the generator at runtime — same forge, same character/templates.
    forge.set_backend("mock")   # e.g. ("comfyui", port=8188) or ("openrouter")
    print("after swap    ->", forge.selfie(scene="sanctuary", seed=1).path.name)

    print(f"\nwrote images to {forge.out_dir}/")


if __name__ == "__main__":
    main()
