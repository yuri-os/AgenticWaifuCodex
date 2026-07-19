"""Partner-model extraction robustness (SPEC §6.3).

Guards the two bugs that lost the user's name over voice with a *local reasoning*
utility model (qwen3:8b):

  1. A <think>…</think> block prepended to the JSON answer must be stripped, not
     parsed as garbage (parse_ops).
  2. Reasoning is ON by default and configurable — `thinking=False` appends the
     qwen `/no_think` soft switch; the default leaves the prompt untouched
     (LiteLLMUtilityModel).

The prompt-quality fix (never record the companion's self-description as a user
fact) is model-dependent and lives in EXTRACT_SYSTEM; it is exercised end-to-end,
not unit-tested here.
"""
from __future__ import annotations

import asyncio
import types

from app.memory import partner
from app.providers.openrouter import LiteLLMUtilityModel


def test_parse_ops_strips_think_block():
    raw = ('<think>The user said their name is Grant. That is a durable identity '
           'fact, so I should add it under Stable.</think>\n'
           '{"ops": [{"section": "Stable", "text": "User\'s name is Grant", '
           '"op": "add", "confidence": 1.0}]}')
    ops = partner.parse_ops(raw)
    assert len(ops) == 1
    assert ops[0].section == "Stable" and "Grant" in ops[0].text


def test_parse_ops_survives_braces_inside_think():
    """A think block that itself contains { } must not corrupt the JSON scan."""
    raw = ('<think>maybe {"section": "Ongoing"}? no, it is stable.</think>'
           '{"ops": [{"section": "Stable", "text": "Grant", "op": "add", '
           '"confidence": 1.0}]}')
    ops = partner.parse_ops(raw)
    assert len(ops) == 1 and ops[0].text == "Grant"


def _capture_messages(monkeypatch) -> dict:
    """Stub litellm.acompletion to capture the messages it was handed."""
    seen: dict = {}

    async def fake_acompletion(*, messages, **kw):
        seen["messages"] = messages
        msg = types.SimpleNamespace(content='{"ops": []}')
        return types.SimpleNamespace(
            choices=[types.SimpleNamespace(message=msg)])

    import app.providers.openrouter as mod
    monkeypatch.setattr(mod.litellm, "acompletion", fake_acompletion)
    return seen


def test_thinking_on_by_default_leaves_prompt_untouched(monkeypatch):
    seen = _capture_messages(monkeypatch)
    util = LiteLLMUtilityModel("ollama/qwen3:8b")
    assert util.thinking is True
    asyncio.run(util.complete([{"role": "system", "content": "SYS"},
                               {"role": "user", "content": "hi"}]))
    assert seen["messages"][0]["content"] == "SYS"          # no /no_think appended


def test_thinking_false_appends_no_think(monkeypatch):
    seen = _capture_messages(monkeypatch)
    util = LiteLLMUtilityModel("ollama/qwen3:8b", thinking=False)
    asyncio.run(util.complete([{"role": "system", "content": "SYS"},
                               {"role": "user", "content": "hi"}]))
    assert seen["messages"][0]["content"].endswith("/no_think")
