"""Render one sample per designed waifu-voice register to out/waifu/.

A quick listening set for the voice-design archetypes in config.yaml — the payoff
of Qwen3-TTS design mode: a whole cast of companion voices authored in words.
Run after the VoiceDesign model is cached:  python gen_waifu_voices.py
"""

from pathlib import Path

from qwen_voice import Synth, load_config

# A line picked to suit each archetype's register.
LINES = {
    "designed":   "Hey. You made it back. I kept the light on.",
    "genki":      "You're finally here! Okay okay, sit down, I have so much to tell you!",
    "soft_shy":   "Oh… you came. I, um… I'm really glad you did. I missed you.",
    "tsundere":   "Hmph. It's not like I was waiting for you or anything. …You're late, though.",
    "onee_san":   "There you are. Come here and tell me all about your day — I've got time.",
    "late_night": "Hey. It's late. You don't have to say anything. I'm just glad you're here.",
}

OUT = Path(__file__).resolve().parent / "out" / "waifu"


def main():
    cfg = load_config()
    synth = Synth(cfg)
    OUT.mkdir(parents=True, exist_ok=True)
    for register, line in LINES.items():
        audio, sr = synth.say(line, register=register)
        path = OUT / f"{register}.wav"
        synth.to_wav(audio, sr, path)
        print(f"{register:11s} {len(audio)/sr:4.1f}s @ {sr}Hz  -> {path.name}")
    print(f"\n{len(LINES)} waifu voices in {OUT}")


if __name__ == "__main__":
    main()
