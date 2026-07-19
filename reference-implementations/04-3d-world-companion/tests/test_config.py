"""Config (SPEC §11) — Build #4's knobs on top of B2's, env-overridable."""
from __future__ import annotations

from world.config import Config


def test_defaults():
    cfg = Config(_env_file=None)
    assert cfg.port == 8767                       # +1 off Build #2
    assert cfg.tools_backend == "mcp"
    assert cfg.tool_max_calls_per_turn == 2
    assert cfg.timer_max_minutes == 180
    assert cfg.idle_enabled and cfg.idle_settle_s == 20.0
    assert cfg.rain_intensity == 0.6
    # the vendored B2 layer is still underneath (one Config object, three builds)
    assert cfg.tts_backend and cfg.vad_onset_frames


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("TOOLS_BACKEND", "off")
    monkeypatch.setenv("IDLE_SETTLE_S", "45.5")
    monkeypatch.setenv("RAIN_INTENSITY", "0.1")
    cfg = Config(_env_file=None)
    assert cfg.tools_backend == "off"
    assert cfg.idle_settle_s == 45.5
    assert cfg.rain_intensity == 0.1
