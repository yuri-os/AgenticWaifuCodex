"""Python control bridge for the VRM viewer.

The viewer (browser) connects to this process as a WebSocket *client*. Each public
method here serializes a command to JSON and broadcasts it to every connected viewer.

The server runs on its own asyncio loop in a background thread, so the public API is
ordinary blocking Python you can call from a script, a REPL, or your own AI loop::

    from vrm_control import VrmController

    vrm = VrmController()
    vrm.start()
    vrm.wait_for_viewer()          # block until the browser tab connects
    vrm.set_expression("happy", 0.8)
    vrm.look_at_camera()
    vrm.set_bone("rightUpperArm", z=-70)   # wave the arm out
    vrm.say(2.0)                   # animate the mouth for ~2s

Command protocol mirrors web/src/stage/types.ts.
"""

from __future__ import annotations

import asyncio
import json
import threading
from typing import Any, Dict, Optional, Set

from websockets.asyncio.server import ServerConnection, serve

# Humanoid bones the viewer understands (VRM standard subset). Exposed for callers
# that want to validate or enumerate; the viewer also warns on unknown names.
HUMANOID_BONES = (
    "hips", "spine", "chest", "upperChest", "neck", "head",
    "leftShoulder", "leftUpperArm", "leftLowerArm", "leftHand",
    "rightShoulder", "rightUpperArm", "rightLowerArm", "rightHand",
    "leftUpperLeg", "leftLowerLeg", "leftFoot",
    "rightUpperLeg", "rightLowerLeg", "rightFoot",
)

# Emotions the viewer's EmoteController knows (spec §5.2).
EMOTIONS = ("happy", "sad", "angry", "surprised", "neutral", "relaxed")

# Material names in the bundled avatar.vrm (VRoid naming). Use these with
# set_material_color(); other models expose their own names (see materialNames() in JS).
MATERIALS = {
    "shirt": "Tops_01_CLOTH",
    "pants": "Bottoms_01_CLOTH",
    "shoes": "Shoes_01_CLOTH",
    "skin": "Body_00_SKIN",
    "hair": "Hair_00_HAIR",
}


class VrmController:
    """Drives one or more connected VRM viewers over WebSocket."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self._clients: Set[ServerConnection] = set()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready = threading.Event()        # server is listening
        self._viewer_present = threading.Event()  # >=1 viewer connected

    # ---- lifecycle ----

    def start(self) -> "VrmController":
        """Start the WebSocket server in a background thread (idempotent)."""
        if self._thread and self._thread.is_alive():
            return self
        self._thread = threading.Thread(target=self._run, name="vrm-bridge", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)
        print(f"[VrmController] listening on ws://{self.host}:{self.port}")
        return self

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self) -> None:
        async with serve(self._handler, self.host, self.port):
            self._ready.set()
            await asyncio.Future()  # run forever

    async def _handler(self, ws: ServerConnection) -> None:
        self._clients.add(ws)
        self._viewer_present.set()
        try:
            async for _message in ws:
                # Viewer→server messages (hello/ready) are informational only.
                pass
        finally:
            self._clients.discard(ws)
            if not self._clients:
                self._viewer_present.clear()

    def wait_for_viewer(self, timeout: Optional[float] = None) -> bool:
        """Block until at least one browser viewer is connected."""
        return self._viewer_present.wait(timeout=timeout)

    @property
    def viewers(self) -> int:
        return len(self._clients)

    # ---- transport ----

    def _send(self, command: Dict[str, Any]) -> None:
        if self._loop is None:
            raise RuntimeError("Controller not started; call start() first.")
        payload = json.dumps(command)
        asyncio.run_coroutine_threadsafe(self._broadcast(payload), self._loop)

    async def _broadcast(self, payload: str) -> None:
        if not self._clients:
            return
        await asyncio.gather(
            *(ws.send(payload) for ws in list(self._clients)),
            return_exceptions=True,
        )

    # ---- control API (channels from the spec) ----

    def set_expression(self, name: str, intensity: float = 1.0) -> None:
        """Channel 2 — trigger an emotion; the viewer auto-resets to neutral after 3s."""
        self._send({"type": "expression", "name": name, "intensity": float(intensity)})

    def set_expression_raw(self, values: Dict[str, float]) -> None:
        """Channel 2 — set raw blendshape weights directly, e.g. {"blink": 1.0}."""
        self._send({"type": "expression_raw", "values": {k: float(v) for k, v in values.items()}})

    def look_at_camera(self) -> None:
        """Channel 5 — make eye contact with the viewer's camera."""
        self._send({"type": "look_at", "mode": "camera"})

    def look_forward(self) -> None:
        """Channel 5 — neutral straight-ahead gaze."""
        self._send({"type": "look_at", "mode": "none"})

    def look_at(self, x: float, y: float, z: float) -> None:
        """Channel 5 — aim gaze at an explicit world-space point."""
        self._send({"type": "look_at", "target": {"x": float(x), "y": float(y), "z": float(z)}})

    def set_bone(self, name: str, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """Channel 6 — override a humanoid bone's local rotation (Euler degrees)."""
        self._send({"type": "bone", "name": name, "euler": {"x": float(x), "y": float(y), "z": float(z)}})

    def reset_bone(self, name: Optional[str] = None) -> None:
        """Release a bone override (or all overrides when name is None)."""
        cmd: Dict[str, Any] = {"type": "bone_reset"}
        if name is not None:
            cmd["name"] = name
        self._send(cmd)

    def set_mouth(self, value: float) -> None:
        """Channel 4 — mouth-open amount in [0,1] (audio-less lip-sync substitute)."""
        self._send({"type": "mouth", "value": float(value)})

    def set_material_color(self, material: str, color: str) -> None:
        """Tint a material by name (CSS hex, e.g. '#3b5bdb'). See MATERIALS for the
        bundled avatar's names, e.g. set_material_color('Tops_01_CLOTH', '#222')."""
        self._send({"type": "material_color", "material": material, "color": color})

    def set_shirt_color(self, color: str) -> None:
        """Convenience: tint the bundled avatar's t-shirt (Tops_01_CLOTH)."""
        self.set_material_color(MATERIALS["shirt"], color)

    def play_animation(self, url: str, loop: bool = True, fade_in: float = 0.3) -> None:
        """Channel 1 — play a .vrma clip (served from the viewer's /public)."""
        self._send({"type": "animation", "url": url, "loop": loop, "fadeIn": float(fade_in)})

    def load_model(self, url: str) -> None:
        """Swap the .vrm model (served from the viewer's /public)."""
        self._send({"type": "load_model", "url": url})

    # ---- convenience helpers ----

    def say(self, seconds: float, fps: int = 30) -> None:
        """Animate the mouth with a simple pseudo-speech wiggle for `seconds`."""
        import math
        import time

        frames = int(seconds * fps)
        for i in range(frames):
            # Two overlapping sines → uneven, speech-like opening.
            v = 0.35 + 0.35 * abs(math.sin(i * 0.9)) + 0.15 * abs(math.sin(i * 0.37))
            self.set_mouth(min(1.0, v))
            time.sleep(1.0 / fps)
        self.set_mouth(0.0)

    def neutral(self) -> None:
        """Reset expression and bone overrides to a calm default."""
        self.set_expression("neutral")
        self.reset_bone()
        self.set_mouth(0.0)
