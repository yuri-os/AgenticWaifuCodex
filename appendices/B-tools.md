# B — Tools and Stacks

Curated short lists, organised by layer. Confirm current versions before committing — this list ages fast.

## Inference (hosted)

- **Anthropic Claude (Opus/Sonnet/Haiku 4.x)** — current best persona stability per dollar at the top.
- **OpenAI GPT-5 family** — strong default; native realtime + tool stack.
- **Google Gemini 2.x** — long context, good multimodal.
- **Together / Fireworks / Replicate / DeepInfra / Modal** — hosted open-weight inference.
- **Groq / Cerebras** — sub-100ms TTFT for small models.

## Inference (local / self-host)

- **vLLM** — server-side default for open models.
- **SGLang** — competitive vLLM alternative.
- **llama.cpp / llamafile / Ollama** — laptop-grade local.
- **MLX** — Apple Silicon local.
- **TensorRT-LLM** — fastest if you've committed to Nvidia.

## Models (open) 2026 short list

- Llama 4 family (Meta)
- Qwen 3 family (Alibaba)
- DeepSeek V3 / R1
- Mistral Large 3
- Gemma 3 (Google)
- Small specialists: Mistral Small, Qwen 2.5-7B, Gemma 3-9B, Phi-3.5

## Memory / RAG

- **pgvector** — Postgres + vectors; the default starter.
- **Qdrant / Weaviate / Chroma** — dedicated vector DBs.
- **Mem0** — opinionated memory framework.
- **Letta** (née MemGPT) — agent-with-self-managed-context.
- **Zep / Graphiti** — temporal + graph memory.
- **GraphRAG (Microsoft)** — graph over a doc corpus.

## Agent / orchestration

- **MCP servers** (Anthropic protocol) — tool surface standard.
- **LangGraph** — explicit graph orchestration; production-grade default.
- **CrewAI / AutoGen** — multi-agent (use sparingly).
- **Claude Agent SDK / OpenAI Agents SDK / Strands (AWS)** — frontier-lab / hyperscaler offerings.
- **Mastra** — TypeScript-native, Next.js-friendly.
- **Pydantic AI** — typed, production Python.
- **ElizaOS** — TypeScript agent framework with character JSON, multi-agent, and out-of-box Discord/Telegram/X/Farcaster/Bluesky/Slack connectors. Web3-flavored but useful for the social-presence layer (→ ch. 02 §5).
- **Pipecat / LiveKit Agents** — real-time voice agents.

## Voice — TTS

- **ElevenLabs** — closed, prosody king.
- **Hume EVI** — voice + emotion.
- **OpenAI Realtime API** — integrated stack.
- **XTTS-v2, StyleTTS2, Kokoro, Orpheus** — open.
- **Sesame, Cartesia** — newer, watch list.

## Voice — STT

- **Whisper / faster-whisper / Distil-Whisper** — open default.
- **Nvidia Parakeet / Canary** — faster.
- **Deepgram / AssemblyAI** — hosted.

## Avatars

- **Live2D Cubism Editor + SDK** — 2D rigged.
- **VRoid Studio** — easy VRM creation.
- **Blender + VRM plugin** — serious VRM.
- **three-vrm** — browser VRM runtime.
- **UniVRM** — Unity VRM.
- **VRM4U** — Unreal Engine VRM with built-in VMC blueprints.

## Avatar control protocols & host runtimes

The AI-brain → avatar pipeline. See ch. 25 for the architecture and trade-offs.

- **VMC Protocol** — OSC-over-UDP standard for VRM control (MIT). Ports 39539/39540. Senders: VSeeFace, Waidayo, MocapForAll, TDPT. Receivers: Warudo, VNyan, EVMC4U (Unity), VRM4U (UE5), VMC4B (Blender).
- **VTube Studio API** — WebSocket/JSON plugin API for Live2D. `VTubeStudioJS` (TS/JS), Python clients, `@hkopenai/vtube-studio-plugin-mcp-server` (MCP).
- **ARKit blendshape vocabulary (52)** — the de facto facial expression naming standard. Emit ARKit names; most hosts understand them.
- **Warudo** — proprietary freeware 3D VTuber app with Steam Workshop plugin ecosystem + C# SDK. VMC receiver.
- **VNyan** — freeware; node-based visual scripting; VMC receiver; node-graph friendly to AI integrations.
- **VSeeFace** — freeware; VMC sender + receiver; classic face-tracking → VRM.
- **VTube Studio** — Live2D incumbent; one-time paid; WebSocket plugin API.
- **AITuberKit** — open-source Next.js + TS toolkit for AI VTubers; VRM + Live2D + Motion PNG; YouTube Live ingestion built in. Closest stack-match to this project's existing repos.

## Image generation

- **ComfyUI** — open default, power-user.
- **A1111** — older but ubiquitous.
- **SDXL / Flux / SD3** — base models.
- **NovelAI** — closed reference for anime consistency.

## Safety / moderation

- **Llama Guard 3 / 4** — open classifier.
- **NeMo Guardrails** — programmable.
- **Granite Guardian** (IBM) — jailbreak focus.
- **OpenAI Moderation / Anthropic safety classifiers** — bundled.

## Frontends / shells

- **SillyTavern** — the RP power-user UI.
- **Open WebUI** — clean LLM web UI.
- **AIRI** — 40k-star self-hosted multi-platform AI waifu (VRM/Live2D, voice, memory, plays games). The closest existing implementation of the agentic-waifu spec (→ ch. 02 §5).
- **Soul of Waifu** — full-stack desktop reference.
- **Open-LLM-VTuber** — voice + Live2D cross-platform.
- **Electron / Tauri** — desktop wrappers.
- **Next.js / SvelteKit / SolidStart** — web frameworks.
- **Three.js / Babylon.js** — browser 3D.

## Distribution

- **GitHub** — code + releases.
- **HuggingFace** — models, adapters, datasets, Spaces.
- **Chub.ai / CharacterHub** — character cards.
- **AICharacterCards.com** — character cards.
- **JanitorAI** — RP frontend + audience.
- **VRChat** — VRM avatar distribution = marketing.

## Creator economy

- **Stripe** — payments.
- **Ko-fi** — donations + small shop.
- **Patreon** — recurring patronage.
- **Buttondown / Ghost / Substack** — newsletter.
- **Gumroad / Lemonsqueezy** — digital product sales.
- **Discord** — community.

## Compliance / safety vendors

- **Yoti / Persona / AU10TIX** — age verification.
- **C2PA / Truepic** — content provenance.
