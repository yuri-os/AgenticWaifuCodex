"""End-to-end over the REAL (vendored) brain (SPEC §2, §13.3), no models.

The unit tests drive the loop with a FakeBrain. This one proves the *actual*
reuse: BrainAdapter builds the vendored Build #1 AppState (assemble,
FileMemoryStore, the corpus, the Vault-git spine) and the voice loop drives it —
with a fake chat model, a fake embedder, and a Vault seeded fresh from the
vendored SOUL into a tmp dir. Standalone: no reference to ../01-….
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
import types
from pathlib import Path

import pytest

pytest.importorskip("app.main")            # the vendored brain

from desktop.brain import BrainAdapter     # noqa: E402
from desktop.config import Config          # noqa: E402
from desktop.voice.backends.fakes import FakeTTS  # noqa: E402
from desktop.voice.fillers import FillerBank      # noqa: E402
from desktop.voice.turn import TurnController     # noqa: E402
from desktop.routes.voice_ws import _encode       # noqa: E402
from desktop.voice.turn import OutEvent           # noqa: E402
from app.main import create_app                    # noqa: E402
from app.routes.chat import ChatRequest, chat      # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOUL_SRC = ROOT / "soul-src"


class FakeChat:
    async def stream(self, messages, **params):
        for tok in ["[happy] ", "There ", "you ", "are. ", "[tender] ", "I ", "missed ", "you."]:
            yield tok


class FakeUtility:
    async def complete(self, messages, **params):
        return '{"ops": []}'                # no partner-model changes, valid JSON


class FakeEmbedder:
    dim = 8

    def embed(self, texts):
        # deterministic, dim-8 — good enough for an empty index round-trip
        return [[float((len(t) + i) % 5) for i in range(self.dim)] for t in texts]


@pytest.fixture
def vault(tmp_path):
    """Seed a throwaway Vault from the vendored SOUL — exactly what a new user
    runs (`scripts/seed_vault.py`), so the test proves the standalone path."""
    if not (SOUL_SRC / "soul.yaml").exists():
        pytest.skip("vendored soul-src missing")
    dst = tmp_path / "vault"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "seed_vault.py"),
                        "--soul", str(SOUL_SRC), "--vault", str(dst)],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    return dst


async def test_real_brain_turn_streams_audio_and_persists(vault):
    cfg = Config(vault_dir=vault, embed_dim=8, tts_backend="fake",
                 stt_backend="fake", vad_backend="fake", mask_latency=False,
                 corpus_dir=vault.parent / "corpus", trace_dir=vault.parent / "traces")
    brain = BrainAdapter.build(cfg, chat_model=FakeChat(),
                               utility_model=FakeUtility(), embedder=FakeEmbedder())
    sid = brain.resolve_session(None)
    controller = TurnController(brain=brain, tts=FakeTTS(), filler_bank=None,
                                mask_latency=False, trace_dir=cfg.trace_dir)

    events = [ev async for ev in controller.run_turn(sid, "hey, i'm home")]
    kinds = [e.kind for e in events]

    assert kinds[-1] == "done"
    assert kinds.count("audio") >= 2                  # streamed sentence by sentence
    assert any(e.kind == "expression" and e.expression == "happy" for e in events)

    # the real corpus line landed (the training asset, from day one — Build #1 §8)
    corpus = (cfg.corpus_dir / "turns.jsonl")
    assert corpus.exists() and corpus.read_text().strip()
    assert '"voice"' in corpus.read_text()             # tagged as a voice turn (§8)

    # and the Vault recorded the turn as exactly one git commit (Build #1 §6.5)
    import subprocess
    log = subprocess.run(["git", "-C", str(vault), "log", "--oneline"],
                          capture_output=True, text=True).stdout
    assert "turn" in log
    # The first completed turn retires onboarding as part of its locked post-turn.
    assert not (vault / "soul" / "BOOTSTRAP.md").exists()
    assert (vault / "soul" / "onboarded" / "BOOTSTRAP.done.md").exists()


async def test_greeting_streams_full_cold_open_without_persisting_a_turn(vault):
    """The actual voice greeting speaks and displays the authored cold open."""
    cfg = Config(vault_dir=vault, embed_dim=8, tts_backend="fake",
                 mask_latency=False, corpus_dir=vault.parent / "corpus")
    brain = BrainAdapter.build(cfg, chat_model=FakeChat(),
                               utility_model=FakeUtility(), embedder=FakeEmbedder())
    sid = brain.resolve_session(None)
    controller = TurnController(brain=brain, tts=FakeTTS(), filler_bank=None,
                                mask_latency=False)

    events = [ev async for ev in controller.run_turn(
        sid, "", persist=False, tokens=brain.stream_greeting(sid))]
    assert events[-1].kind == "done"
    assert any(e.kind == "audio" for e in events)
    # no corpus line from a greeting
    corpus = cfg.corpus_dir / "turns.jsonl"
    assert not corpus.exists() or not corpus.read_text().strip()
    transcript = brain.state.sessions.get(sid)["transcript"]
    assert len(transcript) == 1
    assert transcript[0]["role"] == "assistant"
    assert transcript[0]["content"] == brain.cold_open()


class SlowChat:
    def __init__(self):
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def stream(self, messages, **params):
        self.started.set()
        yield "[happy] "
        await self.release.wait()


async def test_real_brain_cancel_rolls_back_its_provisional_user_message(vault):
    cfg = Config(vault_dir=vault, embed_dim=8, tts_backend="fake",
                 mask_latency=False, corpus_dir=vault.parent / "corpus")
    chat = SlowChat()
    brain = BrainAdapter.build(cfg, chat_model=chat, utility_model=FakeUtility(),
                               embedder=FakeEmbedder())
    sid = brain.resolve_session(None)
    controller = TurnController(brain=brain, tts=FakeTTS(), filler_bank=None,
                                 mask_latency=False)

    async def drain_turn():
        return [event async for event in controller.run_turn(sid, "hello")]

    task = asyncio.create_task(drain_turn())
    await asyncio.wait_for(chat.started.wait(), timeout=2)
    controller.cancel()
    events = await asyncio.wait_for(task, timeout=2)

    assert events[-1].kind == "cancelled"
    assert brain.state.sessions.get(sid)["transcript"] == []
    assert sid not in brain._pending


async def test_real_brain_disconnect_rolls_back_an_open_generator(vault):
    cfg = Config(vault_dir=vault, embed_dim=8, tts_backend="fake",
                 mask_latency=False, corpus_dir=vault.parent / "corpus")
    chat = SlowChat()
    brain = BrainAdapter.build(cfg, chat_model=chat, utility_model=FakeUtility(),
                               embedder=FakeEmbedder())
    sid = brain.resolve_session(None)
    controller = TurnController(brain=brain, tts=FakeTTS(), filler_bank=None,
                                 mask_latency=False)

    agen = controller.run_turn(sid, "hello")
    first = await asyncio.wait_for(agen.__anext__(), timeout=2)
    assert first.kind == "expression"
    await agen.aclose()

    assert brain.state.sessions.get(sid)["transcript"] == []
    assert sid not in brain._pending


class FailingChat:
    async def stream(self, messages, **params):
        yield "partial "
        raise RuntimeError("model stopped")


async def test_sse_error_rolls_back_its_preappended_user_message(vault):
    """An HTTP stream failure must not leave a user-only turn in the session."""
    cfg = Config(vault_dir=vault, embed_dim=8, corpus_dir=vault.parent / "corpus")
    app = create_app(cfg, chat_model=FailingChat(), utility_model=FakeUtility(),
                     embedder=FakeEmbedder())
    sid = app.state.mvw.sessions.create()
    response = await chat(ChatRequest(session_id=sid, message="hello"),
                          types.SimpleNamespace(app=app))
    body = "".join([part async for part in response.body_iterator])

    assert response.status_code == 200
    assert '"error"' in body
    assert app.state.mvw.sessions.get(sid)["transcript"] == []


def test_encode_audio_is_base64_pcm():
    import numpy as np
    ch_ev = OutEvent.say(type("C", (), {"audio": np.ones(4, np.float32),
                                         "sample_rate": 24000, "text": "hi"})())
    enc = _encode(ch_ev)
    assert enc["type"] == "audio" and enc["sr"] == 24000
    import base64
    assert len(base64.b64decode(enc["pcm"])) == 4 * 4        # 4 float32 = 16 bytes
