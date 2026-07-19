# `app/` — the Build #1 brain, vendored (twice removed)

This whole `app/` package is **Build #1 (the Minimum Viable Waifu)**, copied here
verbatim — via Build #2, which vendors it the same way — so Build #4 runs
standalone: copy this folder to any machine, follow the README, and it runs with
no reference to `../01-minimum-viable-waifu/` or `../02-desktop-companion/`.

Nothing in here is Build #4 code. It is the brain ch. 31 walks through line by
line: `app/core/assemble.py` (prompt assembly), `app/memory/store.py` (the
file-backed MemoryStore), `app/corpus.py` (the training log), `app/vaultgit.py`
(one commit per turn), `app/providers/` (the model seams). Build #4 adds the
`world/` package — the VRM body, the tools, the idle machine — and drives this
brain through `world/brain.py` (which subclasses Build #2's `desktop/brain.py`).

**If you are studying the brain, read it in Build #1** (ch. 31). **If you change
the brain, change it in Build #1** and re-vendor down the chain — this copy is
downstream of downstream. To re-sync:

    rsync -a --exclude='__pycache__' ../02-desktop-companion/app/ ./app/

The SOUL source it seeds from lives in `../soul-src/` (also vendored), and
`scripts/seed_vault.py` is Build #1's, copied.
