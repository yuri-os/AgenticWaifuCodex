"""CLI for the GPT-SoVITS voice client.

    python -m sovits_voice health                          # is the server up?
    python -m sovits_voice live                             # realtime streaming terminal
    python -m sovits_voice say "Hey. You made it back."    # clone -> out/say.wav
    python -m sovits_voice say "..." --register late_night
    python -m sovits_voice registers                       # list pinned voices
    python -m sovits_voice eval                             # 4-axis voice eval

Requires a running GPT-SoVITS api_v2 server (see README).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from .config import load_config

OUT = Path(__file__).resolve().parent.parent / "out"


def cmd_health(args) -> int:
    from .client import SovitsClient

    cfg = load_config(args.config)
    up = SovitsClient(cfg).health()
    print(f"{cfg.server_url}: {'UP' if up else 'DOWN'}")
    return 0 if up else 2


def cmd_registers(args) -> int:
    cfg = load_config(args.config)
    print(f"server: {cfg.server_url}   sample_rate: {cfg.sample_rate}")
    for reg, vname in cfg.registers.items():
        v = cfg.voices[vname]
        active = "  (active)" if reg == cfg.active_register else ""
        ft = " [fine-tuned]" if (v.gpt_weights or v.sovits_weights) else " [zero-shot]"
        print(f"  {reg:12s} -> {vname:12s} ref={v.ref_audio}{ft}{active}")
    return 0


def cmd_say(args) -> int:
    from .client import SovitsClient

    cfg = load_config(args.config)
    client = SovitsClient(cfg)
    if not client.health():
        print(f"Server not reachable at {cfg.server_url}. See README.", file=sys.stderr)
        return 2

    chunks = list(client.stream(args.text, register=args.register))
    if not chunks:
        print("Nothing to synthesize.", file=sys.stderr)
        return 1
    out = Path(args.out) if args.out else OUT / "say.wav"
    client.to_wav(np.concatenate([c.audio for c in chunks]), out)

    ttfa = chunks[0].gen_seconds
    gen = sum(c.gen_seconds for c in chunks)
    dur = sum(c.audio_seconds for c in chunks)
    voice = cfg.voice_for_register(args.register)
    print(f"voice={voice.name}  ->  {out}")
    print(f"  {len(chunks)} sentence(s), {dur:.1f}s audio")
    print(f"  time-to-first-audio: {ttfa*1000:.0f} ms")
    print(f"  total render: {gen:.2f}s   real-time factor: {gen/dur:.2f}x")
    return 0


def cmd_live(args) -> int:
    """Realtime streaming terminal: type a line, hear it the moment you hit Enter."""
    from .live import run_live

    return run_live(config_path=args.config, register=args.register)


def cmd_eval(args) -> int:
    from eval.eval import run_eval  # type: ignore

    return run_eval(config_path=args.config, register=args.register)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sovits_voice", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=None, help="path to config.yaml")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("health", help="check the server is up")
    s.set_defaults(func=cmd_health)

    s = sub.add_parser("say", help="clone-synthesize text to a wav")
    s.add_argument("text")
    s.add_argument("--register", default=None)
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_say)

    s = sub.add_parser("live", help="realtime streaming terminal: type a line, hear it")
    s.add_argument("--register", default=None)
    s.set_defaults(func=cmd_live)

    s = sub.add_parser("registers", help="list pinned voices")
    s.set_defaults(func=cmd_registers)

    s = sub.add_parser("eval", help="run the 4-axis voice eval")
    s.add_argument("--register", default=None)
    s.set_defaults(func=cmd_eval)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
