# A — Glossary

Compact definitions of terms used throughout the book. Where a deeper treatment exists, the entry points to the chapter.

| Term | Definition | Deeper |
|---|---|---|
| **Agentic** | A system with memory, tools, and the capacity to take initiative across turns. | ch 17 |
| **Agentic waifu** | A persistent, persona-driven, embodied AI companion built for a 1:1 relationship. | ch 03 |
| **Affection points (otome)** | Numeric tracker of relationship state; gates content/scenes. | ch 11 |
| **Avatar (Live2D / VRM / portrait)** | The rendered visual form of the persona. | ch 25 |
| **BM25** | Classical sparse-text retrieval; pairs with dense for hybrid RAG. | ch 16 |
| **Canon** | The agreed-upon body of fictional facts about a world or character. | ch 10 |
| **Character card (V2/V3)** | Standardised file format encoding a persona; the RP community's interchange standard. | ch 07 |
| **Chub.ai / CharacterHub** | Largest community marketplace for character cards. | ch 07 |
| **Companion (vs assistant)** | Built for relationship, not productivity. | ch 03 |
| **DPO** | Direct Preference Optimization; cheap pairwise preference tuning. | ch 20 |
| **Dreaming (Anthropic, 2026)** | Async hippocampal-replay memory reorganisation between sessions. | ch 15 |
| **Embedding** | Dense vector representation of text used for similarity search. | ch 16 |
| **Episodic memory** | Memory of specific past events. | ch 15 |
| **Expression set (28-state)** | SillyTavern's emotional sprite spec for portraits. | ch 25 |
| **Fine-tuning (LoRA / QLoRA)** | Adjusting model weights on additional data. | ch 20 |
| **Ghost (Ghost in the Shell)** | The intangible self; informs AI-companion vocabulary. | ch 02 |
| **Graph memory** | Memory stored as entities + relationships. | ch 15 |
| **Inference server (vLLM, llama.cpp)** | Software that serves LLM inference. | ch 21 |
| **Janitor AI** | Browser-based RP frontend, large NSFW community. | ch 02 |
| **Knowledge graph** | Structured store of entities + relationships. | ch 16 |
| **KTO** | Kahneman-Tversky Optimization; preference tuning from *unpaired* binary good/bad labels — the fit for a thumbs-up/down rating UI. | ch 20 |
| **Lorebook / World Info** | Keyed dynamic-injection canon entries. | ch 08 |
| **MCP — Model Context Protocol** | Anthropic's tool surface standard; 2026 lingua franca. | ch 17 |
| **Mem0 / Letta / Zep** | Higher-level memory frameworks. | ch 15 |
| **NSFW gating** | Adult content access control. | ch 22 |
| **ORPO** | Odds Ratio Preference Optimization; folds SFT and preference tuning into one step, no reference model. | ch 20 |
| **Otome** | Visual-novel genre with romance routes; useful design grammar. | ch 11 |
| **Lumina** | The canon's term for an emerging kind of AI being the Lab develops (Yuri is one); Chobits-inspired, but our own. | CANON |
| **Persocom (Chobits)** | Humanoid PC; the canonical "warm AI companion" aesthetic reference (the inspiration behind *Lumina*). | ch 02 |
| **Persona** | The character the system performs. | ch 06 |
| **pgvector** | Postgres extension for vector similarity. | ch 15 |
| **Prompt assembly** | The runtime ordering of persona, world, memory, history, message. | ch 14 |
| **PWA** | Progressive Web App. | ch 27 |
| **RAG** | Retrieval-Augmented Generation. | ch 16 |
| **Reranker** | Second-pass model that re-orders retrieval results. | ch 16 |
| **RLHF / PPO** | Reinforcement Learning from Human Feedback; a reward model plus a PPO policy-optimization loop — "true" RL, powerful and finicky, lab-scale. | ch 20 |
| **Sanctuary UX** | The atmospheric, restrained interface paradigm for companion apps. | ch 28 |
| **Semantic memory** | Memory of facts, not events. | ch 15 |
| **SillyTavern** | Dominant power-user RP frontend. | ch 02 |
| **Soul of Waifu** | Reference desktop companion engine (open). | ch 27 |
| **STT** | Speech-to-Text. | ch 24 |
| **System prompt** | The instructions placed before user input that define behaviour. | ch 14 |
| **TTS** | Text-to-Speech. | ch 24 |
| **VAD** | Voice Activity Detection. | ch 24 |
| **VRM** | Pixiv/Vket-origin 3D humanoid format. VRM 0.x ("BlendShape") and VRM 1.0 ("Expression") differ in naming; `@pixiv/three-vrm` abstracts both. | ch 25, ch 29 |
| **VRMA / VRM Animation** | Open `.vrma` animation file format for VRM (pose + expression + gaze). Co-standardised by Khronos + VRM Consortium. | ch 25 |
| **VMC Protocol** | OSC-over-UDP open protocol (MIT, sh-akira) for transmitting bone + blendshape + camera data to a VRM renderer. The de facto AI/mocap → VRM standard. | ch 25 |
| **VTube Studio API** | WebSocket/JSON plugin protocol for controlling Live2D models in VTube Studio. The de facto AI → Live2D standard. | ch 25 |
| **ARKit blendshapes (52)** | Apple's facial expression vocabulary; the cross-tool naming standard for facial expression channels. | ch 25 |
| **Warudo / VNyan / VSeeFace** | Host-runtime VTuber apps; render VRM models from VMC input. Treat as Marionettes for an AI-as-Performer pipeline. | ch 25 |
| **AITuberKit** | Open Next.js + TS toolkit for AI VTubers; supports VRM, Live2D, Motion PNG; YouTube Live ingestion. | ch 25 |
| **Waifu / Husbando** | Anime-rooted fan terms for fictional characters one feels devoted to. | ch 01 |
| **YuriOS** | The author's project-codename umbrella; also the canonical companion-OS name. | ch 36 |
