"""Backend registry — the swap table.

``make_backend("comfyui", port=8188)`` is all the service needs to change
generators. Add a provider by writing one ``ImageBackend`` and registering it here.
Heavy backends are imported lazily so the service runs with only Pillow installed
(the mock backend) and never pays for ``replicate``/networking it isn't using.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from .base import ImageBackend


def _mock(**opts: Any) -> ImageBackend:
    from .mock import MockBackend
    return MockBackend(**opts)


def _openrouter(**opts: Any) -> ImageBackend:
    from .openrouter import OpenRouterBackend
    return OpenRouterBackend(**opts)


def _comfyui(**opts: Any) -> ImageBackend:
    from .comfyui import ComfyUIBackend
    return ComfyUIBackend(**opts)


def _replicate(**opts: Any) -> ImageBackend:
    from .replicate_backend import ReplicateBackend
    return ReplicateBackend(**opts)


def _diffusers(**opts: Any) -> ImageBackend:
    from .diffusers_backend import DiffusersBackend
    return DiffusersBackend(**opts)


REGISTRY: Dict[str, Callable[..., ImageBackend]] = {
    "mock": _mock,
    "openrouter": _openrouter,
    "comfyui": _comfyui,
    "replicate": _replicate,
    "diffusers": _diffusers,
}


def make_backend(name: str, **opts: Any) -> ImageBackend:
    if name not in REGISTRY:
        raise KeyError(f"unknown backend {name!r}; have: {', '.join(REGISTRY)}")
    return REGISTRY[name](**opts)


__all__ = ["ImageBackend", "make_backend", "REGISTRY"]
