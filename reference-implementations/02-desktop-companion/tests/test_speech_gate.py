"""SpeechGate (SPEC §3.4) — the debounce that stops a mechanical keyboard from
counting as speech. The bug it fixes: one high-energy transient (a keystroke over
her voice) fired a barge-in or a junk turn. The gate only acts on a *sustained*
run of speech frames, and holds barge-in to a higher bar than a fresh turn.
"""
from __future__ import annotations

from desktop.voice.speech_gate import SpeechGate


def _feed(gate: SpeechGate, pattern: str, *, speaking: bool = False) -> list[str]:
    """Drive the gate with a string of '#' (speech) / '.' (silence) frames,
    returning the events it fired in order."""
    events = []
    for ch in pattern:
        ev = gate.push(ch == "#", speaking=speaking)
        if ev is not None:
            events.append(ev)
    return events


def test_single_keystroke_transient_is_not_an_onset():
    # one or two lone speech frames (a key click) never clear the onset bar
    gate = SpeechGate(onset_frames=3)
    assert _feed(gate, "#.#..#.") == []
    assert not gate.active and not gate.confirmed


def test_sustained_speech_confirms_an_onset():
    gate = SpeechGate(onset_frames=3)
    events = _feed(gate, "###")               # three in a row → a real turn
    assert events == ["onset"]
    assert gate.active and gate.confirmed


def test_barge_in_needs_more_confidence_than_an_onset():
    # while she's speaking, the onset-length run must NOT interrupt her…
    gate = SpeechGate(onset_frames=3, bargein_frames=5)
    assert _feed(gate, "###", speaking=True) == []
    assert not gate.active
    # …but a longer sustained run does
    assert _feed(gate, "##", speaking=True) == ["bargein"]
    assert gate.active


def test_endpoint_after_sustained_silence():
    gate = SpeechGate(onset_frames=3, hangover_frames=4)
    events = _feed(gate, "####" + "....")     # speak, then four silent frames
    assert events == ["onset", "endpoint"]
    assert not gate.active


def test_brief_pauses_do_not_endpoint():
    gate = SpeechGate(onset_frames=3, hangover_frames=4)
    events = _feed(gate, "###" + "..#.." + "###")  # a short gap mid-utterance
    assert "endpoint" not in events
    assert gate.active


def test_confirmed_survives_until_reset():
    # `confirmed` is what the server reads at endpoint to accept/drop the turn;
    # it must stay set through the silence that follows the speech.
    gate = SpeechGate(onset_frames=3, hangover_frames=4)
    _feed(gate, "###" + "....")
    assert gate.confirmed                      # still true after the endpoint fires
    gate.reset()
    assert not gate.confirmed and not gate.active


def test_pure_silence_never_confirms():
    gate = SpeechGate(onset_frames=3)
    assert _feed(gate, "." * 20) == []
    assert not gate.confirmed                  # an all-noise utterance the server drops
