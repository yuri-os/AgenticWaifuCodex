"""Sentence splitting for streaming (kept local; impls don't share code).

Same lesson as the sibling impls (→ ch. 24): synthesize sentence-by-sentence so
the first words play while the rest render. Qwen3-TTS also streams natively
(dual-track, first packet after one character); this impl does the simpler
per-sentence streaming so time-to-first-audio is comparable across the three.
"""

from __future__ import annotations

import re

_BOUNDARY = re.compile(r"(?<=[.!?…])\s+|\n+")


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return [p.strip() for p in _BOUNDARY.split(text) if p.strip()]
