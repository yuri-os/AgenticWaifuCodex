"""Corpus + git (§8, §6.5, §13.3), against the REAL /api/chat handler:
one turn ⇒ exactly one schema-conformant turns.jsonl line and exactly one
Vault commit; log_turn raises on an illegal collection_scope; a mid-stream
failure writes neither."""
from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from app import vaultgit
from app.corpus import CorpusLogger
from tests.conftest import FakeChat, make_app


async def run_chat(app, message: str) -> list[dict]:
    """POST /api/chat and collect the SSE events."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,
                                 base_url="http://sanctuary") as client:
        sid = (await client.post("/api/session")).json()["session_id"]
        events = []
        async with client.stream("POST", "/api/chat",
                                 json={"session_id": sid,
                                       "message": message}) as r:
            assert r.status_code == 200
            buffer = ""
            async for chunk in r.aiter_text():
                buffer += chunk
            for ev in buffer.split("\n\n"):
                if ev.startswith("data: "):
                    events.append(json.loads(ev[6:]))
    # let the post-turn background pipeline drain (§10.1 step 9)
    for _ in range(500):
        if not app.state.mvw.pending_tasks:
            break
        await asyncio.sleep(0.01)
    return events


async def test_one_turn_one_line_one_commit(vault, tmp_path):
    corpus_dir = tmp_path / "corpus"
    app = make_app(vault, corpus_dir,
                   chat=FakeChat("mm — kept. tell me more about her?"))
    commits_before = len(vaultgit.log(vault, n=100))

    events = await run_chat(app, "my sister Mira is visiting on friday")

    # the stream: tokens, then exactly one done event carrying the turn id
    assert events[-1]["done"] is True and events[-1]["turn_id"]
    reply = "".join(e["token"] for e in events if "token" in e)
    assert "kept" in reply

    # exactly one corpus line (§8.2), faithful to what was sent
    lines = (corpus_dir / "turns.jsonl").read_text().strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    for field in ("id", "session_id", "turn_index", "timestamp", "companion",
                  "messages", "completion", "model", "model_role", "source",
                  "collection_scope", "card_version"):
        assert field in rec, f"§8.2 requires {field}"
    assert rec["model_role"] == "production" and rec["source"] == "live_play"
    assert rec["collection_scope"] == "self"
    assert rec["card_version"] == "yuri-v1@canon-v1"
    assert rec["completion"] == reply
    assert rec["messages"][0]["role"] == "system"     # the full prompt as sent
    assert rec["messages"][-1]["content"].startswith("my sister Mira")

    # exactly one new Vault commit for the turn (§6.5)
    log = vaultgit.log(vault, n=100)
    assert len(log) == commits_before + 1
    assert log[0].split(" ", 1)[1].startswith("turn ")


async def test_midstream_failure_writes_nothing(vault, tmp_path):
    corpus_dir = tmp_path / "corpus"
    chat = FakeChat("this reply will die mid-stream")
    chat.fail = True
    app = make_app(vault, corpus_dir, chat=chat)
    commits_before = len(vaultgit.log(vault, n=100))

    events = await run_chat(app, "hello?")

    # §10.1: an error event, then NO corpus record and NO partial commit
    assert any("error" in e for e in events)
    assert not any(e.get("done") for e in events)
    assert not (corpus_dir / "turns.jsonl").exists()
    assert len(vaultgit.log(vault, n=100)) == commits_before


def test_collection_scope_is_asserted(tmp_path):
    logger = CorpusLogger(tmp_path / "corpus")
    with pytest.raises(AssertionError):
        # the sovereignty boundary, in code (§8.4): a shipped card never logs
        # a stranger's conversation home
        logger.log_turn(session_id="s", turn_index=0, messages=[],
                        completion="x", model="m", card_version="v",
                        collection_scope="downloader_telemetry")


async def test_rating_lands_in_the_sidecar(vault, tmp_path):
    corpus_dir = tmp_path / "corpus"
    app = make_app(vault, corpus_dir)
    events = await run_chat(app, "remember this: I hate mushrooms")
    turn_id = events[-1]["turn_id"]

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,
                                 base_url="http://sanctuary") as client:
        r = await client.post("/api/rate", json={"turn_id": turn_id, "thumbs": 1})
        assert r.json() == {"ok": True}
    rating = json.loads((corpus_dir / "ratings.jsonl").read_text().splitlines()[0])
    assert rating == {"id": turn_id, "thumbs": 1, "by": "user",
                      "timestamp": rating["timestamp"]}  # §8.1 sidecar, keyed by id
