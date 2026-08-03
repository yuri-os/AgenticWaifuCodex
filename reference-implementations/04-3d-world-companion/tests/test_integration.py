"""End-to-end over the REAL vendored brain (SPEC §2, §13), no models, no net.

The unit tests drive the tool loop with a stub state; this one proves the
actual reuse: `ToolBrain.build` constructs the vendored Build #1 AppState
(assemble, FileMemoryStore, the corpus, the Vault-git spine) exactly as
`python -m world` does, a scripted chat model emits a [[set_timer]] marker, a
FakeToolRunner answers it — and a tool-bearing turn still ends as one corpus
line and one Vault commit, with the markers in the record. Standalone: seeded
fresh from the vendored soul-src, no reference to ../01 or ../02.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("app.main")            # the vendored brain

from desktop.voice.backends.fakes import FakeTTS   # noqa: E402
from desktop.voice.turn import TurnController      # noqa: E402
from world.avatar.controller import VrmController  # noqa: E402
from world.brain import ToolBrain                  # noqa: E402
from world.tools.fakes import SPECS, FakeToolRunner  # noqa: E402
from world.tools.guard import Guard                # noqa: E402
from world.tools.timers import TimerBoard          # noqa: E402
from app import vaultgit                           # noqa: E402

from .conftest import ScriptedChat                 # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOUL_SRC = ROOT / "soul-src"

MARKER = '[[set_timer {"minutes": 10, "label": "tea"}]]'


class FakeUtility:
    async def complete(self, messages, **params):
        return '{"ops": []}'                # no partner-model changes, valid JSON


class FakeEmbedder:
    dim = 8

    def embed(self, texts):
        return [[float((len(t) + i) % 5) for i in range(self.dim)] for t in texts]


@pytest.fixture
def vault(tmp_path):
    """Seed a throwaway Vault from the vendored SOUL — the new-user path."""
    if not (SOUL_SRC / "soul.yaml").exists():
        pytest.skip("vendored soul-src missing")
    dst = tmp_path / "vault"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "seed_vault.py"),
                        "--soul", str(SOUL_SRC), "--vault", str(dst)],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    return dst


async def test_tool_turn_over_the_real_brain(vault, cfg, clock):
    cfg = cfg.model_copy(update={
        "vault_dir": vault, "embed_dim": 8,
        "corpus_dir": vault.parent / "corpus",
        "trace_dir": vault.parent / "traces"})
    chat = ScriptedChat([
        ["[happy] ", "Tea? ", "On it. ", MARKER],
        ["Ten ", "minutes ", "— ", "[tender] ", "I'll ", "call ", "you."],
    ])
    guard = Guard(rates_per_min={"set_timer": 6, "play_music": 6, "get_weather": 4},
                  log_dir=cfg.tool_log_dir, clock=clock)
    timers = TimerBoard(clock)
    controller = VrmController()
    runner = FakeToolRunner()

    brain = ToolBrain.build(cfg, guard=guard, timers=timers,
                            controller=controller, chat_model=chat,
                            utility_model=FakeUtility(), embedder=FakeEmbedder())
    brain.set_tools(runner, list(SPECS))
    sid = brain.resolve_session(None)
    tc = TurnController(brain=brain, tts=FakeTTS(), filler_bank=None,
                        mask_latency=False, trace_dir=cfg.trace_dir)

    events = [ev async for ev in tc.run_turn(sid, "set a tea timer, ten minutes")]
    kinds = [e.kind for e in events]

    # the turn completed as one seamless OutEvent stream, tool call and all
    assert kinds[-1] == "done"
    texts = [e.text for e in events if e.kind == "audio"]
    assert any("On it" in t for t in texts)            # the lead-in (pass 1)
    assert any("call you" in t for t in texts)         # the continuation (pass 2)
    assert not any("[[" in (t or "") for t in texts)   # the marker never spoken
    assert any(e.kind == "expression" and e.expression == "happy" for e in events)

    # the prompt carried the ## TOOLS directive, built from discovery (§7.4)
    assert "## TOOLS" in chat.calls[0][0]["content"]
    assert "set_timer" in chat.calls[0][0]["content"]

    # …and the situation block (§2.5): the injected clock's time, the
    # embodiment truth — she may know she is an AI; she is never bodiless
    import datetime
    system = chat.calls[0][0]["content"]
    assert "## THE SITUATION RIGHT NOW" in system
    assert datetime.datetime.fromtimestamp(clock.now()).strftime("%H:%M") in system
    assert "Never say you have no body" in system

    # the tool ran, was guarded + audited, and the host realised it (§7.5)
    assert runner.calls == [("set_timer", {"minutes": 10, "label": "tea"})]
    assert (cfg.tool_log_dir / "calls.jsonl").exists()
    assert [t.label for t in timers.pending()] == ["tea"]

    # ONE corpus line — with the model-verbatim record: markers AND result (§7.4)
    corpus = (cfg.corpus_dir / "turns.jsonl").read_text().strip().splitlines()
    assert len(corpus) == 1
    assert "[[set_timer" in corpus[0] and "set_timer →" in corpus[0]

    # and the Vault recorded the turn as exactly one new git commit (B1 §6.5)
    log = subprocess.run(["git", "-C", str(vault), "log", "--oneline"],
                         capture_output=True, text=True).stdout
    assert sum("turn" in l for l in log.splitlines()) == 1


async def test_ambient_stream_over_the_real_brain_never_persists(vault, cfg, clock):
    cfg = cfg.model_copy(update={
        "vault_dir": vault, "embed_dim": 8,
        "corpus_dir": vault.parent / "corpus"})
    chat = ScriptedChat([["[relaxed] ", "Still ", "raining…"]])
    brain = ToolBrain.build(
        cfg, guard=Guard(rates_per_min={}, log_dir=cfg.tool_log_dir, clock=clock),
        timers=TimerBoard(clock), controller=VrmController(),
        chat_model=chat, utility_model=FakeUtility(), embedder=FakeEmbedder())
    sid = brain.resolve_session(None)
    tc = TurnController(brain=brain, tts=FakeTTS(), filler_bank=None,
                        mask_latency=False)

    events = [ev async for ev in tc.run_turn(
        sid, "", persist=False,
        tokens=brain.stream_ambient(sid, "((one line about the rain))"))]
    assert events[-1].kind == "done"
    assert any(e.kind == "audio" for e in events)
    corpus = cfg.corpus_dir / "turns.jsonl"
    assert not corpus.exists() or not corpus.read_text().strip()


async def test_cancelled_real_turn_is_removed_from_the_next_session_window(vault, cfg, clock):
    cfg = cfg.model_copy(update={
        "vault_dir": vault, "embed_dim": 8,
        "corpus_dir": vault.parent / "corpus"})
    chat = ScriptedChat([["One sentence. ", "Another sentence. "]])
    brain = ToolBrain.build(
        cfg, guard=Guard(rates_per_min={}, log_dir=cfg.tool_log_dir, clock=clock),
        timers=TimerBoard(clock), controller=VrmController(), chat_model=chat,
        utility_model=FakeUtility(), embedder=FakeEmbedder())
    sid = brain.resolve_session(None)
    controller = TurnController(brain=brain, tts=FakeTTS(), filler_bank=None,
                                mask_latency=False)

    async def interrupt_after_first_audio():
        async for event in controller.run_turn(sid, "an interrupted question"):
            if event.kind == "audio":
                controller.cancel()

    await interrupt_after_first_audio()

    session = brain.state.sessions.get(sid)
    assert session["transcript"] == []
    assert sid not in brain._pending


async def test_first_voice_greeting_uses_the_authored_bootstrap(vault, cfg, clock):
    cfg = cfg.model_copy(update={"vault_dir": vault, "embed_dim": 8})
    chat = ScriptedChat([])
    brain = ToolBrain.build(
        cfg, guard=Guard(rates_per_min={}, log_dir=cfg.tool_log_dir, clock=clock),
        timers=TimerBoard(clock), controller=VrmController(), chat_model=chat,
        utility_model=FakeUtility(), embedder=FakeEmbedder())
    sid = brain.resolve_session(None)
    cold_open = brain.cold_open()

    spoken = "".join([token async for token in brain.stream_greeting(sid)])

    assert cold_open is not None
    assert spoken.strip() == cold_open
    assert chat.calls == []
    transcript = brain.state.sessions.get(sid)["transcript"]
    assert len(transcript) == 1
    assert transcript[0]["role"] == "assistant"
    assert transcript[0]["content"] == cold_open


async def test_first_completed_turn_archives_bootstrap_and_restored_copy(vault, cfg, clock):
    cfg = cfg.model_copy(update={
        "vault_dir": vault, "embed_dim": 8,
        "corpus_dir": vault.parent / "corpus"})
    brain = ToolBrain.build(
        cfg,
        guard=Guard(rates_per_min={}, log_dir=cfg.tool_log_dir, clock=clock),
        timers=TimerBoard(clock), controller=VrmController(),
        chat_model=ScriptedChat([["I remember."]]),
        utility_model=FakeUtility(), embedder=FakeEmbedder())
    sid = brain.resolve_session(None)
    controller = TurnController(brain=brain, tts=FakeTTS(), filler_bank=None,
                                mask_latency=False)

    events = [event async for event in controller.run_turn(sid, "hello")]

    assert events[-1].kind == "done"
    bootstrap = vault / "soul" / "BOOTSTRAP.md"
    archived = vault / "soul" / "onboarded" / "BOOTSTRAP.done.md"
    assert not bootstrap.exists() and archived.exists()
    log = subprocess.run(["git", "-C", str(vault), "log", "--oneline"],
                         capture_output=True, text=True).stdout
    assert "first session complete" in log

    # Re-onboarding can restore an untracked bootstrap over an existing archive.
    bootstrap.write_text("A restored first meeting.", encoding="utf-8")
    vaultgit.mv(vault, "soul/BOOTSTRAP.md", "soul/onboarded/BOOTSTRAP.done.md",
                force=True)
    assert archived.read_text(encoding="utf-8") == "A restored first meeting."
