"""Runtime dependencies must match the APIs imported by subprocesses."""
from __future__ import annotations

from pathlib import Path


def test_mcp_is_pinned_to_the_fastmcp_module_generation():
    pyproject = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text()
    assert '"mcp>=1.2,<2"' in pyproject
