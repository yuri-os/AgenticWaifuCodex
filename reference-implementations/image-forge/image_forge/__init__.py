"""image-forge — a swappable image service for YuriOS (→ book ch. 26).

The companion's image capability behind one stable API, with interchangeable
generator backends. Generate selfies, portraits, worldbuilding art, and edits
on-register, from any provider, swappable at runtime.

    from image_forge import ImageForge

    forge = ImageForge.from_config("config.yaml")
    forge.selfie(scene="window", mood="happy")        # an image "of her"
    forge.set_backend("comfyui", port=8188)           # swap the generator, live
"""

from .character import Character
from .service import ImageForge
from .templates import SelfieBook
from .backends import make_backend
from .types import Capabilities, EditRequest, GenRequest, ImageResult

__version__ = "0.1.0"
__all__ = [
    "ImageForge", "Character", "SelfieBook", "make_backend",
    "GenRequest", "EditRequest", "ImageResult", "Capabilities",
]
