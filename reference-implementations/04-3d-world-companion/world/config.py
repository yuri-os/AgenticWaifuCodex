"""Typed configuration (SPEC §11) — extends Build #2's, which extends Build #1's.

The vendored `desktop.config.Config` already holds every brain + voice knob
(models, Vault, STT/TTS/VAD, the loop). This subclass adds Build #4's knobs —
the hands (§7), the idle machine (§8), the room (§6) — and re-points the port.
"""
from __future__ import annotations

from pathlib import Path

from desktop.config import Config as VoiceConfig


class Config(VoiceConfig):
    port: int = 8767                            # +1 off Build #2's 8766
    companion_name: str = "yuri"                # the `hello` event + the chat header

    # --- the hands: tools over MCP (SPEC §7) ---
    # mcp = the real in-repo MCP server over stdio (§7.2). fake = deterministic
    # offline results (tests, and a no-deps demo). off = no hands — she talks
    # about doing things instead of doing them (Build #2 behaviour).
    tools_backend: str = "mcp"                  # mcp | fake | off
    tool_max_calls_per_turn: int = 2            # per-turn cap (§7.3)
    tool_timeout_s: float = 10.0                # per-call timeout (§7.3)
    tool_log_dir: Path = Path("./tool-logs")    # JSONL audit, one line per call (§7.3)
    tool_log_max_bytes: int = 2_000_000         # rotate calls.jsonl at 2 MB
    tool_rate_timer: int = 6                    # calls/minute, token bucket (§7.3)
    tool_rate_music: int = 6
    tool_rate_weather: int = 4
    timer_max_minutes: int = 180                # set_timer upper bound (§7.1)
    weather_backend: str = "open_meteo"         # open_meteo | fake (§7.5)
    weather_city: str = "Tokyo"                 # default when she isn't told one

    # --- her camera: selfies via the vendored forge (SPEC §7.6) ---
    # openrouter = hosted generation (needs OPENROUTER_API_KEY, keeps the GPU
    # free). mock = deterministic placeholder cards, no key, no network (tests,
    # demos). off = no camera — the tool isn't advertised. A missing key
    # degrades openrouter → mock with one loud WARNING (the voice-fakes
    # philosophy). Default model: seedream — cheap enough for casual selfies;
    # sourceful/riverflow-v2.5-pro is the brand-art register (pricier, one knob).
    selfie_backend: str = "openrouter"          # openrouter | mock | off
    selfie_model: str = "bytedance-seed/seedream-4.5"
    selfie_dir: Path = Path("./selfies")        # saved shots, served at /selfies/
    tool_rate_selfie: int = 2                   # calls/minute — images are expensive

    # --- the idle machine: alive when you're quiet (SPEC §8) ---
    idle_enabled: bool = True
    idle_settle_s: float = 20.0                 # quiet after a turn before ambient life
    idle_act_min_s: float = 8.0                 # micro-act window (gaze drift, pulse…)
    idle_act_max_s: float = 25.0
    idle_talk_min_s: float = 120.0              # the Ukagaka idle-talk timer (§8.1)
    idle_talk_max_s: float = 300.0
    idle_seed: int = 0                          # 0 = unseeded; tests pin a seed (§8.2)

    # --- the room (SPEC §6) ---
    rain_intensity: float = 0.6                 # 0..1, pushed to the scene at connect

    # --- the desktop window (SPEC §6.5–§6.6) ---
    # Which body `python -m world --window` floats: the VRM stage (/?desktop=1)
    # or the vendored Build #2 Live2D client (/live2d/?desktop=1). The window
    # frame itself (WINDOW_* knobs) is inherited from the vendored B2 config;
    # the Live2D rig inside it is the inherited AVATAR_MODEL knob.
    desktop_body: str = "vrm"                   # vrm | live2d
