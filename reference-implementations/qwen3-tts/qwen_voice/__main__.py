"""CLI for the Qwen3-TTS voice reference implementation.

    python -m qwen_voice live                                    # realtime voice terminal
    python -m qwen_voice say "Hey. You made it back."            # active register
    python -m qwen_voice say "..." --register designed           # voice-from-text
    python -m qwen_voice say "..." --register preset              # built-in timbre
    python -m qwen_voice design "Hi there." "a bright, cheerful young woman"
    python -m qwen_voice registers
    python -m qwen_voice eval [--register designed]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from .config import load_config

OUT = Path(__file__).resolve().parent.parent / "out"


def cmd_registers(args) -> int:
    cfg = load_config(args.config)
    print(f"language: {cfg.language}   device: {cfg.device}   dtype: {cfg.dtype}")
    for name, reg in cfg.registers.items():
        active = "  (active)" if name == cfg.active_register else ""
        detail = {"clone": f"ref={reg.ref_audio}", "design": f"instruct={reg.instruct!r}",
                  "custom": f"speaker={reg.speaker}"}[reg.mode]
        print(f"  {name:10s} mode={reg.mode:7s} {detail}{active}")
    return 0


def _say(synth, text, register, out):
    chunks = list(synth.stream(text, register=register))
    if not chunks:
        print("Nothing to synthesize.", file=sys.stderr)
        return None
    audio = np.concatenate([c.audio for c in chunks])
    sr = chunks[0].sample_rate
    synth.to_wav(audio, sr, out)
    ttfa = chunks[0].gen_seconds
    gen = sum(c.gen_seconds for c in chunks)
    dur = sum(c.audio_seconds for c in chunks)
    print(f"  -> {out}  ({dur:.1f}s audio @ {sr} Hz)")
    print(f"  time-to-first-audio: {ttfa*1000:.0f} ms   real-time factor: {gen/dur:.2f}x")
    return out


def cmd_say(args) -> int:
    from .synth import Synth

    cfg = load_config(args.config)
    out = Path(args.out) if args.out else OUT / "say.wav"
    return 0 if _say(Synth(cfg), args.text, args.register, out) else 1


def cmd_design(args) -> int:
    """Ad-hoc voice design: synthesize TEXT in a voice described by INSTRUCT."""
    from .config import Register
    from .synth import Synth

    cfg = load_config(args.config)
    synth = Synth(cfg)
    # build a throwaway design register from the CLI args
    reg = Register(name="_cli", mode="design", instruct=args.instruct)
    cfg.registers["_cli"] = reg  # type: ignore[index]
    out = Path(args.out) if args.out else OUT / "design.wav"
    return 0 if _say(synth, args.text, "_cli", out) else 1


def cmd_live(args) -> int:
    """Realtime terminal: type a line, hear it spoken at once in a waifu voice."""
    from .live import run_live

    return run_live(config_path=args.config, register=args.register)


def cmd_eval(args) -> int:
    from eval.eval import run_eval  # type: ignore

    return run_eval(config_path=args.config, register=args.register)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="qwen_voice", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("say", help="synthesize with a configured register")
    s.add_argument("text")
    s.add_argument("--register", default=None)
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_say)

    s = sub.add_parser("design", help="design a voice from a text description")
    s.add_argument("text")
    s.add_argument("instruct", help="natural-language voice description")
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_design)

    s = sub.add_parser("live", help="realtime terminal: type a line, hear it spoken")
    s.add_argument("--register", default=None,
                   help="voice register (default: a kind, gentle designed voice)")
    s.set_defaults(func=cmd_live)

    s = sub.add_parser("registers", help="list configured registers")
    s.set_defaults(func=cmd_registers)

    s = sub.add_parser("eval", help="run the voice eval")
    s.add_argument("--register", default=None)
    s.set_defaults(func=cmd_eval)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
