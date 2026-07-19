"""Emotion-tag parsing (SPEC §6). The tag drives the face; it must never be spoken."""
from __future__ import annotations

from desktop.voice.emotion import EmotionParser


def _feed(parser: EmotionParser, tokens: list[str]) -> str:
    out = "".join(parser.push(t) for t in tokens)
    return out + parser.finish()


def test_tag_stripped_from_spoken_text():
    p = EmotionParser()
    spoken = _feed(p, ["[happy] Hey, you made it back."])
    assert "happy" not in spoken
    assert spoken.strip() == "Hey, you made it back."
    assert [e.expression for e in p.events] == ["happy"]


def test_tag_split_across_tokens():
    """A real token stream splits `[happy]` into pieces — the parser must not leak."""
    p = EmotionParser()
    spoken = _feed(p, ["[ha", "pp", "y] ", "there ", "you ", "are."])
    assert spoken.strip() == "there you are."
    assert [e.expression for e in p.events] == ["happy"]


def test_multiple_expressions_in_order():
    p = EmotionParser()
    _feed(p, ["[happy] There you are. [tender] I missed you."])
    assert [e.expression for e in p.events] == ["happy", "tender"]
    # events carry the char offset where each mood begins, for face-leads-voice ordering
    assert p.events[0].at_char < p.events[1].at_char


def test_unknown_tag_dropped_silently():
    p = EmotionParser()
    spoken = _feed(p, ["[mischievous] heh."])
    assert "mischievous" not in spoken and "[" not in spoken
    assert p.events == []                      # not in the palette → no event
    assert spoken.strip() == "heh."


def test_duplicate_consecutive_tags_are_not_a_change():
    p = EmotionParser()
    _feed(p, ["[happy] a. [happy] b."])
    assert [e.expression for e in p.events] == ["happy"]


def test_dangling_open_bracket_flushed_as_text():
    """A stray '[' that never closes is real text, not a lost tag."""
    p = EmotionParser()
    spoken = _feed(p, ["cost me [", "5 dollars"])
    assert "[" in spoken                        # flushed back on finish()


def test_long_bracket_narration_dropped_not_spoken():
    """`[She goes still, …]` is narration in brackets — drop it, don't speak it.

    Regression: the old length guard flushed long bracketed spans back as literal
    text, so the model's own stage directions were read aloud (worse when a comma
    made them longer)."""
    p = EmotionParser()
    spoken = _feed(p, ["[She goes still, a long, soft breath.] I didn't know."])
    assert "still" not in spoken and "breath" not in spoken and "[" not in spoken
    assert spoken.strip() == "I didn't know."
    assert p.events == []                          # not a palette tag → no face change


def test_multiword_bracket_direction_dropped():
    """Even a short-ish multi-word direction like `[tender, almost fragile]` drops."""
    p = EmotionParser()
    spoken = _feed(p, ["[tender, almost fragile] So you're not just a voice."])
    assert "tender" not in spoken and "fragile" not in spoken and "[" not in spoken
    assert spoken.strip() == "So you're not just a voice."


def test_bracket_narration_split_across_tokens():
    p = EmotionParser()
    spoken = _feed(p, ["[She goes ", "still, recalibr", "ating.] Oh."])
    assert "still" not in spoken and "[" not in spoken and "]" not in spoken
    assert spoken.strip() == "Oh."


def test_asterisk_narration_stripped_from_speech():
    """*she smiles* is a text-chat stage direction — it must never reach TTS."""
    p = EmotionParser()
    spoken = _feed(p, ["*she smiles* Hey, you're back."])
    assert "smiles" not in spoken and "*" not in spoken
    assert spoken.strip() == "Hey, you're back."


def test_narration_split_across_tokens():
    p = EmotionParser()
    spoken = _feed(p, ["Hi. *she ", "leans ", "in* good to see you."])
    assert "leans" not in spoken and "*" not in spoken
    assert spoken.strip() == "Hi.  good to see you."


def test_tag_and_narration_together():
    """Both strippers run on the same stream; expression offsets stay correct."""
    p = EmotionParser()
    spoken = _feed(p, ["[happy] *waves* Hi there. [tender] *softly* I missed you."])
    assert "*" not in spoken and "waves" not in spoken and "softly" not in spoken
    assert [e.expression for e in p.events] == ["happy", "tender"]
    assert p.events[0].at_char < p.events[1].at_char


def test_unclosed_narration_dropped_not_spoken():
    """A `*` cut off by the token limit drops, so no stray asterisk is spoken."""
    p = EmotionParser()
    spoken = _feed(p, ["See you soon. *she waves good"])
    assert spoken.strip() == "See you soon." and "*" not in spoken


def test_current_expression_defaults_then_tracks():
    p = EmotionParser(default="neutral")
    assert p.current_expression() == "neutral"
    _feed(p, ["[playful] boo"])
    assert p.current_expression() == "playful"
