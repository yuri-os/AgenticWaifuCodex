"""Bounded JSONL operational traces."""
from __future__ import annotations

from mind.signals import SignalBus
from mind.trace import TickTrace
from world.clock import VirtualClock


def test_tick_trace_rotates_to_one_previous_generation(tmp_path):
    trace = TickTrace(tmp_path, VirtualClock(), max_bytes=1)
    trace.record(activity_state="IDLE", sensed=[], appraised=[], decided={}, acted={})
    trace.record(activity_state="IDLE", sensed=[], appraised=[], decided={}, acted={})

    assert (tmp_path / "ticks.jsonl.1").exists()
    assert len(trace.tail()) == 1


def test_signal_log_rotates_to_one_previous_generation(tmp_path):
    bus = SignalBus(VirtualClock(), log_dir=tmp_path, max_log_bytes=1)
    bus.post("one")
    bus.post("two")

    assert (tmp_path / "signals.jsonl.1").exists()
    assert '"type": "two"' in (tmp_path / "signals.jsonl").read_text()
