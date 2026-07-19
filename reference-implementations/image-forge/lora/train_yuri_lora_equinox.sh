#!/usr/bin/env bash
# Train the Yuri character LoRA on Equinox v5.0 (SDXL) from the riverflow dataset.
#
# Same trainer/dataset/hyperparams as train_yuri_lora.sh — only the base model differs.
# The illustrij-trained LoRA transfers to Equinox (same Illustrious lineage) but the
# face drifts; this retrains on Equinox so her identity locks in on that base.
#
# Equinox v5.0 ships as a single-file Civitai checkpoint, which the diffusers trainer
# can't load directly, so convert it to a diffusers folder first:
#
#   python examples/convert_single_file_to_diffusers.py \
#       /mnt/6870C6B170C68572/AI/checkpoints/equinox-v5.safetensors \
#       /mnt/6870C6B170C68572/AI/checkpoints/equinox-v5-diffusers
#   bash lora/train_yuri_lora_equinox.sh
#
# Output: lora/yuri_v2_equinox/pytorch_lora_weights.safetensors
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
VENV=/mnt/6870C6B170C68572/AI/yurios_env/bin
export HF_HOME=/mnt/6870C6B170C68572/AI/huggingface

DATASET="$ROOT/out/riverflow_dataset"
OUTPUT="$HERE/yuri_v2_equinox"
BASE="/mnt/6870C6B170C68572/AI/checkpoints/equinox-v5-diffusers"

"$VENV/accelerate" launch --config_file "$HERE/accelerate_config.yaml" \
  "$HERE/train_dreambooth_lora_sdxl.py" \
  --pretrained_model_name_or_path="$BASE" \
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
