"""Load and validate the GPT-SoVITS client config (config.yaml)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config.yaml"


@dataclass(frozen=True)
class Voice:
    """A pinned voice asset: a reference clip + transcript, or a fine-tune."""

    name: str
    ref_audio: str
    prompt_text: str
    prompt_lang: str = "en"
    text_lang: str = "en"
    gpt_weights: str | None = None
    sovits_weights: str | None = None

    def ref_path(self) -> Path:
        """Resolve ref_audio relative to the repo root if not absolute."""
        p = Path(self.ref_audio)
        return p if p.is_absolute() else (ROOT / p)


@dataclass(frozen=True)
class Config:
    server_url: str
    timeout_s: float
    sample_rate: int
    voices: dict[str, Voice]
    registers: dict[str, str]
    active_register: str
    inference: dict = field(default_factory=dict)

    def voice_for_register(self, register: str | None) -> Voice:
        name = register or self.active_register
        if name not in self.registers:
            known = ", ".join(self.registers)
            raise KeyError(f"unknown register {name!r}; config has: {known}")
        return self.voices[self.registers[name]]


def load_config(path: str | Path | None = None) -> Config:
    path = Path(path) if path else DEFAULT_CONFIG
    raw = yaml.safe_load(path.read_text())

    voices = {
        name: Voice(
            name=name,
            ref_audio=v["ref_audio"],
            prompt_text=v["prompt_text"],
            prompt_lang=v.get("prompt_lang", "en"),
            text_lang=v.get("text_lang", "en"),
            gpt_weights=v.get("gpt_weights"),
            sovits_weights=v.get("sovits_weights"),
        )
        for name, v in raw["voices"].items()
    }
    registers = dict(raw["registers"])
    active = raw.get("active_register", next(iter(registers)))
    for reg, vname in registers.items():
        if vname not in voices:
            raise ValueError(f"register {reg!r} points at unknown voice {vname!r}")

    server = raw.get("server", {})
    return Config(
        server_url=server.get("url", "http://127.0.0.1:9880").rstrip("/"),
        timeout_s=float(server.get("timeout_s", 180)),
        sample_rate=int(raw.get("sample_rate", 32000)),
        voices=voices,
        registers=registers,
        active_register=active,
        inference=raw.get("inference", {}),
    )
