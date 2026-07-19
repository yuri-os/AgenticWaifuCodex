# Reference Implementations

Working minimal examples for the builds in `../book/chapters/30-reference-implementations.md`
(overview) and the per-build walkthroughs, chapters 31–35.

The numbered builds (1–5) are the book's teaching ladder; the lettered rows are the
**component services** those builds compose from — shipped first because they run
independently. See ch. 30, "What's actually in the repo today," for how the two relate.

| # | Name | Status | Folder |
|---|------|--------|--------|
| 1 | Minimum Viable Waifu | working | `01-minimum-viable-waifu/` |
| 1a | Memory subsystem — standalone tutorial (book ch. 15) | working | `memory-lab/` |
| 2 | Desktop Companion | working | `02-desktop-companion/` |
| 3 | Character Card Release — the Card Studio web app | working | `03-character-card-release/` |
| 3a | Yuri SOUL + card exporter (converter reused by the Studio) | working | `yuri-soul/` |
| 3b | Image service (selfies/art, swappable backends) | working | `image-forge/` |
| 3c | Voice service (Kokoro TTS, fixed voice, streaming + eval) | working | `kokoro/` |
| 3d | Voice cloning (GPT-SoVITS client, identity eval) | working | `gpt-sovits/` |
| 3e | Voice convergence (Qwen3-TTS: clone/design/preset) | working | `qwen3-tts/` |
| 4 | 3D World Companion | working | `04-3d-world-companion/` |
| 4a | VRM avatar control pipeline (Python-driven, WebSocket) | working | `vrm-viewer/` |
| 5 | Agentic Sanctuary — Build #4 + the always-on mind | working | `05-agentic-sanctuary/` |

See `../book/appendices/D-reference-implementations.md` for the live index and conventions.

## Conventions

- Each impl is **independently runnable**.
- Each impl has its own `README.md` with: what it teaches, prerequisites, run instructions, what it intentionally doesn't do.
- Each impl is intentionally **small** — clarity, not production polish.
- License is MIT unless otherwise noted.
- Implementations may share lore/canon (Yuri) but should not share code without a documented module.
