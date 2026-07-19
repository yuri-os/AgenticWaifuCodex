"""A tiny OpenRouter client: text (chat completions) + images (the Images API).

Deliberately thin — two calls, no SDK — so the seam is obvious and easy to fake
in tests. The app keeps one instance on `app.state.openrouter`; tests swap in a
`FakeOpenRouter` with the same two methods, so nothing hits the network offline.

Endpoints (OpenRouter, mid-2026):
  POST {base_url}/chat/completions   → choices[0].message.content        (text)
  POST {base_url}/images  {model,prompt} → data[].b64_json (+ media_type) (image)
"""
from __future__ import annotations

import base64
import time
from typing import Protocol

import httpx

from .config import Settings


class OpenRouterError(RuntimeError):
    """A failed OpenRouter call, with an HTTP-ish status for the route to relay."""

    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


class OpenRouterProto(Protocol):
    def chat(self, settings: Settings, messages: list[dict], *,
             model: str | None = None, temperature: float | None = None,
             max_tokens: int | None = None) -> str: ...

    def image(self, settings: Settings, prompt: str, *,
              model: str | None = None, n: int | None = None) -> list[bytes]: ...


class OpenRouterClient:
    """The real client. All model ids / key / base url come from live Settings."""

    def __init__(self, timeout: float = 120.0):
        self._timeout = timeout

    def _headers(self, settings: Settings) -> dict:
        key = settings.resolved_key()
        if not key:
            raise OpenRouterError(
                "No OpenRouter API key. Set one in the Settings tab, export "
                "OPENROUTER_API_KEY, or put it in the Build #2 .env.", status=400)
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            # Optional ranking headers OpenRouter documents; harmless if ignored.
            "HTTP-Referer": "https://yurios.local/card-studio",
            "X-Title": "YuriOS Card Studio",
        }

    def chat(self, settings: Settings, messages: list[dict], *,
             model: str | None = None, temperature: float | None = None,
             max_tokens: int | None = None) -> str:
        body = {
            "model": model or settings.chat_model,
            "messages": messages,
            "temperature": settings.temperature if temperature is None else temperature,
            "max_tokens": settings.max_tokens if max_tokens is None else max_tokens,
        }
        data = self._post(settings, "/chat/completions", body)
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as e:
            raise OpenRouterError(f"Unexpected chat response shape: {e}") from e

    def image(self, settings: Settings, prompt: str, *,
              model: str | None = None, n: int | None = None) -> list[bytes]:
        model = model or settings.image_model
        n = settings.image_count if n is None else n
        out: list[bytes] = []
        # The Images API returns one (or more) images per call; we call it `n`
        # times so a studio always offers a few distinct candidates to choose from.
        for _ in range(max(1, n)):
            data = self._post(settings, "/images", {"model": model, "prompt": prompt})
            for item in _extract_image_items(data):
                out.append(item)
        if not out:
            raise OpenRouterError("OpenRouter returned no image data.")
        return out

    def _post(self, settings: Settings, path: str, body: dict) -> dict:
        url = settings.base_url.rstrip("/") + path
        headers = self._headers(settings)
        # One retry on a 429 (a specific model can be transiently rate-limited by
        # its upstream provider even with your own key). Change the model in the
        # Settings tab if it keeps happening.
        for attempt in range(2):
            try:
                resp = httpx.post(url, json=body, headers=headers, timeout=self._timeout)
            except httpx.HTTPError as e:
                raise OpenRouterError(f"Network error calling OpenRouter: {e}") from e
            if resp.status_code == 429 and attempt == 0:
                time.sleep(1.5)
                continue
            break
        if resp.status_code >= 400:
            raise OpenRouterError(
                f"OpenRouter {resp.status_code}: {_short(resp.text)}",
                status=502 if resp.status_code >= 500 else resp.status_code)
        try:
            return resp.json()
        except ValueError as e:
            raise OpenRouterError(f"OpenRouter returned non-JSON: {e}") from e


def _extract_image_items(data: dict) -> list[bytes]:
    """Pull PNG/JPEG bytes out of an Images API response (data[].b64_json), and
    also tolerate the chat-completions image shape (message.images[].image_url.url
    as a data: URL) in case a model routes that way."""
    out: list[bytes] = []
    for item in (data.get("data") or []):
        b64 = item.get("b64_json")
        if b64:
            out.append(base64.b64decode(b64))
    # Fallback: some models return images inside a chat-style message.
    for choice in (data.get("choices") or []):
        for img in ((choice.get("message") or {}).get("images") or []):
            url = (img.get("image_url") or {}).get("url", "")
            if url.startswith("data:") and "," in url:
                out.append(base64.b64decode(url.split(",", 1)[1]))
    return out


def _short(text: str, limit: int = 300) -> str:
    text = (text or "").strip().replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "…"
