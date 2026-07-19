"""The idle machine (SPEC §8) — alive when you're quiet, scripted on purpose.

This is the Ukagaka idle-talk timer reborn (→ ch. 02 §1): a state machine that
calls the same `VrmController` surface a conversation does, between turns. It is
emphatically **not a mind** (SPEC §8.5) — no goals, no salience, no deciding to
reach out. Naming that honestly matters, because Build #5's whole job is to
replace this file with the cognitive tick loop (→ ch. 18) holding the exact same
strings.

Sim-time discipline (SPEC §8.2): every read goes through the injected clock and
every wait through `clock.sleep`, the RNG is seedable, and `step()` — one
decision — is separable from `run()` — the production loop. Tests advance a
VirtualClock and call `step()` directly: hours of idleness in milliseconds.
"""
from __future__ import annotations

import asyncio
import logging
import random
from typing import Awaitable, Callable, Optional

from .avatar.controller import VrmController
from .clock import Clock
from .config import Config
from .tools.timers import Timer, TimerBoard

log = logging.getLogger("world.idle")

# Where the window is, in world space — scene canon, mirrored by the room
# geometry in web/js/stage/SanctuaryScene.js (SPEC §6.1). When she rain-gazes,
# this is what she is looking at.
WINDOW_TARGET = {"x": -1.4, "y": 1.45, "z": 0.6}

ANNOUNCE_CUE = (
    "((The timer for “{label}” just finished. Tell {user} it's done — one "
    "short, warm spoken line, nothing else.))")

SELF_TALK_CUES = (
    "((It's been quiet for a while. Murmur one short line to yourself about the "
    "rain on the window — a private thought said softly aloud, not expecting an "
    "answer.))",
    "((A quiet stretch. One soft spoken line to yourself about this room — the "
    "lamp, the plant, the window seat. Half to yourself.))",
    "((The room is quiet. Let one small remembered thing about {user} surface, "
    "and say one gentle line to yourself about it.))",
)


class IdleMachine:
    """SPEC §8.1's states: engaged · resting · rain_gazing · self_talk · announce."""

    def __init__(self, cfg: Config, clock: Clock, controller: VrmController,
                 timers: TimerBoard,
                 speak: Callable[[str], Awaitable[bool]],
                 rng: Optional[random.Random] = None):
        self.cfg = cfg
        self.clock = clock
        self.controller = controller
        self.timers = timers
        self.speak = speak                     # Runtime.speak_ambient (SPEC §8.4)
        self.rng = rng or random.Random(cfg.idle_seed or None)

        self.state = "engaged"                 # boots quiet; life starts after settle
        self.transitions: list[str] = []       # the journal the tests read
        self._turns_in_flight = 0
        self._last_turn_end = clock.now()
        self._gaze_until = 0.0
        self._next_act = 0.0
        self._next_talk = 0.0
        self._pending: list[Timer] = []        # announcements awaiting delivery (§8.3)
        self._wake = asyncio.Event()

    # ---- notifications from the voice route (SPEC §8.4) ----

    def turn_started(self) -> None:
        self._turns_in_flight += 1
        self._wake.set()

    def turn_ended(self) -> None:
        self._turns_in_flight = max(0, self._turns_in_flight - 1)
        self._last_turn_end = self.clock.now()
        self._wake.set()

    # ---- the machine ----

    def _to(self, state: str) -> None:
        if state != self.state:
            self.state = state
            self.transitions.append(state)

    def _engaged_now(self) -> bool:
        return (self._turns_in_flight > 0
                or (self.clock.now() - self._last_turn_end) < self.cfg.idle_settle_s)

    def _uniform(self, lo: float, hi: float) -> float:
        return self.rng.uniform(lo, hi)

    def _schedule(self) -> None:
        now = self.clock.now()
        self._next_act = now + self._uniform(self.cfg.idle_act_min_s,
                                             self.cfg.idle_act_max_s)
        self._next_talk = now + self._uniform(self.cfg.idle_talk_min_s,
                                              self.cfg.idle_talk_max_s)

    async def step(self) -> None:
        """One decision. `run()` calls this on a cadence; tests call it directly."""
        now = self.clock.now()

        # timer announcements land whatever state we're in (§8.1 announce)
        while not self.timers.due.empty():
            self._pending.append(self.timers.due.get_nowait())

        engaged = self._engaged_now()

        if self._pending and not engaged:
            t = self._pending[0]
            self._to("announce")
            self.controller.set_expression("surprised", 0.6, reset_ms=4000)
            cue = ANNOUNCE_CUE.format(label=t.label, user=self.cfg.user_name)
            if await self.speak(cue):
                self._pending.pop(0)           # delivered
            # no client / turn raced in: stays queued — a timer is a promise (§8.3)
            self._to("resting")
            self._schedule()
            return

        if engaged:
            if self.state != "engaged":
                self._to("engaged")
                self.controller.look_at_camera()   # she turns to you (§8.1)
            return

        if self.state == "engaged":               # settle expired: life resumes
            self._to("resting")
            self._schedule()
            return

        if self.state == "rain_gazing":
            if now >= self._gaze_until:
                self.controller.look_at_camera()
                self._to("resting")
            return

        # resting: the Ukagaka idle-talk timer (§8.1 self_talk)
        if now >= self._next_talk:
            self._to("self_talk")
            cue = self.rng.choice(SELF_TALK_CUES).format(user=self.cfg.user_name)
            await self.speak(cue)                  # False → dropped, not queued (§8.3)
            self._to("resting")
            self._next_talk = now + self._uniform(self.cfg.idle_talk_min_s,
                                                  self.cfg.idle_talk_max_s)
            return

        # resting: micro-acts — the cheap aliveness the room is made of (§8.1)
        if now >= self._next_act:
            act = self.rng.choice(("gaze_drift", "pulse", "posture", "recenter",
                                   "rain_gaze"))
            if act == "gaze_drift":
                self.controller.look_at(self._uniform(-0.9, 0.9),
                                        self._uniform(0.9, 1.6),
                                        self._uniform(-2.0, -0.5))
            elif act == "pulse":
                self.controller.set_expression(
                    self.rng.choice(("relaxed", "happy", "thinking")),
                    self._uniform(0.35, 0.6), reset_ms=5000)
            elif act == "posture":
                self.controller.reset_bone()
                self.controller.set_bone("head",
                                         x=self._uniform(-2.0, 2.0),
                                         z=self._uniform(-3.0, 3.0))
            elif act == "recenter":
                self.controller.reset_bone()
                self.controller.look_at_camera()
            else:                                  # rain_gaze (§8.1)
                self._to("rain_gazing")
                self.controller.look_at(WINDOW_TARGET["x"], WINDOW_TARGET["y"],
                                        WINDOW_TARGET["z"])
                self.controller.set_expression("relaxed", 0.5, reset_ms=0)
                self._gaze_until = now + self._uniform(5.0, 15.0)
            self._next_act = now + self._uniform(self.cfg.idle_act_min_s,
                                                 self.cfg.idle_act_max_s)

    async def run(self) -> None:
        """Production loop: one step every half second, woken early by turns."""
        self._schedule()
        while True:
            try:
                await self.step()
            except Exception:                      # ambient life must never crash the app
                log.exception("idle step failed")
            self._wake.clear()
            await self.clock.sleep(0.5, wake=self._wake)
