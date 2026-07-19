#!/usr/bin/env python3
"""Launch the Card Studio. Run from the build root:  python scripts/run.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8777
    print(f"Card Studio → http://{host}:{port}")
    uvicorn.run("studio.app:app", host=host, port=port, reload=False)
