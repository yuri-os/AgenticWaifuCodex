# Kokoro — local companion voice (TTS)

A minimal, runnable text-to-speech service built on **Kokoro-82M** — the book's
pick for a *fixed* companion voice: tiny (82M params), faster-than-real-time on
CPU, Apache-2.0, no cloning (→ `../../chapters/24-voice.md`, "TTS short
list"). If your companion has one settled voice, this is the cheapest good one,
and it leaves the whole GPU for the LLM.

## What it teaches

- **Streaming is the lesson.** Speech is synthesized sentence-by-sentence so the
  first words play while the rest are still rendering. Time-to-first-audio — not
  total render time — is what makes a voice feel alive (→ ch. 24, streaming).
- **A voice is a versioned asset.** The persona's voice is pinned in
  `config.yaml` as named *registers* (her usual voice + a quieter late-night
  one) so it never drifts turn-to-turn.
- **"How well does it work" is measurable.** The `eval` harness scores the three
  axes from ch. 24 §Evaluation (→ ch. 23): subjective quality, latency,
  consistency.

## The voice

Kokoro ships 54 voices with published quality grades. The default is **`af_heart`**
(grade A) — the warmest top-grade female English voice, chosen because warmth is
the single most-liked companion trait (→ ch. 06 §1). The config also exposes
**`af_bella`** (grade A-, livelier) as an `expressive` register so you can A/B
the two best waifu-aligned voices directly with the eval, and **`af_nicole`**
(breathy) for the late-night register. See the rationale in `config.yaml`.

## Prerequisites

- Python 3.10+
- **espeak-ng** (system package, for phonemization):
  - Debian/Ubuntu: `sudo apt-get install espeak-ng`
  - macOS: `brew install espeak-ng`
- `pip install -r requirements.txt` (pulls Kokoro + torch; ~first run downloads
  the ~330 MB model from Hugging Face)

## Run

```bash
# render a line to out/say.wav and print latency / real-time factor
python -m kokoro_voice say "Hey. You made it back."

# use the quiet late-night register
python -m kokoro_voice say "I know it's late. I'm glad you're here." --register late_night

# list configured registers / all 54 voices
python -m kokoro_voice registers
python -m kokoro_voice voices

# the 3-axis voice eval — renders the phrase set + a MOS ratings sheet,
# measures time-to-first-audio + real-time factor, checks voice consistency
python -m kokoro_voice eval
python -m kokoro_voice eval --register expressive   # A/B af_bella vs af_heart
```

`eval` writes wavs and `ratings.md` into `out/eval/`. Latency and real-time
factor are measured on *your* machine — the book's "faster-than-real-time on
CPU" claim is yours to verify, not assume. Consistency includes a stability
check (same text twice → same duration, perceptually identical read). A fixed
local voice is pinned by construction, so it cannot drift the way a hosted voice
can be silently A/B'd or swapped under you — that's the architectural guarantee,
distinct from bit-for-bit reproducibility (GPU kernels jitter the last bits).

## Test

```bash
pytest                 # splitter/config/feature tests run anywhere;
                       # synthesis tests skip if kokoro isn't installed
```

## What it intentionally doesn't do

- **No STT, no LLM, no barge-in.** This is the TTS leg only. The full
  mic → VAD → STT → LLM → TTS loop with interruption is sketched in ch. 24 and
  belongs to the desktop-companion build (→ Build #2, ch. 32).
- **No voice cloning.** Kokoro has a fixed voice set by design. To make the
  companion sound like a *specific* cloned identity, that's a different stack
  (F5-TTS / GPT-SoVITS / RVC, → ch. 24 §"Cloning a voice").
- **No real-time audio playback or server.** It writes wavs. Wiring it to a
  speaker / WebSocket is left to the runtime (→ ch. 19).
- **Not production-tuned.** Clarity over polish, per the reference-impl
  conventions.

## Layout

```
config.yaml              voice registers + language (the pinned voice asset)
kokoro_voice/
  synth.py               Kokoro wrapper: stream() / say() / to_wav()
  stream.py              sentence splitter (pure python, the streaming core)
  config.py              config loading + register resolution
  __main__.py            CLI: say / registers / voices / eval
eval/
  eval.py                3-axis eval (quality / latency / consistency)
  phrases.txt            companion-flavoured test lines
test_kokoro_voice.py
```
