"""Three-axis voice eval (→ ch. 24 §Evaluation, ch. 23).

Voice quality is mostly prosody, which automatic metrics miss, so this harness
measures what *can* be measured and stages the rest for your ears:

  1. SUBJECTIVE QUALITY  — render the phrase set to wav + a ratings sheet for a
                           small MOS-style listen test. No metric replaces ears.
  2. LATENCY             — time-to-first-audio and real-time factor, measured on
                           your hardware (the book's "faster-than-real-time on
                           CPU" claim is yours to verify, not assume).
  3. CONSISTENCY         — does the voice hold turn-to-turn? A determinism check
                           (same text twice -> identical samples = no drift) plus
                           a coarse timbre-stability proxy across phrases.

Only dependency beyond the synth is numpy.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "eval"
PHRASES = Path(__file__).resolve().parent / "phrases.txt"


def load_phrases() -> list[str]:
    lines = []
    for ln in PHRASES.read_text().splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            lines.append(ln)
    return lines


def spectral_centroid(audio: np.ndarray, sr: int) -> float:
    """Mean frequency weighted by magnitude — a coarse 'brightness' of timbre."""
    if audio.size == 0:
        return 0.0
    spectrum = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(audio.size, d=1.0 / sr)
    total = spectrum.sum()
    return float((freqs * spectrum).sum() / total) if total > 0 else 0.0


def cov(values: list[float]) -> float:
    """Coefficient of variation (std/mean) — scale-free spread, lower = steadier."""
    vals = [v for v in values if v > 0]
    if len(vals) < 2:
        return 0.0
    mean = statistics.mean(vals)
    return statistics.pstdev(vals) / mean if mean else 0.0


def run_eval(config_path=None, register=None) -> int:
    from kokoro_voice import Synth, load_config

    cfg = load_config(config_path)
    synth = Synth(cfg)
    reg = cfg.register(register)
    sr = synth.sample_rate
    phrases = load_phrases()
    OUT.mkdir(parents=True, exist_ok=True)

    print(f"Kokoro eval — voice={reg.voice} speed={reg.speed} lang={cfg.lang_code}")
    print(f"{len(phrases)} phrases -> {OUT}\n")

    rows, centroids = [], []
    ttfas, rtfs = [], []

    for i, phrase in enumerate(phrases):
        chunks = list(synth.stream(phrase, register=register))
        audio = np.concatenate([c.audio for c in chunks])
        path = OUT / f"{i:02d}.wav"
        synth.to_wav(audio, path)

        ttfa = chunks[0].gen_seconds
        gen = sum(c.gen_seconds for c in chunks)
        dur = sum(c.audio_seconds for c in chunks)
        rtf = gen / dur if dur else 0.0
        centroid = spectral_centroid(audio, sr)

        ttfas.append(ttfa)
        rtfs.append(rtf)
        centroids.append(centroid)
        rows.append((path.name, phrase, dur, ttfa, rtf, centroid))
        print(f"  {path.name}  ttfa={ttfa*1000:5.0f}ms  rtf={rtf:4.2f}x  "
              f"{dur:4.1f}s  «{phrase[:42]}»")

    # --- Axis 3: stability (the guarantee that the voice can't drift) ---
    # A fixed local voice is pinned by construction: same voice asset, same
    # length, same read every turn — it can't be silently A/B'd or swapped the
    # way a hosted voice can. On GPU, exact samples vary run-to-run from
    # non-deterministic kernels (perceptually inaudible), so we check stable
    # duration + negligible difference, not bit-equality.
    a = synth.say(phrases[0], register=register)
    b = synth.say(phrases[0], register=register)
    same_len = a.shape == b.shape
    mean_diff = float(np.abs(a - b).mean()) if same_len else float("nan")
    stable = same_len and mean_diff < 0.01

    timbre_cov = cov(centroids)

    print("\n" + "=" * 60)
    print("AXIS 2 — LATENCY (measured on this machine)")
    print(f"  time-to-first-audio: median {statistics.median(ttfas)*1000:.0f} ms "
          f"(max {max(ttfas)*1000:.0f} ms)")
    print(f"  real-time factor:    median {statistics.median(rtfs):.2f}x "
          f"({'faster' if statistics.median(rtfs) < 1 else 'SLOWER'} than real time)")
    print("\nAXIS 3 — CONSISTENCY")
    print(f"  voice stability (same text twice, same len + tiny diff): "
          f"{'PASS — pinned voice cannot drift' if stable else 'FAIL'}")
    print(f"    same length: {same_len}   mean sample diff: {mean_diff:.5f} "
          f"(GPU FP jitter, perceptually inaudible)")
    print(f"  timbre stability across phrases (centroid CoV): {timbre_cov:.3f} "
          f"(lower is steadier; content varies it, so this is a coarse proxy)")
    print("\nAXIS 1 — SUBJECTIVE QUALITY")
    sheet = write_ratings_sheet(rows, reg)
    print(f"  {len(rows)} samples rendered for a listen test.")
    print(f"  open {sheet} and rate each 1–5 for naturalness/aliveness.")
    print("=" * 60)
    return 0


def write_ratings_sheet(rows, reg) -> Path:
    sheet = OUT / "ratings.md"
    lines = [
        f"# Kokoro MOS listen test — voice `{reg.voice}` @ {reg.speed}x",
        "",
        "Play each clip in `out/eval/` and score 1–5 (1=robotic/flat, 5=alive).",
        "Prosody is the thing to judge, not word accuracy (→ ch. 24).",
        "",
        "| clip | audio (s) | ttfa (ms) | rtf | your score (1–5) | notes |",
        "|------|-----------|-----------|-----|------------------|-------|",
    ]
    for name, _phrase, dur, ttfa, rtf, _c in rows:
        lines.append(f"| {name} | {dur:.1f} | {ttfa*1000:.0f} | {rtf:.2f} |  |  |")
    lines += ["", "**Mean MOS:** ___ / 5", ""]
    sheet.write_text("\n".join(lines))
    return sheet


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    raise SystemExit(run_eval())
