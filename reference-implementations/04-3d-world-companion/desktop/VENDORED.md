# `desktop/` — the Build #2 voice stack, vendored

This whole `desktop/` package is **Build #2 (the Desktop Companion), copied here
verbatim** so Build #4 runs standalone. It is the real-time voice loop ch. 32
walks through: the STT/TTS/VAD seams and backends (`voice/protocols.py`,
`voice/backends/`), the turn spine with barge-in-as-cancel (`voice/turn.py`),
the debounced SpeechGate, filler masking, emotion-tag parsing, latency tracing,
and the `BrainAdapter` that drives the vendored Build #1 brain.

Nothing in here is Build #4 code, and **no file in here may be edited** to make
Build #4 work (SPEC §2.2). Build #4's additions live in `world/`:

- `world/brain.py` **subclasses** `desktop/brain.py`'s `BrainAdapter` to add the
  tool loop (SPEC §7) — the vendored class is called, not copied.
- `world/routes/voice_ws.py` is the **one documented fork** of
  `desktop/routes/voice_ws.py` (SPEC §2.2): the same route plus the ambient-speech
  seam the idle machine needs. Every divergence is marked `FORK(B2 §10)`.
- Everything else — turn controller, gates, fillers, emotion parser, backends,
  fakes — is imported from here unchanged.

The desktop-pet pieces are reused too (SPEC §6.5–§6.6): `world/window.py`
imports `desktop/window.py`'s readiness probe and engine pick for
`python -m world --window`; `desktop/routes/settings.py` is included as-is in
`world/main.py` (it edits this build's `.env` — its paths resolve relative to
itself); and `desktop/avatar_models.py` is the rig registry behind
`world/routes/live2d.py`, which serves the vendored Build #2 web client at
`/live2d/` (see `web/live2d/VENDORED.md`). Still unused and deliberately kept
so the rsync below stays a one-liner: `desktop/main.py` (Build #2's own app
factory — Build #4 has `world/main.py`) and `desktop/routes/avatar.py` (its
`WEB_DIR` points at Build #2's layout; the re-aimed copy is
`world/routes/live2d.py`).

**If you are studying the voice loop, read it in Build #2** (ch. 32). **If you
change it, change it there** and re-vendor. To re-sync:

    rsync -a --exclude='__pycache__' ../02-desktop-companion/desktop/ ./desktop/

(then re-check `world/routes/voice_ws.py` against the fresh
`desktop/routes/voice_ws.py` — the fork is small and the markers make the diff
mechanical).
