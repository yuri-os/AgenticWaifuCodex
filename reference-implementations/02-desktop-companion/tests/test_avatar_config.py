"""GET /api/config (SPEC §6) — the browser learns which Live2D rig to mount.

Guards the two behaviours avatar.js relies on: a valid AVATAR_MODEL resolves to
its model3 URL, and an unknown/un-fetched one falls back to the default so the
page still gets a body.
"""
from __future__ import annotations

from starlette.testclient import TestClient

from desktop.avatar_models import DEFAULT, MODELS
from desktop.config import Config
from desktop.main import create_app

FAKES = dict(stt_backend="fake", tts_backend="fake", vad_backend="fake",
             mask_latency=False)


def _client(**over) -> TestClient:
    return TestClient(create_app(Config(**FAKES, **over)))


def test_chosen_model_is_resolved_to_its_url():
    r = _client(avatar_model="mao").get("/api/config")
    assert r.status_code == 200
    body = r.json()
    assert body["avatar_model"] == "mao"
    assert body["avatar_model_url"] == MODELS["mao"]


def test_unknown_model_falls_back_to_default():
    body = _client(avatar_model="does-not-exist").get("/api/config").json()
    assert body["avatar_model"] == DEFAULT
    assert body["avatar_model_url"] == MODELS[DEFAULT]


def test_available_lists_only_installed_rigs():
    body = _client().get("/api/config").json()
    # every advertised rig is a real registry key (fetch_avatar.py installed them)
    assert set(body["avatar_available"]) <= set(MODELS)
    assert DEFAULT in body["avatar_available"]
