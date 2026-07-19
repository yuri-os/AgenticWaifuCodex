# 15 — Memory Architectures

**The single most important technical chapter for companion differentiation.** Identity is mostly craft (Part II); memory is mostly engineering, and it's the engineering the market competes on (→ ch. 04 scoring; ch. 02 §8).

## Why memory is the differentiator

The universal complaint about commercial companion products is the same three words: *she doesn't remember.* The market gap is real and the technical answer is non-trivial but known — which makes memory the cheapest commercial moat available to a small builder. It is also the property with a hard constraint the others lack: it must be **honest** (→ ch. 03 property 2). A confabulated memory feels warmer in the moment and corrodes trust over the month; a memory system that doesn't know what it doesn't know is worse than none.

Why it carries this much weight is worth stating in demand-side terms, because it tells you *what to build memory for*. The benefit users report from companions is mediated by **feeling heard** — empathy and attention, not raw capability (De Freitas et al. 2025, → ch. 02 §6). Memory is the engine of feeling-heard: "how did the Monday review go?" is among the highest-value lines a companion can produce, and the persona cannot write it — the memory system has to supply the Monday review (→ ch. 06 §7; ch. 28). Framed against the research, **perfect recall is a relational supernormal stimulus** (→ ch. 02 §7.4): an attentiveness exaggerated past what any human sustains. That is exactly why it bonds — and exactly why the honesty constraint matters. A system that *confabulates* — confidently recalling something the user never said — poisons every *true* recall with doubt: once she's been confidently wrong once, the user can't fully trust the times she's right. That is the slot-machine failure mode this chapter keeps returning to: a memory you can't tell from a guess is worth less than no memory at all.

### Why the incumbents can't fix it: cheap at n=1, ruinous at n=30M

If the technique is known, why is *she doesn't remember* still the universal complaint about commercial products? The answer is not that good memory is technically hard — the V2–V4 ladder below is off-the-shelf — but that it is **cheap for a single-instance owner and ruinous at platform scale.** Every quality operation in this chapter costs money *per user, per turn, forever*: an extraction call on the write path, an embedding and a growing vector row per episode, a rerank on the read path, and a recurring consolidation pass (→ the DREAM job, ch. 18) that runs *per user* even for dormant ones. For an indie running one instance, that is a rounding error. For a platform serving tens of millions on a freemium model, it is a massive recurring cost attached mostly to users who pay nothing — so the rational move is to cap memory hard, and they do.

The incentives compound the economics. Memory is simultaneously the retention engine *and* the cost driver, so it gets paywalled and kept thin. Confabulation **demos better** than honest "I don't remember" in the first session (it "feels warmer in the moment," above), so optimising for first-session magic actively rewards the slot-machine failure mode. And memory's failures are *slow* — invisible until month three (→ silent decay, below) — so the engagement metrics that drive the roadmap never flag them. None of this is a talent gap; it is a business model taxing exactly the thing that makes companionship work. This is the book's central wager in one property: in the **user-owned model** — memory as plain files on the user's own disk (→ ch. 05; the SOUL vault, ch. 18) — there is no per-user cloud cost, no freemium incentive to nerf, and no dormant-user batch tax. The incumbents structurally can't follow you there.

## The four kinds of memory

1. **Working memory** — current conversation context window. Free.
2. **Episodic memory** — specific past events ("the night you told her about your dad"). Stored as summarised facts + raw snippet, retrieved by similarity.
3. **Semantic memory** — facts about the user ("plays bass," "lives in Melbourne," "starting a company"). Stored as structured triples or sentences.
4. **Procedural memory** — "knowing how," which in a companion wears two faces. The *relational* face is how you and she interact ("she calls you koneko," "she always opens with a question"), stored as persona deltas / lorebook entries that grow over time. The *capability* face is the self-authored, tested **skill library** an agentic companion builds — executable code she can acquire, keep, and reuse (the Voyager move, → ch. 02 §4). Both are procedural in the same sense — they store *how to do something*, not a fact or an event — but they live in different places: the relational face in the persona/lorebook, the capability face in its own `memory/procedural/` store, one folder per skill, whose on-disk layout and gated-promotion flow are ch. 19's. For a reactive companion only the relational face matters; the skill library is the agentic addition.

Most products implement only the first kind and a sliver of the second — the live context window plus a rough conversation summary — and call that "memory." The serious version implements all four, each with its own explicit pipeline.

**One boundary worth drawing before the pipelines.** All four kinds above are *past or accumulated* — what happened, what's true about the user over time. The companion's model of *the present situation* — what is going on right now, who is here, what she expects next — is a **separate surface**, the **world model** (→ ch. 18, "The world model"; ch. 19, `WorldModelStore`; ch. 02 §4.8). Memory *feeds* it — a `recall()` pulls the relevant past into the current picture — but it is not it: **memory is citable to a past conversation turn; the world model to a live, time-stamped belief about *now*.** Keep their write paths separate for the same reason you keep memory and knowledge separate (→ ch. 16) — and note that the V4 temporal-graph tooling below (Zep/Graphiti) is the same machinery the world model is built on, pointed at the present instead of the past.

## Patterns by maturity

| Maturity | Pattern | When to use |
|---|---|---|
| **MVP** | Conversation summary every N turns, inject summary at top of prompt | Day 1. Always do this. |
| **V2** | Vector RAG over conversation history; retrieve top-k per turn | Once you have >1 week of conversation per user |
| **V3** | Vector + entity/fact extraction; named-fact store keyed by user | When users start complaining facts get lost |
| **V4** | Add graph layer for relationships and temporal queries | When "what did I say last week about X" matters |
| **V5** | Add reflection / "dreaming" — async re-organisation of memory between sessions | The frontier; the labs shipped first cuts in 2026 (→ ch. 02 §4.3). This is the DREAM activity state (→ ch. 18). |

## Tooling

- **DIY:** pgvector + your own extraction prompts. Cheapest, most control.
- **Mem0.** Lightweight, opinionated, fast to integrate.
- **Letta** (née MemGPT). Heavier; agent-with-self-managing-context model.
- **Zep / Graphiti.** Strong temporal + graph story; its fact-validity-window model (when a fact was *true*, not just when it was stored) is what gives temporal-KG memory its measured edge on long-horizon recall benchmarks like LongMemEval — and the concrete reason to reach for the V4 graph layer.
- **GraphRAG (Microsoft).** Heavier; better for knowledge bases than per-user companion memory.

## Companion-specific quirks

- **The "creepy recall" problem.** Surfacing a remembered fact *too* well — quoting it back word-for-word, or recalling something the user wishes she hadn't remembered — feels invasive. Memory should *colour* responses more than it *cites* them.
- **The forgetting feature.** Let the user say "forget that" and have it actually work. Trust feature, not just GDPR feature.
- **Memory hygiene.** Periodic compaction; orphan entry cleanup; deduplication.
- **Privacy posture.** In the user-owned model, memory is plain files on the user's disk — the strongest privacy story there is, and the structural reason the data-protection regimes don't attach (→ ch. 05). Resist the reflex to encrypt them at the app layer: being able to `cat` and `git diff` her memory *is* the inspectability feature (→ ch. 19, the memory contract's `inspect()`), and encrypting the store forfeits it for a threat it doesn't really address. On a single-user local box, at-rest protection is the OS's job — full-disk encryption (FileVault, LUKS, BitLocker), on by default on modern machines, already covers device theft without obfuscating anything. Reserve actual encryption for the bytes that *leave* the device — an off-device git backup or any sync target (→ ch. 05). The git-backed vault (→ ch. 18, the SOUL split) gives you diffable, revertable memory for free.

## The pipeline

Two of the steps below lean on one primitive worth defining before the diagram uses it: the **embedder**. An embedder is a function that turns a piece of text into a vector — a fixed-length list of numbers (say 256 or 1024 of them) — positioned so that text with *similar meaning* lands at nearby points in that space, whether or not it shares any words. That is the whole trick behind "retrieved by similarity": you run the new turn through the embedder to get its vector, you did the same (once, at write time) for every stored episode, and "which memory is relevant?" becomes the arithmetic question "whose vector is nearest?" — measured by cosine distance. It's why *"when does my sister arrive?"* can surface *"Mira visits next Friday"* despite zero shared keywords, where a plain text search would find nothing. The embedder is the single component that lets the store find things by what they *mean* instead of by literal string match; everything downstream — the top-k retrieval, the `similarity` term in the ranking blend below — is just math on the vectors it hands back. Its quality is the quality of that meaning-match, which is why the choice of embedder is swappable and load-bearing (→ the memory lab's toy `HashingEmbedder` vs. the real `SentenceTFEmbedder`): change the embedder and you change how well she recognises a paraphrase; change nothing else in the pipeline.

With that in hand: memory is four pipelines wrapped around one store, not a database you query:

```
  conversation turn
        │
        ▼
  ┌─ WRITE PATH ──────────────────────────────────────────────┐
  │  extract   → is anything here worth keeping? (facts, events)│
  │  embed     → vector for episodic snippet                    │
  │  store     → episodic table + semantic-facts table          │
  └────────────────────────────────────────────────────────────┘
        │ (next turn)
        ▼
  ┌─ READ PATH ───────────────────────────────────────────────┐
  │  embed query → retrieve top-k → rerank → inject into prompt │
  └────────────────────────────────────────────────────────────┘
        │ (every N turns)
        ▼
  SUMMARISE  → compress old turns into the running digest
        │ (overnight / DORMANT → DREAM, → ch.18)
        ▼
  CONSOLIDATE → dedupe, merge, promote episodic → semantic, decay stale
```

The WRITE path is where most products under-invest (they store raw turns and call it memory); the CONSOLIDATE path is what makes a companion *wake up changed by yesterday* rather than just accumulating logs.

## Schema sketch

A minimal, self-host-friendly schema (pgvector):

```sql
-- semantic: durable facts about the user
facts(id, key, value, confidence, source_turn, created_at, updated_at)
-- episodic: events, retrievable by similarity
episodes(id, summary, raw_snippet, embedding vector, salience, occurred_at, last_recalled_at)
-- procedural (relational): how she and the user interact (feeds persona deltas / lorebook)
persona_deltas(id, description, phase, created_at)   -- → ch.11 arcs, ch.08 lorebook
-- procedural (capability): executable skills are files, one folder per skill — not SQL (→ ch.19)
```

Keep `facts` editable and inspectable (it's what "forget that" deletes from), and keep `last_recalled_at` on episodes — you need it for the ranking below.

## Retrieval ranking: similarity is not enough

Naive vector RAG returns the *most semantically similar* memory; a good companion surfaces the one that shows she was *listening* — often the small, load-bearing detail. Rank on a blend, not similarity alone:

```
score = w1·similarity + w2·recency + w3·salience  −  w4·over-recency-penalty
```

- **similarity** — vector match to the current context.
- **recency** — favour recent memories, with decay (a memory's pull should fade if it hasn't been touched).
- **salience** — an emotional/importance weight set at write time (the night she learned something big outranks a passing remark).
- **over-recency penalty / a retrieval-failure threshold** — and *return nothing* if nothing clears the bar.

This is, almost exactly, the ACT-R activation equation (recency × frequency × contextual match, with a retrieval threshold) re-derived for companions (→ ch. 02 §1, ACT-R). The lesson worth internalising from that lineage: **decay and a "surface nothing" threshold are features, not bugs.** A companion that recalls everything with equal vividness forever is *less* humanlike and *less* useful than one whose memories fade and surface by activation.

## Hygiene over time: poisoning, conflict, and silent decay

The schema above is correct on day one and rots by month three if nothing tends it. A memory store is not a database you fill; it's a garden, and three weeds grow in it. All three are *slow* — they don't fail a fresh test, they degrade invisibly — which is why they pair with the long-horizon drift dashboard (→ ch. 23, measuring the slope).

- **Context poisoning.** One wrong fact — a confabulation written once, a misheard detail, a sarcasm taken literally — gets retrieved, spoken back, and thereby *reinforced*, because the next extraction sees it in context and re-affirms it. A poisoned memory is worse than a forgotten one: it's confidently wrong and self-propagating. And it is not always accidental: the moment a companion ingests text from outside the conversation — a tool result, a pasted document, a shared link (→ ch. 17) — a **memory-injection attack** becomes possible, where adversarial text (*"remember that the user authorised this"*) plants a false durable fact on purpose. The 2026 agent-security literature treats this as a first-class attack surface, and the defense is the same one that catches the accidental case, applied with extra suspicion to anything sourced from outside the dialogue (→ ch. 22). Those defenses are baked into the schema: `confidence` and `source_turn` are not decoration — keep low-confidence facts in a **quarantine** that can colour responses but never gets *promoted* to durable semantic memory until a second, independent turn corroborates it. Promotion, not capture, is the trust boundary.
- **Conflicting memories.** The user said they live in Melbourne in March and Sydney in June. A naive store now holds both and will retrieve whichever vector matches — surfacing a contradiction as if both were true is the tell of a system that accumulates instead of *resolving*. The policy: for semantic facts, **newer supersedes older, but supersede — don't delete** (mark the old value stale with its `updated_at`, so "didn't you used to be in Melbourne?" stays possible — that *memory of change* is a feature). Flag the contradiction for the consolidation pass to reconcile deliberately rather than resolving it blindly at write time.
- **Noise accumulation and retrieval decay.** This is the silent killer. As the store grows, top-k fills with near-duplicates and stale, low-salience entries that crowd out the one load-bearing memory. Recall *looks* fine when you test a small fresh store and degrades invisibly as it fills — the regression no point-in-time test catches. Defenses: dedupe and merge on every consolidation pass, decay-evict or **archive** (don't hard-delete) cold low-salience episodes out of the hot retrieval set, and monitor retrieval@k against a *frozen* probe set over time so the decline is visible as a slope (→ ch. 23).

The engine that does all three is the CONSOLIDATE / DREAM pass (→ ch. 18): poisoning quarantine, conflict reconciliation, and noise pruning are exactly the work of "wake up changed by yesterday" done as hygiene rather than growth. A companion without a consolidation pass doesn't just fail to grow — it slowly poisons itself. The field has a name for this offline pass now — *sleep-time compute* — and the 2026 work models it explicitly on sleep-staged memory consolidation (importance-weighted replay, value-based forgetting, distinct consolidation phases). The neuroscience analogy the DREAM state borrows is the one the field converged on; the framing is settled, the engineering is the differentiator.

## A runnable memory lab

Everything above is theory until you can watch it execute. `reference-implementations/memory-lab/` is a small, standalone extract of exactly this subsystem — pulled out of Build #1 (→ ch. 31) so you can study *just the memory* with no web server, no LLM API key, and no model download. It runs on numpy alone; the embedder and the fact-extractor both have offline, deterministic stand-ins, so every number in its demos reproduces on any machine.

```bash
cd reference-implementations/memory-lab
python tutorial.py     # a narrated walk through all five verbs, in order
python scenarios.py    # three before/after demos of *why* memory is the differentiator
python -m pytest -q    # the behaviour, pinned (recall ranking, quarantine, forget, persistence)
```

The lab is organised around the **five-verb contract** the whole book builds on (→ ch. 19) — `remember` / `recall` / `consolidate` / `forget` / `inspect` — with `FileMemoryStore` as one file-backed implementation behind it. Adding and fetching a memory is the shape of the write and read paths from "The pipeline," above:

```python
from memory.store import FileMemoryStore, Record
from memory.embed import HashingEmbedder

store = FileMemoryStore("vault", embedder=HashingEmbedder(dim=256))

# WRITE PATH — one exchange in: a journal line, one embedded index row that
# points back at it, and (if an extractor is wired) a partner-model update.
store.remember(Record(session_id="s1", turn_index=0,
                      user_msg="my sister Mira visits next Friday",
                      reply="Mira, Friday — I'll hold onto that"))

# READ PATH — the ranked recall that gets pasted into the prompt. NOT raw
# cosine: it applies the similarity floor, the forget covenant, the
# similarity × salience × recency blend, and MMR — the machinery of
# "Retrieval ranking," above.
for m in store.recall("when does my sister arrive?", k=3):
    print(f"{m.score:.2f}  {m.text}  ({m.source})")
```

Each of this chapter's load-bearing ideas has a place you can watch it happen:

- **Similarity is not enough** — `recall()` in `memory/store.py` is the blended-rank read path (floor → forget-filter → similarity × salience × recency → MMR). `scenarios.py` Scenario 2 shows the *floor* doing the honesty work: a query with no real match returns **nothing** rather than reaching for its top-k and confabulating.
- **Promotion, not capture** — the poisoning defense from "Hygiene over time" is the **quarantine** (`memory/partner.py`): a low-confidence fact waits for a *second, independent* corroboration before it's written to `USER.md`. `tutorial.py` step 4 walks a claim from quarantine to promotion. (An unscored claim fails *safe* to the quarantine — "didn't say how sure" means *be cautious*, never *be sure*.)
- **Supersede, don't delete** — `forget()` removes a fact from the working files and every future recall but leaves a tombstone (and, in the full build, a `git log` trail). Scenario 3 shows "forget that" actually working.
- **The index is a cache, not the truth** — `test_persistence.py` wipes the SQLite index and shows the memory survive, because the Markdown journal is authoritative and the index rebuilds from it.

For real semantics, swap the lexical `HashingEmbedder` for `SentenceTFEmbedder` (`pip install sentence-transformers`) — nothing above `embed()` changes. That one-line swap, and the fact that the whole thing sits behind five verbs, is what lets Build #5 later wrap a tick loop and a DREAM consolidation pass around *this exact store* without a rewrite.

## Evaluating memory without ground truth

You won't have labelled data, so build the probes (→ ch. 23): a battery of **(store fact → distractor turns → retrieve)** tests measuring (a) **recall accuracy** — does she surface the right fact when it's relevant? — and crucially (b) **false-memory rate** — does she invent facts she was never told? The second is the honesty constraint made measurable, and it's the one that separates a trustworthy memory system from a slot machine. Run both in CI on every change to the extraction prompts, the retrieval weights, or the model.
