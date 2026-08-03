"""Latency budget accounting (SPEC §4.2). Per-stage marks + the one end-to-end number."""
from __future__ import annotations

import time

from desktop.voice.latency import TARGETS_MS, TurnTrace


def test_first_audio_is_the_end_to_end_number():
    t = TurnTrace()
    t.mark("endpoint")
    time.sleep(0.005)
    t.mark("first_audio")
    fa = t.first_audio_ms()
    assert fa is not None and fa >= 4.0
    assert t.report()["first_audio_ms"] == round(fa, 1)


def test_over_budget_is_flagged():
    t = TurnTrace()
    # endpoint→first_audio target is 1200 ms; simulate a blown budget by hand
    now = time.perf_counter()
    t.marks["endpoint"] = now
    t.marks["first_audio"] = now + 2.0            # 2000 ms > 1200 ms
    rep = t.report()
    assert "endpoint->first_audio" in rep["over_budget"]
    assert rep["over_budget"]["endpoint->first_audio"] > TARGETS_MS["endpoint->first_audio"]


def test_within_budget_is_empty():
    t = TurnTrace()
    now = time.perf_counter()
    t.marks["endpoint"] = now
    t.marks["first_audio"] = now + 0.5            # 500 ms < 1200 ms
    assert t.report()["over_budget"] == {}


def test_missing_marks_do_not_crash():
    t = TurnTrace()
    t.mark("endpoint")                            # no first_audio (barged-in early)
    rep = t.report()
    assert rep["first_audio_ms"] is None
    assert rep["over_budget"] == {}


def test_trace_written_to_disk(tmp_path):
    t = TurnTrace()
    t.mark("endpoint")
    t.mark("first_audio")
    t.finish(barged_in=False, trace_dir=tmp_path)
    line = (tmp_path / "latency.jsonl").read_text().strip()
    assert '"first_audio_ms"' in line


def test_trace_rotation_keeps_one_previous_generation(tmp_path):
    first = TurnTrace()
    first.mark("endpoint")
    first.mark("first_audio")
    first.finish(trace_dir=tmp_path, max_bytes=1)

    second = TurnTrace()
    second.mark("endpoint")
    second.mark("first_audio")
    second.finish(trace_dir=tmp_path, max_bytes=1)

    assert (tmp_path / "latency.jsonl.1").exists()
    assert (tmp_path / "latency.jsonl").exists()
