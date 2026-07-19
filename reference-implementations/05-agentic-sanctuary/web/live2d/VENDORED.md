# `web/live2d/` — the Build #2 web client, a documented fork

This directory is **Build #2 (the Desktop Companion)'s browser client**, copied
here — no longer verbatim: since the single-bus re-architecture (SPEC §10) it is
a **documented fork**, the same discipline as `world/routes/voice_ws.py`. Every
departure is marked `FORK(B2)` in-file.

**Still byte-identical to Build #2:** `avatar.js` (the Live2D body and the
name → Live2D-parameter expression map), `voice.js` (the edge VAD / barge-in
client — its `expression` wire case is now dead code, harmless), `settings.js`.
If you change those, change them in Build #2 and re-sync:

    rsync -a ../02-desktop-companion/web/avatar.js \
             ../02-desktop-companion/web/voice.js \
             ../02-desktop-companion/web/settings.js \
             ./web/live2d/

**Forked (marked `FORK(B2)`):**

- `index.html` — adds the chat column (SPEC §2.6) beside the body, moves the
  `#text` composer into it, and loads the two bus scripts below.
- `sanctuary.css` — the chat-column styles + its desktop-mode hide rule.
- `events.js` — **new, Build #4's file, not B2's**: the bus adapter. It boots
  the shared chat panel (`/js/chat.js`, served from the VRM page's tree) and
  maps `avatar`/`expression` events from `/api/events` onto `Avatar.setExpression`
  — expressions no longer ride `/ws/voice` (SPEC §10). The other puppet ops
  still aren't realised: the Live2D body remains a guest, not a second puppet
  (SPEC §6.6).

The server APIs this page touches:

- `/ws/voice` — the forked route (`world/routes/voice_ws.py`): mic PCM up,
  her audio down, barge-in — the audio-only wire (SPEC §10).
- `/api/events` + `/api/history` — the bus + the chat backfill (SPEC §2.6).
- `/api/config` — the rig registry, re-aimed at this directory
  (`world/routes/live2d.py`, over the vendored `desktop/avatar_models.py`).
- `/api/settings` — the vendored B2 settings router, included as-is in
  `world/main.py` (it edits this build's `.env`).

The Live2D runtime + models are **fetched, not committed** (proprietary Cubism
Core + Live2D Free-Material rigs — B2 §8.2's rule): run
`python scripts/fetch_live2d.py`, which is B2's `scripts/fetch_avatar.py`
re-aimed at `web/live2d/vendor/`. With `vendor/` empty the page runs voice-only
and says so.
