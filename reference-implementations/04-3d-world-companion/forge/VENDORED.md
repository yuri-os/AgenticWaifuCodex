# Vendored: image-forge (her camera — SPEC §7.6)

A slice of `../image-forge` (the repo's swappable image service, → book ch. 26),
copied so this build stays standalone. Taken verbatim: `types.py`,
`character.py`, `templates.py`, `provenance.py`, `service.py`,
`backends/{base,mock}.py`, `templates/selfie.yaml`.

**What was left behind, on purpose:** the `comfyui` / `replicate` / `diffusers`
backends (local-GPU and hosted-GPU paths), the CLI (`__main__.py`), and
`config.yaml`. Build #4's selfies are GPU-free by construction — `mock` needs
nothing, `openrouter` needs a key — because her voice stack already owns the
local compute budget. Want the local uncensored path? Point the code at the
sibling `../image-forge` install instead; the `ImageForge` surface is identical.

## Deviations (both marked `VENDOR DEVIATION` in-file)

1. **`backends/openrouter.py`** — the constructor takes an `api_key` and the env
   fallback also accepts `OPENROUTER_API_KEY` (this repo's convention; the typed
   config reads `.env` without exporting, so the host injects the key). The
   `modalities` handling is also generalised: the source hard-codes `["image"]`
   only for `sourceful/` ids, so a non-riverflow image model (the default here,
   `bytedance-seed/seedream-4.5`) would 404 — this build asks `["image"]` first
   and retries once with `["image","text"]` on a 404, so any OpenRouter image
   route works without a per-prefix registry.
2. **`characters/yuri.yaml`** — the `trigger` + `lora` block is dropped: those
   drive the diffusers backend, which isn't vendored, and a stray trigger token
   would pollute the hosted prompt.
3. **`backends/__init__.py`** — the registry is trimmed to `mock` + `openrouter`
   (documented in the file header).

If image-forge changes, re-diff this folder against it.
