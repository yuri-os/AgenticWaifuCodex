"""Convert a single-file SDXL checkpoint (.safetensors) to a diffusers-format folder.

The DreamBooth-LoRA trainer (lora/train_dreambooth_lora_sdxl.py) loads its base with
``from_pretrained``, which needs a diffusers-format *folder* (model_index.json + the
unet/vae/text_encoder subfolders) — it can't read a single Civitai-style .safetensors.
This converts one so we can train the Yuri LoRA on it (e.g. Equinox v5.0).

    python examples/convert_single_file_to_diffusers.py \
        /mnt/6870C6B170C68572/AI/checkpoints/equinox-v5.safetensors \
        /mnt/6870C6B170C68572/AI/checkpoints/equinox-v5-diffusers

Loads on CPU (no GPU needed); writes fp16 weights. ~6.5 GB out.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from diffusers import StableDiffusionXLPipeline


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    if not src.exists():
        sys.exit(f"source checkpoint not found: {src}")
    print(f"loading single-file: {src}", flush=True)
    pipe = StableDiffusionXLPipeline.from_single_file(src, torch_dtype=torch.float16)
    print(f"saving diffusers format: {dst}", flush=True)
    pipe.save_pretrained(dst)
    print("done.", flush=True)


if __name__ == "__main__":
    main()
