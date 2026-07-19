"""Transcript sanity filter (SPEC §3.2) — the last net against a keyboard the mic
heard as ". . . .". Whisper hallucinates punctuation out of non-speech; those must
never become turns in her memory. The filter rejects only what cannot be speech,
so terse-but-real utterances always pass.
"""
from __future__ import annotations

import pytest

from desktop.voice.transcript import is_meaningful_transcript


@pytest.mark.parametrize("junk", [
    None,
    "",
    "   ",
    "\n\t ",
    ".",
    "...",
    ". . . . . .",          # the literal journal line this was written against
    "... ... ...",
    "- -",
    "?!",
    "。。。",                 # full-width punctuation
])
def test_rejects_noise_and_punctuation(junk):
    assert is_meaningful_transcript(junk) is False


@pytest.mark.parametrize("real", [
    "ok",
    "mm, okay",
    "8",
    "hey, i'm back",
    "yes.",                 # one real word + a period still passes
    "가",                    # non-latin speech
    "count to 10.",
])
def test_accepts_real_speech(real):
    assert is_meaningful_transcript(real) is True
