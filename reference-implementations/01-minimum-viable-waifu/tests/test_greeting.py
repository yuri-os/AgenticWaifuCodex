"""The continuity greeting (§9.3) + bootstrap lifecycle (§5.4) — the DoD
headline: first-ever run gets the authored cold open; once she has met you the
bootstrap retires (git mv, committed) and openers are memory-grounded."""
from __future__ import annotations

import asyncio
import json

import httpx

from app import vaultgit
from tests.conftest import FakeChat, make_app


async def collect_sse(client, url: str) -> tuple[str, list[dict]]:
    events = []
    async with client.stream("GET", url) as r:
        assert r.status_code == 200
        buffer = ""
        async for chunk in r.aiter_text():
            buffer += chunk
        for ev in buffer.split("\n\n"):
            if ev.startswith("data: "):
                events.append(json.loads(ev[6:]))
    text = "".join(e["token"] for e in events if "token" in e)
    return text, events


async def drain(app):
    for _ in range(500):
        if not app.state.mvw.pending_tasks:
            break
        await asyncio.sleep(0.01)


async def test_first_ever_greeting_is_the_cold_open(vault, tmp_path):
    app = make_app(vault, tmp_path / "corpus")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,
                                 base_url="http://sanctuary") as client:
        sid = (await client.post("/api/session")).json()["session_id"]
        text, _ = await collect_sse(client, f"/api/greeting?session_id={sid}")
        # BOOTSTRAP.md#Cold open, verbatim (§5.4) — not model-generated
        assert "You found the signal" in text
        # and it entered the transcript
        history = (await client.get(f"/api/session/{sid}/history")).json()
        assert history["messages"][-1]["role"] == "assistant"
    # hand-authored, so no corpus record was written (§8 logs model completions)
    assert not (tmp_path / "corpus" / "turns.jsonl").exists()


async def test_return_greeting_retires_bootstrap_and_uses_memory(vault, tmp_path):
    chat = FakeChat("Welcome back. Did Mira make it in on friday?")
    app = make_app(vault, tmp_path / "corpus", chat=chat)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,
                                 base_url="http://sanctuary") as client:
        sid = (await client.post("/api/session")).json()["session_id"]
        # one real exchange, so the journal exists — she has met you now
        async with client.stream("POST", "/api/chat",
                                 json={"session_id": sid,
                                       "message": "my sister Mira visits friday"}) as r:
            async for _ in r.aiter_text():
                pass
        await drain(app)

        text, events = await collect_sse(client, f"/api/greeting?session_id={sid}")
        await drain(app)

        # bootstrap retired (§5.4): git mv → soul/onboarded/, committed
        assert not (vault / "soul" / "BOOTSTRAP.md").exists()
        assert (vault / "soul" / "onboarded" / "BOOTSTRAP.done.md").exists()
        assert any("first session complete" in line
                   for line in vaultgit.log(vault, n=20))

        # the opener is model-generated from memory, not the cold open (§9.3)
        assert "You found the signal" not in text
        assert "Mira" in text
        # and the prompt that produced it carried the memory blocks
        greet_prompt = chat.calls[-1][0]["content"]
        assert "WHO YOU ARE TO HER" in greet_prompt
        # greetings are corpus-logged (they are model completions), tagged
        lines = (tmp_path / "corpus" / "turns.jsonl").read_text().splitlines()
        tagged = [json.loads(l) for l in lines if "tags" in json.loads(l)]
        assert any("greeting" in rec["tags"] for rec in tagged)
        assert events[-1].get("done") is True


async def test_sanctuary_page_is_served(vault, tmp_path):
    """GET / → the static page (§10) — one page, no build step (§9)."""
    app = make_app(vault, tmp_path / "corpus")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,
                                 base_url="http://sanctuary") as client:
        r = await client.get("/")
        assert r.status_code == 200
        assert "sanctuary.css" in r.text and "app.js" in r.text
