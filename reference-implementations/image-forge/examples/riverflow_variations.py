"""Step 1 of the character-LoRA pipeline: generate N canon-frame candidates.

Calls the same model/API that made the locked register (sourceful/riverflow-v2.5-pro
on OpenRouter) with the exact manifest prompt, N times. Each call is a fresh sample,
so you get N variations of the same character concept — pick the best one to anchor
the dataset (→ lora/TRAINING.md, step 1).

    OPENROUTER_TOKEN=... python examples/riverflow_variations.py --n 5

Output: out/riverflow_variations/variation-1..N.png (Pillow-resaved, metadata stripped).
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
API = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "sourceful/riverflow-v2.5-pro"
MANIFEST = ROOT.parents[1] / "artworks/manifest.json"
REGISTER_ID = "register-anime-25d"


def api_key() -> str:
    key = os.environ.get("OPENROUTER_TOKEN", "").strip()
    if not key:
        f = Path.home() / ".config/openrouter/key"
        key = f.read_text().strip() if f.exists() else ""
    if not key:
        sys.exit("no API key: set $OPENROUTER_TOKEN or write ~/.config/openrouter/key")
    return key


def gen(key, prompt, i, out):
    body = json.dumps({"model": MODEL,
                       "messages": [{"role": "user", "content": prompt}],
                       "modalities": ["image"]}).encode()
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
            p = out / f"variation-{i}.png"
            Image.open(io.BytesIO(raw)).save(p, "PNG")   # strip upstream metadata
            return i, p.name, time.time() - t0, None
        except Exception as e:
            err = e
            time.sleep(2)
    return i, None, 0, err


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "out/riverflow_variations"))
    args = ap.parse_args()

    m = json.loads(MANIFEST.read_text())
    prompt = next(e["prompt"] for e in m["images"] if e["id"] == REGISTER_ID)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    key = api_key()

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(gen, key, prompt, i, out) for i in range(1, args.n + 1)]
        for f in as_completed(futs):
            i, name, dt, err = f.result()
            print(f"  [{i}] {'-> '+name+f'  ({dt:.0f}s)' if name else 'FAILED: '+repr(err)}", flush=True)
    print(f"done -> {out}/  (pick the best as the dataset anchor)", flush=True)


if __name__ == "__main__":
    main()
