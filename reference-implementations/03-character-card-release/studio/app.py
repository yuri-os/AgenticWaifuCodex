"""The Card Studio web app (FastAPI).

Routes (all JSON under /api; the SPA is served from web/):
  GET  /api/state           draft + settings(public) + portrait flag + principles
  GET/POST /api/draft       load / save the working draft
  POST /api/assist          AI help for one field (OpenRouter, grounded in ch.06)
  POST /api/chat            test-chat with the current draft (OpenRouter)
  POST /api/image           generate candidate art from a prompt (OpenRouter)
  GET/POST/DELETE /api/portrait   the selected portrait (base64 in, PNG out)
  GET/POST /api/settings    OpenRouter config (key masked on the way out)
  POST /api/build           build + self-verify the .PNG; returns the token report
  GET  /api/download/card   the built .PNG (attachment)
  GET  /api/download/soul   the draft exported as an editable soul folder (.zip)

`create_app(openrouter=...)` lets tests inject a FakeOpenRouter so nothing hits
the network offline.
"""
from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from . import cardmodel, config, principles, prompts
from .config import Settings
from .openrouter import OpenRouterClient, OpenRouterError, OpenRouterProto

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


# --- working-draft persistence (workspace/draft.json) -----------------------

def _draft_path() -> Path:
    return config.WORKSPACE / "draft.json"


def load_draft() -> dict:
    p = _draft_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    return cardmodel.starter_draft()


def save_draft(draft: dict) -> None:
    config.WORKSPACE.mkdir(parents=True, exist_ok=True)
    _draft_path().write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")


def _portrait_path() -> Path:
    return config.WORKSPACE / "portrait.png"


def _dist_dir() -> Path:
    return config.WORKSPACE / "dist"


class _DemoOpenRouter:
    """Offline stand-in used when CARD_STUDIO_FAKE_OR=1 — lets the UI be demoed
    (and end-to-end tested) with no key and no network. Canned, not clever."""

    def chat(self, settings, messages, *, model=None, temperature=None, max_tokens=None):
        return "*she smiles* (demo mode — set a real OpenRouter key to talk to a model)."

    def image(self, settings, prompt, *, model=None, n=None):
        from PIL import Image, ImageDraw
        n = n if n is not None else settings.image_count
        out = []
        for i in range(max(1, n)):
            img = Image.new("RGB", (384, 576), (17 + i * 8, 17, 26))
            ImageDraw.Draw(img).text((20, 20), f"demo art #{i + 1}", fill=(255, 43, 214))
            buf = io.BytesIO(); img.save(buf, format="PNG"); out.append(buf.getvalue())
        return out


def create_app(openrouter: OpenRouterProto | None = None) -> FastAPI:
    app = FastAPI(title="YuriOS Card Studio")
    if openrouter is None and os.environ.get("CARD_STUDIO_FAKE_OR") == "1":
        openrouter = _DemoOpenRouter()
    app.state.openrouter = openrouter or OpenRouterClient()
    app.state.settings = Settings.load()

    def orr() -> OpenRouterProto:
        return app.state.openrouter

    def settings() -> Settings:
        return app.state.settings

    # ---- state / draft -----------------------------------------------------
    @app.get("/api/health")
    def health():
        return {"ok": True}

    @app.get("/api/state")
    def state():
        return {
            "draft": load_draft(),
            "settings": settings().public_dict(),
            "has_portrait": _portrait_path().exists(),
            "principles": principles.PRINCIPLES,
            "field_principles": principles.FIELD_PRINCIPLES,
        }

    @app.get("/api/draft")
    def get_draft():
        return load_draft()

    @app.post("/api/draft")
    def post_draft(draft: dict = Body(...)):
        save_draft(draft)
        return {"ok": True}

    @app.post("/api/draft/reset")
    def reset_draft():
        d = cardmodel.starter_draft()
        save_draft(d)
        return d

    # ---- AI assist ---------------------------------------------------------
    @app.post("/api/assist")
    async def assist(body: dict = Body(...)):
        field = body.get("field", "")
        if field not in prompts.FIELD_LABELS:
            raise HTTPException(400, f"unknown field: {field!r}")
        msgs = prompts.assist_messages(
            field, body.get("current", ""), mode=body.get("mode", "improve"),
            instruction=body.get("instruction", ""), draft=body.get("draft"))
        text = await _chat(msgs, model=settings().assist_model)
        return {"suggestion": text.strip(), "principles": principles.for_field(field)}

    # ---- test chat ---------------------------------------------------------
    @app.post("/api/chat")
    async def chat(body: dict = Body(...)):
        draft = body.get("draft") or load_draft()
        message = (body.get("message") or "").strip()
        if not message:
            raise HTTPException(400, "empty message")
        msgs = prompts.chat_messages(draft, body.get("history") or [], message)
        text = await _chat(msgs, model=settings().chat_model)
        return {"reply": text.strip()}

    async def _chat(msgs, *, model):
        try:
            return await run_in_threadpool(orr().chat, settings(), msgs, model=model)
        except OpenRouterError as e:
            raise HTTPException(e.status, str(e))

    # ---- image generation --------------------------------------------------
    @app.post("/api/image")
    async def image(body: dict = Body(...)):
        prompt = (body.get("prompt") or "").strip()
        if not prompt:
            raise HTTPException(400, "empty prompt")
        try:
            imgs = await run_in_threadpool(
                orr().image, settings(), prompt,
                model=body.get("model"), n=body.get("n"))
        except OpenRouterError as e:
            raise HTTPException(e.status, str(e))
        return {"images": ["data:image/png;base64," + base64.b64encode(b).decode()
                            for b in imgs]}

    # ---- portrait ----------------------------------------------------------
    @app.get("/api/portrait")
    def get_portrait():
        p = _portrait_path()
        if not p.exists():
            raise HTTPException(404, "no portrait selected")
        return FileResponse(p, media_type="image/png")

    @app.post("/api/portrait")
    def set_portrait(body: dict = Body(...)):
        data_url = body.get("image", "")
        if "," in data_url:
            data_url = data_url.split(",", 1)[1]
        try:
            raw = base64.b64decode(data_url)
        except (ValueError, TypeError):
            raise HTTPException(400, "image must be base64 (optionally a data: URL)")
        config.WORKSPACE.mkdir(parents=True, exist_ok=True)
        _portrait_path().write_bytes(raw)
        return {"ok": True}

    @app.delete("/api/portrait")
    def clear_portrait():
        _portrait_path().unlink(missing_ok=True)
        return {"ok": True}

    # ---- settings ----------------------------------------------------------
    @app.get("/api/settings")
    def get_settings():
        return settings().public_dict()

    @app.post("/api/settings")
    def post_settings(patch: dict = Body(...)):
        # a masked key coming back from the browser (contains '…') is a no-op
        if "…" in (patch.get("openrouter_api_key") or ""):
            patch.pop("openrouter_api_key")
        s = settings().update(patch)
        s.save()
        return s.public_dict()

    # ---- build -------------------------------------------------------------
    @app.post("/api/build")
    def build(body: dict = Body(default={})):
        draft = body.get("draft") or load_draft()
        if body.get("draft"):
            save_draft(draft)
        spec = body.get("spec", "v3")
        try:
            summary = cardmodel.build(draft, _portrait_path(), _dist_dir(), spec=spec)
        except Exception as e:  # build_card raises on a card SillyTavern couldn't read
            raise HTTPException(500, f"build failed: {e}")
        return summary

    @app.get("/api/download/card")
    def download_card():
        pngs = sorted(_dist_dir().glob("*.png")) if _dist_dir().exists() else []
        if not pngs:
            raise HTTPException(404, "no card built yet — click Generate first")
        p = pngs[0]
        return FileResponse(p, media_type="image/png", filename=p.name)

    @app.get("/api/download/soul")
    def download_soul():
        draft = load_draft()
        data = cardmodel.soul_zip(draft, _portrait_path())
        name = cardmodel.to_card_data(draft)["name"].lower().replace(" ", "-")
        return Response(
            data, media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{name}-soul.zip"'})

    @app.post("/api/import")
    def import_card_route(body: dict = Body(...)):
        raw_b64 = body.get("data", "")
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]
        try:
            raw = base64.b64decode(raw_b64)
        except (ValueError, TypeError):
            raise HTTPException(400, "file must be base64 (optionally a data: URL)")
        try:
            draft, portrait = cardmodel.import_card_bytes(raw, body.get("filename", "card.png"))
        except (ValueError, KeyError) as e:
            raise HTTPException(400, f"not a readable character card: {e}")
        save_draft(draft)
        if portrait:
            config.WORKSPACE.mkdir(parents=True, exist_ok=True)
            _portrait_path().write_bytes(portrait)
        return {"draft": draft, "has_portrait": bool(portrait)}

    # ---- static SPA (mounted last so /api wins) ----------------------------
    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

    return app


app = create_app()
