"""Shared test fixtures: an isolated workspace + a fake OpenRouter (offline)."""
import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402

from studio import config  # noqa: E402
from studio.app import create_app  # noqa: E402


class FakeOpenRouter:
    """Same two methods as OpenRouterClient; canned, deterministic, no network."""

    def __init__(self):
        self.chat_calls = []
        self.image_calls = []

    def chat(self, settings, messages, *, model=None, temperature=None, max_tokens=None):
        self.chat_calls.append({"messages": messages, "model": model})
        last = messages[-1]["content"] if messages else ""
        return f"FAKE_REPLY[{model}]: {last[:48]}"

    def image(self, settings, prompt, *, model=None, n=None):
        n = n if n is not None else settings.image_count
        self.image_calls.append({"prompt": prompt, "model": model, "n": n})
        out = []
        for i in range(max(1, n)):
            buf = io.BytesIO()
            Image.new("RGB", (16, 16), (20 + i * 10, 20, 30)).save(buf, format="PNG")
            out.append(buf.getvalue())
        return out


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    ws = tmp_path / "workspace"
    monkeypatch.setattr(config, "WORKSPACE", ws)
    monkeypatch.setattr(config, "SETTINGS_PATH", ws / "settings.json")
    # isolate from the real sibling .env + env key so tests are hermetic
    monkeypatch.setattr(config, "SIBLING_ENV", tmp_path / "no-such.env")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    return ws


@pytest.fixture
def fake():
    return FakeOpenRouter()


@pytest.fixture
def client(workspace, fake):
    from fastapi.testclient import TestClient
    c = TestClient(create_app(openrouter=fake))
    c.fake = fake
    return c
