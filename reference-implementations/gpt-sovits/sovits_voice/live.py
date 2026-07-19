"""Realtime test terminal for GPT-SoVITS: type a line, hear it streamed back.

The point of this impl over the Qwen one: GPT-SoVITS *actually* streams. We hit
the api_v2 server with ``streaming_mode`` + ``raw`` PCM and play each packet the
instant it arrives through a persistent ``sounddevice`` output stream, so the
voice starts before the sentence has finished rendering. Each line prints its
measured **time-to-first-audio** and real-time factor — so this doubles as a
latency test for the cloning voice (→ ch. 24).

The voice is whatever the active register clones (config.yaml) — point it at your
waifu reference clip or a fine-tune. Type a line, press Enter, hear it at once.
"""

from __future__ import annotations

import sys
import time

_AUDIO_HINT = (
    "sounddevice is not installed (needed for realtime playback). Run:\n"
    "    pip install sounddevice\n"
    "(it needs PortAudio: `apt install libportaudio2` on Debian/Ubuntu)."
)

_PROMPT = "\033[36myou ▸\033[0m "      # cyan, matches the brand accent
_INFO = "\033[2m  {}\033[0m"            # dim, latency line


def _speak_line(client, stream, text: str, register: str) -> None:
    """Stream `text` from the server, playing PCM as it lands; report latency."""
    t0 = time.perf_counter()
    ttfa = None
    frames = 0
    for chunk in client.stream_pcm(text, register=register):
        if chunk.size == 0:
            continue
        if ttfa is None:
            ttfa = time.perf_counter() - t0
        frames += chunk.size
        stream.write(chunk.reshape(-1, 1))
    if ttfa is None:
        print(_INFO.format("(no audio returned)"))
        return
    sr = stream.samplerate
    total = time.perf_counter() - t0
    dur = frames / sr
    rtf = total / dur if dur else 0.0
    print(_INFO.format(
        f"time-to-first-audio: {ttfa*1000:.0f} ms   {dur:.1f}s audio   RTF {rtf:.2f}x"))


def run_live(config_path=None, register: str | None = None) -> int:
    from .client import SovitsClient
    from .config import load_config

    cfg = load_config(config_path)
    register = register or cfg.active_register
    voice = cfg.voice_for_register(register)  # validates register early

    client = SovitsClient(cfg)
    if not client.health():
        print(f"GPT-SoVITS server not reachable at {cfg.server_url}.\n"
              "Start the api_v2 server first (see README).", file=sys.stderr)
        return 2

    try:
        import sounddevice as sd
    except ImportError:
        print(_AUDIO_HINT, file=sys.stderr)
        return 1

    stream = sd.OutputStream(samplerate=cfg.sample_rate, channels=1, dtype="float32")
    stream.start()
    try:
        # Warm the server (first request loads the model + ref) so the first
        # typed line isn't penalised by a cold start.
        print(f"Cloning voice '{voice.name}' — warming the server…")
        _speak_line(client, stream, "Hi. I'm here.", register)

        print(
            f"\nGPT-SoVITS realtime terminal — voice '{voice.name}' @ {cfg.sample_rate} Hz.\n"
            "Type a line and press Enter to hear it streamed. Ctrl-D or 'quit' to exit.\n"
        )
        while True:
            try:
                text = input(_PROMPT)
            except EOFError:
                print()
                break
            text = text.strip()
            if not text:
                continue
            if text.lower() in {"quit", "exit", ":q"}:
                break
            try:
                _speak_line(client, stream, text, register)
            except Exception as e:  # keep the loop alive on a server hiccup
                print(f"  (error: {e})", file=sys.stderr)
    except KeyboardInterrupt:
        print()
    finally:
        stream.stop()
        stream.close()
    return 0
