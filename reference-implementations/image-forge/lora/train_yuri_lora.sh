#!/usr/bin/env bash
# Train the Yuri character LoRA on illustrij (SDXL) from the riverflow dataset.
#
# Uses the vendored diffusers DreamBooth-LoRA SDXL trainer (train_dreambooth_lora_sdxl.py,
# pinned to diffusers v0.37.0 + a one-line imagefolder patch). Per-image captions come
# from out/riverflow_dataset/metadata.jsonl. Tuned for a 16 GB GPU: bf16, 8-bit Adam,
# gradient checkpointing, unet-only LoRA. Run with the yurios_env python on the PATH.
#
#   bash lora/train_yuri_lora.sh
#
# Output: lora/yuri_v2/pytorch_lora_weights.safetensors  (~tens of MB).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
VENV=/mnt/6870C6B170C68572/AI/yurios_env/bin
export HF_HOME=/mnt/6870C6B170C68572/AI/huggingface

DATASET="$ROOT/out/riverflow_dataset"
OUTPUT="$HERE/yuri_v2"

"$VENV/accelerate" launch --config_file "$HERE/accelerate_config.yaml" \
  "$HERE/train_dreambooth_lora_sdxl.py" \
  --pretrained_model_name_or_path="John6666/illustrij-v50-sdxl" \
  --pretrained_vae_model_name_or_path="madebyollin/sdxl-vae-fp16-fix" \
  --dataset_name="$DATASET" \
  --image_column=image \
  --caption_column=text \
  --instance_prompt="yuri_v2" \
  --output_dir="$OUTPUT" \
  --resolution=1024 \
  --center_crop \
  --train_batch_size=1 \
  --gradient_accumulation_steps=1 \
  --gradient_checkpointing \
  --learning_rate=1e-4 \
  --lr_scheduler=constant \
  --lr_warmup_steps=0 \
  --rank=24 \
  --max_train_steps=1400 \
  --mixed_precision=bf16 \
  --use_8bit_adam \
  --checkpointing_steps=100000 \
  --seed=0
