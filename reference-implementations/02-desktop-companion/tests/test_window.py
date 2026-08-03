"""desktop/window.py — the `--window` desktop-pet launcher.

The module must import with no GUI backend installed (pywebview is imported
lazily inside run()), the page URL must carry ?desktop=1 and never point at
0.0.0.0, and the readiness probe must return quickly for a dead port.
"""
from __future__ import annotations

import socket
import time

import pytest

from desktop import window
from desktop.config import Config


def test_module_imports_without_pywebview():
    # importing desktop.window at the top of this file already proves it; assert
    # the public helpers are present so the loader can't silently no-op.
    assert callable(window.run) and callable(window.desktop_url)


def test_desktop_url_carries_flag_and_is_local():
    url = window.desktop_url(Config(port=8766))
    assert url == "http://127.0.0.1:8766/?desktop=1"


def test_desktop_url_never_targets_wildcard_host():
    # a browser can't connect to 0.0.0.0 — it must be rewritten to loopback
    url = window.desktop_url(Config(host="0.0.0.0", port=9000))
    assert url == "http://127.0.0.1:9000/?desktop=1"


def test_run_refuses_an_occupied_port():
    # if a previous instance still holds the port, run() must die loudly instead
    # of letting the window connect to the stale server (old code, old .env)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
        with pytest.raises(SystemExit, match="already in use"):
            window.run(Config(port=port))


def test_wait_for_server_times_out_fast_on_dead_port():
    t0 = time.monotonic()
    assert window._wait_for_server("127.0.0.1", 1, timeout=0.5) is False
    assert time.monotonic() - t0 < 3.0


def test_wsl_rebinds_loopback_for_the_windows_browser(monkeypatch):
    monkeypatch.setattr(window, "_is_wsl", lambda: True)
    cfg = Config(host="127.0.0.1", port=9000)
    assert window.wsl_server_config(cfg).host == "0.0.0.0"
    assert window.wsl_server_config(Config(host="0.0.0.0", port=9000)).host == "0.0.0.0"


def test_wsl_handoff_uses_windows_browser(monkeypatch):
    calls = []
    monkeypatch.setattr(window.subprocess, "check_output",
                        lambda *args, **kwargs: "172.30.1.2\n")
    monkeypatch.setattr(window.subprocess, "run",
                        lambda args, **kwargs: calls.append((args, kwargs)))

    window.open_wsl_window(9000)

    assert calls[0][0][:2] == ["powershell.exe", "-NoProfile"]
    assert "172.30.1.2:9000" in calls[0][0][-1]
