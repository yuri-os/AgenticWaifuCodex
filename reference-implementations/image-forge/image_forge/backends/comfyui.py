"""ComfyUI backend — the local, owned, uncensored path (→ ch. 26 tooling).

ComfyUI is the power-user default and the only backend that is fully *yours*: your
GPU, your checkpoint, your LoRA, no refusals. This talks to a running ComfyUI over
its HTTP API.

How it injects a prompt: ComfyUI runs a node graph saved as JSON ("API format",
exported from ComfyUI with *Save (API Format)*). Rather than hard-code node IDs,
this backend does placeholder substitution on the workflow text — your workflow
contains the tokens ``%POSITIVE%``, ``%NEGATIVE%``, ``%SEED%``, ``%WIDTH%``,
``%HEIGHT%``, ``%CKPT%`` where those values go. A ready-to-run SD/SDXL example
ships in ``comfy_workflows/txt2img.json``.

Editing uses a second workflow with a ``LoadImage`` node; the source image is
uploaded via ``/upload/image`` and its filename substituted for ``%IMAGE%``. This
is where you'd wire FLUX.1 Kontext / Qwen-Image-Edit for identity-preserving
re-renders (→ ch. 26, reference-driven consistency).
"""

from __future__ import annotations

import json
import random
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from ..types import Capabilities, EditRequest, GenRequest, ImageResult
from .base import ImageBackend


class ComfyUIBackend(ImageBackend):
    name = "comfyui"

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8188,
        *,
        workflow: str | Path = "comfy_workflows/txt2img.json",
        edit_workflow: Optional[str | Path] = None,
        checkpoint: str = "",
        extra_tokens: Optional[Dict[str, Any]] = None,
        poll_interval: float = 0.5,
        timeout: float = 300.0,
    ) -> None:
        self.base = f"http://{host}:{port}"
        self.workflow = Path(workflow)
        self.edit_workflow = Path(edit_workflow) if edit_workflow else None
        self.checkpoint = checkpoint
        # Optional workflow-specific tokens (e.g. {"%LORA_STRENGTH%": 0.85}) for
        # graphs that carry extra knobs beyond the standard prompt/seed/size set.
        self.extra_tokens = {k: str(v) for k, v in (extra_tokens or {}).items()}
        self.poll_interval = poll_interval
        self.timeout = timeout
        self.client_id = uuid.uuid4().hex

    # ---- HTTP helpers ----

    def _get(self, path: str) -> bytes:
        with urllib.request.urlopen(self.base + path, timeout=self.timeout) as r:
            return r.read()

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        req = urllib.request.Request(
            self.base + path, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read())

    @staticmethod
    def _is_number(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _fill(self, wf_path: Path, subs: Dict[str, str]) -> Dict[str, Any]:
        # The workflow file is valid JSON with quoted tokens ("%SEED%"). For a
        # numeric value (int OR float, e.g. a LoRA strength) we replace the
        # *quoted* token with a bare number so ComfyUI receives a number, not a
        # string; for text we JSON-escape in place.
        subs = {**subs, **self.extra_tokens}
        text = wf_path.read_text()
        for token, value in subs.items():
            if self._is_number(value):
                text = text.replace(f'"{token}"', value)
            text = text.replace(token, json.dumps(value)[1:-1])  # JSON-escape
        graph = json.loads(text)
        # Drop doc-only keys (e.g. "_comment"): ComfyUI treats every top-level
        # key as a node and 400s on any without a class_type.
        return {k: v for k, v in graph.items() if not k.startswith("_")}

    def _run_graph(self, graph: Dict[str, Any], meta: Dict[str, Any]) -> ImageResult:
        prompt_id = self._post("/prompt", {"prompt": graph, "client_id": self.client_id})["prompt_id"]
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            hist = json.loads(self._get(f"/history/{prompt_id}"))
            if prompt_id in hist:
                outputs = hist[prompt_id]["outputs"]
                for node in outputs.values():
                    for img in node.get("images", []):
                        q = urllib.parse.urlencode(
                            {"filename": img["filename"], "subfolder": img.get("subfolder", ""),
                             "type": img.get("type", "output")})
                        data = self._get(f"/view?{q}")
                        return ImageResult.new(data, self.name, **meta)
                raise RuntimeError("ComfyUI finished but produced no image")
            time.sleep(self.poll_interval)
        raise TimeoutError(f"ComfyUI did not finish within {self.timeout}s")

    # ---- backend API ----

    def generate(self, req: GenRequest) -> ImageResult:
        seed = req.seed if req.seed is not None else random.randint(0, 2**31 - 1)
        graph = self._fill(self.workflow, {
            "%POSITIVE%": req.prompt,
            "%NEGATIVE%": req.negative_prompt,
            "%SEED%": str(seed),
            "%WIDTH%": str(req.width),
            "%HEIGHT%": str(req.height),
            "%CKPT%": self.checkpoint,
        })
        return self._run_graph(graph, dict(model=f"comfyui:{self.checkpoint or 'workflow'}",
                                           seed=seed, prompt=req.prompt, negative=req.negative_prompt))

    def edit(self, req: EditRequest) -> ImageResult:
        if not self.edit_workflow:
            raise NotImplementedError("set edit_workflow to a Kontext/Qwen-Edit graph to use edit()")
        filename = self._upload_image(Path(req.image))
        seed = req.seed if req.seed is not None else random.randint(0, 2**31 - 1)
        graph = self._fill(self.edit_workflow, {
            "%IMAGE%": filename,
            "%POSITIVE%": req.instruction,
            "%NEGATIVE%": req.negative_prompt,
            "%SEED%": str(seed),
            "%CKPT%": self.checkpoint,
        })
        return self._run_graph(graph, dict(model=f"comfyui-edit:{self.checkpoint or 'workflow'}",
                                           seed=seed, prompt=req.instruction))

    def _upload_image(self, path: Path) -> str:
        # multipart/form-data POST to /upload/image
        boundary = "----imageforge" + uuid.uuid4().hex
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="image"; filename="{path.name}"\r\n'.encode(),
            b"Content-Type: image/png\r\n\r\n",
            path.read_bytes(), b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ])
        req = urllib.request.Request(
            self.base + "/upload/image", data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read())["name"]

    def capabilities(self) -> Capabilities:
        return Capabilities(
            name=self.name, supports_edit=self.edit_workflow is not None,
            supports_reference_images=self.edit_workflow is not None, max_reference_images=10,
            supports_lora=True, uncensored=True,
            notes="local ComfyUI; capability depends on your installed models/workflow",
        )

    def health(self) -> bool:
        try:
            self._get("/system_stats")
            return True
        except Exception:
            return False
