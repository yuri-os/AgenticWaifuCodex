"""Realtime voice terminal: type a line, hear it spoken in a kind waifu voice.

The smallest possible end-to-end loop on top of `Synth`: read a line from the
terminal and, the moment Enter is pressed, synthesize it sentence-by-sentence
and play each chunk through the speakers as soon as it's rendered. A background
playback thread lets sentence N+1 render while sentence N is still speaking, so
the first words start almost immediately and long lines stay responsive.

Defaults to the `designed` register — a warm, gentle young-woman voice authored
purely in words (Qwen3-TTS design mode) — so it runs with no reference clip.
Pass `--register` to drive any voice in config.yaml (genki, soft_shy, …).
"""

from __future__ import annotations

import queue
import sys
import threading

# A kind, soft waifu voice that needs no reference clip (see config.yaml).
DEFAULT_REGISTER = "designed"

_AUDIO_HINT = (
    "sounddevice is not installed (needed for realtime playback). Run:\n"
    "    pip install sounddevice\n"
    "(it needs PortAudio: `apt install libportaudio2` on Debian/Ubuntu)."
)

_PROMPT = "\033[36myou ▸\033[0m "      # cyan, matches the brand accent
_SPEAK = "\033[35m  ♪ {}\033[0m"        # magenta, what she's saying


class _Player:
    """Serial speaker playback on a worker thread, fed from the synth loop.

    Chunks are queued in order as they're rendered and played one after another,
    so synthesis of the next sentence overlaps playback of the current one.
    """

    def __init__(self):
        import sounddevice as sd  # noqa: F401  (validate early, fail with a hint)

        self._sd = sd
        self._q: queue.Queue = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while True:
            item = self._q.get()
            if item is None:        # shutdown sentinel
                self._q.task_done()
                return
            audio, sr = item
            try:
                self._sd.play(audio, sr)
                self._sd.wait()
            except Exception as e:  # don't let a playback glitch kill the loop
                print(f"\n(playback error: {e})", file=sys.stderr)
            finally:
                self._q.task_done()

    def play(self, audio, sr) -> None:
        self._q.put((audio, sr))

    def drain(self) -> None:
        """Block until everything queued so far has finished playing."""
        self._q.join()

    def close(self) -> None:
        self.drain()
        self._q.put(None)
        self._thread.join(timeout=2.0)


def _speak_line(synth, player: _Player, text: str, register: str) -> None:
    """Render `text` sentence-by-sentence, playing each chunk as it's ready."""
    spoke = False
    for chunk in synth.stream(text, register=register):
        if chunk.audio.size:
            print(_SPEAK.format(chunk.text))
            player.play(chunk.audio, chunk.sample_rate)
            spoke = True
    if spoke:
        player.drain()  # let her finish before the next prompt


def run_live(config_path=None, register: str | None = None) -> int:
    from .config import load_config
    from .synth import Synth

    cfg = load_config(config_path)
    register = register or DEFAULT_REGISTER
    cfg.register(register)  # validate up front (clear error if it's unknown)

    try:
        player = _Player()
    except ImportError as e:
        print(_AUDIO_HINT, file=sys.stderr)
        return 1

    print("Loading the voice… (first run downloads weights)")
    synth = Synth(cfg)
    # Warm the model so the first typed line isn't penalised by the cold load.
    _speak_line(synth, player, "Hi. I'm here.", register)

    print(
        f"\nRealtime voice terminal — register '{register}'.\n"
        "Type a line and press Enter to hear it. Ctrl-D or 'quit' to exit.\n"
    )
    try:
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
            _speak_line(synth, player, text, register)
    except KeyboardInterrupt:
        print()
    finally:
        player.close()
    return 0
