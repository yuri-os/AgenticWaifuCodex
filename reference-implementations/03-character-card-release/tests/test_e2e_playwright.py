"""Optional UI end-to-end test with Playwright.

Skips cleanly if Playwright (or its browsers) isn't installed — it is NOT a
default dependency. To run it:

    pip install playwright && playwright install chromium
    python -m pytest tests/test_e2e_playwright.py

It launches the real app in offline demo mode (CARD_STUDIO_FAKE_OR=1) so it needs
no key and no network, then drives the browser through the core journey:
edit a field → Generate the card → see the token report → Download appears.
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def server(tmp_path):
    port = _free_port()
    env = {**os.environ, "CARD_STUDIO_FAKE_OR": "1", "PYTHONPATH": str(ROOT)}
    # isolate the workspace so the test doesn't touch a real draft
    env["HOME"] = str(tmp_path)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "studio.app:app",
         "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(ROOT), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    base = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            import urllib.request
            urllib.request.urlopen(base + "/api/health", timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    else:
        proc.terminate()
        pytest.fail("server did not start")
    yield base
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def test_ui_journey(server):
    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch()
    except Exception as e:                    # browsers not installed
        pytest.skip(f"chromium unavailable: {e}")
    try:
        page = browser.new_page()
        page.goto(server, wait_until="networkidle")
        # the five tabs are present
        for name in ["Design", "Art", "Test", "Generate", "Settings"]:
            assert page.query_selector(f"text={name}")
        # edit the name field (first text input in Design)
        name_input = page.query_selector("#tab-design input[type=text]")
        name_input.fill("Testchan")
        page.wait_for_timeout(700)            # let autosave fire
        # go to Generate and build
        page.click("#tabs button[data-tab=generate]")
        page.click("text=Generate card")
        page.wait_for_selector("text=verified", timeout=15000)
        assert page.query_selector("text=Download .PNG")
        # the report table rendered
        assert page.query_selector("table.report")
    finally:
        browser.close()
        pw.stop()
