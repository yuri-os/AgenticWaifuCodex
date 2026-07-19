"""API endpoint tests with a faked OpenRouter (offline)."""


def test_health(client):
    assert client.get("/api/health").json() == {"ok": True}


def test_state_has_draft_and_principles(client):
    st = client.get("/api/state").json()
    assert st["draft"]["name"] == "Mira"
    assert len(st["principles"]) == 10
    assert st["settings"]["has_key"] is False   # hermetic: no key available
    assert "openrouter_api_key" in st["settings"]
    assert "…" not in st["settings"]["openrouter_api_key"] or st["settings"]["openrouter_api_key"] == ""


def test_draft_save_and_load(client):
    draft = client.get("/api/draft").json()
    draft["name"] = "Nova"
    assert client.post("/api/draft", json=draft).json()["ok"] is True
    assert client.get("/api/draft").json()["name"] == "Nova"


def test_assist_uses_openrouter_and_returns_suggestion(client):
    r = client.post("/api/assist", json={"field": "description", "current": "x",
                                         "mode": "improve"})
    assert r.status_code == 200
    body = r.json()
    assert body["suggestion"].startswith("FAKE_REPLY")
    assert len(body["principles"]) >= 1
    # the assist call used the assist_model and injected ch.06 principles
    sent = client.fake.chat_calls[-1]
    assert "ch. 06" in sent["messages"][0]["content"]


def test_assist_rejects_unknown_field(client):
    assert client.post("/api/assist", json={"field": "nope"}).status_code == 400


def test_chat_assembles_card_and_replies(client):
    r = client.post("/api/chat", json={"message": "hi there", "history": []})
    assert r.status_code == 200
    assert r.json()["reply"].startswith("FAKE_REPLY")
    sysmsg = client.fake.chat_calls[-1]["messages"][0]["content"]
    assert "You are Mira" in sysmsg          # the draft was assembled as a system prompt


def test_chat_empty_message_400(client):
    assert client.post("/api/chat", json={"message": "  "}).status_code == 400


def test_image_returns_data_urls(client):
    r = client.post("/api/image", json={"prompt": "an anime portrait", "n": 3})
    assert r.status_code == 200
    imgs = r.json()["images"]
    assert len(imgs) == 3
    assert all(u.startswith("data:image/png;base64,") for u in imgs)
    assert client.fake.image_calls[-1]["n"] == 3


def test_portrait_set_get_delete(client):
    # 1x1 red pixel PNG (base64)
    px = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGP4z8AAAAMBAQDJ"
          "/pELAAAAAElFTkSuQmCC")
    assert client.get("/api/portrait").status_code == 404
    assert client.post("/api/portrait", json={"image": "data:image/png;base64," + px}).json()["ok"]
    assert client.get("/api/portrait").status_code == 200
    assert client.request("DELETE", "/api/portrait").json()["ok"]
    assert client.get("/api/portrait").status_code == 404


def test_settings_save_masks_key(client):
    r = client.post("/api/settings", json={"openrouter_api_key": "sk-or-secret-abcdef123456",
                                           "chat_model": "some/model"})
    body = r.json()
    assert body["chat_model"] == "some/model"
    assert body["has_key"] is True
    assert body["key_source"] == "settings"
    assert "sk-or" not in body["openrouter_api_key"] or "…" in body["openrouter_api_key"]
    # a masked key coming back in is ignored (not persisted as the literal mask)
    client.post("/api/settings", json={"openrouter_api_key": body["openrouter_api_key"]})
    assert client.get("/api/settings").json()["has_key"] is True


def test_build_returns_report_and_verified(client):
    r = client.post("/api/build", json={"spec": "v3"})
    assert r.status_code == 200
    body = r.json()
    assert set(body["verified_chunks"]) == {"chara", "ccv3"}
    assert any(row["field"] == "description" for row in body["report"])


def test_download_card_after_build(client):
    assert client.get("/api/download/card").status_code == 404   # nothing built yet
    client.post("/api/build", json={"spec": "v3"})
    r = client.get("/api/download/card")
    assert r.status_code == 200
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_download_soul_zip(client):
    r = client.get("/api/download/soul")
    assert r.status_code == 200
    assert r.content[:2] == b"PK"    # zip magic


def test_import_card_roundtrip_through_api(client):
    client.post("/api/build", json={"spec": "v3"})
    png = client.get("/api/download/card").content
    import base64
    r = client.post("/api/import", json={"filename": "mira.png",
                                         "data": base64.b64encode(png).decode()})
    assert r.status_code == 200
    assert r.json()["draft"]["name"] == "Mira"


def test_serves_spa_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "CARD" in r.text and "app.js" in r.text
