"""Injected time (SPEC §8.2) — the YuriOS discipline, sized for this build.

Everything timed in Build #4 — the idle machine, the timer board, the guard's
rate buckets — takes a `Clock` and never reads the wall clock or bare-sleeps.
That one rule is the whole test story: a `VirtualClock` runs hours of idleness
in milliseconds (SPEC §13), deterministically, on any machine.
"""
from __future__ import annotations

import asyncio
import time


class Clock:
    """Real time. Every read and every cadence wait goes through this object."""

    def now(self) -> float:
        """Seconds, monotonic-enough for scheduling (wall epoch)."""
        return time.time()

    async def sleep(self, seconds: float, *, wake: asyncio.Event | None = None) -> None:
        """Sleep up to `seconds`, waking early if `wake` is set (a turn started,
        a timer landed — the idle machine reacts now, not at the next tick)."""
        if wake is None:
            await asyncio.sleep(seconds)
            return
        try:
            await asyncio.wait_for(wake.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            pass


class VirtualClock(Clock):
    """Deterministic clock for sim-time tests: hours run in milliseconds."""

    def __init__(self, start: float = 1_000_000.0):
        self._now = start

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds

    async def sleep(self, seconds: float, *, wake: asyncio.Event | None = None) -> None:
        # Simulated waits advance virtual time and yield once so other tasks run.
        if wake is not None and wake.is_set():
            return
        self.advance(seconds)
        await asyncio.sleep(0)
