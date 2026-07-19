"""The idle machine (SPEC §8, §13) — states, windows, preemption, all in sim time.

Hours of idleness run in milliseconds: the VirtualClock advances, `step()` is
called directly, and a scripted RNG makes every "random" act deterministic.
"""
from __future__ import annotations

import pytest

from world.idle import WINDOW_TARGET, IdleMachine


class ScriptRandom:
    """uniform() returns lo (deterministic windows); choice() follows a script."""

    def __init__(self, choices=()):
        self.choices = list(choices)

    def uniform(self, lo, hi):
        return lo

    def choice(self, seq):
        return self.choices.pop(0) if self.choices else seq[0]


class Speaker:
    """A speak_ambient stand-in: scripted accept/refuse + a transcript."""

    def __init__(self, accept=True):
        self.accept = accept
        self.cues: list[str] = []

    async def __call__(self, cue: str) -> bool:
        self.cues.append(cue)
        return self.accept


def machine(cfg, clock, controller, timers, speaker, choices=()):
    return IdleMachine(cfg, clock, controller, timers, speaker,
                       rng=ScriptRandom(choices))


async def test_silent_while_engaged(cfg, clock, controller, timers):
    speaker = Speaker()
    m = machine(cfg, clock, controller, timers, speaker)
    m.turn_started()
    clock.advance(3600)                     # an hour of conversation
    for _ in range(10):
        await m.step()
    assert m.state == "engaged"
    assert controller.commands == [] and speaker.cues == []


async def test_settle_window_then_life_resumes(cfg, clock, controller, timers):
    m = machine(cfg, clock, controller, timers, Speaker())
    m.turn_started(); m.turn_ended()
    clock.advance(cfg.idle_settle_s - 1)    # still inside the settle window
    await m.step()
    assert m.state == "engaged"
    clock.advance(2)                        # settle expired
    await m.step()
    assert m.state == "resting"
    assert "resting" in m.transitions


async def test_micro_act_fires_at_the_scheduled_window(cfg, clock, controller,
                                                       timers):
    m = machine(cfg, clock, controller, timers, Speaker(), choices=["pulse"])
    m.turn_ended()
    clock.advance(cfg.idle_settle_s + 1)
    await m.step()                          # → resting, schedules next act at +8 s
    clock.advance(cfg.idle_act_min_s + 0.1)
    await m.step()
    pulses = [c for c in controller.commands if c["type"] == "expression"]
    assert len(pulses) == 1
    assert pulses[0]["intensity"] == pytest.approx(0.35)   # uniform() == lo


async def test_rain_gaze_looks_at_the_window_then_returns(cfg, clock, controller,
                                                          timers):
    m = machine(cfg, clock, controller, timers, Speaker(), choices=["rain_gaze"])
    m.turn_ended()
    clock.advance(cfg.idle_settle_s + 1)
    await m.step()                          # resting
    clock.advance(cfg.idle_act_min_s + 0.1)
    await m.step()                          # rain_gazing
    assert m.state == "rain_gazing"
    looks = [c for c in controller.commands if c["type"] == "look_at"]
    assert looks[-1]["target"] == WINDOW_TARGET     # scene canon (§6.1)
    clock.advance(5.1)                      # gaze window (uniform → 5 s) expires
    await m.step()
    assert m.state == "resting"
    assert controller.commands[-1] == {"type": "look_at", "mode": "camera"}


async def test_self_talk_speaks_through_the_ambient_seam(cfg, clock, controller,
                                                         timers):
    speaker = Speaker()
    m = machine(cfg, clock, controller, timers, speaker)
    m.turn_ended()
    clock.advance(cfg.idle_settle_s + 1)
    await m.step()                          # resting; talk scheduled at +120 s
    clock.advance(cfg.idle_talk_min_s + 1)
    await m.step()
    assert len(speaker.cues) == 1
    assert "((" in speaker.cues[0]          # a cue, not user text
    assert m.state == "resting" and "self_talk" in m.transitions


async def test_self_talk_dropped_when_nobody_listens(cfg, clock, controller,
                                                     timers):
    speaker = Speaker(accept=False)         # no client / injector busy → False
    m = machine(cfg, clock, controller, timers, speaker)
    m.turn_ended()
    clock.advance(cfg.idle_settle_s + 1)
    await m.step()
    clock.advance(cfg.idle_talk_min_s + 1)
    await m.step()
    assert len(speaker.cues) == 1           # offered once…
    assert m._pending == []                 # …and dropped, never queued (§8.3)


async def test_timer_announcement_waits_for_engagement_to_end(cfg, clock,
                                                              controller, timers):
    speaker = Speaker()
    m = machine(cfg, clock, controller, timers, speaker)
    timers.add(id="t", label="tea", seconds=60)
    clock.advance(61)
    timers.poll()                           # the timer lands on the due queue

    m.turn_started()                        # but she's mid-conversation
    await m.step()
    assert speaker.cues == []               # never talks over the user (§8.1)
    assert m._pending and m._pending[0].label == "tea"

    m.turn_ended()
    clock.advance(cfg.idle_settle_s + 1)
    await m.step()
    assert len(speaker.cues) == 1 and "tea" in speaker.cues[0]
    assert m._pending == []                 # delivered
    assert "announce" in m.transitions
    surprise = [c for c in controller.commands if c["type"] == "expression"]
    assert surprise and surprise[0]["name"] == "surprised"


async def test_undeliverable_announcement_stays_queued(cfg, clock, controller,
                                                       timers):
    """A timer is a promise (§8.3): if no client is connected when it lands, the
    announcement queues and delivers on the next chance — unlike self-talk."""
    speaker = Speaker(accept=False)
    m = machine(cfg, clock, controller, timers, speaker)
    timers.add(id="t", label="oven", seconds=10)
    clock.advance(cfg.idle_settle_s + 11)
    timers.poll()
    await m.step()
    assert len(speaker.cues) == 1 and m._pending    # offered, not delivered

    speaker.accept = True                   # a client reconnects
    await m.step()
    assert len(speaker.cues) == 2 and m._pending == []


async def test_engagement_preempts_and_she_turns_to_you(cfg, clock, controller,
                                                        timers):
    m = machine(cfg, clock, controller, timers, Speaker())
    m.turn_ended()
    clock.advance(cfg.idle_settle_s + 1)
    await m.step()                          # resting
    m.turn_started()                        # the user speaks
    await m.step()
    assert m.state == "engaged"
    assert controller.commands[-1] == {"type": "look_at", "mode": "camera"}
