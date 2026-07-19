# Vendored converter — source of truth is `yuri-soul/`

`build_card.py` and `import_card.py` in this folder are **vendored copies** of the
converter shipped by the sibling reference implementation
[`../../../yuri-soul/`](../../../yuri-soul/). That folder is the canonical Build
#3 SOUL ⇄ card converter; the Card Studio is a web front-end *over* it, so it
reuses the exact card-format code rather than forking a second implementation of
the PNG `tEXt` embedding, the self-verification, and the round-trip importer.

This mirrors the repo convention (reference-implementations/README.md):
> Implementations may share lore/canon (Yuri) but should not share code without a
> documented module.

This file is that documentation.

## The one adaptation

The files are copied byte-for-byte with a **single** change: in `import_card.py`,

```python
import build_card            # yuri-soul original (sibling module on sys.path)
```

becomes

```python
from . import build_card     # here: soulkit is a package
```

because in `yuri-soul/` the two scripts sit side by side on `sys.path`, whereas
here they live inside the `soulkit` package. No other line differs.

## What the studio uses from it

- `build_card.wrap_card`, `build_card.embed_png`, `build_card.verify_png` — build
  and self-check the `.PNG` card the Generate tab hands back.
- `build_card.soul_md` — the OpenClaw/Hermes single-file `SOUL.md` export.
- `build_card.extract_card` — read a card back out of a `.PNG` (used by import).
- `import_card.intended_card` / `import_card.write_soul` — export the studio's
  draft as an editable soul folder (the round-trip story of ch. 33).

## Re-syncing

If `yuri-soul/build_card.py` or `import_card.py` change, re-copy them and re-apply
the one-line import adaptation:

```bash
cp ../../../yuri-soul/build_card.py  build_card.py
cp ../../../yuri-soul/import_card.py import_card.py
# then change `import build_card` -> `from . import build_card` in import_card.py
```

`tests/test_converter.py` re-runs the converter's own round-trip contract, so a
bad re-sync fails loudly.
