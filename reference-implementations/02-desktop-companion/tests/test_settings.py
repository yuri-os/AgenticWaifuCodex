"""GET/POST /api/settings (SPEC §11) — the .env settings panel.

Covers the three behaviours the UI relies on: the schema comes back with the
live values filled in, a POST upserts only the submitted keys into .env while
preserving the surrounding comments, and an unknown key is ignored rather than
written.
"""
from __future__ import annotations

import desktop.routes.settings as settings_mod
from desktop.config import Config
from desktop.main import create_app
from starlette.testclient import TestClient

FAKES = dict(stt_backend="fake", tts_backend="fake", vad_backend="fake",
             mask_latency=False)


def _client(**over) -> TestClient:
    # present a loopback client host so _require_local() lets the request through
    return TestClient(create_app(Config(**FAKES, **over)), client=("127.0.0.1", 5555))


def _point_env_at(tmp_path, monkeypatch, text: str):
    env = tmp_path / ".env"
    env.write_text(text)
    monkeypatch.setattr(settings_mod, "ENV_PATH", env)
    return env


def test_schema_carries_live_values():
    body = _client(avatar_model="ren", port=9999).get("/api/settings").json()
    fields = {f["key"]: f for g in body["groups"] for f in g["fields"]}
    assert fields["AVATAR_MODEL"]["value"] == "ren"
    assert fields["AVATAR_MODEL"]["type"] == "select"
    assert "hiyori" in fields["AVATAR_MODEL"]["options"]
    assert str(fields["PORT"]["value"]) == "9999"
    # secrets are typed password so the UI masks them
    assert fields["OPENROUTER_API_KEY"]["type"] == "password"


def test_post_upserts_and_preserves_comments(tmp_path, monkeypatch):
    _point_env_at(tmp_path, monkeypatch,
                  "# a precious comment\nAVATAR_MODEL=hiyori\n# QWEN_REF_AUDIO=/old\n")
    r = _client().post("/api/settings", json={
        "AVATAR_MODEL": "kei",            # existing uncommented → replaced
        "QWEN_REF_AUDIO": "/voice.wav",   # commented → uncommented + set
        "MAX_REPLY_TOKENS": 250,          # absent → appended
    })
    res = r.json()
    assert res["ok"] and res["restart_required"]
    assert set(res["written"]) == {"AVATAR_MODEL", "QWEN_REF_AUDIO", "MAX_REPLY_TOKENS"}
    written = settings_mod.ENV_PATH.read_text()
    assert "# a precious comment" in written           # comment survived
    assert "AVATAR_MODEL=kei" in written
    assert "QWEN_REF_AUDIO=/voice.wav" in written
    assert "# QWEN_REF_AUDIO=/old" not in written      # old commented line replaced
    assert "MAX_REPLY_TOKENS=250" in written


def test_post_quotes_values_with_spaces(tmp_path, monkeypatch):
    _point_env_at(tmp_path, monkeypatch, "SOVITS_PROMPT_TEXT=\n")
    _client().post("/api/settings", json={"SOVITS_PROMPT_TEXT": "hello there friend"})
    assert 'SOVITS_PROMPT_TEXT="hello there friend"' in settings_mod.ENV_PATH.read_text()


def test_bool_serialises_to_true_false(tmp_path, monkeypatch):
    _point_env_at(tmp_path, monkeypatch, "MASK_LATENCY=true\n")
    _client().post("/api/settings", json={"MASK_LATENCY": False})
    assert "MASK_LATENCY=false" in settings_mod.ENV_PATH.read_text()


def test_unknown_key_ignored_not_written(tmp_path, monkeypatch):
    _point_env_at(tmp_path, monkeypatch, "AVATAR_MODEL=hiyori\n")
    res = _client().post("/api/settings", json={"HACK_ME": "x"}).json()
    assert res["ignored"] == ["HACK_ME"]
    assert res["written"] == []
    assert "HACK_ME" not in settings_mod.ENV_PATH.read_text()


def test_non_local_caller_is_refused(tmp_path, monkeypatch):
    # a request from a non-loopback address gets 403 on both verbs, and nothing
    # is written — the panel is local-only even under HOST=0.0.0.0.
    env = _point_env_at(tmp_path, monkeypatch, "AVATAR_MODEL=hiyori\n")
    remote = TestClient(create_app(Config(**FAKES)), client=("203.0.113.7", 40000))
    assert remote.get("/api/settings").status_code == 403
    assert remote.post("/api/settings", json={"AVATAR_MODEL": "kei"}).status_code == 403
    assert env.read_text() == "AVATAR_MODEL=hiyori\n"
