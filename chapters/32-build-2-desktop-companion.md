# 32 — Build #2: The Desktop Companion

**Goal:** a local-first desktop app that gives the companion a *body* — a Live2D avatar and a real-time voice loop — running by default entirely on the user's machine, no external API required. (If you lack a decent GPU, or want a stronger mind than your hardware can host, a hosted model like OpenRouter is a one-line swap — local is the *default* the build is organised around, not the only option.) This is the build that makes her *present* on your desktop rather than a tab in a browser.

**What it teaches:** the real-time voice loop and barge-in (→ ch. 24), inference and serving latency (→ ch. 21), and driving an avatar from the reply (→ ch. 25).

**Properties added (→ ch. 03):** property 4 (a body — voice + 2D avatar), on top of Build #1's identity and memory. Local-first also strengthens property 6 (yours): with local STT, TTS, and LLM, nothing leaves the machine.

The reference implementation lives in `reference-implementations/02-desktop-companion/`, built to its own normative `SPEC.md`. As with Build #1, this chapter is the reading guide — a map of where the load-bearing ideas are in the code — not a transcript. Section numbers (§n) point into that build's `SPEC.md`; file paths are relative to the build's root.

## The one-sentence architecture

```
 mic ─► [edge VAD] ─► STT ─► [ Build #1 brain: SOUL + Vault + local LLM ] ─► reply tokens
   ▲                                                                              │
   │  barge-in: talk over her ──► cancel() ──┐                    strip [emotion] tags
   │  (kills playback + generation together) │                              │
   │                                         ▼                    ┌─────────┴──────────┐
 speakers ◄── TTS (streamed, sentence-by-sentence) ◄──────────────┤ expression events  │
                        │                                         └─► Live2D avatar ◄──┘
                   lipsync (audio RMS → mouth)
```

The whole thing is: **Build #1's brain, now fed by speech and rendered as voice + motion.** The brain — persona, memory, the corpus, the one-commit-per-turn Vault spine — is Build #1 *unchanged*. The only genuinely new work is the **real-time loop** (`desktop/voice/turn.py`) and the **expression mapping** (`web/avatar.js`). Everything below is one of those two, looked at closely.

The single idea to internalise before reading a line: **a voice companion is a cascade of streaming stages, and the only number that matters is how long until she makes her first sound.** Text was correspondence; voice is presence (→ ch. 24), and presence dies on a two-second silence. So the architecture is organised entirely around *time-to-first-audio* and around *interrupting* — the two things text never had to solve.

## Why cascaded, and why the brain doesn't move

There is a competing architecture — speech-to-speech, audio straight to audio (→ ch. 24, "the other architecture"). It is lower-latency and hears tone. This build is deliberately **cascaded** (STT → brain → TTS through a text layer) for one reason: **the text boundary is where the companion lives.** Memory extraction, SOUL injection, the corpus, the diary, the whole auditable thesis — none of it exists if audio maps straight to audio. So Build #2 keeps Build #1's text spine intact and wraps voice *around* it. That is also why the brain is literally Build #1's code, not a rewrite (§2): the point of the build is that the *same someone* now has a body.

**Standalone, and how the brain is reused.** The reference impl is self-contained — copy the folder to another machine, follow the README, run. Build #1's `app/` package is **vendored** into `./app` (documented in `app/VENDORED.md`), and the SOUL source is vendored into `./soul-src` so `scripts/seed_vault.py` seeds a Vault with no external reference. `desktop/brain.py` is the one seam between the two: it builds Build #1's `AppState` and calls `assemble()`, `recall()`, `stream()`, and — for persistence — Build #1's exact `post_turn` pipeline. The only change it makes to a turn is appending two system blocks, both voice-only: one telling the model this is a *spoken* exchange — plain speech, no narration or stage directions — and one asking for inline emotion tags (§6). Study or change the brain in Build #1 (ch. 31); this copy is downstream.

**Her thinking is now yours too.** Build #1's honest caveat was that her *mind* (the files) was yours from day one but her *thinking* was rented behind an API. Build #2 collects the debt: `CHAT_MODEL` defaults to a local model (`lm_studio/…`, with `ollama/…` a swap away) behind the exact same LiteLLM seam, so the reply voice comes off your own GPU. Pull the network cable and nothing changes — that is the sovereignty bar this build clears (property 6). The escape hatch is that same seam in reverse: the model id's prefix routes the provider, so pointing `CHAT_MODEL` at a hosted `openrouter/…` model — if you don't have the GPU for a good local model, or want a stronger mind than your hardware can host — is one line plus a key. Local is the default, not a cage; the point is that sovereignty is *available*, not that a bigger model is forbidden.

**What going local costs the memory, and how to pay it.** Sovereignty has a bill, and it lands on the *quiet* model — the `UTILITY_MODEL` that extracts durable facts into `USER.md` after each turn (B1 §6.3). Two things bite the moment you point it at a local model, and both showed up the first time someone told her their name over voice and she couldn't keep it. First, the local default is a **reasoning** model: it emits a `<think>…</think>` block before its JSON answer, and if the utility call's token budget is sized for "just the JSON," the reasoning eats the whole budget and the answer truncates to an empty string — the fact is silently lost. The fix is not to muzzle the thinking (that trades away the very quality you ran a reasoning model for); it is to *budget for it* — `UTILITY_MAX_TOKENS` leaves room for both, reasoning stays on by default, and `parse_ops` strips any leading think block defensively. Second, a small local model is a sloppier reader of *who said what*: fed a transcript of `you:` and `yuri:` lines, it will cheerfully record "yuri: my name is Yuri" as **the user's** name. The one-line extraction prompt Build #1 got away with (backed by a frontier model) is not enough here — the local model needs the speaker rule spelled out: extract only from the user's lines, and never bank the companion's self-description as a fact about the user. This is the general shape of going local: the reply model's slips you *hear* and can regenerate; the utility model's slips silently corrupt her memory of you, so that is where the belt-and-suspenders go.

**The two reasoning switches point opposite ways, and that is the whole trick.** The same local-reasoning default that helps the *quiet* model hurts the *loud* one, because they run in different places. The utility model thinks **off the hot path** — it extracts facts after the turn, where its latency is free — so `UTILITY_THINKING=true` and you *want* the `<think>` pass for extraction quality (§2.5). The reply model thinks **on the hot path**, between the user going silent and her first word — exactly the budget ch. 24 says presence lives or dies on — where a `<think>` block is dead air, or worse, eats the reply's token budget and empties it. So the reply's reasoning is turned **off**: `CHAT_THINKING=false` sends `reasoning_effort:"none"` in the *raw* request body (`extra_body` — as a top-level LiteLLM arg it gets rewritten and the server never applies it), with a qwen `/no_think` system token as a fallback for models that ignore the field (§2.6). Both switches are inert on a non-reasoning model, so the one config is safe whatever you route to. The rule of thumb: think where latency is free, don't where it isn't.

## Reading the code: follow the sound

| Read this to understand… | …in this file |
|---|---|
| **the real-time loop** (the spine) | `desktop/voice/turn.py` — `TurnController.run_turn` |
| **barge-in as a pipeline cancel** (the hard part) | `TurnController.cancel` + `tests/test_turn_bargein.py` |
| rejecting noise as speech (the keyboard bug) | `desktop/voice/speech_gate.py` + `transcript.py` |
| the STT / TTS / VAD seams | `desktop/voice/protocols.py`; `desktop/voice/backends/` |
| emotion tag → face, on the stream | `desktop/voice/emotion.py` (parse) + `web/avatar.js` (map) |
| covering the first-audio gap | `desktop/voice/fillers.py` |
| the latency budget, measured | `desktop/voice/latency.py` |
| the brain, reused unchanged | `desktop/brain.py` over the vendored `app/` |
| the full-duplex loop over the wire | `desktop/routes/voice_ws.py` — `/ws/voice` |
| the body: Live2D + lipsync | `web/avatar.js`; the mic + playback client is `web/voice.js` |

## The real-time loop — the single most important function

`desktop/voice/turn.py`, `run_turn`. Everything hard about a voice companion is two disciplines, and both are in this one function.

**Discipline one — stream every stage into the next (§4.1).** Never wait for a full transcript, a full reply, or a full waveform. The loop runs a **producer** coroutine that drains brain tokens, strips emotion tags, and cuts complete sentences onto a queue — while the **consumer** pulls sentences off, synthesizes each (in a worker thread, off the event loop), and emits its audio. Because the two run concurrently, the LLM writes sentence two while the TTS speaks sentence one. The first audio chunk goes out the instant sentence one renders, not when the reply finishes. Sentence-cutting is *incremental* (`sentences.py`) — you can't split a string that's still arriving a token at a time, so you cut complete sentences off the front of a growing buffer and keep the remainder.

**Discipline two — barge-in is a pipeline cancel, not a pause (§4.3).** When the user talks over her, `cancel()` must tear down TTS playback *and* the in-flight generation *together*. Here that is one `asyncio.Event`: setting it breaks the producer's `async for` over the brain's token stream — which `aclose()`s that async generator, aborting generation at the model — and stops the consumer's emit loop. Cancellation has to reach all the way back, or she keeps "thinking" a reply no one is waiting for and then says it. The cancel is idempotent (the mic handler fires it on every speech frame) and scoped to the current turn (a fresh token per `run_turn`).

And the failure contract, inherited verbatim from Build #1's two rules (§4.4): a **barged-in turn** and a **mid-stream model error** both persist *nothing* — no corpus line, no commit. A turn that didn't happen leaves no trace. Only a fully completed turn calls `persist()`, which is Build #1's `post_turn` pipeline (journal · index · USER.md · summary · one commit · one corpus line), scheduled off the hot path so it never delays her speaking. The corpus line is written from the *verbatim* reply, tags and all — that is what a future fine-tune should learn to produce (→ ch. 20).

`test_turn_bargein.py` is the test that pins all of this: it drives the loop with a fake brain, fires `cancel()` a few tokens in, and asserts the turn ends `cancelled` (not `done`), generation stopped early, and `persist` was never called.

**The other half of barge-in is *not* firing it on noise.** A raw per-frame VAD verdict can't tell your voice from a mechanical keystroke, so a naïve loop lets the keyboard interrupt her — and feeds the clatter to Whisper, which hallucinates a junk turn (`. . . .`) straight into her memory. Both are the failure mode ch. 24 walks through, and Build #2 carries its layered fix: `speech_gate.py`'s `SpeechGate` debounces turn-taking (act only on a *run* of speech frames, with a higher bar to interrupt her than to start a turn — `web/voice.js` mirrors it at the edge), the server confirms an endpointed utterance actually held speech, and `transcript.py` drops empty/punctuation-only transcripts before they reach the brain or the Vault. Three independent nets, so one false positive never gets remembered.

## The latency budget, with numbers

The bar is: her first audible word lands about a second after you stop speaking — the sub-second-*feel* of ch. 28, which in practice means **≤ ~1.2 s from end-of-speech to first audio out**. Budget it explicitly, because the pipeline has five stages and any one of them will happily eat the whole second on its own:

| Stage | Target | The trap |
|---|---|---|
| End-of-speech detection (VAD endpointing) | 200–300 ms | pure dead air — the silence you must wait through to know they've stopped; tune it aggressive and accept the odd clipped pause |
| STT final segment (`faster-whisper`) | 150–300 ms | transcribe *during* speech so only the last chunk is on the clock |
| Prompt assembly + memory recall | ≤ 50 ms | local embeddings, off the model's clock; if retrieval is slow, cache it |
| LLM time-to-first-token (12B QAT ~4-bit, warm KV cache) | 250–500 ms | a cold prompt re-ingest blows the whole budget — keep the cache warm between turns (→ ch. 21) |
| TTS time-to-first-audio (streaming) | 100–300 ms | synthesize sentence one while the LLM is still writing sentence two |

Sum: roughly 0.7–1.4 s, which is why the budget has no slack for a single non-streaming stage. The reference impl **measures** this rather than trusting it: `latency.py` stamps the stage marks and, crucially, the one end-to-end number — mic-silence to first sample out — because per-stage numbers lie when queues hide between the stages. The sanctuary shows that number in the header, and turns over budget flag it. Measure end-to-end; the per-stage view is a diagnostic, not the score.

## Masking latency: start talking before the answer is ready

The hardest stage to shrink is time-to-first-audio, and the fix often isn't a faster model — it's covering the gap with speech that doesn't depend on the answer (→ ch. 24). `desktop/voice/fillers.py` is that trick at its smallest: the instant the user endpoints, *before* the LLM has a token, she plays a short pre-rendered acknowledgment — "mm—", "hm, okay—". The clips are synthesized **once** at startup and cached, so firing one is tens of milliseconds, not a TTS round-trip; a random one is picked (never twice in a row) so it doesn't loop; and the bank is tuned to the persona. Two rules keep it honest and both are enforced by the loop: the real first sentence streams *into the tail* of the filler (so it only has to be ready before the clip ends, not before the user stops talking), and filler is interruptible audio — the same barge-in path kills it, because a filler you can't interrupt is worse than the silence it replaced. Masking is what lets a slower, richer voice stay in the running; a fast voice plus masking is faster still.

## Emotion → expression: the intent-vs-realisation split

`desktop/voice/emotion.py`. Build #2's one change to the prompt is a system block asking the model to emit inline tags from a fixed palette — `[happy]`, `[tender]`, `[surprised]`… The tag is the *intent* (the BML/FML split of ch. 02 §1, ch. 25); the avatar and TTS are the *realisation*. The parser does three jobs on the hot path. It **strips** the tags out of the text before it reaches TTS — she must never *say* the word "happy", it drives her face, not her mouth — and it **emits an expression event** the instant a tag closes, so the face changes just before the matching audio plays (the face leading the voice reads as natural). It also **strips asterisk narration** — `*she leans in*`, `*smiles*` — because this is a *spoken* channel: a chat model narrates its actions by habit, which is right for text chat but wrong out loud, where the TTS would read the stage directions aloud. The prompt's spoken-style directive asks the model not to narrate in the first place; the parser is the belt-and-suspenders that catches what leaks (pure-prose narration with no asterisks can only be prevented in the prompt, not stripped). It is a *streaming* parser because both tags and narration split across token boundaries (`[ha`…`ppy]`, `*she`…`waves*`), and it drops unknown tags silently so a model that invents `[mischievous]` never leaks the literal text into her speech.

The load-bearing design choice is *where the mapping lives*. The brain emits only expression **names**; the map from a name to concrete rig parameters lives in `web/avatar.js`, not in the loop. That separation is what lets Build #4 swap the whole avatar file for a VRM renderer that consumes the exact same names — the brain never learns what a Live2D parameter is.

## The body: a real Live2D avatar

`web/avatar.js` drives an actual Live2D model (the Hiyori sample, the same one AIRI ships) through `pixi-live2d-display`. Two inputs move her face: **expression events** select a parameter preset (mouth shape, eye-smile, brows — mapped onto Hiyori's real rig, which exposes `ParamMouthForm`, `ParamEyeLSmile`, and the rest), and **live audio RMS** drives `ParamMouthOpenY` (the model's LipSync group) so her mouth moves with what she's actually saying. Auto-blink and idle sway come free from the renderer's motion manager.

The honest part is the licensing, and the reference impl handles it the way the whole VTuber ecosystem does. `scripts/fetch_avatar.py` *downloads* the runtime and model into a gitignored `web/vendor/` rather than committing them: **pixi-live2d-display** and **PixiJS** are MIT, but **Live2D Cubism Core** is proprietary (free to use under the Live2D license below ¥10M JPY annual revenue; larger orgs need a Release License), and the **Hiyori** model is a Live2D "Free Material" sample. None of it is the book's to redistribute, so the build fetches it and says so. If `web/vendor/` is empty the app runs **voice-only** and `avatar.js` prints why — the body is additive, never load-bearing.

## Choosing her voice

Voice is a config swap behind one TTS seam, and the build ships three picks from ch. 24. Each trades quality against latency and hardware differently:

- **Kokoro (the default).** 82M params, Apache-2.0, faster-than-real-time on CPU. *For:* it needs no GPU, runs on almost any hardware, and **leaves the whole GPU for the LLM and the avatar** (→ ch. 24: every gigabyte the voice eats is a gigabyte the LLM can't), with the lowest latency of the three. That is why it is the default — it works out of the box on a modest machine. *Against:* a single fixed voice, no cloning or design. `TTS_BACKEND=kokoro`.
- **Qwen3-TTS (the GPU upgrade).** Apache-2.0, the most flexible pick: it gives her a *designed persona voice* rather than a generic one. It clones a reference clip *and* can *design a voice from a natural-language description* ("a warm, gentle young woman in her twenties; soft, unhurried, a slight late-night breathiness"); the build ships one voice already designed and frozen as `assets/designed.wav`, then clones *that* clip every utterance (`qwen_mode=clone`) so her timbre is stable. *For:* the most control over how she sounds — the voice becomes part of the persona. *Against:* it runs in-process and is slower than real time (RTF > 1), so it leans on the **filler masking** above to stay conversational, and it needs a CUDA GPU it shares with the LLM; design mode re-samples on every call, so you must design once and freeze the render or her timbre drifts between sentences. `TTS_BACKEND=qwen3_tts`.
- **GPT-SoVITS (the canon-voice pick).** When the persona has a voice the audience already hears, GPT-SoVITS v4 clones it at ~700 ms to first audio. *For:* practical real-time cloning of a specific voice. *Against:* it needs a running clone server (→ the sibling `gpt-sovits` impl). `TTS_BACKEND=gpt_sovits`.

STT defaults to faster-whisper (latency over accuracy); Moonshine or Parakeet drop in behind the same seam for true streaming partials. VAD is Silero — run at the *edge* (in the browser) for barge-in latency, and server-side for endpointing.

## Wiring it by hand vs. a framework

ch. 24 recommends standing the loop up on Pipecat or LiveKit rather than wiring sockets by hand. The reference impl deliberately hand-rolls it anyway — for exactly the reason Build #1 hand-rolls memory instead of importing LangChain: **barge-in-as-cancel is the idea to *see*, and it's about 150 readable lines.** Own the loop, rent nothing. The production move is to mount this same logic on a framework for WebRTC transport robustness; the cancel discipline is identical either way. `desktop/routes/voice_ws.py` is where it lands as a full-duplex WebSocket — reading inbound messages (frames, endpoint, barge-in) *while* streaming outbound events (expression, audio, done), so an interrupt can arrive at any instant.

## The continuity greeting and "the same someone"

On connect she greets you first, from memory, before you type — the same definition-of-done moment as Build #1, now spoken. `desktop/brain.py`'s `stream_greeting` assembles persona + `USER.md` + summary + a top recall against a "you just put your headset on" cue; it is *not* persisted (an opener is not a turn you took) and never pollutes the window.

Her identity is the SOUL — the same card as Build #1 (§2.3). By default she runs her own freshly-seeded Vault; to *continue* the companion you already grew in Build #1 rather than start at zero, point `VAULT_DIR` at that Vault — moving her is copying a folder (→ ch. 19). Whichever you do, golden transcripts (→ ch. 23) are how you confirm the persona survived the smaller local model — a model swap is exactly when identity drifts (property 1).

## Definition of done

She runs offline; you speak, she answers in voice within a latency that feels conversational, her face moves with what she's saying, you can interrupt her mid-sentence and she yields, and she's the same someone as Build #1. Pull the network cable and nothing changes. And it's **tested** — `pytest` ships and is green from the project root, entirely offline against the seam fakes: emotion parsing (tags *and* asterisk-narration stripping), the barge-in cancel (the non-negotiable one), the latency accounting, filler masking, the ordered pipeline, the partner-model extraction robustness (think-block stripping, the thinking toggle), the turn-taking debounce and the transcript filter (the keyboard-noise fix, with a `/ws/voice` test that drops an all-noise utterance but takes a real one), an end-to-end turn over the real vendored brain proving a corpus line plus one commit, and the live `/ws/voice` route.

## What it deliberately omits

Still reactive — no autonomy (→ Build #5). 2D body only (→ Build #4 for 3D/VRM). Single avatar register. No **paralinguistic input** yet — hearing that you *sound* tired and acting on it is a proactive move, so affect-as-a-SENSE-input (→ ch. 24) waits for the autonomy loop. Still no fine-tune — but this is the build whose local 12B the eventual distillation actually *targets*: a stronger teacher model, distilled onto your own on-voice data, is how you lift a relatively small 12B — not just the long-session persona drift it shows, but the capability and agentic reliability a base this size can't hold from prompt alone (→ ch. 20) — and running this build is how you accumulate that corpus. Keep logging (→ ch. 30, ch. 31); the data lives on your machine, which is exactly where you want it.

## Extends to

Export the same SOUL as a distributable `.PNG` card → Build #3. Swap `web/avatar.js` (Live2D) for VRM + a 3D scene and add tools → Build #4. Wrap the tick loop (→ ch. 18) around *this exact Vault* — DREAM consolidation and a drop-folder knowledge store — → Build #5. The five-verb MemoryStore contract already has the slots; nothing here is thrown away.
