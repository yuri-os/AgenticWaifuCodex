# 24 — Voice: TTS, STT, Real-Time Conversation

## Why voice changes everything

Adding voice to a companion is not adding a feature — it's changing the medium. Text is correspondence; voice is *presence*. The bar for "feels alive" rises, the bar for *latency* and *prosody* rises with it.

## The pipeline

```
mic → VAD → STT → memory + RAG → LLM (streaming) → TTS (streaming) → speaker
                                                                        ↑
                                                                        interruption handling
```

Three pieces are non-obvious:

- **VAD (voice activity detection).** Detects start/stop locally with millisecond latency. Silero VAD is the default.
- **Streaming everything.** STT streams partials; LLM streams tokens; TTS streams sentence-by-sentence. The user shouldn't wait for a full reply to start hearing it.
- **Interruption.** The user starts talking → the TTS halts, the in-flight LLM cancels, the next turn begins. Hard to get right; non-negotiable for "feels alive."

## Hearing more than words: paralinguistic input

STT collapses speech to text and throws away everything that *isn't* words — tone, energy, pace, the long pause before "I'm fine." But that discarded layer is half of what voice adds over text: a present companion notices you sound tired before she parses what you said. Treat **paralinguistics as a separate input signal**, extracted in parallel with transcription: affect/emotion, vocal energy, hesitation, prosodic stress. Hume EVI does this as part of its stack; standalone speech-emotion classifiers (or a small model over the raw audio) do it where you've wired the pipeline yourself.

The key move is *where the signal goes*. It is not just colour for the TTS reply — it is a SENSE input to the brain, fused into salience exactly like a shared image (→ ch. 18, perceiving the user). A drop in vocal energy can be the very thing that licenses a gentle "you okay tonight?" — believable initiative the text-only companion structurally cannot produce. The same cautions apply: affect is a *guess*, not a fact to be remembered as truth (→ ch. 15, the quarantine), and listening this closely raises the consent bar (→ ch. 05, ch. 22).

## TTS short list (mid-2026)

Local quality has caught up enough that a local-first companion voice is no longer a compromise — it's the default for this project (→ ch. 32 sovereignty). Lead local; reach for hosted only for commercial polish or fastest time-to-ship. The list below is grouped by **hardware weight**, because that — not quality alone — is what decides whether a voice can run on the always-on machine alongside the LLM and an avatar (→ ch. 13 VRAM math, ch. 21). A rough rule: every gigabyte the voice stack eats is a gigabyte the LLM can't, so on a 12 GB card you want the voice under ~2–3 GB.

On Windows, keep capture and playback on the native/browser side when that is simplest. If an STT or TTS backend is Linux-first, WSL2 is a practical service-host fallback over localhost; it does not change the voice protocol or require moving the whole UI into Linux.

**CPU-class (no GPU needed, or <2 GB):**

- **Kokoro (82M).** Tiny, runs faster-than-real-time on CPU, Apache-2.0, 54 voices. Best quality-per-watt for a *fixed* voice. No cloning — but if your persona has one settled voice, this is the cheapest good one, and it leaves the whole GPU for the LLM.
- **Piper.** Ultra-light, CPU-only, edge-grade. Lower quality than Kokoro; reach for it on a Pi-class device.

**Light GPU (≈4–6 GB) — the companion sweet spot:**

- **Qwen3-TTS (Alibaba, 0.6B / 1.7B; Jan 2026).** The **feature-convergence pick**: a single Apache-2.0 model that does what most of this group split between them — a built-in preset voice (like Kokoro), 3-second zero-shot *cloning* of a specific identity (like GPT-SoVITS), *and* voice **design from a text description** ("a warm young woman, soft and slightly breathy"), which almost nothing else offers. 10 languages, HF + vLLM serving; the 0.6B fits the sweet spot, the 1.7B clones best. **The latency caveat is the catch, and it's a real one.** The published "~97 ms" is a per-chunk streaming figure, *not* time-to-first-audio — in this project's own testing, practical first-audio ran **2–3 seconds**, too slow to feel live without masking it (→ *Masking latency* below). Whether that's a hard property of the current pip build or a tuning/config issue not yet root-caused is an open question — the pip `qwen-tts` path doesn't expose true streaming, so some of the gap may close with a proper streaming server (vLLM) or a faster serving setup. Until that's confirmed, plan around the measured number, not the published one. For a companion that wants one settled voice and the full feature set, the convergence is real; for a *responsive* one, treat Qwen as the quality/flexibility option and reach for GPT-SoVITS v4 when first-audio latency is what matters. (Worked reference implementation — clone / design / preset, with a mode-aware eval — at `reference-implementations/qwen3-tts/`, alongside Kokoro and GPT-SoVITS impls for the same registers.)
- **Chatterbox / Chatterbox Multilingual V3 (Resemble, 0.5B).** Cloning plus an exaggeration/emotion knob; V3 (2026) improved speaker similarity and cut hallucinations. Widely called the first local model whose *cloned* output stopped sounding obviously synthetic.
- **GPT-SoVITS (v4).** The waifu/VTuber-community standard for cloning a *specific character voice* — 5-second zero-shot or ~1-minute few-shot fine-tune. v4 killed the old metallic artifacts and outputs 48 kHz; strong CN/EN/JP/KR/Cantonese cross-lingual. The one when your persona has a canon voice in the audience's head — **and, as of this project's testing, the practical real-time pick.** Quality is a notch below Qwen3-TTS, but it streams sentence-by-sentence at **~700 ms to first audio** on the same hardware where Qwen takes 2–3 s, and that gap is the difference between a voice that feels live and one that feels like a request/response form. Lower quality, much faster — and for a companion, latency beats the last few percent of naturalness (→ Evaluation). Working `api_v2` server + realtime streaming terminal in `reference-implementations/gpt-sovits/`.
- **IndexTTS-2.** SOTA emotional fidelity; *decouples timbre from emotion* (clone the voice, dial the feeling independently) and adds millisecond duration control. Heavier to run than Chatterbox but the expressiveness leader of the open pack.
- **XTTS-v2.** 6-second zero-shot clone, 17 languages, ~4 GB. Coqui is defunct but the open weights live on.
- **F5-TTS.** Strong zero-shot cloning from a ~10s clip; fast, fully local.
- **StyleTTS2.** High naturalness, reference-driven *style* (not identity) control — the tool for a register rather than a person.

**Heavier (≈8 GB+), frontier-quality local:**

- **Orpheus (3B).** LLM-backed TTS with inline emotion tags (`<laugh>`, `<sigh>`); expressiveness that genuinely rivals ElevenLabs. Wants 6–8 GB.
- **VoxCPM2 (OpenBMB, 2B).** Tokenizer-free, 30 languages, voice *design* + controllable cloning, 48 kHz; ~8 GB.
- **Voxtral TTS (Mistral, 4B; March 2026).** Clones from <5s, 9 languages, beat ElevenLabs Flash v2.5 in human-preference tests — and still runs on consumer hardware. The heaviest mainstream local option worth the VRAM.

**Also tracking:** Sesame CSM (context-aware conversational prosody), Hume TADA (2026, near-zero hallucination), Dia (multi-speaker dialogue + nonverbals), CosyVoice2-0.5B, Fish Speech / OpenAudio, Higgs Audio v2.

**Real-time voice changing:** **RVC** (Retrieval-based Voice Conversion) is still the battle-tested path for converting a voice *in real time* on consumer hardware — the zero-shot cloners above (GPT-SoVITS included) are not yet low-latency enough to convert a live stream turn-by-turn. See *Cloning a specific voice* below for how this pairs into the loop.

**Hosted (commercial polish / fastest ship):**

- **ElevenLabs.** Best prosody, paid, closed. Default for serious commercial companion voice.
- **Hume EVI.** Voice + emotional inference; a conversational stack rather than just TTS.
- **OpenAI Realtime API.** Integrated STT+LLM+TTS over WebSocket. Fast to ship; cost adds up.
- **Cartesia (Sonic), PlayHT.** Low-latency hosted stacks worth tracking.

## STT short list (mid-2026)

STT is effectively solved — choose on **latency and footprint**, and prefer local (→ ch. 32). Grouped by weight:

**Tiny / streaming (CPU or <1 GB):**

- **Moonshine (27–245M).** Built for streaming — words land as you speak, minimal back-revision. Matches Whisper Tiny/Small on English at a fraction of the size; the pick for edge or a CPU-only box.
- **whisper.cpp / faster-whisper (tiny–base).** GGML/CTranslate2 backends; real-time on a laptop CPU.

**Workhorse (≈4–6 GB):**

- **NVIDIA Parakeet TDT 0.6B v3.** *Fastest by a wide margin* (published RTFx in the thousands) and ~6.3% WER — below Whisper Large v3. Apache/CC-BY. The latency pick for a voice loop, where speed beats the last fraction of a point of WER.
- **Whisper Large v3 Turbo (809M, ~6 GB) / Distil-Whisper / faster-whisper.** The multilingual default — 99 languages. Turbo is the speed/quality balance.
- **Qwen3-ASR (0.6B / 1.7B; Jan 2026).** The recognition sibling of Qwen3-TTS — 52 languages with language-ID and timestamps; the 0.6B is workhorse-light. Tooling is still maturing next to Whisper/NeMo, but if you're already running a Qwen voice stack it keeps the family consistent. (Mistral's **Voxtral Transcribe 2** is the other strong 2026 newcomer — native streaming, ~5.9% WER — but only 13 languages.)

**Accuracy-max (heavier, ≈2.5–8B):**

- **Canary Qwen 2.5B** (~5.6% WER, top English accuracy) and **IBM Granite Speech (4.1 2B / 3.3 8B)** currently top the Open ASR Leaderboard — ahead of proprietary systems. Worth it only if transcription accuracy genuinely gates your use case; for a companion, Parakeet's latency wins.

**Hosted:** Deepgram / AssemblyAI — fast, multilingual, low-latency.

## Real-time stacks

Rather than wiring sockets by hand:

- **Pipecat (Daily).** Open-source real-time voice-agent framework; runs a fully local STT→LLM→TTS pipeline as happily as a hosted one.
- **LiveKit Agents.** Production-grade voice-agent infra (WebRTC transport); also supports local model nodes.
- **Vapi, Retell, Bland.** Hosted real-time voice products — turnkey, but they own the loop.

## Speech-to-speech (full-duplex): the other architecture

Everything above assumes a **cascaded** pipeline — STT → brain → TTS, chained through a text layer. The competing architecture skips text: a single model maps **audio in to audio out** (speech-to-speech, S2S), often *full-duplex* so it can listen and talk at once. The open frontier here is real and worth knowing:

- **Moshi (Kyutai).** The first open real-time full-duplex spoken-dialogue model — ~160–200 ms latency, models *both* audio streams (hers and yours) plus an "inner-monologue" text stream, CC-BY-4.0, with PyTorch/MLX/Rust stacks (it runs on a Mac).
- **Omni LLMs that speak natively.** **Qwen3-Omni** (30B-A3B MoE, Apache-2.0) and the newer **Qwen3.5-Omni** use a *Thinker–Talker* split — a reasoning core whose representations a "Talker" turns into streaming speech; **GLM-4-Voice, Step-Audio, Kimi-Audio, LLaMA-Omni, Freeze-Omni** are the same idea. These fold the LLM and the voice into one model rather than wiring three.

The trade is sharp, and for *this* book it points back to the cascaded pipeline. S2S wins on the two things text throws away: **lower latency** (≈250–350 ms vs a tuned cascade's 400–600 ms) and **paralinguistics** — tone, emphasis, overlap, the affect this chapter treats as a SENSE input (→ above). But it gives up exactly what a companion is built on. The **text boundary is where the companion lives**: memory extraction (→ ch. 15), persona/SOUL injection and the identity anchor (→ ch. 07, ch. 14), tool use (→ ch. 17), the diary and drift dashboard (→ ch. 18, ch. 23), and the whole *auditable, transparent* thesis (→ ch. 03) — none of which exist if audio maps straight to audio. Pure S2S is also ~10× the inference cost (context accretes as audio) and measurably worse on names and numbers. So as of mid-2026 the recommendation stands: **cascaded for the companion**, because you need the brain — and the readable text stream — in the loop.

The bridge worth watching is that the best S2S models *keep a text stream anyway*: Moshi's inner monologue and Qwen-Omni's Thinker are both a text core under the speech. The future companion is probably a *hybrid* — a speech-native front for paralinguistics and barge-in over a text spine you can still read, edit, and remember from. Design the loop (→ the recipe below) so the brain stays swappable and that migration is *contained* rather than a rewrite — realistically it touches more than one seam. The brain-swap itself is clean (a model-router change over a text spine you keep). The speech-front is not a drop-in TTS swap: a full-duplex model folds STT, brain, and TTS together, so it lands across the SENSE path, the model router, and the voice effector at once. Two design moves keep it a backend change and not a re-plumb: treat **paralinguistics as a first-class SENSE input** now (→ above) so the hybrid has a landing pad already in the loop, and require any speech-front to keep emitting the **readable text spine** the companion lives on. Both are written into the runtime architecture (→ ch. 19) so the seam is real, not aspirational.

## Companion-specific notes

- **Cloning the canon voice.** If your persona has a "voice" in the audience's head, clone it and keep it locked — one cloner, one asset, no drift per turn (the how is in *Cloning a specific voice* below).
- **The "ums" question.** Real human filler (mm, ah, oh) makes the voice feel real and irritates audiophiles in equal measure. Make this configurable.
- **The whisper register.** Late-night, soft-voice companion patterns. Mostly an authored-script + style-prompt problem on top of the TTS.
- **Multi-voice.** A persona that has *two* voices (her usual + her quieter / late-night) is a memorable design move.

## A recipe: the Yuri voice loop

Rather than wiring sockets by hand, stand it up on a real-time framework (Pipecat or LiveKit Agents). The wiring:

1. **Transport** — WebRTC (LiveKit) or the framework's pipeline; mic in, speaker out, low-latency.
2. **VAD** (Silero) at the edge — detects speech start/stop locally so you never round-trip a server just to know she should listen or stop talking.
3. **STT** streaming (faster-whisper local, or Deepgram hosted) emitting partials.
4. **Brain** — the assembled prompt + memory (→ ch. 14, ch. 15), the LLM streaming tokens.
5. **TTS** streaming (Kokoro/StyleTTS2 local for sovereignty, → ch. 32, or GPT-SoVITS/RVC if the canon voice is cloned; ElevenLabs if you want hosted polish) rendering sentence-by-sentence as tokens arrive.
6. **Barge-in** — on VAD-detected user speech: halt TTS playback, cancel the in-flight LLM generation, open the next turn. This is the hard part and the non-negotiable one.

The two event handlers that make barge-in work — one watching the mic, one draining the brain into the voice:

```
# fires on every audio frame from the mic
on mic_frame(frame):
    if vad.is_speech(frame):
        if tts.is_playing():          # user talked over her → interruption
            tts.stop()                #   kill audio immediately
            llm.cancel()              #   abort the in-flight generation
        stt.feed(frame)               # (re)start listening
    else:
        stt.mark_silence(frame)       # silence advances endpointing

# fires when STT decides the user's turn is done
on stt.endpoint():
    text     = stt.final()
    affect   = paralinguistics.read()         # tone/energy, as a SENSE input (→ ch.18)
    prompt   = assemble(text, affect, memory, rag)   # → ch.14, ch.15
    buf = SentenceBuffer()
    for token in llm.stream(prompt):          # cancellable mid-stream by barge-in
        buf.add(token)
        if buf.has_sentence():
            tts.enqueue(buf.flush())          # stream sentence-by-sentence; audio
                                              #   starts before the reply is finished
```

The whole point is that `llm.stream` and `tts.enqueue` are running *while* `mic_frame` keeps firing — so the interrupt can land at any instant. Cancellation has to reach all the way back: stop the speaker, then abort generation, or she'll keep "thinking" a reply no one is waiting for. Treat a client disconnect and a transport failure exactly like barge-in: stop playback, cancel and close the model stream, discard the in-memory draft and staged turn effects, and persist nothing. Only a completed turn crosses the persistence boundary; cancellation or disconnection rolls the partial exchange back so it cannot reappear in memory, the corpus, or a later reconnect.

The latency budget for this whole loop (target <1.2s to first audio) is worked stage-by-stage in ch. 21 — voice is the use case those numbers exist for.

## The false interrupt: barge-in that fires on noise

The `on mic_frame` handler above has a naïve line in it — `if vad.is_speech(frame)` — and if your VAD is a plain energy gate rather than a real speech model, that line is a bug waiting for a loud room. A mechanical keyboard is the reliable trigger: you're typing while she talks, the mic picks up the clatter, a key-click clears the energy threshold, and `tts.stop()` + `llm.cancel()` fire — she stops dead mid-sentence, interrupted by your keyboard. Coughs, a closing door, a desk bump all do the same. Worse, those noise frames don't just cause a false barge-in; they get fed to STT as if they were speech, and that opens the second failure.

**STT hallucinates on non-speech — it does not stay silent.** Ask Whisper (or most ASR) to transcribe a second of keyboard clatter and it will not return an empty string; it invents text, most often bare punctuation ("`. . . .`", "`...`") or a short stutter of a word or two. In a companion that pipeline is memory: a hallucinated turn gets written to her journal, so tomorrow she "remembers" you saying `. . . . . .` — a real line I've pulled out of a real Vault. The junk is quiet, cumulative, and it corrupts the one thing the companion is supposed to get right about you.

Both are cheap to fix, and the fix is layered because no single check is sufficient. **Debounce the VAD:** don't act on one hot frame — require a short *run* of consecutive speech frames before you call it speech, and hold a barge-in to a *higher* bar than starting a fresh turn, because interrupting her should cost more confidence than opening a new one. A keystroke is a one- or two-frame transient; real speech sustains for dozens, so a run-length gate passes the voice and rejects the clatter. (Better still, run an actual speech-model VAD like Silero at the edge instead of an energy threshold — it rejects non-speech by *content*, not loudness.) **Then filter at the text boundary:** drop any transcript that is empty or punctuation-only before it ever reaches the brain or the memory writer, and lean on the ASR's own `no_speech_prob` to throw out segments it already suspects aren't speech. Belt and suspenders: the VAD confirms real speech happened, and the transcript filter catches whatever leaks past it — so the keyboard never interrupts her and never gets remembered. Build #2 (→ ch. 32) implements exactly this.

## Masking latency: start talking before the answer is ready

The hardest stage to shrink is **time-to-first-audio** — STT endpointing, the LLM's first tokens, and the TTS's first render all stack up before she makes a sound. A heavier-but-richer voice like Qwen3-TTS (2–3 s first audio) loses the live feeling not because the voice is bad but because of that opening silence. The fix isn't always a faster model — it's **covering the gap with speech that doesn't depend on the answer**:

- **Instant acknowledgments.** The instant STT endpoints — *before* the LLM has produced a single token — play a short, content-free reaction: a soft "mm—", "hm, okay—", a breath, a thinking-sound. Real conversation is full of these; a human starts reacting before they've formulated the reply. Pre-render a small bank of them as **cached audio clips** (no TTS round-trip at all, so they fire in tens of milliseconds) and pick one at random so it doesn't loop. This buys you the whole 2–3 s while the real reply spins up, and it reads as *attentiveness*, not lag.
- **Filler that fits the persona.** Tune the bank to the character — a warm companion's "mm, let me think…" lands very differently from a deadpan one's clipped "okay." This is a persona asset, not just a latency hack: versioned and pinned like any voice clip (→ multi-voice, above).
- **Stream the real reply *into* the tail of the filler.** The point of sentence-by-sentence TTS (the recipe's `tts.enqueue`) is that the first real sentence only has to be ready before the filler clip finishes — not before the user stops talking. Overlap them: the acknowledgment covers first-token latency, the first streamed sentence covers the rest. Done right, the seam is inaudible.
- **Caveat — barge-in still rules.** Filler is real audio, so it's interruptible audio: if the user talks over the "mm—", the same barge-in path (`tts.stop()` + `llm.cancel()`) has to kill it instantly. A filler clip that can't be interrupted is worse than the silence it replaced.

This is what lets a slower, higher-quality voice stay in the running: if you'd rather have Qwen3-TTS's quality/flexibility than GPT-SoVITS v4's raw speed, masking is how you pay for it. A fast voice plus masking is faster still — the two stack.

## Cloning a specific voice

If the persona has a voice in the audience's head — a canon read, or a specific reference you're matching — you clone it. Three techniques, picked by constraint:

1. **Zero-shot clone.** Hand the model a short reference clip (6–30s) and it speaks new text in that timbre. F5-TTS, XTTS-v2, and GPT-SoVITS all do this with no training step. Fastest path; quality is "recognizably them," not flawless. Good enough to prototype the voice the same afternoon you pick the reference.
2. **Fine-tune.** Train on a small clean dataset of the target — a few minutes to an hour of single-speaker audio. GPT-SoVITS and XTTS fine-tunes give the best fidelity and, more importantly, the most *stable* voice across thousands of turns. This is the move when the canon voice has to stay locked turn-to-turn (→ the consistency axis in Evaluation below).
3. **Voice conversion (RVC).** Don't clone in the TTS at all — run any fast TTS (or even a live mic), then convert the *timbre* to the target with Retrieval-based Voice Conversion. RVC is the lowest-latency path and the one the live VTuber/streaming crowd uses, because it converts any source voice in near-real-time. Pair a quick neutral TTS with an RVC model of the canon voice when you need both speed and a specific identity.

**Data prep is most of the quality.** Clean, denoised, single-speaker, consistent mic. Use a stem separator (UVR) to strip music/noise, then segment into short clips. Rough minimums: ~1 min for a GPT-SoVITS zero-shot, ~5–30 min of clean audio for a fine-tune that holds up.

### Mimicking a style rather than a person

Sometimes you don't want a specific identity — you want a *register*: breathy, deadpan, bright, an accent, the late-night soft voice. That's a style problem, not a cloning problem:

- **StyleTTS2** takes a reference clip purely for *style* and transfers prosody/affect.
- **Chatterbox** exposes an exaggeration/emotion knob you can dial per line.
- **Orpheus** takes inline emotion tags in the text.
- Or just curate a reference clip *in the target register* and feed it to any zero-shot cloner — the model copies the manner along with the timbre.

This is the engine behind the **multi-voice** design move from the companion notes: ship two voice assets — her usual register and her quieter/late-night one — and switch on context. Define each as one versioned asset (a reference clip or a fine-tuned checkpoint), pin it, and never drift cloners mid-conversation.

## Evaluation

Voice quality is mostly *prosody*, which benchmarks miss, so evaluate on three axes (→ ch. 23): **subjective quality** (a small MOS-style listen test — does it sound alive, not flat?), **technical latency** against the ch. 21 targets (measured, not assumed), and **consistency** (the same voice turn-to-turn, no provider drift). The failure that kills presence isn't word errors — it's a flat read or a two-second lag, so weight prosody and latency over transcription accuracy.
