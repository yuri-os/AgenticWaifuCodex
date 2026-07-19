# Build #2 — The Desktop Companion — SPEC

Normative specification for the reference implementation of **book ch. 32**. Keywords
**MUST**, **SHOULD**, **MAY** are used in the RFC-2119 sense. Section numbers (§n) are cited
from the code and the README. Where this build reuses Build #1, it cites that build's SPEC as
**B1 §n** rather than restating it.

---

## §1 — Goal and properties

A local-first desktop app that gives the Build #1 companion a **body** — a Live2D avatar and a
real-time voice loop — running by default entirely on the user's machine, no external API
required. Local is the default the build is organised around; pointing `CHAT_MODEL` at a hosted
model (OpenRouter) for weaker hardware or a stronger mind is a one-line swap (§2.4), not a
forbidden path.

- It **MUST** add **property 4** (a body: voice + 2D avatar) on top of Build #1's identity and
  memory, and **MUST** strengthen **property 6** (yours): with local STT/TTS/LLM, nothing
  leaves the machine. Pulling the network cable **MUST NOT** change behaviour once the local
  models are installed.
- It **MUST** remain **reactive** (no autonomy) — that is Build #5.
- It **MUST** be **standalone** (§2.1).

## §2 — The brain is Build #1, reused

- §2.1 **Standalone.** The Build #1 brain **MUST** be vendored into `./app` so the build runs
  with no path reference to `../01-minimum-viable-waifu`. `app/VENDORED.md` **MUST** document
  the provenance and the re-sync command. The SOUL source **MUST** be vendored (`./soul-src`)
  so `scripts/seed_vault.py` seeds a Vault standalone.
- §2.2 **Unchanged.** No file under `app/` **MAY** be edited to make Build #2 work. All new
  behaviour lives under `desktop/`. Prompt assembly, recall, the partner model, the corpus,
  and the one-commit-per-turn spine are **called**, not reimplemented (B1 §6–§8).
- §2.3 **Identity.** Her identity is the SOUL (the same card as Build #1). The build **MUST**
  default to her own seeded Vault and **MUST** allow `VAULT_DIR` to point at an existing
  Build #1 Vault to *continue* that companion (→ ch. 19, "copy the folder to move her").
- §2.4 **Local by default.** `CHAT_MODEL`, `UTILITY_MODEL`, and `EMBED_BACKEND` **MUST**
  default to local. Build #1's LiteLLM seam routes by the model-id prefix (B1 §3.1–§3.2), so a
  local **Ollama**, a local **LM Studio** server (`lm_studio/…` ids + `LMSTUDIO_BASE_URL`), and
  hosted OpenRouter are each a one-line change. The reference `.env` ships an LM Studio model
  (`lm_studio/google/gemma-4-12b-qat`) with `EMBED_BACKEND=lm_studio` reusing that **same**
  server, so a single local process backs both the mind and its memory. Switching
  `EMBED_BACKEND` at the same vector width (Ollama `nomic`↔ LM Studio `nomic`) **MUST NOT**
  silently poison recall: the index carries an embedder fingerprint and the runtime
  **auto-reindexes from the `.md` files** on a mismatch (B1 §4.3).
- §2.5 **Reasoning utility model.** The default local `UTILITY_MODEL` (partner-model fact
  extraction + summarisation, B1 §6.3/§7.3) is a *reasoning* model (e.g. qwen3, or the
  reference `gemma-4-12b-qat`). Its `<think>` block runs before the JSON answer, so the utility
  call **MUST** budget enough tokens for both (`UTILITY_MAX_TOKENS`) — too small a budget
  truncates the answer to an empty string and silently loses the fact. `parse_ops` **MUST**
  strip a leading `<think>…</think>` block. Reasoning stays ON here (`UTILITY_THINKING=true`):
  extraction quality matters and this call runs **off the hot path** (post-turn), so its latency
  is free. Extraction **MUST** attribute facts to the correct speaker: the companion's own
  self-statements (`"My name is Yuri"`) **MUST NOT** be recorded as facts about the user.
- §2.6 **Reply reasoning is OFF for real-time voice.** When `CHAT_MODEL` is a reasoning model,
  its `<think>` pass runs *on* the hot path and would delay — or, worse, consume the whole token
  budget and empty — the spoken reply. So Build #2 **MUST** disable the reply's reasoning
  (`CHAT_THINKING=false`) while leaving the utility model thinking (§2.5). The off-switch is
  `reasoning_effort:"none"`, which **MUST** be sent in the raw request body (`extra_body`) — as a
  top-level LiteLLM arg it is rewritten and the server never applies it — with a qwen `/no_think`
  system-token as a fallback for models that ignore it. Both are inert on a non-reasoning model,
  so this knob is safe across every route (B1 §3.2).

## §3 — The voice seams

All vendor-facing voice surfaces **MUST** sit behind Protocols in `desktop/voice/protocols.py`;
nothing else in the voice layer **MAY** import an STT/TTS/VAD SDK. Fakes (`backends/fakes.py`)
**MUST** implement each seam so the whole loop runs offline (§13).

- §3.1 **Audio convention.** Audio **MUST** be float32 mono in [-1, 1], sample rate carried
  alongside the array (`AudioChunk`).
- §3.2 **STT** (`STT`): `reset` / `feed(frame)` / `final()`. Default `faster_whisper`; tuned
  for latency over accuracy (→ ch. 24). Streaming partials **MAY** be added behind the seam.
  Non-speech that leaks past the VAD (mechanical-keyboard clatter, a cough) makes STT
  *hallucinate* rather than return empty — usually bare punctuation (". . . ."). `final()`
  **SHOULD** drop segments the model itself flags as non-speech (`no_speech_prob`), and the
  loop **MUST** reject a transcript with no alphanumeric content (`transcript.is_meaningful_transcript`)
  before it becomes a turn: a `you: . . . .` line **MUST NOT** reach the brain or the Vault.
- §3.3 **TTS** (`TTS`): `sample_rate`; `stream(text) -> Iterator[AudioChunk]`, **MUST** yield
  sentence-by-sentence so time-to-first-audio is short. Default `kokoro` — a fixed voice that
  runs faster-than-real-time on CPU, needs no GPU, and leaves the whole GPU for the LLM and the
  avatar (→ ch. 24); it is the default because it works out of the box on a modest machine at
  the lowest latency of the three. `qwen3_tts` (the "designed" persona voice: authored once from
  a description, frozen as the bundled `assets/designed.wav`, then **cloned** from that one clip
  for every utterance — it **MUST** pin a single voice, since designing per turn re-samples the
  timbre and she comes out as two different voices, the filler vs. the reply; it runs in-process,
  is higher-quality but slower, needs a CUDA GPU, and so **MUST** lean on the §5 filler masking)
  and `gpt_sovits` (canon clone) **MUST** remain one-line `TTS_BACKEND` swaps.
- §3.4 **VAD** (`VAD`): `is_speech(frame)` / `reset`. Default Silero. The **edge** VAD (barge-in)
  **MUST** run client-side (§8.3); the server-side VAD confirms endpointed utterances.
  A raw per-frame verdict **MUST NOT** trigger a turn or a barge-in on its own — a single
  high-energy transient (one keystroke) clears any frame-level gate, and acting on it is the
  "I typed and she stopped" bug. Turn-taking **MUST** be *debounced* (`speech_gate.SpeechGate`):
  act only after N *consecutive* speech frames, and confirm a **barge-in** with a strictly
  higher count than a new-turn **onset** (interrupting her costs more confidence). The edge
  (§8.3) and the server **MUST** apply the same debounce on the same constants. The server
  **SHOULD** additionally require the VAD to confirm real speech in an endpointed utterance
  (`SpeechGate.confirmed`, gated by `VAD_CONFIRM`) before transcribing it, so all-noise
  utterances are dropped; it **MUST** be disable-able for a quiet mic / over-strict VAD.
- §3.5 **ReplyBrain** (`ReplyBrain`): `stream_reply(session_id, text)` and `persist(...)`. The
  loop **MUST** depend only on this Protocol, so it is drivable by a fake brain (§13).

## §4 — The real-time loop

`desktop/voice/turn.py` `TurnController.run_turn` is the spine. One instance per connection.

- §4.1 **Stream into the next.** Reply tokens **MUST** be consumed while earlier sentences are
  still synthesizing (a producer coroutine → sentence queue → the consumer synthesizes and
  emits). The first audio chunk **MUST** be emitted as soon as sentence one renders, not when
  the reply completes. Sentence splitting **MUST** be incremental (`sentences.py`).
- §4.2 **Latency budget.** The loop **MUST** measure end-of-speech → first-audio and **SHOULD**
  record per-stage marks (`latency.py`). Target ≤ **1200 ms** end-to-end. The measurement of
  record is the end-to-end number, because per-stage numbers lie when queues hide between
  stages. Traces **SHOULD** be written to `TRACE_DIR` (gitignored, like the corpus).
- §4.3 **Barge-in is a cancel.** `cancel()` **MUST** tear down TTS emission *and* the in-flight
  brain generation together. It **MUST** be idempotent (the mic handler fires it per frame) and
  **MUST** be scoped to the current turn (a fresh cancel token per `run_turn`).
- §4.4 **Failure/cancel leave no trace.** A barged-in turn and a mid-stream brain error **MUST**
  persist nothing — no corpus line, no commit (mirrors B1's mid-stream rule). Only a fully
  completed turn calls `persist()` (Build #1's post-turn pipeline), off the hot path.
- §4.5 **Noise is not a turn.** A turn **MUST** be gated on evidence it was actually speech, at
  three independent points so no single false positive persists a junk turn: the debounced edge
  VAD rejects transient clatter before it fires a turn or barge-in (§3.4, §8.3); the server
  confirms the endpointed utterance held speech (§3.4); and a punctuation-only/empty transcript
  is dropped at the text boundary (§3.2). A dropped utterance **MUST** leave no trace (§4.4).

## §5 — Latency masking

- §5.1 The build **SHOULD** cover the first-audio gap with an **instant acknowledgment**: on
  endpoint, before the first token, play a short pre-rendered filler ("mm—"). The bank **MUST**
  be pre-rendered once (`FillerBank.prime`), tuned to the persona, and **MUST NOT** repeat the
  same clip twice in a row.
- §5.2 Filler is interruptible audio: the barge-in path (§4.3) **MUST** kill it. Masking
  **MUST** be disable-able (`MASK_LATENCY=false`).

## §6 — Emotion → expression

- §6.1 The model **MUST** be asked (appended system blocks) to (a) treat this as a *spoken*
  exchange — plain speech, no narration, stage directions, or asterisk actions — and (b) emit
  inline expression tags from a fixed palette. The palette is names only; the map from name →
  renderer parameters **MUST** live in the frontend (`web/avatar.js`), so the brain stays
  renderer-agnostic. Both blocks are voice-only; Build #1's text chat keeps neither.
- §6.2 The parser (`emotion.py`) **MUST** strip tags from the spoken text (she never *says* the
  feeling word), **MUST** emit an expression event when a tag closes, **MUST** tolerate tags
  split across tokens, and **MUST** drop unknown tags silently. It **MUST** also strip
  `*asterisk narration*` from the spoken text (the belt-and-suspenders to the §6.1 directive),
  streaming-safe across token boundaries, dropping an unclosed span rather than speaking it.
- §6.3 The expression event for a sentence **SHOULD** be emitted before that sentence's audio
  (the face leads the voice).

## §7 — The greeting (she speaks first)

On connect the build **SHOULD** greet from memory before the user speaks (continuity, → ch. 28).
The greeting **MUST NOT** be persisted (an opener is not a turn the user took) and **MUST NOT**
pollute the session window. It **MUST** fire at most once per session: a reconnect — or a second
socket opened for the same session — **MUST NOT** speak a second greeting over the first.

## §8 — The sanctuary and the body

- §8.1 The frontend **MUST** be one static page served by the app, styled as a place (Build #1's
  tokens), avatar centre-stage. No build step.
- §8.2 The avatar **MUST** render a real Live2D model via pixi-live2d-display. Runtime + model
  are **fetched** into `web/vendor/` (gitignored), never committed — Cubism Core is proprietary
  (free under ¥10M JPY revenue) and the model is sample-licensed. With `web/vendor/` empty the
  app **MUST** still run (voice-only). Lipsync **MUST** drive `ParamMouthOpenY` from playback
  amplitude; expressions **MUST** map to rig parameter presets.
- §8.3 The client **MUST** run its own VAD for barge-in and **MUST** stop local playback the
  instant it detects the user speaking (debounced, §3.4) over her, in addition to signalling
  the server.
- §8.4 **Warm in the background.** The voice stack (STT/TTS models, ~20 s cold) **MAY** load
  off-thread so the page — her body — appears immediately. A connection **MUST** wait for the
  stack to be ready before its first turn or greeting rather than answering with a stand-in.

## §9 — Desktop presence

`python -m desktop --window` **MAY** host the served page in a frameless, transparent,
always-on-top native window (pywebview; `desktop/window.py`) so she floats on the desktop as a
pet rather than sitting in a browser tab. It is a shell over this exact server — the loop does
not change — and needs the `[desktop]` extra. Window size / on-top / engine are config knobs
(`WINDOW_*`). Not required for the DoD.

## §10 — The websocket API

`/ws/voice`, full-duplex. The handler **MUST** read inbound messages while streaming outbound
events, so barge-in can land mid-reply.

Client → server: `hello{session_id?}`; binary Float32 frames (16 kHz) during speech;
`endpoint`; `bargein`; `text{text}`. Server → client: `session{session_id}`;
`filler|audio{text,sr,pcm(base64 float32)}`; `expression{expression}`;
`done{latency,expression}` | `cancelled` | `error{message}`.

## §11 — Config

Typed (`desktop/config.py`), read once from env/`.env`, extending Build #1's config. Every knob
in `.env.example` **MUST** have a default. No secrets in code; the default stack needs no key.
Inherited from B1 §11 and re-defaulted here: the model routes + `LMSTUDIO_BASE_URL` (§2.4), the
reasoning switches `CHAT_THINKING=false` / `UTILITY_THINKING=true` (§2.5–§2.6), and
`EMBED_BACKEND=lm_studio` with its auto-reindex (§2.4). `MAX_REPLY_TOKENS` stays voice-short.
A settings UI (`/settings`, `desktop/routes/settings.py`) **MAY** read and write the `.env` knobs
live; if present it **MUST** refuse non-local callers and **MUST** preserve comments and
formatting when it rewrites the file.

## §12 — Omissions (normative)

No autonomy/tick loop; 2D only; single register; no fine-tune (it *collects* the corpus); no
paralinguistic SENSE input (deferred to Build #5). The lorebook stays card-native flavor.

## §13 — Tests (the hard gate)

`pytest` **MUST** ship and be green from the project root, entirely offline against the §3
fakes. It **MUST** pin at least: emotion parsing (§6), **barge-in cancels TTS + generation and
persists nothing** (§4.3–§4.4), the latency accounting (§4.2), filler masking (§5), the ordered
end-to-end pipeline, an end-to-end turn over the **real vendored brain** (seeded Vault, fake
models) proving a corpus line + one commit, the live `/ws/voice` route, the turn-taking debounce
(`SpeechGate`) and the transcript sanity filter, and that `/ws/voice` **drops an all-noise
utterance while taking a real one** (§3.2, §3.4, §4.5).

## §14 — Extends to

Build #3 (card export, same SOUL); Build #4 (VRM + 3D, swap `avatar.js`, add tools); Build #5
(tick loop + DREAM + knowledge store around this exact Vault).
