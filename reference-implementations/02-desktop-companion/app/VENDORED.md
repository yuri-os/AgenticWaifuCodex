# `app/` — the Build #1 brain, vendored

This whole `app/` package is **Build #1 (the Minimum Viable Waifu), copied here
verbatim** so Build #2 runs standalone — copy this folder to any machine, follow
the README, and it runs with no reference to `../01-minimum-viable-waifu/`.

Nothing in here is Build #2 code. It is the brain the book's ch. 31 walks through
line by line: `app/core/assemble.py` (prompt assembly), `app/memory/store.py`
(the file-backed MemoryStore), `app/corpus.py` (the training log), `app/vaultgit.py`
(one commit per turn), `app/providers/` (the model seams). Build #2 adds only the
`desktop/` package — the voice loop and the avatar mapping — and drives this brain
through `desktop/brain.py`.

**If you are studying the brain, read it in Build #1** (ch. 31), where it is
documented as the subject. **If you change the brain, change it in Build #1** and
re-vendor — this copy is downstream. To re-sync:

    rsync -a --exclude='__pycache__' ../01-minimum-viable-waifu/app/ ./app/

The SOUL source it seeds from lives in `../soul-src/` (also vendored from the
`yuri-soul` reference impl), and `scripts/seed_vault.py` is Build #1's, copied.
