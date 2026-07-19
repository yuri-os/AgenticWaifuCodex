# Reference voices (for clone-mode registers)

Clone-mode registers in `../config.yaml` point at a reference clip here plus its
exact transcript (`ref_text`). Qwen3-TTS clones from as little as **3 seconds**,
but a clean 6–15 s single-speaker clip (no music/noise) clones more reliably.

Only `clone` registers need a file here. `design` registers invent a voice from
a text description and `custom` registers use a built-in timbre, so neither
references this folder.

`.wav` files are gitignored. For a self-contained test, render a reference clip
with the sibling Kokoro impl — see the main README's "Try it end-to-end."
