"""Sentence splitting for streaming (kept local; impls don't share code).

Same lesson as the Kokoro impl (→ ch. 24): stream sentence-by-sentence so the
first words play while the rest render. GPT-SoVITS is heavier than Kokoro, so
time-to-first-audio matters *more* here, not less.
"""

from __future__ import annotations

import re

_BOUNDARY = re.compile(r"(?<=[.!?…])\s+|\n+")


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return [p.strip() for p in _BOUNDARY.split(text) if p.strip()]
