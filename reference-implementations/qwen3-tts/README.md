# Qwen3-TTS — the convergence companion voice (TTS)

A minimal, runnable TTS service on **Qwen3-TTS** (QwenLM/Qwen3-TTS, Apache-2.0,
Jan 2026). It's the single most capable *local* option for a companion voice
because it collapses what the two sibling impls do separately into one model:

- a **fixed/preset** voice (cf. [`../kokoro`](../kokoro)) — `custom` mode, built-in timbres;
- **zero-shot cloning** of a specific identity from ~3 s of audio (cf. [`../gpt-sovits`](../gpt-sovits)) — `clone` mode;
- and a trick neither has: **designing a voice from a text description** — `design` mode.

All open-weight (0.6B / 1.7B), ~97 ms latency, streaming, 10 languages
(→ `../../book/chapters/24-voice.md` §"TTS short list").

## What it teaches

- **One model, three ways to get a voice.** A register declares its `mode`
  (`clone` / `design` / `custom`); the synth loads the right model variant and
  caches it.
- **Voice design is new.** You can author a companion's voice in *words* —
  `python -m qwen_voice design "..." "a warm, gentle young woman, slightly
  breathy"` — no reference clip, no fine-tune.
- **The eval is mode-aware** (→ ch. 24 §Evaluation, ch. 23): identity fidelity
  for `clone`, plus quality / latency / consistency for all modes.

## Setup

Single in-process model (no separate server, unlike the GPT-SoVITS impl). You
need Python 3.10+ and an NVIDIA GPU (bf16).

```bash
# 1. Use a conda env. On this machine the repo's `base` env already has a working
#    stack: Python 3.12, torch 2.9.1+cu130 (native Blackwell sm_120), qwen-tts.
conda activate base        # or: conda create -n qwen-tts python=3.11 -y && conda activate qwen-tts

# 2. Client + model deps (first synthesis downloads weights from HF, several GB).
pip install -r requirements.txt        # qwen-tts (pulls torch/transformers), soundfile, sounddevice, numpy, PyYAML
# Optional eval axes:  pip install resemblyzer

# 3. Realtime playback needs PortAudio + a libstdc++ newer than conda ships.
sudo apt install libportaudio2
#    GOTCHA (seen on conda `base` here): sounddevice fails to load PortAudio with
#    "GLIBCXX_3.4.32 not found". Fix once:
conda install -n base -c conda-forge "libstdcxx-ng>=13"
```

**Attention / FlashAttention-2:** not required. `config.yaml` uses `attn: sdpa`
(built into PyTorch). You'll see a `flash-attn is not installed` warning — it
comes from the clone-mode reference encoder only and is harmless. If you hit an
attention error, set `model.attn: eager`.

**Performance reality (measured on an RTX 5070 Ti):** generation runs at
**~1.7x real-time** after warmup (≈3 s to speak a short line), and it's the
*same* for the 0.6B and 1.7B variants (overhead-bound, not size-bound). The pip
`qwen-tts` build does **not** expose true streaming, so `live` plays
sentence-by-sentence — responsive for one-liners, not sub-second. For genuinely
realtime cloning use the **[`../gpt-sovits`](../gpt-sovits)** impl instead.

## Run

```bash
# Realtime voice terminal — type a line, hear it the instant you press Enter,
# spoken in a kind, gentle waifu voice (the `designed` register; no clip needed):
python -m qwen_voice live
python -m qwen_voice live --register soft_shy                 # or any register below

python -m qwen_voice registers                                # list registers
python -m qwen_voice say "Hey. You made it back."             # active (clone) register
python -m qwen_voice say "I'm glad you're here." --register designed
python -m qwen_voice say "..." --register preset              # built-in timbre

# design a voice from a description, ad hoc:
python -m qwen_voice design "Come here, tell me about it." \
    "A warm young woman, soft and unhurried, with a late-night breathiness."

python -m qwen_voice eval                      # clone-register eval (4 axes)
python -m qwen_voice eval --register designed  # design-register eval (3 axes)
```

### Try it end-to-end (self-contained)

The default `clone` register expects `voices/ref_default.wav`. Borrow one from
the Kokoro impl so the loop is reproducible:

```bash
# in ../kokoro:
python -m kokoro_voice say "I kept the light on. I'm really glad you're back." \
    --out ../qwen3-tts/voices/ref_default.wav
# back here — config.yaml already names that file + its transcript:
python -m qwen_voice eval
```

## Test

```bash
pytest        # splitter/config/validation run anywhere;
              # the synthesis test skips unless qwen-tts is installed
```

## What it intentionally doesn't do

- **No STT / LLM / barge-in.** TTS leg only (full voice loop → ch. 24, Build #2).
- **No native token-streaming.** Qwen3-TTS streams natively (dual-track); this
  impl does the simpler per-sentence streaming so latency is comparable across
  the three voice impls. Wiring the native stream is a runtime concern (→ ch. 19).
- **No bundled weights or voices.** Large and often not yours to redistribute;
  `voices/*.wav` is gitignored.
- **Not production-tuned.** Clarity over polish.

## Why this exists alongside Kokoro and GPT-SoVITS

Kokoro still wins on absolute minimal footprint (82M, CPU, no GPU); GPT-SoVITS
still has the deeper fine-tuning ecosystem for a locked canon voice. But for most
companion builds Qwen3-TTS is the **headline recommendation** — one Apache-2.0
model that gives you a good fixed voice, a 3-second clone, *and* a designed voice,
at low latency. The three impls together are the honest map of the trade space.

## Layout

```
config.yaml              registers (mode + per-mode inputs) + model variants
qwen_voice/
  synth.py               model wrapper: clone / design / custom, per-mode cache
  stream.py              sentence splitter (streaming core)
  live.py                realtime terminal: type a line -> speak it at once
  config.py              config + register validation/resolution
  __main__.py            CLI: live / say / design / registers / eval
eval/
  eval.py                mode-aware eval (identity / quality / latency / consistency)
  speaker.py             speaker-embedding similarity (resemblyzer, optional)
  phrases.txt
voices/                  reference clips for clone mode (gitignored)
test_qwen_voice.py
```
