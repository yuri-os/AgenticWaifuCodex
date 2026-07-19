"""GPT-SoVITS voice — a cloning TTS client for a specific canon voice.

Reference implementation for ch. 24 §"Cloning a specific voice." Where the
`../kokoro` impl picks one fixed voice, this one clones a *specific* identity
from a short reference clip (zero-shot) or a fine-tune, via the GPT-SoVITS
api_v2 server. Importing the package is cheap; the client pulls `requests` only.
"""

from .config import Config, Voice, load_config
from .stream import split_sentences

__all__ = ["Config", "Voice", "load_config", "split_sentences", "SovitsClient"]


def __getattr__(name):
    if name == "SovitsClient":
        from .client import SovitsClient

        return SovitsClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
