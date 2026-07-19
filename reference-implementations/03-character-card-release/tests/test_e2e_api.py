"""End-to-end flow through the API, the way the UI drives it: load → edit →
AI-assist → generate art → select portrait → test-chat → build → download →
verify the emitted .PNG imports the way SillyTavern would. All offline (fake OR)."""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from studio.soulkit import build_card


def test_full_authoring_journey(client):
    # 1. open the studio
    st = client.get("/api/state").json()
    draft = st["draft"]

    # 2. edit a field
    draft["name"] = "Aria"
    draft["personality"] = "warm, wry, devoted, keeps a chipped mug she won't replace"
    assert client.post("/api/draft", json=draft).json()["ok"]

    # 3. AI-assist the description (fake model), accept the suggestion
    sug = client.post("/api/assist", json={"field": "description",
                                           "current": draft["description"],
                                           "mode": "improve", "draft": draft}).json()["suggestion"]
    draft["description"] = sug
    client.post("/api/draft", json=draft)

    # 4. generate candidate art and select #1 as the portrait
    imgs = client.post("/api/image", json={"prompt": "anime portrait, warm", "n": 2}).json()["images"]
    assert len(imgs) == 2
    assert client.post("/api/portrait", json={"image": imgs[0]}).json()["ok"]
    assert client.get("/api/portrait").status_code == 200

    # 5. test-chat with the current card
    reply = client.post("/api/chat", json={"message": "hello", "history": [],
                                           "draft": draft}).json()["reply"]
    assert reply

    # 6. build the card (V3) and confirm the report + self-verification
    built = client.post("/api/build", json={"draft": draft, "spec": "v3"}).json()
    assert built["verified_chunks"]["chara"] == "Aria"
    assert built["used_placeholder_portrait"] is False   # we selected real art in step 4

    # 7. download the .PNG and verify it parses as a character card
    png = client.get("/api/download/card").content
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    card = build_card.extract_card(Path(built["png"]))
    assert card["data"]["name"] == "Aria"
    assert card["spec"] == "chara_card_v3"

    # 8. the round-trip: download the editable soul and confirm it's a real soul
    import io
    import zipfile
    soul = client.get("/api/download/soul").content
    names = zipfile.ZipFile(io.BytesIO(soul)).namelist()
    assert {"CONSTITUTION.md", "PERSONA.md", "SCENARIO.md", "soul.yaml"} <= set(names)
