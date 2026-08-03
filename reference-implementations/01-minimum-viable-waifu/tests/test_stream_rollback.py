"""SSE failures cannot leave a one-sided provisional turn in the Vault."""
from __future__ import annotations

from types import SimpleNamespace

from app.routes import chat as chat_route
from app.sessions import SessionStore
from tests.conftest import FakeChat, make_app


def test_drop_last_requires_the_expected_latest_role(vault):
    sessions = SessionStore(vault)
    session_id = sessions.create()
    sessions.append_message(session_id, "user", "hello")

    assert not sessions.drop_last(session_id, "assistant")
    assert sessions.window(session_id, 1)[0]["content"] == "hello"
    assert sessions.drop_last(session_id, "user")
    assert sessions.window(session_id, 1) == []


async def test_closing_an_http_sse_stream_rolls_back_only_the_provisional_user(vault, tmp_path):
    app = make_app(vault, tmp_path / "corpus", chat=FakeChat("one two"))
    session_id = app.state.mvw.sessions.create()
    response = await chat_route.chat(
        chat_route.ChatRequest(session_id=session_id, message="hello"),
        SimpleNamespace(app=app))

    first_event = await anext(response.body_iterator)
    assert '"token"' in first_event
    await response.body_iterator.aclose()

    session = app.state.mvw.sessions.get(session_id)
    assert session["transcript"] == []
    assert session["turn_count"] == 0
    assert not (tmp_path / "corpus" / "turns.jsonl").exists()
