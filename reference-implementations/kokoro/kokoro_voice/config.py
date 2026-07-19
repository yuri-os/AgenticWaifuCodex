"""Load and validate the voice config (config.yaml)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"


@dataclass(frozen=True)
class Register:
    """One pinned voice asset (a Kokoro voice id + speed)."""

    voice: str
    speed: float = 1.0


@dataclass(frozen=True)
class VoiceConfig:
    lang_code: str
    sample_rate: int
    registers: dict[str, Register]
    active_register: str

    @property
    def active(self) -> Register:
        return self.registers[self.active_register]

    def register(self, name: str | None) -> Register:
        """Resolve a register by name, falling back to the active one."""
        if name is None:
            return self.active
        if name not in self.registers:
            known = ", ".join(self.registers)
            raise KeyError(f"unknown register {name!r}; config has: {known}")
        return self.registers[name]


def load_config(path: str | Path | None = None) -> VoiceConfig:
    path = Path(path) if path else DEFAULT_CONFIG
    raw = yaml.safe_load(path.read_text())

    registers = {
        name: Register(voice=r["voice"], speed=float(r.get("speed", 1.0)))
        for name, r in raw["registers"].items()
    }
    active = raw.get("active_register", "default")
    if active not in registers:
        raise ValueError(f"active_register {active!r} not in registers")

    return VoiceConfig(
        lang_code=raw.get("lang_code", "a"),
        sample_rate=int(raw.get("sample_rate", 24000)),
        registers=registers,
        active_register=active,
    )
