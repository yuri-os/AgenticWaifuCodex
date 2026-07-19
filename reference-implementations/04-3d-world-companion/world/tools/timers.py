"""The timer board (SPEC §7.5) — the host schedules the wake, not the MCP server.

`set_timer`'s MCP call validates and returns the contract (`seconds`, `due`);
*this* object owns the actual countdown, on the injected clock, because only the
host owns her voice — when a timer lands, an announcement is queued and the idle
machine speaks it (SPEC §8.1 `announce`). The same ownership split survives into
Build #5, where the engine's scheduler takes this exact job.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from ..clock import Clock


@dataclass
class Timer:
    id: str
    label: str
    due: float                       # clock seconds


@dataclass
class TimerBoard:
    clock: Clock
    _timers: list[Timer] = field(default_factory=list)
    # elapsed timers, consumed by the idle machine's announce state (§8.1)
    due: asyncio.Queue = field(default_factory=asyncio.Queue)
    _wake: asyncio.Event = field(default_factory=asyncio.Event)

    def add(self, *, id: str, label: str, seconds: float) -> Timer:
        t = Timer(id=id, label=label, due=self.clock.now() + seconds)
        self._timers.append(t)
        self._wake.set()             # re-plan the sleep: a nearer deadline may exist
        return t

    def pending(self) -> list[Timer]:
        return sorted(self._timers, key=lambda t: t.due)

    def poll(self) -> list[Timer]:
        """Move every elapsed timer onto the announcement queue. Deterministic —
        the sim-time tests drive this directly (SPEC §13)."""
        now = self.clock.now()
        landed = [t for t in self._timers if t.due <= now]
        self._timers = [t for t in self._timers if t.due > now]
        for t in sorted(landed, key=lambda t: t.due):
            self.due.put_nowait(t)
        return landed

    async def run(self) -> None:
        """Production loop: sleep to the nearest deadline, wake early on add."""
        while True:
            self.poll()
            now = self.clock.now()
            wait = min((t.due - now for t in self._timers), default=60.0)
            self._wake.clear()
            await self.clock.sleep(max(0.05, min(wait, 60.0)), wake=self._wake)
