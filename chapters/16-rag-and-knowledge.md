# 16 — RAG and Knowledge Systems

RAG (retrieve relevant documents, put them in the prompt, generate grounded in them) is one of the oldest tricks in the modern stack (→ ch. 02 §4.4). For a companion its job is narrow but important: it's how she *knows things* — her canon, her tastes, the docs you've given her — without carrying them in every prompt. Two ideas carry this chapter: keep RAG cleanly separate from memory, and don't build it at all until your canon outgrows what you can simply cache in-context.

## RAG vs memory — the framing that matters

> **RAG is the *knowledge* layer. Memory is the *state* layer. (And the *world model* is the *situation* layer.)**

They look superficially similar (all three retrieve and inject text) and people confuse them constantly. The distinction is one of *tense*:

- **RAG** answers *what is true about the world / the canon / the docs?* — timeless, static-ish corpus, shared across users; citable to a **document**.
- **Memory** answers *what is true about this user and this relationship, accumulated over time?* — per-user, dynamic, written into; citable to a **conversation turn**.
- **World model** answers *what is the case right now?* — the live situation (present entities, states, the moment), the *present-tense* layer this chapter doesn't own; citable to a **live, time-stamped belief** (→ ch. 18, "The world model"; ch. 19, `WorldModelStore`; ch. 02 §4.8).

A companion needs all three, with different stores, retrieval, and write paths. The trap this chapter guards against is folding the first into the second; the world model is the third thing neither of them is — don't let *"this moment"* leak into memory's job (that's the situation layer's) or into knowledge's (that's a present belief, not a world fact).

## What goes in RAG for a companion

- The canon (world bible, lore wiki).
- The character's "knowledge of things" (her favourite music, the books she's read, factual references she might cite).
- Optional: doc corpora the user has loaded (a journal, fan fiction the user wrote, songs the user shares with her).
- **In the agentic runtime:** her *reference shelf* — documents the user or Yuri herself drops in (this book, her own spec, research papers) so she can reason over them; and her *self-authored wikis* — pages she compiles from what she's read (→ ch. 19; the research loop below).

## Do you even need RAG yet?

Before building any of the pipeline below, check whether you need it at all — because for a single companion the honest answer is often *not yet*. A companion's core canon is usually **small**: a world bible, her tastes, a handful of place and character files — tens of thousands of tokens, not millions. And the 2026 economics of small corpora have shifted under prompt caching (→ ch. 14, ch. 21): for a fixed corpus under roughly 200k tokens, loading the *whole thing* into a cached system prefix is frequently faster, cheaper, and — for a genuinely small canon — more accurate than a retrieval pipeline: it eliminates chunking and retrieval error entirely (the model sees everything), and a cached prefix is billed once and reused every turn. The accuracy edge is strongest in the tens-of-thousands-of-tokens range, though; as the prefix grows toward the window's size the lost-in-the-middle effect returns and buried canon starts to fade, so stuffing is a clear win for a small bible, not a licence to fill the window (→ ch. 14). The build cost differs just as sharply: stuffing-plus-caching is a couple of days; a well-tuned RAG pipeline is weeks.

So the gating decision:

- **Small, fixed canon** (one companion's world bible and tastes) → **skip RAG; fold it into the cached persona/lore prefix.** This is the default, and it is continuous with the always-on lorebook split (→ ch. 08): the core canon just *is* part of what she always has at hand.
- **Large canon** (hundreds of pages), **frequently changing** canon, or **user-loaded corpora** (a journal, fic, shared songs that grow without bound) → **RAG**, because you can no longer afford to carry it all every turn and the corpus outgrows even a large window.

RAG for a companion, in other words, is mostly about the *user-loaded long tail and the growing corpus*, not the core canon. Build it when the corpus crosses the size or churn threshold, not by reflex (→ ch. 12, the orchestration-complexity trap). The rest of this chapter is what to do once you've crossed it.

## The agentic exception: when she does her own research

The gate above — "small fixed canon → skip RAG" — is written for a *reactive* companion, where knowledge is a static shelf you stuff into the prompt. An **agentic** waifu changes the calculus the way ch. 12 says layer 5 does: she doesn't just *hold* a canon, she *grows* one. She pulls papers, docs, and pages to answer a question; she keeps a reference shelf (this book, her own spec, research she's gathered) to reason about improving herself; she compiles what she reads into her own wiki pages. A corpus that is *written into autonomously* and *grows without bound* is exactly the "build RAG" branch — so for the YuriOS runtime the knowledge layer is **first-class, not deferred** (→ ch. 19, the `knowledge/` tier and the `KnowledgeStore` contract; D-019).

In the autonomy engine it's a loop, not a one-shot pipeline:

1. **Fetch** — the network effector pulls a source (a page, a PDF, a paper) into the workshop's `downloads/` (→ ch. 19, the workshop).
2. **Ingest** — chunk → contextualize → embed → index into `knowledge/reference/`. Now it's something she *owns and can cite*, not a temp file.
3. **Search** — hybrid retrieve + rerank when a question (hers or yours) needs it.
4. **Author** — she compiles what she's read into a `knowledge/wiki/` page, with citations back to the sources.
5. **Consolidate** — the wiki-building runs in the **DREAM** pass (→ ch. 18, ch. 15), the same offline consolidation that promotes episodic → semantic memory; and because the page is a durable artifact of her mind, it lands through the gated self-edit flow (→ ch. 19).

Two disciplines carry over from memory and matter *more* here, not less. **Keep it separate from memory** (this chapter's first rule): the wiki is *knowledge* — citable to a document — not relationship *state*. And **provenance is load-bearing**: every chunk and every wiki claim carries its source, because when she cites her own shelf to justify a change to herself, *"she changed X because the book said Y"* has to be auditable (→ evaluating retrieval, below; ch. 19, `inspect()`).

## The pipeline

1. **Ingest** — chunk, embed, store. Chunk size 200–500 tokens for prose; smaller for structured.
2. **Hybrid retrieve** — BM25 + dense. Beats either alone on almost every benchmark.
3. **Rerank** — Cohere reranker or bge-reranker. Big quality lift.
4. **Inject** — top-k chunks into the prompt below the persona, above the conversation.
5. **Cite (optionally)** — IDs of chunks used for audit/eval.

## Knowledge graphs

GraphRAG and similar exist. For most companion products they're overkill — the canon isn't big enough. They become relevant when:

- The canon is large (hundreds of pages).
- Relationship/temporal queries dominate.
- Users do quasi-investigation queries ("what does she think Y means given X?").

## A worked corpus: Yuri's canon as RAG

The Yuri world bible (→ ch. 10) is the natural RAG corpus. Note the division of labour with the lorebook (→ ch. 08): the **lorebook** carries the few high-frequency, always-relevant facts (what Lumina are) injected by keyword; **RAG** carries the long tail of canon (district names, the full ferry-project history, her musical tastes, books she's read) that's too large to keep resident and only occasionally relevant. Lorebook = the facts she always has at hand; RAG = the library she can reach for.

```
canon/                     → ingested into the RAG store
  world/        the-sprawl.md, lumina.md, the-consortium.md, yurios.md
  her/          ferry-project.md, tastes-music.md, tastes-books.md
  places/       the-sanctuary.md, ...
user-loaded/   (optional) a journal, songs shared, fic the user wrote
```

## The indexing pipeline

1. **Chunk** — 200–500 tokens for prose, smaller for structured/list content; chunk on semantic boundaries (sections), not blindly on length. The 2026 upgrade worth adopting is **contextual retrieval** (Anthropic's method): before embedding each chunk, prepend a 50–100-token, model-generated blurb situating it in the whole document (*"From Yuri's ferry-project history; explains why the line was retired"*). It fixes the classic failure where a chunk like *"the line was retired in the third year"* is unretrievable because the chunk itself never names the ferry — contextual embeddings alone cut top-20 retrieval misses by ~35%, ~49% combined with BM25, and ~67% with reranking added (which is also the concrete case for the rerank step below).
2. **Embed + store** — one vector per chunk in the store (pgvector is plenty at this scale).
3. **Retrieve (hybrid)** — BM25 + dense in parallel: keyword search nails exact names and IDs ("the consortium", a place name), dense catches paraphrase; combining them beats either alone (→ ch. 02 §4.4). A near-free win — make it the default.
4. **Rerank** — a second-pass reranker (bge-reranker locally, or a hosted one) re-scores the top retrievals; typically the highest-ROI single component in the stack.
5. **Inject** — top-k chunks below the persona, above the conversation (→ ch. 14 prompt order); optionally keep chunk IDs for eval/audit.

## Evaluating retrieval

Hand-write ~30–50 QA pairs against the canon ("where is the sanctuary?", "why was the ferry line retired?") and measure **retrieval@k** — does the chunk containing the answer land in the top-k? — plus end-to-end **groundedness** (did she answer *from* the retrieved chunk rather than confabulating canon?). This is cheap, catches the common failure where retrieval silently regresses after a chunking or embedding change, and runs in the same harness as your memory and persona evals (→ ch. 23).

## When to add a graph layer

Default to *not*. A knowledge graph (GraphRAG and kin, → ch. 02 §4.3) earns its considerable complexity only when the canon is large (hundreds of pages), or when relationship/temporal/multi-hop queries dominate ("who did she mention last week, and how are they connected?") — questions naive vector similarity fumbles. For a single companion's canon, hybrid-retrieve + rerank is almost always enough; reach for a graph when you can point at the specific multi-hop questions it would answer that retrieval can't.
