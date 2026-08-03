"""Bounded high-frequency latency diagnostics."""
from __future__ import annotations

from desktop.voice.latency import TurnTrace


def test_latency_log_rotates_without_affecting_the_corpus(tmp_path):
    trace = TurnTrace()
    trace.mark("endpoint")
    trace.finish(trace_dir=tmp_path, max_log_bytes=1)
    TurnTrace().finish(trace_dir=tmp_path, max_log_bytes=1)

    assert (tmp_path / "latency.jsonl.1").exists()
    assert len((tmp_path / "latency.jsonl").read_text().splitlines()) == 1
