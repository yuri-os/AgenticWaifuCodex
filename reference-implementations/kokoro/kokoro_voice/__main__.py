"""CLI for the Kokoro voice reference implementation.

    python -m kokoro_voice say "Hey. You made it back."   # render to out/say.wav
    python -m kokoro_voice say "..." --register late_night
    python -m kokoro_voice registers                       # list configured voices
    python -m kokoro_voice voices                          # list all Kokoro voices
    python -m kokoro_voice eval                             # 3-axis voice eval
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config

OUT = Path(__file__).resolve().parent.parent / "out"

# The 54 Kokoro voices, grouped by language/gender prefix. a/b=American/British
# English, j=Japanese, z=Mandarin, e=Spanish, f=French, h=Hindi, i=Italian,
# p=Brazilian Portuguese. Second letter: f=female, m=male.
ALL_VOICES = {
    "American English": [
        "af_heart", "af_alloy", "af_aoede", "af_bella", "af_jessica",
        "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky",
        "am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam",
        "am_michael", "am_onyx", "am_puck", "am_santa",
    ],
    "British English": [
        "bf_alice", "bf_emma", "bf_isabella", "bf_lily",
        "bm_daniel", "bm_fable", "bm_george", "bm_lewis",
    ],
    "Japanese": ["jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro", "jm_kumo"],
    "Mandarin": [
        "zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi",
        "zm_yunjian", "zm_yunxi", "zm_yunxia", "zm_yunyang",
    ],
    "Spanish": ["ef_dora", "em_alex", "em_santa"],
    "French": ["ff_siwis"],
    "Hindi": ["hf_alpha", "hf_beta", "hm_omega", "hm_psi"],
    "Italian": ["if_sara", "im_nicola"],
    "Brazilian Portuguese": ["pf_dora", "pm_alex", "pm_santa"],
}


def cmd_registers(args) -> int:
    cfg = load_config(args.config)
    print(f"lang_code: {cfg.lang_code}   sample_rate: {cfg.sample_rate}")
    for name, reg in cfg.registers.items():
        active = "  (active)" if name == cfg.active_register else ""
        print(f"  {name:12s} voice={reg.voice:14s} speed={reg.speed}{active}")
    return 0


def cmd_voices(args) -> int:
    for lang, voices in ALL_VOICES.items():
        print(f"\n{lang}")
        print("  " + ", ".join(voices))
    total = sum(len(v) for v in ALL_VOICES.values())
    print(f"\n{total} voices.")
    return 0


def cmd_say(args) -> int:
    from .synth import Synth

    cfg = load_config(args.config)
    synth = Synth(cfg)
    out = Path(args.out) if args.out else OUT / "say.wav"

    chunks = list(synth.stream(args.text, register=args.register))
    if not chunks:
        print("Nothing to synthesize.", file=sys.stderr)
        return 1

    audio = __import__("numpy").concatenate([c.audio for c in chunks])
    synth.to_wav(audio, out)

    ttfa = chunks[0].gen_seconds
    gen = sum(c.gen_seconds for c in chunks)
    dur = sum(c.audio_seconds for c in chunks)
    reg = cfg.register(args.register)
    print(f"voice={reg.voice} speed={reg.speed}  ->  {out}")
    print(f"  {len(chunks)} sentence(s), {dur:.1f}s audio")
    print(f"  time-to-first-audio: {ttfa*1000:.0f} ms")
    print(f"  total render: {gen:.2f}s   real-time factor: {gen/dur:.2f}x "
          f"({'faster' if gen < dur else 'slower'} than real time)")
    return 0


def cmd_eval(args) -> int:
    from eval.eval import run_eval  # type: ignore

    return run_eval(config_path=args.config, register=args.register)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="kokoro_voice", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=None, help="path to config.yaml")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("say", help="synthesize text to a wav")
    s.add_argument("text")
    s.add_argument("--register", default=None, help="register name (e.g. late_night)")
    s.add_argument("--out", default=None, help="output wav path")
    s.set_defaults(func=cmd_say)

    s = sub.add_parser("registers", help="list configured registers")
    s.set_defaults(func=cmd_registers)

    s = sub.add_parser("voices", help="list all Kokoro voices")
    s.set_defaults(func=cmd_voices)

    s = sub.add_parser("eval", help="run the 3-axis voice eval")
    s.add_argument("--register", default=None)
    s.set_defaults(func=cmd_eval)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
