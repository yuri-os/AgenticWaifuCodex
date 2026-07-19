"""Sentence splitting for streaming synthesis.

The book's core voice lesson (→ ch. 24): stream TTS sentence-by-sentence so the
user hears the first words while later ones are still rendering. Time-to-first-
audio is what makes a voice feel alive; total render time barely matters if the
first sentence lands fast. This module has no model dependency so the splitter
is unit-testable on its own.
"""

from __future__ import annotations

import re

# Split after sentence-ending punctuation followed by whitespace. Keeps the
# punctuation with its sentence. Deliberately simple — good enough for prose
# replies; not a full sentence tokenizer.
_BOUNDARY = re.compile(r"(?<=[.!?…])\s+|\n+")


def split_sentences(text: str) -> list[str]:
    """Split text into sentence-ish chunks for incremental synthesis."""
    text = text.strip()
    if not text:
        return []
    parts = (p.strip() for p in _BOUNDARY.split(text))
    return [p for p in parts if p]
