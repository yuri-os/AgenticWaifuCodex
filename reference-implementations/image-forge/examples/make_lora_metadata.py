"""Step 3 of the character-LoRA pipeline: turn the curated folder into a trainable
imagefolder (→ lora/TRAINING.md, step 3).

Writes metadata.jsonl ({"file_name", "text"}) from each image's .txt caption sidecar,
and moves contact_sheet.png out of the folder (an image with no caption row breaks the
HuggingFace imagefolder loader). Run after you've culled the contact sheet.

    python examples/make_lora_metadata.py
    python examples/make_lora_metadata.py --dir out/riverflow_dataset
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(ROOT / "out/riverflow_dataset"))
    args = ap.parse_args()
    ds = Path(args.dir)

    # Move the contact sheet aside — it has no caption and would break imagefolder.
    cs = ds / "contact_sheet.png"
    if cs.exists():
        aux = ds.parent / (ds.name + "_aux")
        aux.mkdir(exist_ok=True)
        cs.rename(aux / "contact_sheet.png")
        print(f"moved contact_sheet.png -> {aux}/")

    rows = []
    for png in sorted(ds.glob("*.png")):
        txt = png.with_suffix(".txt")
        if not txt.exists():
            print(f"  WARNING: no caption for {png.name}, skipping")
            continue
        rows.append({"file_name": png.name, "text": txt.read_text().strip()})

    (ds / "metadata.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print(f"wrote {ds/'metadata.jsonl'} with {len(rows)} rows")


if __name__ == "__main__":
    main()
