"""End-to-end demo: drive the VRM model from Python.

Run the viewer first (see ../../README.md):

    cd web && npm install && npm run dev      # http://127.0.0.1:5173

Then run this script:

    cd server && pip install -r requirements.txt && python examples/demo.py

The avatar will look around, cycle through emotions, wave, and "talk".
"""

import sys
import time
from pathlib import Path

# Allow `python examples/demo.py` without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vrm_control import EMOTIONS, VrmController  # noqa: E402


def main() -> None:
    vrm = VrmController().start()

    print("Open http://127.0.0.1:5173 in your browser; waiting for the viewer to connect…")
    if not vrm.wait_for_viewer(timeout=120):
        print("No viewer connected within 120s — is the web app running?")
        return
    print(f"Viewer connected ({vrm.viewers}). Starting demo.")
    time.sleep(0.5)
    vrm.set_shirt_color("#2b3a67") 

    # 1. Gaze: make eye contact.
    vrm.look_at_camera()
    time.sleep(1.5)

    # 2. Emotions: cycle the catalog.
    for emotion in EMOTIONS:
        print(f"  emotion → {emotion}")
        vrm.set_expression(emotion, 0.9)
        time.sleep(1.8)

    vrm.neutral()
    time.sleep(0.5)

    # 3. Pose: raise and wave the right arm via direct bone control.
    print("  pose → wave")
    vrm.set_bone("rightUpperArm", z=-75)   # lift arm out to the side
    for _ in range(3):
        vrm.set_bone("rightLowerArm", z=-30)
        time.sleep(0.3)
        vrm.set_bone("rightLowerArm", z=-70)
        time.sleep(0.3)
    vrm.reset_bone()
    time.sleep(0.5)

    # 4. Speech: happy + animate the mouth.
    print("  speak")
    vrm.set_expression("happy", 0.7)
    vrm.say(2.5)

    vrm.neutral()
    print("Demo complete. Controller stays alive; Ctrl-C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
