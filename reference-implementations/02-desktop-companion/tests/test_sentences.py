"""Incremental sentence splitting (SPEC §4.1) — the streaming-TTS unit."""
from __future__ import annotations

from desktop.voice.sentences import cut_sentences


def test_complete_sentence_cut_remainder_kept():
    done, rest = cut_sentences("Hey there. How are y")
    assert done == ["Hey there."]
    assert rest == "How are y"


def test_no_boundary_everything_pending():
    done, rest = cut_sentences("still writing this")
    assert done == []
    assert rest == "still writing this"


def test_multiple_sentences():
    done, rest = cut_sentences("One. Two! Three? four")
    assert done == ["One.", "Two!", "Three?"]
    assert rest == "four"


def test_newline_is_a_boundary():
    done, rest = cut_sentences("line one\nline two still going")
    assert done == ["line one"]
    assert rest == "line two still going"
