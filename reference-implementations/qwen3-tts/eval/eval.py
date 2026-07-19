"""Voice eval for Qwen3-TTS (→ ch. 24 §Evaluation, ch. 23).

Mode-aware. For a CLONE register it scores all four axes; for design/custom
registers there's no target identity, so the identity axis is skipped and the
rest still run:

  0. IDENTITY FIDELITY  — clone mode only: cosine similarity to the reference
                          clip's speaker embedding.
  1. SUBJECTIVE QUALITY — render the phrase set + a MOS ratings sheet.
  2. LATENCY            — time-to-first-audio + real-time factor (the 97 ms claim
                          is yours to verify on your hardware).
  3. CONSISTENCY        — mean pairwise speaker-similarity across renders (does
                          the voice hold turn-to-turn?).

Identity + consistency need resemblyzer (optional); they skip without it.
"""

from __future__ import annotations

import itertools
import statistics
import sys
from pathlib import Path

import numpy as np

from . import speaker

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "eval"
PHRASES = Path(__file__).resolve().parent / "phrases.txt"


def load_phrases() -> list[str]:
    out = []
    for ln in PHRASES.read_text().splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            out.append(ln)
    return out


def _load_ref(path: Path):
    import soundfile as sf

    audio, sr = sf.read(str(path), dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    return audio.astype(np.float32), sr


def run_eval(config_path=None, register=None) -> int:
    from qwen_voice import Synth, load_config

    cfg = load_config(config_path)
    reg = cfg.register(register)
    synth = Synth(cfg)
    phrases = load_phrases()
    OUT.mkdir(parents=True, exist_ok=True)

    print(f"Qwen3-TTS eval — register={reg.name} mode={reg.mode} "
          f"model={cfg.model_for(reg.mode)}")
    print(f"{len(phrases)} phrases -> {OUT}\n")

    use_spk = speaker.available()
    is_clone = reg.mode == "clone"
    if not use_spk:
        print("(resemblyzer not installed — identity/consistency axes skipped)\n")

    ref_emb = None
    if use_spk and is_clone and reg.ref_path() and reg.ref_path().exists():
        ref_audio, ref_sr = _load_ref(reg.ref_path())
        ref_emb = speaker.embed(ref_audio, ref_sr)

    ttfas, rtfs, embeds, id_sims = [], [], [], []
    for i, phrase in enumerate(phrases):
        chunks = list(synth.stream(phrase, register=register))
        audio = np.concatenate([c.audio for c in chunks])
        sr = chunks[0].sample_rate
        path = OUT / f"{i:02d}.wav"
        synth.to_wav(audio, sr, path)

        ttfa = chunks[0].gen_seconds
        gen = sum(c.gen_seconds for c in chunks)
        dur = sum(c.audio_seconds for c in chunks)
        rtf = gen / dur if dur else 0.0
        ttfas.append(ttfa)
        rtfs.append(rtf)

        sim_str = ""
        if use_spk:
            emb = speaker.embed(audio, sr)
            embeds.append(emb)
            if ref_emb is not None:
                s = speaker.cosine(emb, ref_emb)
                id_sims.append(s)
                sim_str = f"  id={s:.3f}"
        print(f"  {path.name}  ttfa={ttfa*1000:5.0f}ms  rtf={rtf:4.2f}x  "
              f"{dur:4.1f}s{sim_str}  «{phrase[:38]}»")

    print("\n" + "=" * 60)
    if use_spk and id_sims:
        m = statistics.mean(id_sims)
        print("AXIS 0 — IDENTITY FIDELITY (vs reference clip)")
        print(f"  mean speaker-similarity: {m:.3f}  (min {min(id_sims):.3f})  "
              f"[>0.80 strong, 0.75–0.80 recognizable, <0.75 weak]")
    print("AXIS 2 — LATENCY (measured on this machine)")
    print(f"  time-to-first-audio: median {statistics.median(ttfas)*1000:.0f} ms "
          f"(max {max(ttfas)*1000:.0f} ms)")
    print(f"  real-time factor:    median {statistics.median(rtfs):.2f}x "
          f"({'faster' if statistics.median(rtfs) < 1 else 'slower'} than real time)")
    if use_spk and len(embeds) >= 2:
        sims = [speaker.cosine(a, b) for a, b in itertools.combinations(embeds, 2)]
        print("AXIS 3 — CONSISTENCY (does the voice hold turn-to-turn?)")
        print(f"  mean pairwise speaker-similarity across renders: "
              f"{statistics.mean(sims):.3f} (higher = steadier; >0.85 is locked)")
    print("AXIS 1 — SUBJECTIVE QUALITY")
    sheet = write_ratings_sheet(phrases, reg)
    print(f"  {len(phrases)} samples in {OUT}; rate them in {sheet.name}")
    print("=" * 60)
    return 0


def write_ratings_sheet(phrases, reg) -> Path:
    sheet = OUT / "ratings.md"
    lines = [
        f"# Qwen3-TTS MOS listen test — register `{reg.name}` (mode {reg.mode})",
        "",
        "Play each clip in `out/eval/` and score 1–5 (1=robotic, 5=alive).",
        "Judge prosody, not word accuracy (→ ch. 24).",
        "",
        "| clip | score (1–5) | notes |",
        "|------|-------------|-------|",
    ]
    for i in range(len(phrases)):
        lines.append(f"| {i:02d}.wav |  |  |")
    lines += ["", "**Mean MOS:** ___ / 5", ""]
    sheet.write_text("\n".join(lines))
    return sheet


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    raise SystemExit(run_eval())
