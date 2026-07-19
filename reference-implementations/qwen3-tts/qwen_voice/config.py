"""Load and validate the Qwen3-TTS config (config.yaml)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config.yaml"

MODES = ("clone", "design", "custom")


@dataclass(frozen=True)
class Register:
    """One pinned voice asset. Fields used depend on `mode`."""

    name: str
    mode: str
    # clone:
    ref_audio: str | None = None
    ref_text: str | None = None
    # design:
    instruct: str | None = None
    # custom:
    speaker: str | None = None

    def ref_path(self) -> Path | None:
        if not self.ref_audio:
            return None
        p = Path(self.ref_audio)
        if str(p).startswith(("http://", "https://")) or p.is_absolute():
            return p
        return ROOT / p


@dataclass(frozen=True)
class Config:
    models: dict[str, str]          # mode -> model id
    device: str
    dtype: str
    attn: str
    language: str
    registers: dict[str, Register]
    active_register: str

    def model_for(self, mode: str) -> str:
        return self.models[mode]

    def register(self, name: str | None) -> Register:
        name = name or self.active_register
        if name not in self.registers:
            known = ", ".join(self.registers)
            raise KeyError(f"unknown register {name!r}; config has: {known}")
        return self.registers[name]


def _validate(reg: Register) -> None:
    if reg.mode not in MODES:
        raise ValueError(f"register {reg.name!r}: mode must be one of {MODES}")
    need = {"clone": ("ref_audio", "ref_text"),
            "design": ("instruct",),
            "custom": ("speaker",)}[reg.mode]
    for field in need:
        if not getattr(reg, field):
            raise ValueError(f"register {reg.name!r} (mode={reg.mode}) needs {field!r}")


def load_config(path: str | Path | None = None) -> Config:
    path = Path(path) if path else DEFAULT_CONFIG
    raw = yaml.safe_load(path.read_text())

    registers = {}
    for name, r in raw["registers"].items():
        reg = Register(
            name=name, mode=r["mode"],
            ref_audio=r.get("ref_audio"), ref_text=r.get("ref_text"),
            instruct=(r.get("instruct") or "").strip() or None,
            speaker=r.get("speaker"),
        )
        _validate(reg)
        registers[name] = reg

    m = raw["model"]
    models = {mode: m[mode] for mode in MODES}
    active = raw.get("active_register", next(iter(registers)))
    if active not in registers:
        raise ValueError(f"active_register {active!r} not in registers")

    return Config(
        models=models,
        device=m.get("device", "cuda:0"),
        dtype=m.get("dtype", "bfloat16"),
        attn=m.get("attn", "flash_attention_2"),
        language=raw.get("language", "English"),
        registers=registers,
        active_register=active,
    )
