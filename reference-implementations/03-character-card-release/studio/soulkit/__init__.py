"""soulkit — the vendored SOUL ⇄ card converter (Build #3 core).

The card-format code (PNG tEXt embedding, self-verification, the soul.yaml
field resolver, the SOUL.md flattening, and the card→soul importer) is the load-
bearing, non-trivial part of the release build. Rather than reimplement it, the
Card Studio reuses it verbatim from the `yuri-soul/` reference implementation
(reference-implementations/yuri-soul), which is its source of truth.

See VENDORED.md for the (single, documented) adaptation and how to re-sync.
"""
from . import build_card, import_card

__all__ = ["build_card", "import_card"]
