"""Replicate backend — hosted GPUs, ship without owning the hardware (→ ch. 26).

Runs any of the ch. 26 pipelines on Replicate: a base generator (FLUX / Qwen-Image)
for ``generate``, and an instruction-edit model (FLUX.1 Kontext) for ``edit`` —
the reference-driven consistency path. Needs the ``replicate`` package and
``$REPLICATE_API_TOKEN``.

Fal/Modal would be near-identical backends; this one stands in for "any hosted
inference provider" — the seam is the same.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from ..types import Capabilities, EditRequest, GenRequest, ImageResult
from .base import ImageBackend


def _fetch(url: str) -> bytes:
    import urllib.request

    with urllib.request.urlopen(url) as r:
        return r.read()


def _to_bytes(output) -> bytes:
    """Replicate returns a URL, a list, or a FileOutput depending on the model."""
    if isinstance(output, list):
        output = output[0]
    if hasattr(output, "read"):          # FileOutput
        return output.read()
    if isinstance(output, str):          # URL
        return _fetch(output)
    raise RuntimeError(f"unexpected Replicate output type: {type(output)!r}")


class ReplicateBackend(ImageBackend):
    name = "replicate"

    def __init__(
        self,
        model: str = "black-forest-labs/flux-1.1-pro",
        *,
        edit_model: str = "black-forest-labs/flux-kontext-pro",
        uncensored: Optional[bool] = False,
    ) -> None:
        self.model = model
        self.edit_model = edit_model
        self._uncensored = uncensored

    def _client(self):
        try:
            import replicate
        except ImportError as e:
            raise RuntimeError("pip install replicate (and set $REPLICATE_API_TOKEN)") from e
        if not os.environ.get("REPLICATE_API_TOKEN"):
            raise RuntimeError("set $REPLICATE_API_TOKEN")
        return replicate

    def generate(self, req: GenRequest) -> ImageResult:
        replicate = self._client()
        inp = {
            "prompt": req.prompt,
            "aspect_ratio": req.extra.get("aspect_ratio", "2:3"),
            "output_format": "png",
        }
        if req.seed is not None:
            inp["seed"] = req.seed
        inp.update(req.extra.get("input", {}))
        out = replicate.run(self.model, input=inp)
        return ImageResult.new(_to_bytes(out), self.name, model=self.model,
                               seed=req.seed, prompt=req.prompt, negative=req.negative_prompt)

    def edit(self, req: EditRequest) -> ImageResult:
        replicate = self._client()
        with open(req.image, "rb") as fh:
            inp = {"prompt": req.instruction, "input_image": fh, "output_format": "png"}
            if req.seed is not None:
                inp["seed"] = req.seed
            inp.update(req.extra.get("input", {}))
            out = replicate.run(self.edit_model, input=inp)
        return ImageResult.new(_to_bytes(out), self.name, model=self.edit_model,
                               seed=req.seed, prompt=req.instruction)

    def capabilities(self) -> Capabilities:
        return Capabilities(
            name=self.name, supports_edit=True, supports_reference_images=True,
            max_reference_images=1, uncensored=self._uncensored,
            notes=f"Replicate gen={self.model} edit={self.edit_model}",
        )

    def health(self) -> bool:
        return bool(os.environ.get("REPLICATE_API_TOKEN"))
