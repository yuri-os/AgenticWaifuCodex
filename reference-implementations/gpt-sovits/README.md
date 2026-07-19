# GPT-SoVITS — cloned companion voice (TTS)

A minimal client for **GPT-SoVITS**, the book's pick when the persona has a
*specific* voice you need to reproduce — a canon read, a reference you're
matching (→ `../../book/chapters/24-voice.md` §"Cloning a specific voice"). It
clones an identity from a short reference clip (zero-shot) or a fine-tune, where
the sibling [`../kokoro`](../kokoro) impl instead picks one fixed, un-cloned
voice. That's the whole trade: identity control vs. weight and latency.

## What it teaches

- **Cloning, not just speaking.** A voice is defined as a *pinned reference
  asset* (a clip + its transcript) and the model speaks new text in that timbre.
- **A heavy model belongs behind a seam.** GPT-SoVITS is dependency-finicky, so
  it runs as its own server (`api_v2.py`) and this impl is a thin HTTP client —
  the swappable backend pattern from ch. 26. The runtime never imports it.
- **Identity is the axis that matters.** The `eval` harness adds **identity
  fidelity** (does it still sound like her?) and a real **consistency** test
  (does the clone hold turn-to-turn?) on top of quality + latency — the cloner
  failure modes the book warns about (→ ch. 24 §Evaluation, ch. 23).

## Architecture

```
your runtime ──HTTP──> GPT-SoVITS api_v2.py ──> cloned audio
  (this client)          (own env, GPU, weights)
```

## Setup

This is **two processes**: the heavy GPT-SoVITS **server** (its own conda env,
GPU, model weights) and this lightweight **client** (any env with `requests` +
audio libs). Set up the server once; then the client talks to it over HTTP.

```
┌─ conda env: GPTSoVits ──────────┐        ┌─ conda env: base (or any) ─┐
│ upstream GPT-SoVITS repo        │  HTTP  │ this folder (the client)   │
│ python api_v2.py  :9880   <─────┼────────┤ python -m sovits_voice ... │
└─────────────────────────────────┘        └────────────────────────────┘
```

### A. Server (one-time, the heavy part)

These are the **exact steps verified working on this machine** (RTX 5070 Ti).
The `sovits` conda env already has every dependency (Python 3.10.12,
torch 2.11+cu128, pyopenjtalk, funasr, gradio 4.44.1, fastapi, uvicorn), so we
reuse it and skip `install.sh` entirely — we only need the repo + model weights.

```bash
# 1. System libraries (Debian/Ubuntu) — if not already present
sudo apt install ffmpeg libsox-dev

# 2. Clone the upstream repo (it is NOT part of this book repo). Verified location:
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 \
    https://github.com/RVC-Boss/GPT-SoVITS.git /mnt/6870C6B170C68572/AI/GPT-SoVITS
cd /mnt/6870C6B170C68572/AI/GPT-SoVITS

# 3. Download just the v2 pretrained models the default config needs (~1.1 GB)
#    into GPT_SoVITS/pretrained_models/ (the repo ships that dir empty):
conda run -n sovits python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("lj1995/GPT-SoVITS",
    local_dir="GPT_SoVITS/pretrained_models",
    allow_patterns=["chinese-roberta-wwm-ext-large/*",
                    "chinese-hubert-base/*",
                    "gsv-v2final-pretrained/*"])
PY

# 4. Start the inference API in the sovits env. Leave it running in its own terminal.
conda activate sovits
python api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml
```

Or just use the helper script in this folder, which does the pre-flight checks
(env exists, repo + v2 models present, port free) and launches it for you:

```bash
./start_server.sh                          # uses the verified defaults
PORT=9881 GSV_REPO=~/AI/GPT-SoVITS ./start_server.sh   # override via env vars
```

When it's up you'll see `Uvicorn running on http://127.0.0.1:9880`. The default
`tts_infer.yaml` uses the **v2** models (the `custom:` block) on `cuda`,
`is_half: true`. For other model versions (v2Pro / v3 / v4) download the matching
weights and edit that yaml — but v2 is the right, light default here.

> The conda env is named **`sovits`** on this machine — not the upstream README's
> generic `GPTSoVits`. `conda env list` if unsure. To rebuild from scratch
> instead of reusing it: `conda create -n GPTSoVits python=3.10 -y &&
> conda activate GPTSoVits && bash install.sh --device CU128 --source HF`.

The server must read the reference clips named in `config.yaml`. Here `ref_audio`
paths are repo-relative to *this client folder*; since the server runs locally it
resolves them fine. On a remote server, copy the clips over and use absolute
server-side paths.

### B. Client (this folder)

```bash
# Any env works; the repo's `base` conda env is fine. Install client deps:
pip install -r requirements.txt          # requests, soundfile, sounddevice, numpy, PyYAML
# Optional eval axes:  pip install resemblyzer

# GOTCHA (conda `base` on this machine): sounddevice needs a libstdc++ newer than
# conda ships, or it fails to load PortAudio (GLIBCXX_3.4.32 not found). Fix once:
#   conda install -n base -c conda-forge "libstdcxx-ng>=13"
# PortAudio system lib:  sudo apt install libportaudio2
```

Point `server.url` in `config.yaml` at the server (default already
`http://127.0.0.1:9880`), then confirm the link:

```bash
python -m sovits_voice health        # -> "http://127.0.0.1:9880: UP"
```

## Run

With the server up and the client deps installed:

```bash
python -m sovits_voice health                              # server up?
python -m sovits_voice live                                # realtime streaming terminal
python -m sovits_voice registers                           # pinned voices
python -m sovits_voice say "Hey. You made it back."        # -> out/say.wav
python -m sovits_voice say "I'm glad you're here." --register late_night
python -m sovits_voice eval                                 # 4-axis eval
```

### Realtime test (`live`)

Type a line, press Enter, hear it **streamed back as it renders**. Unlike a
fixed/design model, GPT-SoVITS actually streams: `live` calls the server with
`streaming_mode` + `raw` PCM and plays each packet the instant it arrives via a
persistent `sounddevice` output stream — so the cloned voice starts before the
sentence finishes. Every line prints its measured **time-to-first-audio** and
real-time factor, so this doubles as a latency test for the voice.

```bash
python -m sovits_voice live                    # active register's cloned voice
python -m sovits_voice live --register late_night
```

Needs `sounddevice` (in `requirements.txt`; PortAudio: `apt install libportaudio2`)
and a running server. The voice is whatever the register clones — point it at
your own waifu reference clip (or a fine-tune) in `config.yaml`.

**Measured (RTX 5070 Ti, v2 models, streaming):** first request ~11 s (cold model
warmup); **warm: ~600–860 ms time-to-first-audio at RTF ~0.56–0.64x** — i.e.
faster than real time, with the voice starting well under a second. This is the
realtime path the Qwen impl can't match (its build doesn't expose streaming).

### Try it end-to-end (self-contained)

No canon clip handy? Borrow one from the Kokoro impl so the whole loop is
reproducible: render a reference with Kokoro, drop it in `voices/`, point
`config.yaml` at it, then clone *that* with GPT-SoVITS and compare.

```bash
# in ../kokoro:
python -m kokoro_voice say "I kept the light on. I'm really glad you're back." \
    --out ../gpt-sovits/voices/ref_default.wav
# back here: config.yaml's default voice already names that file + transcript
python -m sovits_voice eval
```

## Test

```bash
pytest        # splitter/config/payload/decode run anywhere;
              # the synthesis test skips unless the server is up
```

## What it intentionally doesn't do

- **No STT / LLM / barge-in.** TTS leg only (the full voice loop → ch. 24,
  Build #2 in ch. 32).
- **No training UI.** Zero-shot and *using* a fine-tune are covered; producing a
  fine-tune (data prep with UVR, the train tab) is the upstream repo's job
  (→ ch. 24 §"Data prep is most of the quality").
- **No bundled weights or voices.** Both are large and often not yours to
  redistribute; `.wav` files in `voices/` are gitignored.
- **Not production-tuned.** Clarity over polish.

## Layout

```
config.yaml              server url + pinned voices (clip + transcript)
sovits_voice/
  client.py              HTTP client to api_v2 (stream_pcm / say / weight-switch)
  live.py                realtime streaming terminal: type a line -> stream it
  stream.py              sentence splitter (streaming core)
  config.py              config + voice/register resolution
  __main__.py            CLI: health / live / say / registers / eval
eval/
  eval.py                4-axis eval (identity / quality / latency / consistency)
  speaker.py             speaker-embedding similarity (resemblyzer, optional)
  phrases.txt
voices/                  reference clips (gitignored) + how-to
test_sovits_voice.py
```
