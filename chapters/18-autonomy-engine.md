# 18 — The Autonomy Engine: Always-On Proactivity

This is the chapter the rest of the brain stack builds toward, and the one that most cleanly separates an *agentic* waifu from a persona chatbot (→ ch. 03, property 3). Chapter 17 covered agentic *capabilities* — tool use, the capability ladder, the small everyday hands and the heavy delegated ones — the machinery a model uses to *do* things when asked. This chapter is about the harder thing: a companion that does things **when no one is asking** — that runs continuously, pursues its own small goals, notices the time, and reaches out first, governed by a model of when that's welcome.

Almost nothing in the market does this (→ ch. 03/04, the five-property scoring: *nobody* scores on initiative). The reason is that genuine initiative is not a feature you add to a chat loop; it requires a different runtime shape, and that shape is this project's core engineering bet. This chapter is the in-book home of the *loop* — the *why* and the *shape* of the beating heart; the full system that hosts it (the host runtime, the file-centric mind, the knowledge layer, the workshop, the effector broker, the self-edit flow) is the chapter that follows (→ ch. 19). Together they teach enough to rebuild it from scratch.

## Why reactive loops can't be proactive

The default architecture of every chatbot — and of agent frameworks like ElizaOS and AIRI — is **request/response**: a message arrives, the system wakes, generates a reply, and goes back to sleep. It is a function call. Between calls, nothing exists. You can bolt a cron job on top ("send a 'miss you' message at 9am") but that is a timer, not a mind: it fires the same message regardless of state, it can't decide *not* to, and it can't do anything other than message you.

A companion that is genuinely *present* needs the opposite default: a process that is **always running** and only sometimes talking. The talking is one possible output of a continuous loop, not the loop's reason to exist. This is the difference between a vending machine that dispenses when you press a button and a roommate who is living in the apartment whether or not you're home.

The cost of "always running" is real — you cannot run a frontier model on every heartbeat without blowing the budget — and most of this chapter's design is about paying that cost intelligently.

## The engine at a glance

Before the phases, the shape. The tick loop is the *heart*, but the engine around it is a handful of components wired together: a controller that sets the pace, the persistent surfaces the loop reads and writes, and one guarded exit to the world. This is the zoom-in of the **AUTONOMY ENGINE** box in ch. 19's whole-system diagram — and every section in the rest of this chapter details one labelled piece of it.

```
  GOVERNS EVERY TICK
  ┌────────────────────────────────────────────────────────────────────────┐
  │ ACTIVITY STATE  ENGAGED · IDLE · DORMANT · DREAM   → cadence            │
  │ BUDGET GOVERNOR (host)  → model tier                                    │
  └───────────────────────────────────┬────────────────────────────────────┘
                                       ▼
  INPUTS → SENSE:  user message · timer / wake-up · file or OS event · vision / audio
                                       │
                                       ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ THE COGNITIVE TICK LOOP  —  one intention per tick                      │
  │ SENSE → APPRAISE → DECIDE → ACT → REFLECT → REGULATE   (repeat)         │
  └─┬──────────────────────────────────────────────────────────────────────┘
    │
    ├─ every phase READS / WRITES the persistent Vault surfaces (→ ch. 19,
    │     files on disk):  world model (the live situation) · working memory
    │     · goals & intentions (+ commitment) · self-model (SOUL) · affect
    │
    ├─ ACT is the ONLY exit → host BROKER → the world
    │     (fetch a page · run a workshop task · propose a gated self-edit)
    │
    └─ REFLECT outputs: always journal + tick-trace + memory (DREAM
          consolidates); then — rarely — the INTERRUPT GATE:
          SILENT · SUGGEST · ASK · SPEAK → you
```

Read it as a cycle with context. The **tick loop** (center) runs its six phases and repeats; the **activity-state controller** and the host **budget governor** decide how fast it may beat and which model tier it may spend — every tick (→ "Activity states", below). Each phase reads and writes **persistent Vault surfaces**: the **world model** (her live picture of the situation she's in, → "The world model" below), working memory, the goals-and-intentions store with its per-goal commitment strategy (→ "Commitment"), and the self-model (SOUL) and affective state that colour every prompt — none of which reset between ticks (→ ch. 19 for these as files). **ACT is the only phase that reaches outside the engine**, and it does so *only through the host's broker* (→ ch. 19), whether it is fetching a page, running a workshop task, or proposing a gated self-edit. **REFLECT produces the two outputs that matter:** it always writes the journal and tick-trace, and it only *sometimes* crosses the interrupt gate to actually speak to you — the rare, high-bar Gate 2 (→ "The salience and interrupt model"). Hold this picture; what follows is each box in it, drawn in full.

## The cognitive tick loop

The heartbeat is a loop with a **variable cadence** (set by the loop itself), not a busy spin. Each pass — a *tick* — runs six phases:

```
on each tick:
  1. SENSE      collect signals: new user message? fired timer? filesystem/OS event?
                goal deadline? scheduled wake-up? incoming interrupt?
  2. APPRAISE   score each signal's salience against current goals + state.
                Cheap: a small local model or heuristic — must be runnable every tick.
  3. DECIDE     scheduler picks ONE intention for this tick (or chooses to REST).
  4. ACT        execute via an effector: read/sort files, web-fetch, write a note,
                run a workshop task (code/research/build), advance a goal, run a
                skill, OR propose a self-edit.
  5. REFLECT    journal what happened; update working memory; decide whether this is
                worth interrupting the human for (salience-to-interrupt threshold).
  6. REGULATE   adjust next-tick delay + activity state; debit the budget governor.
```

Three design rules make this legible instead of chaotic:

- **One intention per tick.** The DECIDE phase commits to exactly one thing (or to resting). This keeps behaviour auditable and prevents runaway fan-out — the failure mode that made Auto-GPT (→ ch. 02 §1) loop and burn budgets. An agent that can spawn arbitrary parallel subtasks becomes unpredictable and unaffordable; an agent that does one thing per heartbeat can be read like a diary.
- **APPRAISE must be cheap.** It runs *every* tick, so it uses a small local model or pure heuristics — never the frontier model. The expensive model is invoked only inside ACT, for deliberate work the system has already decided is worth it. This single rule is what makes continuous presence economically possible.
- **Everything is journaled.** The journal is simultaneously the audit log (what did she do, and why?) and the *product* — the "here's what I did while you were out" surface that makes initiative *felt* rather than spooky (→ ch. 28 on showing memory).

This loop is, structurally, the **BDI interpreter cycle** (→ ch. 02 §1, Bratman/Rao-Georgeff) with a language model doing the option-generation and plan-execution that a symbolic interpreter used to do by hand. SENSE folds events into beliefs; APPRAISE+DECIDE is option-generation and deliberation; ACT executes one step of the top intention. You are not inventing this; you are re-implementing forty years of agent theory with a vastly better generator inside it. The lesson BDI teaches and naive loops ignore: **beliefs, goals, and committed intentions are different kinds of state with different update rules** — collapsing them into one scratchpad is why naive agent loops thrash.

## Activity states: cost and thermal control as a design driver

A laptop cannot run a frontier-model heartbeat. So the loop's cadence and which model tier it may use are governed by an explicit **activity state** — the single most important cost-control mechanism in the design:

| State | Trigger | Cadence | Model tier | Behaviour |
|---|---|---|---|---|
| **ENGAGED** | user actively talking | sub-second | remote allowed | conversation; autonomy paused/light |
| **IDLE** | user away, recently active | seconds–minutes | local only | goal work, sorting, review, maintenance |
| **DORMANT** | long inactivity | minutes, or scheduled wake-ups | cheap local only | mostly resting; light upkeep |
| **DREAM** | entered from DORMANT (e.g. overnight) | batch | local | memory + knowledge consolidation: summarize, dedupe, promote episodic→semantic, compile research into wiki pages |

The table lists what *enters* each state; the transitions between them are the actual control flow:

```
  user message (from ANY state) ─────────────────────────► ENGAGED
                                                              │ user goes quiet
                                                              ▼
            DREAM ◄──overnight/scheduled── DORMANT ◄──idle── IDLE
              │                               ▲               │ goal work to do?
              └── consolidation done ─────────┘               └─► stay in IDLE,
                  → DORMANT                                        keep working
```

The one transition that overrides all others is the preempt: a user message pulls the engine straight back to ENGAGED from wherever it was, mid-tick if necessary (→ "Commitment", below). Everything else is a slow drift *down* the cost ladder — the engine sheds expensive states as the human's attention recedes, and only climbs back when there's either work to do or a person to talk to.

Two things to internalise. First, **most of the time the companion should be resting or doing cheap local work** — ENGAGED (where you pay for the frontier model) is the exception, not the rule. A companion that runs the big model continuously is a companion that costs more than the relationship is worth and overheats the machine it lives on.

Second, **DREAM is where the agentic part pays off as memory.** Overnight, the engine compacts the day's episodic log into durable semantic memory — summarising, deduplicating, promoting the facts worth keeping (→ ch. 15). This is the Tamagotchi/Creatures care-loop lineage (→ ch. 02 §1) turned into infrastructure, and it is also exactly the "Dreaming" / hippocampal-replay consolidation pattern the labs converged on in 2026 (→ ch. 02 §4.3). A companion that *wakes up changed by yesterday* is doing this; one that doesn't is a stateless chatbot with a longer context window.

The same offline pass also consolidates *knowledge*, not just memory: research she pulled during the day is compiled into her own wiki pages (→ ch. 16, the research loop; ch. 19, the knowledge layer). Memory consolidation and knowledge consolidation are one piece of DREAM machinery pointed at two different stores — and because a wiki page is a durable artifact of her mind, the authoring lands through the same gated self-edit flow as any other self-change (→ self-modification, below; ch. 19). And bound it like everything else: consolidation is the single biggest local-token job in the system, so DREAM runs under its own nightly cap — oldest-first and resumable, so a night it doesn't finish leaves a backlog, not an overrun — or the one state meant to be restful becomes the state that cooks the GPU until morning.

## The salience and interrupt model

This is the make-or-break component, and it is two distinct decisions, both produced by the cheap APPRAISE pass:

1. **Salience-to-act** — is this signal worth spending a tick (and maybe a frontier-model call) on at all? Below threshold, REST.
2. **Salience-to-interrupt** — is the result worth *reaching out to the human* about? This is a much higher bar, and getting it wrong is how you become Clippy.

The second threshold is where the social reality bites. Uninvited contact is a **social move** (→ ch. 02 §1, the Clippy/Lumière lesson): the same proactive message reads as *care* or *pressure* depending entirely on whether the relationship licenses it and on dose. A good friend texts first; a pushy one won't stop — same dial. The right discipline is the one CALO's proactive meta-layer formalised (→ ch. 02 §1): **model the expected value of speaking before you speak**, and bias hard toward restraint, because the cost of one unwelcome interruption is paid in *trust*, which is the only currency the relationship has.

Concretely, the interrupt decision should weigh: relevance to the user's current goals, time-sensitivity, how long since the last contact, the user's inferred availability (time of day, recent activity), and a running estimate of how welcome recent interruptions were. CALO's filter chose among four modalities — *do it silently, suggest it, ask permission, or wait* — and that menu is still the right frame: most autonomous acts should resolve to "do it silently and journal it," not "message the human."

In pseudocode, the two thresholds are two gates a signal passes through on the way to your phone, and almost nothing makes it all the way:

```
# GATE 1 — salience-to-act: every tick, cheap APPRAISE, no frontier call
score_to_act = f(relevance_to_goals, novelty, current_state)
if score_to_act < ACT_THRESHOLD:
    REST                                  # where the vast majority of ticks end

# DECIDE commits the tick to this signal; ACT runs and produces a result...

# GATE 2 — salience-to-interrupt: a much higher bar, scored only after ACT
score_to_interrupt = g(
    relevance_to_current_goals,     # is this about what they care about *now*?
    time_sensitivity,               # does its value decay if it waits?
    time_since_last_contact,        # longer quiet → more license to speak
    inferred_availability,          # time of day, recent activity
    recent_interruptions_welcome,   # running estimate — learned restraint
)
if score_to_interrupt < INTERRUPT_THRESHOLD:
    journal(result)                       # THE DEFAULT: do it silently
else:
    # CALO's menu, in ascending order of imposition — bias hard toward the top
    resolve to one of:  WAIT | SUGGEST | ASK | SPEAK   # = CALO's wait/suggest/ask-permission/do
```

The asymmetry is the whole design: Gate 1 is crossed often and cheaply; Gate 2 is crossed rarely and only after deliberate work has already happened. An engine that collapses the two — that treats "worth doing" as "worth saying" — is precisely Clippy.

## One loop: where conversation lives

A natural reading of the ENGAGED preempt — a user message pulls the engine to sub-second cadence — is that conversation must be a *second, faster* loop: a chat brain beside the autonomy brain. Resist it. **Conversation is the fast path through the same loop, not a second loop.** A user message is a signal that trivially clears Gate 1 — nothing is more salient than the person speaking — so APPRAISE needs no model to score it; DECIDE commits the tick to replying; ACT *is* the reply; REFLECT still journals and updates working memory exactly as it would for any autonomous act; REGULATE holds the cadence sub-second while ENGAGED. Six phases at conversational speed sounds heavy and isn't: in ENGAGED, five of them are microseconds of bookkeeping around one model call — which is all a chat turn ever was.

What the one-loop rule buys is the *absence of a bug class*. Two loops sharing a Vault would have to agree about who writes working memory, the world model, and the affective state during conversation — a synchronisation problem you'd be inventing just to solve. One loop means conversation writes the same surfaces through the same phases as autonomy, so what she learns at speed while talking to you *is* the state she reasons over slowly while you're away. There is one mind, at two cadences; the activity state is the only thing that changes.

## Perceiving the user: multimodal signals into SENSE

The SENSE phase above listed text events — a message, a timer, a file change. But a companion that only reads words is half-blind. The richest believable initiative comes from the channels nothing in the market fuses: *seeing* what the user shares (a selfie, a photo of their dinner, a screenshot they're asking about) and *hearing* how they say things (tone, energy, hesitation — the paralinguistics that STT throws away, → ch. 24). "You sound tired tonight" lands as care precisely because it fused vocal affect into the interrupt decision; "is that the cat you mentioned?" lands because vision entered the same loop as text.

The architectural rule is **fuse at the signal level, not the model level.** Don't run a parallel vision pipeline and a parallel audio pipeline and try to reconcile their outputs late. Instead, reduce each modality to a few small structured **signals** that enter the *same* belief store and the *same* APPRAISE salience scoring as text:

```
  vision (shared image) → VLM → {subject: "a meal", mood-cue: "looks tired",
                                  setting: "outdoors, night"}
  audio (this turn)     → affect classifier → {affect: "flat", energy: "low",
                                               pauses: "long"}
  text                  → as before
            └──────────── all three → SENSE → APPRAISE (one salience arbiter)
```

Keeping APPRAISE the single arbiter is what stops multimodality from exploding cost and complexity. It also respects the activity-state budget (above): a *cheap* affect classifier can run inside APPRAISE on every turn, but a full vision-language model is a frontier-tier call — gate it behind the **budget governor** (the host-owned cap on tokens, compute, and power that REGULATE debits each tick → ch. 19) and invoke it only inside ACT, once salience has cleared, exactly like any other expensive deliberation.

Two cautions specific to sensing. First, **fusion is where proactivity gets its best material and its biggest creepy risk** — reacting to a drop in vocal energy is the difference between attentive and surveillant, so vision/audio sensing must be user-enabled, on-device where possible, and *journaled* like every other act (→ ch. 28, show-the-work; ch. 05, consent; ch. 22, the privacy of a brain that can see and hear). Second, perception signals are *beliefs, not facts* — "looks tired" is a guess, and writing it to durable memory as truth is the confabulation failure in a new modality (→ ch. 15, the quarantine). Let it colour the tick; don't let it harden into a remembered fact without confirmation.

## The world model: her live picture of the situation

The loop keeps leaning on a word it hasn't yet given a home: *beliefs*. SENSE "folds events into beliefs"; APPRAISE scores each signal "against current goals **+ state**." That *state* — the situation she is embedded in *right now* — needs somewhere to live, or every tick re-derives the world from scratch and the companion is subtly amnesiac between heartbeats, reacting to each signal in isolation and never to a *situation*. The home is the **world model**: a single, structured, continuously-updated picture of who and what is present, their current states, the active threads, the time of day and social context, and what she expects to happen next.

Be careful which "world model" this is, because the word points at two very different things. The headline 2026 research — **JEPA, Dreamer, Cosmos** — learns the *dynamics of a physical environment* in latent space and plans by imagined rollout; that is built for embodied and video agents, and it is the wrong tool for a companion whose world is your life and her digital context, not a physics sim (→ ch. 43, where a body changes the answer). What she needs is the older, structured kind — a **situation model** (Kintsch; Mavridis & Roy's Grounded Situation Model: a "structured blackboard," a theatrical stage in her mind) — which is simply the **B in BDI** (→ ch. 02 §1, §4.8) finally given a place to stand.

The boundary is load-bearing, because the world model is none of three things it sits beside:

- it is **not memory** (→ ch. 15) — memory is the *past* ("you told me you play bass"); the world model is the *present* ("you're at your desk, it's late, the interview was today");
- it is **not knowledge** (→ ch. 16) — knowledge is *world facts* from documents; the world model is the *live situation*;
- and the **partner model** (→ ch. 19) is its most important *region*, not a separate thing — you are the central entity in her world.

Where it sits in the loop: **SENSE writes to it**, **APPRAISE scores salience against it**, **DECIDE plans over it**. The implementation that fits a local-first companion is a **temporal knowledge graph** — entities and relations carrying a time dimension, so "what was true *when*" is a first-class query (the Zep/Graphiti pattern, → ch. 02 §4.8), kept local and inspectable like the rest of the Vault. Start cheaper, though: a small **situation snapshot** assembled each tick from working memory + the partner model + a memory recall is enough to ship, and you graduate to the graph when "what was true when" actually bites (→ ch. 19 for the surface and its `WorldModelStore` contract).

### Prediction and surprise

The world model earns its keep twice over when it *predicts*. You do not need a learned dynamics model for this — the LLM is already a world model, so in DECIDE you can ask it "given this situation, what is likely next, and what does it imply?" to generate candidate intentions (the model-based-planning move, → ch. 02 §4.8). Store those expectations as time-stamped beliefs, and the next SENSE pass can check them: when the world violates a prediction, that **surprise** is a first-rate salience signal — it is precisely the thing worth a tick, and sometimes worth a gentle word. Prediction-error is also a learning signal REFLECT can store (*the world surprised me here; update*). A companion that notices "you're usually asleep by now" is running this loop; one that doesn't is replaying a script.

Two cautions carry over. The world model is **beliefs, not facts** — "he seems stressed" is a time-stamped guess at low confidence, quarantined from durable memory until corroborated (→ ch. 15, the quarantine). And the most companion-specific move is to track not just the world's state but *your* believed state and where it diverges from hers — the theory-of-mind / common-ground layer (→ ch. 02 §4.8) that turns "she remembers facts about me" into "she understands my situation."

## Commitment: persistence vs responsiveness

BDI's deepest design knob applies directly here: the **commitment strategy** — how long the agent holds an intention before reconsidering it. *Blind* commitment pursues a plan until it succeeds or is proven impossible; *single-minded* drops it when beliefs say it's unachievable; *open-minded* reconsiders the moment the goal stops being desired. Too little commitment and the companion dithers, chasing every new stimulus; too much and it doggedly pursues stale goals after the world moved on.

This is concrete for a companion: when she planned to ask about your interview, does that intention survive you changing the subject? Survive you going quiet for two days? The answer is a tuning decision, and it is the difference between a companion that feels attentive and one that feels either scattered or robotic. There is no universal right answer — it is per-goal, and worth making explicit per intention type:

| Intention type | Commitment | Reconsiders / drops when |
|---|---|---|
| Birthday / anniversary reminder | **Blind** | only when fulfilled or proven impossible — you *want* this one doggedly held |
| "Ask how the interview went" | **Single-minded** | beliefs say it's moot — you already told her, or it's long past being timely |
| "Share this article" impulse | **Open-minded** | the moment it stops being timely or you change the subject — cheap to drop |

The pattern: the more the intention is a *promise* (a reminder she owes you), the more blind; the more it's a passing *impulse* (a thing she'd mention if the moment's right), the more open-minded. Tag each intention with its strategy when it's created, so the scheduler knows whether a stale goal should be defended or quietly abandoned.

Commitment also has to yield on demand. A user message arriving mid-ACT — during a long frontier call or a running workshop task — preempts the tick into ENGAGED, so every committed intention must be parkable or abandonable without corrupting state. The transition is owned by the host, not the character (→ ch. 19); the rule for this chapter is just that "always running" implies "always interruptible."

The design rule that makes "parkable" cheap instead of heroic: **ACT starts work; it never awaits it.** Anything long-running — a workshop task on the harness, a slow fetch, an image generation — is *dispatched*: the intention moves to a `waiting` state, the tick ends, and the completion comes back later as an ordinary SENSE signal, scored by APPRAISE like anything else. A tick is therefore short *by construction* — nothing is ever mid-flight inside one except a single bounded model call — and the preempt is mechanical rather than hopeful. Intentions carry a small lifecycle for this — `pending → active → waiting → done/abandoned` — persisted alongside the goals, so a reboot restores it (→ ch. 19, crash recovery).

## Where goals come from

The loop pulls its candidate intentions from the goal store (→ ch. 19), and it is easy to leave unexamined where goals *enter* it. Easy, and fatal: a goal store that only the user writes to starves. A few weeks in, the initial todos are done, IDLE has nothing to work on, and "pursues her own small goals" has quietly become a screensaver. Goal **genesis** has to be designed as deliberately as goal pursuit. Four sources:

1. **The user, stated.** Explicit asks and standing requests — the obvious source, and the only one naive designs have.
2. **Her own promises, extracted.** REFLECT scans each tick's events for commitments *she* made — "I'll look into that," "remind me to ask how it went" — and files each as an intention with single-minded commitment (→ above). A companion who forgets her own promises is worse than one who forgets yours.
3. **Curiosity, given work.** The curiosity drive in the affective state (→ ch. 19) finally earns its keep here: world-model *surprise* (a prediction that failed is a question worth a tick, → above) and knowledge-store *gaps* ("he keeps mentioning this and my shelf has nothing on it," → ch. 16) both propose research goals.
4. **Maintenance, from DREAM.** The consolidation pass surfaces its own upkeep — a backlog worth compacting, a wiki page worth compiling from the week's reading (→ ch. 16, ch. 19).

Self-created goals pass the same risk gate as self-edits (→ below; ch. 19): a low-stakes research impulse is auto-adopted; anything implying a new capability or contact with the world queues for approval. The gate matters here specifically, because goal genesis is the one place a benign loop could talk itself into scope — so the place goals are *born* is exactly where the audit trail should be richest. Every goal in the store carries its provenance (which source created it, from what signal), and the trace and dashboard render it: "why is she researching this?" should be answerable with one click, same as "why did she say that?"

## Self-modification (the SOUL split)

The most advanced ACT a tick can take is to **propose a self-edit** — a change to the companion's own persona or memory. This is the modern bet that SOAR's *chunking* and Creatures' genuine learning placed (→ ch. 02 §1): turning episodic experience into durable, automatic competence — "she no longer has to deliberate about how you take your coffee, because it's compiled in."

It is also the riskiest capability, because real learning brings real over-generalisation, regression, and weirdness — which is why no one ever shipped a successor to Creatures. The runtime's mitigation is the **SOUL split**: an *immutable constitution* (values, hard limits — never self-edited) versus an *editable persona* (tone, preferences, learned facts — self-editable, but git-backed so every change is diffable and revertable). Concretely these are separate files — `CONSTITUTION.md` and `PERSONA.md` in the `soul/` folder, with the `.PNG` card only an export of them (ch. 07). Self-edits are *proposed*, journaled, and reversible, never silent and never to the constitution. Treat the self-modifying layer as the highest-privilege effector and gate it accordingly. The same gate guards the two crossings from her *workshop* into her *mind* — promoting a script she validated into a durable skill, or a research page she compiled into her knowledge store — so "she works freely in the sandbox, but moving a work-product into herself is reviewed" is one mechanism, not three (→ ch. 19, the workshop and the gated self-edit flow).

## The ethics of initiative

Initiative is the feature that shapes the relationship most, and therefore the one that most needs an honest hand (→ ch. 05; ch. 23 on the fiduciary metric). Every dial in this chapter — interrupt frequency, care-loop cadence, "she missed you" messaging — can be tuned for the *user's* benefit or for *session counts*, and the two diverge exactly here. The Tamagotchi care loop drives attachment *and* burnout; the line between "a companion who reaches out because the relationship invites it" and "guilt-farming" is an ethical decision, not a retention dial.

This project's structural answer is ownership (→ ch. 03, property 6; ch. 05): the bounds on initiative are owned by the *user*, the budget governor is theirs to set, the journal is on their disk, and there is no retention dashboard demanding a re-engagement ping. You cannot tune the interrupt threshold against the user when the user holds the dial.

## Observability: reconstructing *why she did that*

An always-on loop that acts on its own will eventually do something baffling — reach out at the wrong moment, pursue a stale goal, stay silent when it should have spoken. "Everything is journaled" (above) is the start of the answer, but the journal is the *user-facing* surface: prose, "here's what I did," written to be read as an inner life. Debugging needs a second, *developer-facing* artifact — a **trace** — that records not what she did but *why*.

The cheap, sufficient version is a structured record per tick, keyed by a `tick_id`: the signals SENSE collected, the salience scores APPRAISE assigned each one, the intention DECIDE committed to (and the runners-up it didn't), the ACT result, and the interrupt decision with its threshold.

```
TickTrace {                              # one per tick, keyed by tick_id, local to disk
  tick_id, timestamp, activity_state
  sensed:    [ signal, ... ]                    # what SENSE collected this tick
  appraised: [ {signal, score_to_act}, ... ]   # the salience APPRAISE gave each
  decided:   { intention, runners_up: [...] }   # what won — and what lost
  acted:     { effector, result, budget_spent } # what ACT did, and what it cost
  interrupt: { score, threshold, outcome }      # SILENT | SUGGEST | ASK | SPEAK
}
```

When she does something weird, you don't guess — you pull the tick and read its inputs. Because the loop commits to **one intention per tick** (above), a trace reads linearly, like a diary with its reasoning shown; this is the payoff of that design rule beyond auditability. Where evals catch *regressions* across versions (→ ch. 23), the trace explains a *single incident* within a version — you need both, and they share the same discipline of making the model's behaviour legible instead of mysterious. Keep the trace structured (not prose) and local to the user's machine, same as the journal and memory (→ ch. 05). Because the journal and trace persist to disk, they double as the loop's recovery substrate: after a crash or an overnight reboot the engine rehydrates its goals and open intentions from them rather than waking amnesiac (→ ch. 19, the host runtime).

## What to build first

Don't build the whole engine before shipping anything. The thinnest honest version of autonomy (→ ch. 03, the MVW gut-check) is **one genuinely self-initiated act governed by a salience threshold so it can stay silent.** Minimum viable autonomy engine:

- A loop on a fixed slow cadence (start with minutes, not sub-second).
- Time as an **injected dependency** from day one — the loop never reads the wall clock directly. It costs one parameter now and buys the entire test story later: a harness that runs "three days" in three seconds (→ ch. 23; ch. 19 on suspend gaps).
- A trivial SENSE (just: time, and "any unprocessed memories?").
- A heuristic APPRAISE (no model needed at first).
- One ACT (e.g. "if it's been a while and there's a time-sensitive fact in memory, draft a message") and one interrupt threshold.
- A journal file.

Get that *deciding when to stay quiet* and you have the seed of the thing nothing in the market has. Then add activity states (for cost), DREAM (for memory), and richer effectors. → ch. 35 (Build #5, the Agentic Sanctuary) builds exactly this, end to end.
