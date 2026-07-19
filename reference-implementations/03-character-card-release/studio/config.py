"""Settings: OpenRouter config + studio knobs, persisted to workspace/settings.json.

The OpenRouter API key is never *stored* by default — it is resolved at call time
from (in order): the value saved in settings.json, the OPENROUTER_API_KEY env var,
or the sibling Build #2 `.env` (reference-implementations/02-desktop-companion/.env),
which is where the reader already put their key. The Settings tab can override any
of this; when it saves a key, it is written to settings.json (gitignored).
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, fields
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                          # 03-character-card-release/
WORKSPACE = ROOT / "workspace"              # gitignored working dir
SETTINGS_PATH = WORKSPACE / "settings.json"

# Where to look for a key the reader already has (the user's stated location).
SIBLING_ENV = ROOT.parent / "02-desktop-companion" / ".env"

# Defaults for a companion card. The chat/assist model is a strong, current model
# (verified live). NOTE: glm-5.2 is a *reasoning* model — it emits a separate
# reasoning field and its thinking shares the token budget, so max_tokens is kept
# generous below or short replies come back truncated/empty (the Build #2 lesson).
# The image model is a fast, capable text-to-image default. All are editable in
# the Settings tab — model ids drift, so treat these as a starting point (presets
# in the UI; uncensored options like venice/uncensored are one click away).
DEFAULT_ASSIST_MODEL = "z-ai/glm-5.2"
DEFAULT_CHAT_MODEL = "z-ai/glm-5.2"
DEFAULT_IMAGE_MODEL = "google/gemini-2.5-flash-image"


@dataclass
class Settings:
    openrouter_api_key: str = ""            # blank => resolve from env / sibling .env
    base_url: str = "https://openrouter.ai/api/v1"
    assist_model: str = DEFAULT_ASSIST_MODEL
    chat_model: str = DEFAULT_CHAT_MODEL
    image_model: str = DEFAULT_IMAGE_MODEL
    image_count: int = 2                    # candidate images per generate
    image_size: str = "1024x1024"
    temperature: float = 0.9
    max_tokens: int = 2048          # generous: the default is a reasoning model

    # ---- persistence -------------------------------------------------------
    @classmethod
    def load(cls) -> "Settings":
        data = {}
        if SETTINGS_PATH.exists():
            try:
                data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                data = {}
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    def save(self) -> None:
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    def update(self, patch: dict) -> "Settings":
        known = {f.name for f in fields(self)}
        for k, v in patch.items():
            if k in known and v is not None:
                setattr(self, k, v)
        return self

    # ---- key resolution ----------------------------------------------------
    def resolved_key(self) -> str:
        """The API key to actually use, without persisting anything."""
        if self.openrouter_api_key.strip():
            return self.openrouter_api_key.strip()
        env = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if env:
            return env
        return _read_env_key(SIBLING_ENV)

    def key_source(self) -> str:
        """Human-readable description of where the key comes from (no secret)."""
        if self.openrouter_api_key.strip():
            return "settings"
        if os.environ.get("OPENROUTER_API_KEY", "").strip():
            return "OPENROUTER_API_KEY env"
        if _read_env_key(SIBLING_ENV):
            return f"sibling .env ({SIBLING_ENV.name})"
        return "none"

    def public_dict(self) -> dict:
        """Settings safe to send to the browser: the key is masked, and the
        resolved source + whether a key is available are surfaced instead."""
        d = asdict(self)
        key = self.resolved_key()
        d["openrouter_api_key"] = _mask(self.openrouter_api_key)
        d["has_key"] = bool(key)
        d["key_source"] = self.key_source()
        return d


_ENV_KEY_RE = re.compile(r"^\s*OPENROUTER_API_KEY\s*=\s*(.+?)\s*$", re.MULTILINE)


def _read_env_key(env_path: Path) -> str:
    """Parse OPENROUTER_API_KEY out of a .env file, ignoring blanks/comments."""
    try:
        text = env_path.read_text(encoding="utf-8")
    except OSError:
        return ""
    for m in _ENV_KEY_RE.finditer(text):
        val = m.group(1).strip().strip('"').strip("'")
        if val and not val.startswith("#"):
            return val
    return ""


def _mask(secret: str) -> str:
    secret = (secret or "").strip()
    if not secret:
        return ""
    if len(secret) <= 8:
        return "•" * len(secret)
    return f"{secret[:4]}…{secret[-4:]}"
