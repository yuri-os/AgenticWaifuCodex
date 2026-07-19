# Reference voices (pinned cloning assets)

Each voice in `../config.yaml` points at a reference clip here plus its exact
transcript (`prompt_text`). This is the pinned asset the book insists on — one
versioned clip per register, never swapped mid-conversation (→ ch. 24).

## Adding a voice

1. Drop a clean clip here, e.g. `ref_default.wav`:
   - **6–30 s**, single speaker, no music/background (use UVR to strip noise).
   - Consistent mic; the clip's *manner* (energy, pace) is copied along with the
     timbre, so pick a clip in the register you want.
2. Add an entry to `../config.yaml` under `voices:` with `ref_audio`,
   `prompt_text` (the clip's **exact** transcript), and the languages.
3. Point a register at it.

`.wav` files here are gitignored (voices are large and often not yours to
redistribute). For a quick self-contained test you can generate a reference clip
with the sibling Kokoro impl — see the main README's "Try it end-to-end."
