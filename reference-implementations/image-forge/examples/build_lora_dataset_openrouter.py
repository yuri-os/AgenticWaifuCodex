"""Step 2 of the character-LoRA pipeline: build the training set by reference-editing
a single canon frame with a hosted OpenRouter image-edit model (→ lora/TRAINING.md, step 2).

Any OpenRouter model that accepts an input image and returns one works here — set it with
`--model` (default `sourceful/riverflow-v2.5-pro`). The closed/hosted editors in this class
(riverflow, Google's Nano Banana, FLUX/Qwen edit endpoints) differ in how well they hold a
character; **test a few and use whichever keeps your character most consistent** to build the
set. We feed the chosen canon frame back in as the identity anchor and have the model render
her in new scenes/outfits/expressions at full quality — same person, varied context. Two
phases, because reference-editing from one frame copies the source's head tilt and expression
unless you force otherwise:

  SCENES       — varied outfit/scene/pose from the primary anchor (identity + variety).
  EXPRESSIONS  — varied head ANGLE + expression, forced, and rotated across 2-3 anchors
                 (variation-2/3/4) so tilt/expression also vary at the source. This is
                 what stops the LoRA baking in one tilt + one smile.

    OPENROUTER_TOKEN=... python examples/build_lora_dataset_openrouter.py
    python examples/build_lora_dataset_openrouter.py --model google/gemini-2.5-flash-image
    python examples/build_lora_dataset_openrouter.py --scenes-only
    python examples/build_lora_dataset_openrouter.py --expr-only

Outputs PNG + .txt caption pairs and a contact_sheet.png for culling. Curate (delete
off-model PNG+TXT pairs), then `python examples/make_lora_metadata.py` + train.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import math
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
API = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "sourceful/riverflow-v2.5-pro"
TRIGGER = "yuri_v2"
WHO = "1girl, cat ears, cat tail, long dark hair, choker"
VARDIR = ROOT / "out/riverflow_variations"

KEEP = ("Keep this EXACT character — identical face, eye colour, long flowing dark hair "
        "with an iridescent magenta-and-cyan sheen, fluffy dark cat ears and a long "
        "elegant cat tail, same high-end 2.5D semi-realistic anime art style.")

SCENE_PROMPT = KEEP + (" Only change the scene and outfit: {scene}. Full clarity on her "
                       "face. {fr}. No nudity.")
EXPR_PROMPT = KEEP + (" IMPORTANT: do NOT copy the reference's head tilt or smile — change "
                      "her head angle and expression to: {expr}. Simple clean background, "
                      "{fr}. No nudity.")

FRAMING = {"close": "Tight head-and-shoulders portrait",
           "medium": "Waist-up framing", "full": "Full-body framing"}

# (label, framing, "outfit, scene, pose, expression") — single primary anchor.
SCENES = [
    ("kitchen",   "medium", "cream knit sweater and an apron, in a bright sunny kitchen holding a coffee mug, gentle happy smile"),
    ("cafe",      "medium", "knit cardigan, sitting at a sunny cafe table with a latte, calm content smile"),
    ("beach",     "full",   "light summer sundress, walking on a sunny beach with hair in the wind, joyful laugh"),
    ("library",   "medium", "blouse and pleated skirt, reading a book in a quiet warm library, focused expression"),
    ("park",      "full",   "long coat and scarf, walking through an autumn park looking back over her shoulder, soft smile"),
    ("bedroom",   "medium", "oversized hoodie, lying among soft blankets in a cozy bedroom propped on one elbow, relaxed look"),
    ("rain",      "full",   "yellow raincoat holding a clear umbrella on a rainy city street at day, calm expression"),
    ("gym",       "full",   "sporty crop top and leggings, stretching in a bright gym, determined expression"),
    ("office",    "medium", "smart blouse, seated at a modern office desk with a laptop, poised professional look"),
    ("forest",    "full",   "flowing fantasy dress, standing in a sunlit forest clearing, serene expression"),
    ("snow",      "medium", "padded winter coat and mittens, on a snowy street with breath visible, soft warm smile"),
    ("garden",    "full",   "floral summer dress, kneeling in a flower garden holding a bouquet, content expression"),
    ("bookstore", "medium", "soft cardigan, browsing shelves in a warm cozy bookstore, curious expression"),
    ("balcony",   "full",   "elegant evening dress, leaning on a balcony railing at golden sunset, wistful expression"),
    ("studio1",   "close",  "simple fitted top, clean studio headshot on a soft grey backdrop, neutral calm expression"),
    ("studio2",   "close",  "casual t-shirt, clean studio close-up portrait, warm gentle smile, soft even light"),
    ("pool",      "full",   "one-piece swimsuit, sitting at the edge of a pool with feet in the water, playful smile"),
    ("street",    "full",   "denim jacket and jeans, walking a busy daytime city street, bright cheerful smile"),
    ("rooftopday","medium", "casual hoodie, sitting on a rooftop in the daytime with a blue sky behind, easy smile"),
]

# (label, framing, expr) — forced head-angle + expression, rotated across the anchors.
EXPRESSIONS = [
    ("lookup",    "medium", "looking up toward the sky, chin raised, head upright, soft wonder, lips slightly parted"),
    ("profile",   "close",  "head turned to a 3/4 side profile looking away to the side, calm composed expression"),
    ("laugh",     "medium", "laughing brightly with eyes closed and an open-mouth smile, head tilted back, joyful"),
    ("surprised", "close",  "surprised expression, wide eyes, raised eyebrows, mouth slightly open, head facing forward"),
    ("annoyed",   "close",  "annoyed expression, slight frown, furrowed brows, cheeks puffed, looking to the side"),
    ("sad",       "close",  "sad expression, teary glistening eyes, downturned mouth, head lowered slightly"),
    ("neutral",   "close",  "calm neutral expression, no smile, relaxed mouth, head upright facing straight ahead"),
    ("lookdown",  "close",  "looking down with lowered eyes, gentle thoughtful expression, head tilted down"),
    ("wink",      "medium", "playful wink with one eye closed and a cheeky grin, head straight"),
    ("serious",   "medium", "serious confident expression, direct intense gaze, slight smirk, head level"),
]


def api_key() -> str:
    key = os.environ.get("OPENROUTER_TOKEN", "").strip()
    if not key:
        f = Path.home() / ".config/openrouter/key"
        key = f.read_text().strip() if f.exists() else ""
    if not key:
        sys.exit("no API key: set $OPENROUTER_TOKEN or write ~/.config/openrouter/key")
    return key


def data_url(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def gen(key, model, ref_url, stem, instr, caption, out):
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": [
        {"type": "text", "text": instr},
        {"type": "image_url", "image_url": {"url": ref_url}},
    ]}], "modalities": ["image"]}).encode()
    for _ in range(3):
        try:
            req = urllib.request.Request(API, data=body, headers={
                "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            t0 = time.time()
            r = json.load(urllib.request.urlopen(req, timeout=300))
            imgs = r["choices"][0]["message"].get("images") or []
            if not imgs:
                raise RuntimeError("no image in response")
            raw = base64.b64decode(imgs[0]["image_url"]["url"].split(",", 1)[1])
            Image.open(io.BytesIO(raw)).save(out / f"{stem}.png", "PNG")
            (out / f"{stem}.txt").write_text(caption + "\n")
            return stem, time.time() - t0, None
        except Exception as e:
            err = e
            time.sleep(3)
    return stem, 0, err


def contact_sheet(out, cols=5, thumb=320):
    paths = sorted(p for p in out.glob("*.png") if p.name != "contact_sheet.png")
    if not paths:
        return
    rows = math.ceil(len(paths) / cols)
    cw, ch = thumb, int(thumb * 1216 / 832)
    sheet = Image.new("RGB", (cols * cw, rows * ch), (20, 20, 24))
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB"); im.thumbnail((cw, ch))
        sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
    sheet.save(out / "contact_sheet.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help="any OpenRouter image-edit model (accepts + returns an image); "
                         "test a few and keep whichever holds your character best")
    ap.add_argument("--ref", default=str(VARDIR / "variation-2.png"), help="primary identity anchor")
    ap.add_argument("--extra-anchors", nargs="*",
                    default=[str(VARDIR / "variation-3.png"), str(VARDIR / "variation-4.png")],
                    help="extra anchors rotated through the expression batch for pose/tilt variety")
    ap.add_argument("--scenes-only", action="store_true")
    ap.add_argument("--expr-only", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "out/riverflow_dataset"))
    args = ap.parse_args()

    key = api_key()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    primary_url = data_url(Path(args.ref))
    anchors = [primary_url] + [data_url(Path(p)) for p in args.extra_anchors if Path(p).exists()]

    jobs = []  # (ref_url, stem, instr, caption)
    if not args.expr_only:
        # Seed with the chosen canon frame itself (the rooftop anchor).
        Image.open(args.ref).convert("RGB").save(out / "00-anchor.png", "PNG")
        (out / "00-anchor.txt").write_text(
            f"{TRIGGER}, {WHO}, black techwear crop top and shorts, sitting on a neon rooftop ledge at night, looking at viewer\n")
        for i, (lbl, fr, scene) in enumerate(SCENES, start=1):
            instr = SCENE_PROMPT.format(scene=scene, fr=FRAMING[fr])
            cap = f"{TRIGGER}, {WHO}, {scene}"
            jobs.append((primary_url, f"{i:02d}-{lbl}", instr, cap))
    if not args.scenes_only:
        for i, (lbl, fr, expr) in enumerate(EXPRESSIONS, start=20):
            ref = anchors[(i - 20) % len(anchors)]      # rotate anchors for tilt variety
            instr = EXPR_PROMPT.format(expr=expr, fr=FRAMING[fr])
            cap = f"{TRIGGER}, {WHO}, {expr}, {FRAMING[fr].lower()}"
            jobs.append((ref, f"{i:02d}-{lbl}", instr, cap))

    print(f"model={args.model}  ref={Path(args.ref).name}  anchors={len(anchors)}  jobs={len(jobs)}  workers={args.workers}", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(gen, key, args.model, ru, stem, instr, cap, out) for ru, stem, instr, cap in jobs]
        for f in as_completed(futs):
            stem, dt, err = f.result()
            print(f"  {stem} {'-> ok ('+str(int(dt))+'s)' if not err else 'FAILED: '+repr(err)}", flush=True)

    contact_sheet(out)
    n = len([p for p in out.glob("*.png") if p.name != "contact_sheet.png"])
    print(f"\ndone -> {out}/  ({n} images + contact_sheet.png)", flush=True)
    print("Curate the contact sheet, delete off-model PNG+TXT pairs, then run make_lora_metadata.py.", flush=True)


if __name__ == "__main__":
    main()
