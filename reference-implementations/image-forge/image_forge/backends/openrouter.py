"""OpenRouter image backend — the repo's proven generation path.

This is the live, on-demand sibling of ``artworks/generate.py``: same API
(OpenRouter chat-completions with ``modalities:["image"]``), same default model
(``sourceful/riverflow-v2.5-pro``), so a runtime selfie matches the locked brand
set. Auth, like the batch script: ``$OPENROUTER_TOKEN`` or
``~/.config/openrouter/key`` — never store the key in this folder.

Editing: models that accept an input image (e.g. a Gemini-image / "nano-banana"
route, → ch. 26) can re-render *her* into a new scene. riverflow is generate-only,
so ``edit`` is gated on the configured model accepting image input.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request
from pathlib import Path
from typing import Optional

from ..types import Capabilities, EditRequest, GenRequest, ImageResult
from .base import ImageBackend

API = "https://openrouter.ai/api/v1/chat/completions"


def _api_key() -> str:
    key = os.environ.get("OPENROUTER_TOKEN", "").strip()
    if not key:
        f = Path.home() / ".config/openrouter/key"
        if f.exists():
            key = f.read_text().strip()
    if not key:
        raise RuntimeError("no API key: set $OPENROUTER_TOKEN or write ~/.config/openrouter/key")
    return key


class OpenRouterBackend(ImageBackend):
    name = "openrouter"

    def __init__(
        self,
        model: str = "sourceful/riverflow-v2.5-pro",
        *,
        timeout: int = 300,
        supports_edit: bool = False,
        uncensored: Optional[bool] = False,
    ) -> None:
        self.model = model
        self.timeout = timeout
        self._supports_edit = supports_edit
        self._uncensored = uncensored

    def _post(self, content) -> bytes:
        # riverflow 404s if "text" is requested alongside "image".
        modalities = ["image"] if self.model.startswith("sourceful/") else ["image", "text"]
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "modalities": modalities,
        }).encode()
        req = urllib.request.Request(API, data=body, headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        })
        r = json.load(urllib.request.urlopen(req, timeout=self.timeout))
        msg = r["choices"][0]["message"]
        images = msg.get("images") or []
        if not images:
            raise RuntimeError(f"no image in response (text: {(msg.get('content') or '')[:200]!r})")
        raw = base64.b64decode(images[0]["image_url"]["url"].split(",", 1)[1])
        return raw, (r.get("usage") or {}).get("cost")

    def generate(self, req: GenRequest) -> ImageResult:
        # OpenRouter image routes take a single prompt string; fold the negative
        # in the way these models expect.
        prompt = req.prompt
        if req.negative_prompt:
            prompt += f"\n\nAvoid: {req.negative_prompt}"
        raw, cost = self._post(prompt)
        return ImageResult.new(raw, self.name, model=self.model, seed=req.seed,
                               prompt=req.prompt, negative=req.negative_prompt, cost_usd=cost)

    def edit(self, req: EditRequest) -> ImageResult:
        if not self._supports_edit:
            raise NotImplementedError(
                f"model {self.model!r} is generate-only; configure an image-input "
                "(edit) model to use edit()")
        b64 = base64.b64encode(Path(req.image).read_bytes()).decode()
        content = [
            {"type": "text", "text": req.instruction},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ]
        raw, cost = self._post(content)
        return ImageResult.new(raw, self.name, model=self.model, seed=req.seed,
                               prompt=req.instruction, cost_usd=cost)

    def capabilities(self) -> Capabilities:
        return Capabilities(
            name=self.name, supports_edit=self._supports_edit,
            supports_reference_images=self._supports_edit, max_reference_images=1,
            uncensored=self._uncensored,
            notes=f"OpenRouter model {self.model}",
        )

    def health(self) -> bool:
        try:
            _api_key()
            return True
        except RuntimeError:
            return False
