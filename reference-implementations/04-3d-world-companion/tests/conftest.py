"""Shared fixtures. The whole suite runs offline (SPEC §13): fake voice backends
(B2 §3), a fake tool runner, an in-memory MCP session, MockTransport weather,
and a VirtualClock for everything timed."""
from __future__ import annotations

import pytest

from desktop.config import Config as VoiceConfig  # noqa: F401 (re-export habit)
from world.avatar.controller import VrmController
from world.clock import VirtualClock
from world.config import Config
from world.tools.guard import Guard
from world.tools.timers import TimerBoard


@pytest.fixture
def clock() -> VirtualClock:
    return VirtualClock()


@pytest.fixture
def cfg(tmp_path) -> Config:
    return Config(
        tts_backend="fake", stt_backend="fake", vad_backend="fake",
        mask_latency=False, tools_backend="fake",
        selfie_backend="mock", selfie_dir=tmp_path / "selfies",
        vault_dir=tmp_path / "vault", db_path=tmp_path / "mvw.db",
        corpus_dir=tmp_path / "corpus", trace_dir=tmp_path / "traces",
        tool_log_dir=tmp_path / "tool-logs")


@pytest.fixture
def guard(cfg, clock) -> Guard:
    return Guard(rates_per_min={"set_timer": 6, "play_music": 6, "get_weather": 4},
                 log_dir=cfg.tool_log_dir, clock=clock)


@pytest.fixture
def timers(clock) -> TimerBoard:
    return TimerBoard(clock)


class SpyController(VrmController):
    """A VrmController that also journals every command for assertions."""

    def __init__(self):
        super().__init__()
        self.commands: list[dict] = []

    def _send(self, cmd, sticky=None):
        self.commands.append(cmd)
        super()._send(cmd, sticky=sticky)

    def kinds(self) -> list[str]:
        return [c["type"] for c in self.commands]


@pytest.fixture
def controller() -> SpyController:
    return SpyController()


class ScriptedChat:
    """A chat model whose stream yields one scripted token list per pass, and
    records the messages of every call — the tool loop's test double."""

    def __init__(self, passes: list[list[str]]):
        import asyncio
        self.passes = list(passes)
        self.calls: list[list[dict]] = []
        # fires when pass i starts streaming — lets a test time a barge-in
        self.pass_started = [asyncio.Event() for _ in passes]

    async def stream(self, messages, **params):
        import asyncio
        i = len(self.calls)
        self.calls.append([dict(m) for m in messages])
        if i < len(self.pass_started):
            self.pass_started[i].set()
        tokens = self.passes[i] if i < len(self.passes) else []
        for tok in tokens:
            yield tok
            await asyncio.sleep(0)     # a real await point — cancellation lands here


class StubState:
    """The minimum of Build #1's AppState the tool loop touches."""

    def __init__(self, chat):
        self.chat = chat


def make_toolbrain(cfg, guard, timers, controller, chat, runner=None,
                   specs=None, selfies=None):
    """A ToolBrain over a stub state — unit tests drive _stream_with_tools
    directly; the full vendored path is pinned in test_integration.py."""
    from world.brain import ToolBrain
    from world.tools.fakes import SPECS
    tb = ToolBrain(StubState(chat), cfg, guard=guard, timers=timers,
                   controller=controller, selfies=selfies)
    if runner is not None:
        tb.set_tools(runner, specs if specs is not None else list(SPECS))
    return tb


async def collect(agen) -> list[str]:
    return [t async for t in agen]
