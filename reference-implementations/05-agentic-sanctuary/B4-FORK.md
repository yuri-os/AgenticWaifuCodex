# Forked from Build #4 (SPEC Part I)

This build is **Build #4, forked in place** — not vendored under a subfolder the way
`./app` (Build #1), `./desktop` (Build #2), and `./forge` (image-forge) are, because
Build #5 does not *wrap* the 3D world companion, it **is** the 3D world companion with
a mind behind it. The chassis — `world/`, `web/`, the vendored trio, `soul-src/`, the
inherited tests — was copied file-for-file from
`../04-3d-world-companion` at repo commit `784e6f7` and remains normatively specified
by **B4's SPEC** (`../04-3d-world-companion/SPEC.md`, cited as `B4 §n`; see this
build's SPEC.md preamble for the §-numbering convention).

To re-diff against Build #4 after it changes:

```bash
# from this folder — expect exactly the deltas listed below
diff -ru --exclude=SPEC.md --exclude=README.md --exclude=B4-FORK.md \
     --exclude=mind --exclude='test_mind*' --exclude='test_policy.py' \
     --exclude='test_world_model.py' --exclude='test_knowledge.py' \
     --exclude='test_dream.py' --exclude='test_selfedit.py' \
     --exclude=.venv --exclude=__pycache__ --exclude='*.egg-info' \
     ../04-3d-world-companion .
```

## What Build #5 changed in the chassis

**Deleted** (replaced by `mind/`):

- `world/idle.py`, `tests/test_idle_machine.py` — the scripted idle machine. The tick
  loop (`mind/loop.py`) holds the same strings; its body micro-acts survive as
  REGULATE reflexes, its announce/self-talk as decided acts (SPEC §15.5).

**Modified** (each change small and purposeful; everything else is byte-identical):

- `world/main.py` — the `Runtime` builds a `SignalBus` + `MindLoop` instead of the
  `IdleMachine`; the boot board's `idle` service becomes `mind`; the mind router is
  included.
- `world/routes/voice_ws.py` — one more marked fork block, `FORK(B5 §16)`: the signal
  tee (`user_message`, `turn_committed`).
- `world/routes/events.py` — presence signals on subscriber attach/detach (SPEC §16.2).
- `world/routes/health.py` — reports `mind` + `activity` instead of `idle`.
- `world/brain.py` — `set_world()`: the situation block is filled by the
  `WorldModelStore` when the mind runs (the B4 §2.5 seam swap, SPEC §19.2).
- `world/situation.py` — docstring only: demoted from "the world model" to the
  world model's host-lines renderer. The rendering itself is unchanged.
- `world/clock.py`, `world/tools/timers.py`, `world/boot.py` — docstrings/comments
  re-aimed at the mind; behaviour unchanged (timers' due queue is now drained by the
  loop's SENSE instead of the idle machine).
- `world/config.py`, `.env.example` — the `IDLE_ENABLED`/`IDLE_SEED` knobs give way
  to the `MIND_*` family (SPEC §25); the reflex windows (`IDLE_*_S`) survive;
  port 8767 → 8768.
- `web/index.html`, `web/sanctuary.css` — the chat column gains the **inner life**
  tab (SPEC §24.3); `web/js/mind.js` is new.
- `scripts/demo_avatar.py` — `MIND_ENABLED=false` instead of `IDLE_ENABLED=false`.
- `pyproject.toml` — project renamed `agentic-sanctuary`; `mind*` added to packages.
- `tests/` — inherited suites updated only where they toggled the idle machine
  (`mind_enabled=False`) or pinned the port/config defaults.

**Added**: `mind/` (the autonomy engine), `world/routes/mind.py`, `web/js/mind.js`,
and the `tests/test_mind_*`, `test_policy`, `test_world_model`, `test_knowledge`,
`test_dream`, `test_selfedit` suites.

The vendored layers (`app/`, `desktop/`, `forge/`, `web/live2d/`, `web/vendor/`,
`soul-src/`) are untouched; their own `VENDORED.md` files and re-sync commands apply
as in Build #4.
