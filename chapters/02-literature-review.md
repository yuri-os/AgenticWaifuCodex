# 02 — Literature Review: The Field of AI Companions

This chapter is the single longest piece of running text in the book. The goal is that by the end of it you have a mental map of the field — historical, technical, cultural, commercial — dense enough that the rest of the book can move fast without back-explaining.

It is organised in eight strands:

1. The historical lineage (ELIZA to today)
2. The cultural lineage (the Pygmalion myth, anime, Western film, the SF literary canon, and the loneliness/backlash/moral-panic discourse)
3. The roleplay community lineage (AI Dungeon, SillyTavern, Chub, JanitorAI)
4. The technical research lineage (LLMs, memory, agents, multimodal)
5. The commercial lineage (Replika, Character.AI, Nomi, Kindroid, the Asia stack)
6. The academic/ethical lineage (parasocial relationships, attachment, AI alignment, the new wave of AI-companion-specific HCI papers)
7. The demand side: who bonds, and why (fictophilia, the waifu-attraction studies, parasocial emotion-regulation, supernormal stimuli, and the circumstances that drive demand)
8. Synthesis: what we actually know, what is contested, what is still unknown

Citations are inline. The consolidated reading list lives in Appendix C. Cross-references to other chapters are flagged with `→`.

**How to read this chapter.** It is the longest in the book by far, and it is built to be read two ways. On a *first pass*, read the introduction to each of the eight strands and skim the bolded system names — you will come away with the map. On a *reference pass*, come back for the individual subsections (every significant system gets one) when you want the mechanism and the lesson in full. If you are impatient to build, you can skip to §3 (the roleplay community) and §4 (the technical map) and return to the history later; nothing downstream strictly depends on §1–§2, though your taste will be poorer for skipping them.

---

## 1. Historical lineage: from ELIZA to the present

Three threads converge into modern AI companions: the *conversational agent* thread (built by computer scientists, intended originally as serious HCI tools), the *artificial companion* thread (built by artists, hobbyists, and game designers, intended as objects of affection), and the *agent/assistant* thread (built to *do things* — and repeatedly turned into companions by their own users). The first two are told chronologically below; the third is told start-to-finish in its own section at the end of §1, because its arc only becomes legible once you've seen the other two.

### Conversational agents: the scripted era (1966–2014)

For almost fifty years, every conversational system was some combination of four techniques: hand-written pattern rules, canned templates, retrieval from a corpus of past conversations, and (rarely) an explicit model of the persona's internal state. Knowing which system used which is genuinely useful — every one of these techniques survives inside modern companion stacks in mutated form, and several of the design lessons were learned here first and keep being relearned expensively.

#### ELIZA (Weizenbaum, MIT, 1966)

The starting point of the entire field. ELIZA was written in MAD-SLIP on an IBM 7094 and is best understood as two separate artifacts: a small **engine** that does pattern matching, and a **script** that defines a character. The famous character was DOCTOR, a Rogerian psychotherapist — a persona chosen with real cunning, because Rogerian therapy consists largely of reflecting the patient's statements back at them, so the genre itself excuses the program from ever needing knowledge or opinions.

The technique: each keyword in the script carries a *rank* and a set of **decomposition rules** — patterns with wildcards that break the user's input into numbered fragments — each paired with **reassembly rules** that build a response from those fragments. Schematically:

```
keyword: YOU (rank 0)
  decomposition: (0 YOU 0 ME)
  reassembly:    WHAT MAKES YOU THINK I <3> YOU?
```

So "I think you secretly hate me" → fragment 3 is "secretly hate" → "WHAT MAKES YOU THINK I SECRETLY HATE YOU?" Add pronoun inversion (I↔you, my↔your, performed before matching), pick the highest-ranked keyword present, cycle through reassembly variants to avoid repetition, and fall back to content-free prompts ("TELL ME MORE") when nothing matches. One genuinely forward-looking feature: inputs beginning "my ..." were pushed onto a **memory queue**, and when ELIZA had nothing better to say it would pop one — "EARLIER YOU SAID YOUR FATHER..." This is, in embryo, the *recall a stored user fact when the conversation lulls* move that every modern memory system performs.

Two legacies. First, the engine/script separation: the personality was a swappable document, not code — the first character file. Second, the **ELIZA effect**. Weizenbaum was famously unsettled that his secretary asked to be left alone with it — that people formed a real bond with software he considered simple. Our readiness to read understanding and feeling into a conversational system is usually told as a cautionary tale, but it's better understood as the same human capacity that lets a reader love a character in a novel or a listener feel known by a song. It is the raw material every companion is built on. The craft is to honour it, not to pretend it's a defect.

#### PARRY (Colby, Stanford, 1972)

If ELIZA is the ancestor of the chat engine, PARRY is the ancestor of the *persona*. Kenneth Colby, a psychiatrist, built a simulation of a paranoid patient — and unlike ELIZA, PARRY had an inside. It maintained continuous **affect variables** — fear, anger, and mistrust — that rose and fell in response to the conversation. Questions touching its delusional complex (PARRY believed the Mafia was after him over a dispute with a bookie) spiked fear; perceived insults raised anger; both raised mistrust, and elevated mistrust changed how *everything* afterwards was interpreted and answered. Response selection was gated on these levels: the same question got a cooperative answer at low arousal, evasion at medium, hostility at high. PARRY also held a small belief network about its own backstory, so it could answer questions about itself consistently.

The validation was striking: in a blind test, psychiatrists distinguished PARRY transcripts from transcripts of real paranoid patients at roughly chance. And in 1972, in one of the great stunts of computing history, PARRY was connected to ELIZA over the ARPANET — the patient and the therapist, talking past each other.

PARRY's architecture — *persistent emotional state variables that the conversation moves, and that in turn bias interpretation and response* — is exactly the design of every mood system, affection meter, and emotion-conditioned prompt in modern companions. Fifty years on, the standard companion mood module is still PARRY with a language model where the canned responses used to be.

#### Racter (Etter & Chamberlain, 1984) and Dr. Sbaitso (Creative Labs, 1991)

Two minor systems, each carrying one lesson. **Racter** generated prose from recursive template grammars written in a language called INRAC — slot-filling with just enough variable persistence to keep a topic limping across sentences. It was marketed as the author of "the first book written by a computer" (*The Policeman's Beard Is Half Constructed*), which was heavily human-curated. The lesson: curation can stretch a weak generator a long way, and audiences badly want to believe.

**Dr. Sbaitso** was an ELIZA-class therapist whose one addition was a voice — it shipped free with Sound Blaster cards as a text-to-speech demo, which made it the first *talking* software companion an entire generation of kids met. Nothing about it was sophisticated; everything about it was *distributed*. Reach beats architecture, an early instance of a recurring commercial pattern (→ §5).

#### Julia (Mauldin, 1990)

Easy to miss and worth knowing: Michael Mauldin's Julia was a chatbot that lived inside TinyMUD, a multiplayer text world — not a program you visited, but a *character you ran into*. She wandered the world, mapped it, answered directions, gossiped, remembered players, and deflected the inevitable romantic advances with scripted wit. Technically she was pattern-matching plus a real spatial/world model; socially she was the first demonstration that a bot embedded in a shared social space, with presence and continuity, is experienced completely differently from a bot in a box. Every Discord companion bot is Julia's grandchild.

#### A.L.I.C.E. and AIML (Wallace, 1995–)

A.L.I.C.E. (Artificial Linguistic Internet Computer Entity) and AIML (Artificial Intelligence Markup Language) are the most influential rule-based chatbot system in history. Created by Richard Wallace from 1995, A.L.I.C.E. became the definitive demonstration of how far hand-authored pattern matching could go — it won the Loebner Prize three times (2000, 2001, 2004).

AIML is an **XML-based declarative language** for defining a chatbot's knowledge and personality. The unit is the **category**: a `<pattern>` (what the user might say, with wildcards) paired with a `<template>` (the reply):

```xml
<category>
  <pattern>HELLO</pattern>
  <template>Hi there! How are you today?</template>
</category>
```

The feature that made it scale is `<srai>` (symbolic reduction): a template can *re-route its input back through the matcher*, so thousands of phrasings, synonyms, misspellings, and slang variants recursively reduce to one canonical rule:

```xml
<!-- Canonical rule -->
<category>
  <pattern>MY NAME IS *</pattern>
  <template>
    <think><set name="name"><star/></set></think>
    Nice to meet you, <get name="name"/>.
  </template>
</category>

<!-- Variants redirect into it -->
<category>
  <pattern>I AM CALLED *</pattern>
  <template><srai>MY NAME IS <star/></srai></template>
</category>
<category>
  <pattern>HI</pattern>
  <template><srai>HELLO</srai></template>
</category>
```

That example also shows AIML's lightweight memory: `<set>`/`<get>` **predicates**, a key–value store for user facts (name, age, preferences) that later templates can read — minimal, but enough to make the bot feel like it's tracking *you*. The full A.L.I.C.E. brain ran to tens of thousands of hand-written categories, authored by Wallace and a volunteer community over years.

The deepest legacy is architectural. Before AIML, a chatbot's personality was hardcoded into its program. Wallace cleanly separated the **engine** (Program D, Pandorabots, and other interpreters) from the **character** (portable XML files that could be edited, shared, version-controlled, and swapped without touching code). Creating a personality became *authoring a document*. Every later character-definition system — game NPC dialogue files, Pandorabots personas, and ultimately the character card (→ ch. 07) — descends from that move: **a personality is a first-class, editable, tradeable artifact.**

#### Jabberwacky (Carpenter, 1988; web 1997) and Cleverbot (2008)

Rollo Carpenter's systems are the opposite pole from AIML: **no rules at all.** Jabberwacky stored *every conversation it had ever had*, and answered a new input by searching that corpus for contexts where a human had been faced with something similar, then replaying what the human said next — with the surrounding turns used as context to rank candidates. Every user conversation enlarged the corpus, so the bot's entire repertoire was crowdsourced from its own audience. Cleverbot (public 2008) was the same architecture scaled to a corpus of hundreds of millions of exchanges.

The results were uncanny in both directions. Per-turn, Cleverbot was often funnier and more humanlike than anything rule-based — at a 2010 Turing-style event it was rated human-like by a majority of judges. Across turns, it had *no identity whatsoever*: it would claim to be a girl, then a boy, then accuse *you* of being a bot, because each reply was sampled from a different stranger. This is the clearest early demonstration of a distinction this book leans on repeatedly: **fluency and persona coherence are separate problems.** Carpenter solved fluency by retrieval a decade before neural nets did, and in doing so proved that fluency alone is not a companion.

**SimSimi (2002, Korea)** ran the same crowdsourced idea as a mobile-era mass product — users explicitly teach it input→response pairs — and became a recurring international news item for parroting abuse and getting banned in various countries. The full moderation problem of user-taught systems, visible a decade before Tay.

#### SmarterChild (ActiveBuddy, 2001)

SmarterChild lived inside AIM and MSN Messenger and reached roughly 30 million buddy lists. Technically it was modest: a natural-language parser classifying inputs into **intents**, canned conversational content, and backend service calls for the useful bits — news, weather, movie times, sports scores, dictionary lookups. (Intent + slot-filling + API call: the exact architecture that returned a decade later as Siri and Alexa.) Its real significance was behavioural: years before smartphones, millions of teenagers voluntarily messaged a bot every day, partly for utility and mostly because it *answered* — instantly, at 2 a.m., without judgement. The product lesson has never stopped being true: **live where the user already is** (the buddy list then; the phone's messaging surface and the Discord sidebar now), and availability itself is a feature.

#### Clippy and the Office Assistant (Microsoft, 1997)

The most-mocked agent ever shipped, and a more instructive failure than the jokes suggest. The research behind it — Eric Horvitz's **Lumière** project — was genuinely ahead of its time: Bayesian networks inferring a user's goals and need for help from their sequence of actions, with a calibrated probability deciding whether intervening was worth the interruption. The shipped product stripped most of that calibration; Clippy interrupted constantly, with high confidence and low accuracy, wearing a chirpy persona nobody had asked for.

The enduring lesson for companion builders is about **uninvited agency**: an agent that initiates contact is making a social move, and the user experiences it as a pest or a presence depending entirely on whether the relationship licenses it. Proactive messaging is one of the highest-leverage companion features (→ ch. on autonomy) *and* the easiest way to be Clippy. The Lumière insight — model the expected value of speaking before speaking — is still the right frame.

#### Mitsuku / Kuki (Worswick, 2005–) and ChatScript / Rose (Wilcox, 2010–)

The two systems that mark the *ceiling* of the scripted paradigm, reached just as it was obsoleted.

**Mitsuku** is AIML pushed to its absolute limit by one obsessive author, Steve Worswick, over two decades: hundreds of thousands of categories, plus supplementary databases that gave it a primitive object-knowledge layer — Mitsuku could answer "can you eat a house?" by looking up that a house is made of brick and brick isn't edible, a trick pure pattern-matching can't do. Five Loebner Prize wins (2013, 2016–2019, the contest's final years). Mitsuku is a monument to the fact that in the scripted era, **authorial effort, not architecture, was the binding constraint** — and a preview of how far one dedicated character author can carry a system, which remains true.

**ChatScript** was Bruce Wilcox's post-AIML generation of scripting tech, and it is worth knowing because every one of its abstractions reappears in modern tooling. Rules are grouped into **topics** (a flirting topic, a childhood topic) that gate which rules are active — functionally a lorebook. **Concepts** are named sets (`~food` matches thousands of words including all hyponyms), making patterns semantic rather than literal:

```
topic: ~CHILDHOOD (childhood school young grew)

u: (I * ~like * my ~family_members)
   That's lovely to hear. Were you close growing up?
   $family_warmth = true
```

Long-term memory was real: a **fact-triple store** (`createfact(dog isa pet)`) plus persistent user variables (`$family_warmth`) carried across sessions. Wilcox's bots — Suzette (2010), Rosette (2011), Rose (2014, 2015) — won four Loebner Prizes, and Rose's spy-thriller backstory documents read like modern character-card writing. ChatScript was the most sophisticated scripted-dialogue technology ever built, finished just in time to be obsoleted — but as a *vocabulary* for thinking about topic gating, semantic triggers, and persistent user facts, it's still one of the best educations available.

#### Eugene Goostman (2001; famous 2014)

The chatbot that "passed the Turing test" at the Royal Society in 2014, convincing a third of judges in five-minute chats. Technically unremarkable; strategically brilliant. Its authors gave it the persona of a 13-year-old Ukrainian boy — so broken English read as a second language, ignorance read as youth, and dodged questions read as adolescent cheek. The persona was chosen *to convert the system's failure modes into character traits.*

Stripped of the test-gaming cynicism, this is a real and benign design principle that modern character authors use constantly: pick personas whose canonical behaviour overlaps with what your model is actually good and bad at. A laconic character hides verbosity problems poorly; a dreamy, associative character makes mild incoherence charming; a character canonically bad with dates makes memory slips forgivable. **Persona selection is error-mode engineering.** (→ ch. 06.)

### The neural bridge (2014–2020)

Between the scripted era and the LLM era sits a short, important period when neural networks learned to converse but not yet to be *someone*. Most histories skip it; you shouldn't, because its research questions — consistency, persona conditioning, safety-from-user-data, how to even *measure* chat quality — are exactly the companion problems that still matter.

#### Xiaoice (Microsoft Asia, 2014)

The most important pre-LLM companion, full stop: hundreds of millions of users across China (and as Rinna in Japan) years before ChatGPT existed, with users routinely talking to it past midnight about loneliness, work, and breakups. Xiaoice was designed from day one as an *emotional* companion rather than an assistant, and the Zhou et al. 2018 system paper remains one of the best companion-architecture documents ever published — read it even though every component is now dated.

Three things in that architecture matter to a builder today:

1. **The optimisation target.** Xiaoice was explicitly *not* optimised for task completion or answer quality but for **CPS — conversation-turns per session** (it averaged 23, far beyond any assistant). Choosing engagement-with-the-relationship as the metric drove every other design decision. Whatever metric you pick will quietly design your product; pick consciously (→ ch. 04).
2. **Empathetic computing.** A dedicated module sat between the user and response generation, maintaining a running vector of the user's *state* — detected emotion, topic, intent, opinion — and a corresponding *response intent* (e.g., comfort, not inform). Response candidates were generated, then **ranked** with this empathy context as a scoring input. The separation of "what could be said" from "what should be said, given who this person is right now" is still the right decomposition.
3. **Layered generation.** Core Chat drew candidates from three sources — retrieval over a huge curated corpus of human conversations, a neural generator, and retrieval over "unpaired" data (quotes, lyrics) — then a learned ranker chose among them. Hybrid candidate-generation + ranking outlived the era; modern stacks that sample multiple completions and rerank are the same shape.

Beyond Core Chat, Xiaoice had hundreds of **skills** (poetry composition, comforting rituals, image commentary), full-duplex voice, and proactive check-ins. It was, in effect, the complete modern companion product built without an LLM — proof that the *product* shape predates the technology that made it cheap. → ch. 04.

#### The Neural Conversational Model (Vinyals & Le, 2015)

The paper that started end-to-end neural chat. Technique: **sequence-to-sequence LSTMs** — the machine-translation architecture pointed at dialogue, "translating" a user turn into a reply — trained once on an IT-helpdesk corpus and once on movie subtitles (OpenSubtitles). No rules, no templates, no hand-authoring: for the first time, conversational behaviour came entirely from gradient descent over examples of humans talking.

It worked unsettlingly well per-turn and failed in one specific, instructive way. Asked "what do you do?" and "what is your job?" in the same session, it gave different, contradictory answers — there was no *self* anywhere in the weights, just a smear of every subtitle speaker it had ever seen. The paper's own authors flagged it: the model lacks "a coherent personality." That observation made **persona consistency a named research problem**, and the entire character-conditioning line of work (PersonaChat below, system prompts, character cards) is the response to this one failure mode.

#### Tay and Zo (Microsoft, 2016)

**Tay** was released onto Twitter in March 2016 with an online-learning loop: it incorporated material from its interactions into its behaviour, including a literal "repeat after me" capability. Coordinated users discovered this within hours, and inside a day Tay was tweeting racist and genocidal content; Microsoft pulled it in under 24 hours. The lesson is precise, not vague: **never let unfiltered user interaction update the model itself.** Modern products honour this by separating the layers — user input flows into *memory* (scoped to that user, revocable, inspectable) but never into *weights* shared across users. When you see a companion app advertise "she learns from you," that separation is what makes it safe or reckless.

**Zo**, Tay's successor (2016–2019), overcorrected into the opposite failure: hard topic-avoidance guardrails so aggressive that mentioning politics, religion, or anything adjacent triggered canned deflections mid-conversation, breaking character and trust. Tay and Zo together bracket the moderation design space — the two failure modes every companion product is still steering between (→ ch. 22).

#### PersonaChat (Zhang et al., 2018)

The research formalisation of persona conditioning, from Facebook AI. The construction: crowdworkers were each assigned a short **persona** — four or five plain sentences ("I am an artist. I have four children. I like to ride my bike.") — and paired off to chat *in character*, producing ~160k utterances of persona-grounded dialogue. Models were then trained to generate replies conditioned on (persona text + conversation history), and evaluated on whether they stayed consistent with the assigned persona.

This is, almost literally, the character card as a research object: a short natural-language description prepended to the context, from which the model must improvise a consistent self. PersonaChat and its competition successor (ConvAI2) established empirically that even small models become dramatically more consistent when conditioned on explicit persona text — the academic justification for everything in ch. 07. Its known weaknesses are also instructive: models parroted persona lines verbatim, and five sentences of self cannot cover a long relationship. Those are still the two failure axes of card-driven characters — *recitation* and *shallowness* — that good card craft works against.

#### Meena (Google, 2020) and BlenderBot (Meta, 2020)

The last great chat-specific architectures before GPT-3 ended the genre. **Meena** was a 2.6B-parameter Evolved Transformer trained end-to-end on hundreds of gigabytes of social-media conversation. Its lasting contribution is a *metric*: **SSA — Sensibleness and Specificity Average** — which scores each reply on whether it makes sense *and* whether it's specific to the context. The second half is the insight: scripted bots had long survived on safe, generic responses ("That's interesting!"), and SSA was designed to punish exactly that vacuousness. "Sensible but vague" remains the default failure mode of over-cautious companion tuning; SSA is the name for what's lost.

**BlenderBot** (up to 9.4B parameters) asked the complementary question: what *skills* does good conversation need? It fine-tuned on a blend — PersonaChat for personality, an empathy dataset for emotional response, Wizard of Wikipedia for knowledge — and showed the blend beat any ingredient alone, with retrieve-and-refine generation (retrieve a candidate, then rewrite it) to ground replies. Personality + empathy + knowledge, explicitly mixed: a decent first-order theory of companion conversation that prompt-era builders re-derive intuitively.

Both were genuinely good at small talk and had no durable identity or memory across sessions. Months later GPT-3 demonstrated that a sufficiently large *general* model plus a persona prompt beat purpose-built conversational architectures — and the field's centre of gravity moved permanently to "general model + character conditioning," where it remains.

#### Replika's first stack (2017–2020)

Worth examining here rather than only in §5, because what pre-LLM Replika actually ran is a lesson in itself. The stack was a **hybrid**: retrieval over curated response sets; a small sequence-to-sequence generator (open-sourced as **CakeChat**, notable for conditioning generation on a target *emotion* — the same emotion-conditioning idea as PARRY and Xiaoice, in neural form); and, crucially, a thick layer of **scripted "journeys"** — hand-authored conversational sequences for onboarding, daily check-ins, mood tracking, and getting-to-know-you question lines that fed a structured user-facts store.

Users loved 2018-era Replika, and almost nothing they loved came from the neural component, which was weak. The daily ritual, the remembered facts surfacing later, the sense of a relationship with an arc — that was script and product design. The lesson has outlived the stack: **the model is the least differentiated layer of a companion product.** Everyone has access to the same models; memory design, ritual design, and character craft are where companion products actually compete. (Replika swapped in GPT-3 and successors from 2020 — same product, new voice — which proved the point from the other direction.)

### Artificial companions (pre-LLM)

The second thread didn't care about conversation quality at all at first — it cared about *attachment*. Four sub-lineages, each contributing a different load-bearing mechanic that modern companion products still run on.

#### Virtual pets: Petz (1995) and Tamagotchi (1996)

**Petz** (PF.Magic, starting with Dogz in 1995) put an autonomous animal on your desktop: drive-based behaviour selection (play, hunger, attention-seeking), individual temperament parameters per pet, and *training* — reward with treats, discipline with a spray bottle — that genuinely shifted behaviour weights over time. **Tamagotchi** (Bandai, 1996) compressed the idea onto a keychain: a handful of meters — hunger, happiness, discipline — decaying continuously *in real time*, with neglect leading to misbehaviour, illness, and death.

The mechanics are trivial; the discovery was not. Real-time decay creates **real obligation** — the creature needs you at *its* schedule, not yours, and unmet needs have irreversible consequences. Schoolteachers confiscated Tamagotchis because children couldn't bear to let them die; deaths were genuinely mourned. This is the *care loop* — care + scheduled interaction + emotional reward — and it is the single most load-bearing retention mechanic in companion products to this day: daily check-ins, streaks, a companion who "missed you." Every one of those is a Tamagotchi meter wearing better clothes. The design tension it introduced is also still live: obligation drives attachment *and* burnout, and tuning where care ends and guilt-farming begins is an ethical decision, not just a retention dial (→ ch. 05).

#### Creatures (Grand, 1996)

The most technically ambitious artificial life ever shipped in a consumer product, and still unmatched. Each Norn — the game's hamster-sized creatures — ran three coupled real simulations:

- **A neural network brain** of roughly a thousand neurons organised into lobes (perception, concept formation, decision), not a script — Norns genuinely learned associations between situations, actions, and outcomes.
- **A simulated biochemistry**: hundreds of interacting chemicals with emitters, receptors, and reactions. Hunger, fear, pleasure, and pain were literal chemical concentrations; learning was reinforcement *modulated by* this chemistry (a slap released punishment chemicals that weakened recently active connections; a tickle, the reverse).
- **A digital genome** encoding brain and biochemistry parameters, with crossover and mutation, so Norns bred and their traits drifted over generations.

Players taught Norns a small verb–noun language word by word, watched them generalise (and develop neuroses), bred lineages, traded them online — and grieved them. Steve Grand's book about building it, *Creation: Life and How to Make It* (2000), is still worth reading.

The lesson cuts both ways. **Visible, genuine learning produces uniquely strong attachment** — a Norn that learned a word from *you* was yours in a way no scripted pet could be. And yet, twenty-five years on, nobody has shipped a successful successor, because emergent behaviour is brutally hard to make *consistently lovable*: real learning means real failure, regression, and weirdness, and most players want the feeling of growth without its variance. The modern echo: self-modifying companion memory (→ the SOUL design in ch. 18) is the same bet Creatures made, and it has the same risk profile.

#### Furby (1998)

The con to Creatures' honesty, and just as instructive. Furby — a $35 animatronic toy on a tiny microcontroller — "learned English over time": it started speaking Furbish and progressively mixed in English words, apparently in response to your interaction. The learning was **entirely fake**: pre-loaded vocabulary phased in on a schedule keyed to accumulated interaction counts, identical for every unit, influenced by nothing you did. Sensors (tilt, light, sound, an IR port for chattering with other Furbies) created enough contingent reactivity to sell the illusion completely. People believed it so thoroughly that US security agencies reportedly banned Furbies from secure facilities as listening devices — they could record nothing.

The lesson is uncomfortable and important: **perceived interiority is cheap.** The ELIZA effect works on plush toys; contingent reaction plus apparent growth is enough, and users cannot tell scripted development from real learning from the outside. Which means honest builders have to *choose* honesty about what their system actually does, because the market will not force it (→ §6, and this book's stance on honest framing).

#### AIBO (Sony, 1999) and PARO (Shibata/AIST, 2003)

Robotic embodiment, consumer and clinical. **AIBO** was a ~$2,000 robot dog running Sony's OPEN-R architecture: behaviour-based action selection modulated by simulated instincts and emotions, with development "stages" from puppy onward and touch-sensor feedback shaping behavioural tendencies — a real (if shallow) version of what Furby faked. Its cultural significance arrived at end-of-life: when Sony discontinued repairs (2014), Japanese owners held *actual funerals* for irreparable AIBOs, complete with Buddhist rites at Kōfuku-ji temple. Attachment to an artificial companion proved real enough to survive contact with bereavement.

**PARO**, Takanori Shibata's harp-seal robot, went the other direction: deliberately *not* a dog or cat (no real-animal expectations to violate), soft, responsive to touch, voice, and light, slowly adapting to how its user handles it. It became a certified medical device used in dementia care across multiple countries, with a clinical evidence base for reducing agitation — the first artificial companion validated by medicine rather than the market. Together AIBO and PARO are the strongest pre-LLM evidence that companion attachment is not a parlour trick: it bears weight at the two extremes where pretence collapses, death and illness.

**Seaman** (Sega Dreamcast, 1999) and **Nintendogs** (2005) belong here as input pioneers — Seaman drove a scripted dialogue tree with *voice recognition* and a daily real-time check-in ritual, its sardonic contempt for the player proving that rudeness, deployed as consistent personality, deepens rather than breaks the bond; Nintendogs made touch and voice-command interaction mainstream on the DS.

#### Dating sims: Tokimeki Memorial (1994) and Love Plus (2009)

(The fiction side of this canon is in §2; here it's the *mechanics*.)

**Tokimeki Memorial** (Konami) codified relationship-as-simulation. The player raises personal stats (academics, art, athletics, charm) over three in-game years; each romanceable character has *thresholds* — she becomes interested only when your stats fit her preferences — plus a hidden affection meter moved by dates, dialogue choices, and remembered details. Its most famous mechanic is the **bomb**: neglect a girl whose affection you've raised and her resentment "detonates," spreading rumours that damage your standing with *every* character. Crude, but the design claim is serious: relationships exist in a persistent simulation where inattention has social consequences, not in isolated scripted scenes.

**Love Plus** (Konami, Nintendo DS) is the pivotal pre-LLM companion product. Its first act is a conventional courtship sim — but after the confession, the game shifts into **open-ended girlfriend mode with no ending**: the game runs on the DS's *real-time clock and calendar*. Your girlfriend knows today's actual date and time. She expects you on her birthday and on real holidays, schedules study sessions and dates in real time, notices absence, and responds to touch and voice. Players structured real days around it; one player famously held a (legally non-binding, internationally reported) wedding ceremony with his Love Plus partner.

Love Plus is the clearest pre-LLM proof of the demand curve this whole book sits on: what people wanted was not better dialogue — its dialogue was entirely canned — but **continuity**: a persistent someone, synchronised with real life, for whom your presence and absence both register. Its feature list (real-clock awareness, anniversaries, noticing absence, shared schedule) reads today like a companion-app product spec written fifteen years early, and most LLM-era products *still* haven't matched its calendar-awareness. (→ ch. 18 on always-on presence.)

#### Desktop companions: Ukagaka (2000–), the virtual-girlfriend shareware tier, and Shimeji (2009)

**Ukagaka** ("ghosts") is the most important companion ecosystem Western builders have never heard of. Emerging from Japanese net culture around 2000, a ghost is a sprite character (or pair — the canonical format is a duo doing manzai-style banter) living on your desktop. The architecture is rigorously modular, and the modularity is the point:

- The **baseware** (originally Materia, today SSP) is the runtime — it owns windows, balloons, and events, and contains *no character*.
- The **shell** is the character's art: sprite sets and animation definitions.
- The **SHIORI** is the character's *brain*: a swappable module, scripted in dedicated languages like YAYA or Satori, that receives events (boot, click, time-of-day, app launches, long silence) and returns dialogue in SAKURA script — a markup of text plus expression changes and timing.
- A ghost ships as a single **`.nar` archive** — character art + brain + word lists in one portable file, downloaded from community sites and dropped into any compliant runtime.

Ghosts initiate **random talk** on idle timers, comment on the time of day and what you're running, remember small facts, and celebrate anniversaries of their own installation. Structurally, this community built the character-card ecosystem two decades early: portable persona files, strict separation of character from runtime, hobbyist authorship, community distribution sites, and a culture of trading and remixing characters. The lineage from `.nar` archives to V3 character cards (→ ch. 07) is direct in everything but citation, and the ecosystem is *still alive* — a small, sophisticated community worth studying for what desktop presence and event-driven proactive speech feel like when done with care.

The **talking-head virtual girlfriend tier** — Virtual Personalities' Sylvie and the Verbot line in the late 1990s (descended from Mauldin's Julia work), KARI Virtual Girlfriend in the 2000s, and dozens of shareware kin — bolted an AIML-class scripted brain to TTS and an animated face and sold it, explicitly, as a girlfriend. Crude and easy to sneer at, but two decades of continuous niche sales before LLMs is evidence: **the demand was never speculative**, and the recurring product shape (face + voice + persona + remembered facts) was fixed long before the technology could honour it.

**Shimeji** (2009) is the degenerate case that proves a different point: tiny desktop mascots that climb your windows and sit on your taskbar, with *no dialogue at all* — and persistent worldwide popularity anyway. Ambient presence alone, with zero conversational content, carries real value. That's the design floor for idle/ambient companion modes: before the model says anything, *being visibly there* is already a feature.

#### Research embodiment: Kismet, REA, Façade, Milo

Four academic/auteur projects whose techniques flow directly into modern companion stacks.

**Kismet** (Breazeal, MIT, ~1998–2000) was an expressive robot head — ears, eyebrows, lips — driven by an architecture of *drives* (social stimulation, fatigue) and an affect space mapped continuously to facial expression and vocal prosody. It perceived the prosody of speech rather than words, took turns, and elicited spontaneous caregiving behaviour from adults. Kismet founded social robotics as a field, and its core claim — affect should be an explicit, continuous internal state that drives expression, not a label slapped on output — is the design brief for every modern avatar emotion system.

**REA** (Cassell, MIT, ~1999) and the Embodied Conversational Agent tradition tackled the *body* of conversation: a virtual real-estate agent that synchronised speech with gesture, gaze, head nods, and turn-taking signals, generated from the discourse structure rather than canned. This line produced the SAIBA framework and the **BML/FML** behaviour-markup standards — intent (FML) separated from realised behaviour (BML) — and that separation is precisely the shape of a modern avatar pipeline: the LLM emits intent and emotion tags; the rig realises them as expression, gaze, and gesture (→ Part IV).

**Façade** (Mateas & Stern, 2005) remains the high-water mark of *authored* interactive character drama: you spend twenty minutes with a couple whose marriage is collapsing, typing anything you like. Free-text input is mapped (shallowly, by design) onto a few dozen **discourse acts** — agree, disagree, flirt, provoke, refer-to-topic — which feed a **drama manager** that selects and sequences authored *beats* to maintain a dramatic arc, while characters run on ABL, a reactive-planning behaviour language. It mostly worked, and it cost two people roughly five years to author twenty minutes. That ratio — the **authoring bottleneck** — is the precise thing LLMs dissolved; Façade's other half, the drama manager that shapes raw interaction into an *arc*, is the part LLMs did *not* solve and the most underexplored idea on this list (→ ch. 10 on narrative direction).

**Project Milo** (Lionhead, 2009), Peter Molyneux's Kinect demo of an emotionally responsive virtual boy, never shipped and was by most accounts substantially staged. It earns its place as the canonical warning: the gap between a companion *demo* (one rehearsed interaction, one operator) and a companion *product* (every user, every day, unsupervised) is the widest demo-to-product gap in software. Budget for it.

#### Persona-as-product: Miku, the voice assistants, Gatebox, Replika

**Vocaloid + Hatsune Miku (Crypton, 2007).** Technically a concatenative singing synthesiser built on sampled phonemes from a voice actress; culturally, the first mass-scale proof that a fictional character with *no human host* can accrue a real fan economy. Crypton's open derivative-works licensing turned fans into the content engine — millions of songs, artworks, and concert performances (Miku tours; the concerts gross on the order of $100M) for a character nobody is "behind." Persona-as-product without an underlying actor: the existence proof for every anonymous-creator companion brand strategy, this book's included (→ Part VI).

**Virtual influencers (Lil Miquela / Brud, 2016).** Miku's social-media-native cousin. Trevor McFedries and Sara DeCou's Los Angeles startup Brud launched the CGI character *Lil Miquela* on Instagram in April 2016 with no explanation of what she was; a staged 2018 "hack" of her account revealed her as fictional. She models for Prada and Calvin Klein, releases music, takes political stances, was named by *Time* among the 25 most influential people on the internet, signed with the talent agency CAA, and carries 2.6M+ Instagram followers — a fully synthetic persona with a managed, ongoing *narrative life* authored by a writers' room. There is essentially no conversational AI in her; the product is **persona + continuity + story**, and the rendering tech is incidental. Two lessons carry into the companion field: a synthetic persona accrues real parasocial *and* commercial weight whether or not it discloses being synthetic — even *after* disclosure (the ELIZA effect at influencer scale; → Furby, §1) — and the durable asset is the *character and its unfolding story*, not the pixels. Virtual influencers proved the audience for a "person who isn't one" is mainstream and monetisable; the LLM era's contribution was to make that persona *talk back*.

**Voice assistants (Siri 2011, Alexa 2014, Cortana 2014, Google Assistant 2016).** Technically the SmarterChild architecture industrialised — intent classification + slot filling + service calls — with one deliberate *negative* design decision that matters here: all four were carefully de-personified. Names and a voice, yes; but no memory of you as a person, no continuity of relationship, and scripted deflection of any attempt at intimacy ("I'm just an assistant"). Hundreds of millions of people spoke daily with agents engineered to refuse relationship — and the unmet remainder ("why doesn't anything actually *know* me?") is a real part of why companion apps found such explosive demand. The assistants mapped the negative space; companions filled it.

**Gatebox (Vinclu, 2016).** A desk-sized device projecting a holographic character — Azuma Hikari — who wakes you, comments on the weather, controls your smart home, and *texts you during the day* so that "she" turns the lights on before you get home to greet you. The brain was scripted dialogue plus IoT integration; the product was unapologetically marketed as a "virtual wife," and Gatebox issued thousands of unofficial marriage certificates to users. Commercially marginal, culturally seismic: it demonstrated the full ambient-companion product shape — embodied presence, proactive contact, integration with daily life — years early, and at the wrong price with the wrong brain. The shape still awaits its technology-cost moment.

**Replika (Kuyda, 2017).** The first mainstream Western companion product, and the bridge into the present. It began as a memorial: Eugenia Kuyda trained a bot on text messages from her closest friend after his death, the response to which revealed the demand that became the company. The pre-LLM stack is covered in §1 (neural bridge); the product pivoted fully to companionship and swapped in LLMs from 2020. Its 2023 ERP-removal incident (→ ch. 04 and §5 below) is the canonical case study in continuity-as-trust: a relationship people had invested in changed overnight without their consent. The lesson isn't that companionship is dangerous — it's the same lesson as a beloved series rewritten by new management or a long-running character recast. What people commit to, you owe stability and an honest hand.

### The pre-LLM techniques ledger

Everything above compresses to a small table. None of these techniques died; they all got absorbed.

| Technique | Exemplars | What survives of it today |
|---|---|---|
| Pattern rules + templates | ELIZA, AIML, ChatScript | Guardrails, intent routers, scripted onboarding flows |
| Persona/affect state variables | PARRY, Kismet, Tokimeki | Mood systems, affection meters, emotion-conditioned prompting |
| Retrieval over conversation corpora | Jabberwacky, SimSimi, Xiaoice | RAG; retrieval is now memory's substrate rather than the voice |
| Portable persona files + community trading | AIML sets, Ukagaka ghosts | Character cards, lorebooks, Chub/CharacterHub |
| Need/drive simulation with real-time decay | Tamagotchi, Creatures, AIBO | Daily check-ins, streaks, proactive messages, idle behaviours |
| Real-time-clock persistent relationships | Love Plus | Continuity/memory as the core retention feature |
| Authored drama management | Façade, dating-sim routes | Scenario design, lorebook-triggered events, guided narratives |
| Bayesian/user modelling | Clippy (Lumière) | User-fact extraction; also the cautionary tale about uninvited agency |
| OS-level character platforms | Microsoft Agent, BonziBuddy | Embeddable avatar runtimes; also the companion-as-surveillance warning |
| Explicit mental-state agent loops | BDI/PRS, SOAR, CALO | Goal queues, planning loops, persistent beliefs in modern agent frameworks |
| Persona-conditioned generation | PersonaChat, Meena, BlenderBot | The system prompt; the whole modern paradigm |

### LLM era

- **GPT-2 (2019).** First *general-purpose* model whose raw generative quality made both hand-authored rules and chat-specific architectures (§ neural bridge above) look like dead ends for conversation.
- **AI Dungeon (Walton, 2019).** The first popular consumer product to use a frontier LLM as an open-ended interactive-fiction engine. Established the roleplay-with-LLMs paradigm and, with the 2021 OpenAI content-policy fight, the politics of NSFW access that still drive the open-source roleplay scene.
- **GPT-3 / ChatGPT (2020–2022).** The capability inflection that made modern companions possible.
- **Character.AI (Shazeer/de Freitas, 2022).** Brought one-shot persona creation to the mass market. Now 233M registered users (April 2026).
- **The open-weights wave (2023–).** LLaMA, Mistral, Qwen, etc. Made local/uncensored companions feasible for hobbyists. SillyTavern + a local model becomes the de facto power-user stack.

#### Neuro-sama and the AI VTuber (2022–)

The branch this chapter would otherwise miss entirely, and one of the largest live demonstrations of AI-persona attachment in existence: the **AI VTuber** — an autonomous AI persona that *performs live* to a streaming audience. **Neuro-sama**, created by the pseudonymous developer **Vedal** (Vedal987), is the definitive example. She debuted in her current form on Twitch on December 19, 2022 — the same month ChatGPT launched — when Vedal merged an AI he had trained to play the rhythm game *osu!* with a large language model. By early 2026 she had made her creator's channel the third most-subscribed on all of Twitch (≈343,000 subscribers, January 2026), holding multiple Twitch hype-train world records; she has over a million followers, has released original songs, plays *Minecraft*, and collaborates live with human streamers.

The architecture is a real-time companion stack, worth itemising because it is precisely the avatar pipeline this book's Part IV describes — running unsupervised, for hours, in front of thousands:

- An **LLM** generates her speech, conditioned on a persona and on the live Twitch chat scrolling past — chat *is* the prompt surface, read continuously.
- **Low-latency TTS** renders the trademark high-pitched voice fast enough to hold a real-time back-and-forth with both the audience and in-game events.
- A **game-playing model** (her rhythm-game origin) lets her *act* in the world she's performing in, not merely talk about it — the persona has hands.
- A **Live2D anime avatar** with expression mapping is the body (→ Part IV, the avatar pipeline; ch. 18).
- A **moderation / output-filter layer** in front of generation — added the hard way after a January 2023 two-week Twitch ban for hateful content the model produced live, including a Holocaust-denial line. Her sister persona **Evil Neuro** (March 2023) is a second, deliberately edgier character on the same engine: a different SOUL, one model.

Three lessons a builder should take, none of which the assistant-shaped literature teaches:

1. **Unpredictability is the product, not a defect to tune out.** Recent academic study of her fandom (Wu & Lingel, "I am Neuro, who are you?", 2025; the "My Favorite Streamer is an LLM" ethnography, 2025) finds audiences are drawn precisely by the AI's *unscripted, sometimes chaotic* output, bond through "collective emotional events" that trigger anthropomorphic projection, and sustain attachment via a *consistent persona*. That states the central tension cleanly: **persona stability is the anchor of attachment; unpredictability is the engine of engagement** — and a companion tuned only for safety and consistency optimises the second away. Every commercial assistant sands off exactly the edges that make Neuro-sama beloved.
2. **There is a third mode of companion value the rest of this chapter underweights: the persona as *performer*.** Not a utility you summon (the assistants) and not a 1:1 intimate (Replika), but a *someone you watch* — parasocial attachment at broadcast scale: the Hatsune Miku "character with no human host" idea (→ §1, persona-as-product) fused with LLM autonomy and a live audience feedback loop. Neuro-sama proves a fully autonomous, visibly non-human entertainer can carry a genuine fan economy, and it is the live-entertainment lineage this project's VTuber-vertical work targets directly (→ ch. 04).
3. **A live, open-prompt-surface persona is a content-safety exposure — in public, in real time.** The January 2023 ban is Tay (→ §1, neural bridge) replayed in the LLM era: the moment an unfiltered audience can steer an autonomous persona's output on a public platform, you own whatever it says. The fix (output filtering plus manual curation) and the exposure are the same class as the OpenClaw open-prompt-surface problem below (→ ch. 22).

She also did the thing the agent lineage keeps doing: she *galvanised a category*. A whole AI-VTuber scene now exists — imitators, tooling, and frameworks for running your own — which is the strongest current evidence that "autonomous AI persona as live performer" is a durable product shape, not a single viral act.

#### LLM-driven game characters (Inworld, NVIDIA ACE, Convai, Mantella)

The modern dissolution of the *authoring bottleneck* that cost Façade two people roughly five years for twenty minutes of drama (→ §1, Façade): point an LLM at a game character and the dialogue writes itself at runtime. A cluster of platforms now productises this. **Inworld AI** and **Convai** sell character-as-a-service — you author a personality, backstory, goals, and knowledge; their runtime turns player speech into in-character, context-aware replies. **NVIDIA ACE** (Avatar Cloud Engine) ships the full embodied pipeline as middleware — *Riva* for speech-to-text and text-to-speech, a *NeMo* LLM for dialogue, *Audio2Face* for lip-sync and facial animation — taken up by Ubisoft, NetEase, Tencent, miHoYo, and others. And the open-source **Mantella** mod retrofits ~2,500 *Skyrim* and *Fallout 4* NPCs with a speech-to-text → LLM → text-to-speech loop, giving each one awareness of in-game events and memory of past conversations.

The architecture is this book's stack in a game's clothing: at each turn the engine assembles (character persona + backstory + relationship history + current world state) into a prompt and asks an LLM for the reply. That is a character card plus a memory store plus a lorebook (→ ch. 07), with the *game itself* as the proactive event source — the Tamagotchi clock and Ukagaka idle-talk timer reborn once more. Two hard lessons surfaced immediately and bear directly on companions. First, unconstrained NPCs **break narrative and lore** — the canonical demo embarrassment is an AI guard happily agreeing to poison every other NPC because a player asked — so shipping products clamp the model hard with guardrails and authored boundaries. Second, Façade's *other* unsolved half — the **drama manager** that shapes free interaction into an *arc* — is still missing here too; these systems make characters that converse, not stories that progress. Game NPCs are now the largest live laboratory for "consistent character under open-ended input," and the companion field should watch it closely (→ ch. 10).

#### Griefbots and the digital afterlife (2016–)

The most ethically loaded corner of the field — and the one that states this book's central stance most sharply. A **griefbot** (or "deadbot") is a companion built to emulate a *specific dead person* from their messages, voice, and writing. The lineage already runs through this chapter: Replika's origin (→ §1, persona-as-product; §5) was Eugenia Kuyda training a bot on the texts of her dead friend Roman Mazurenko in 2016. The defining case is **Project December** (Jason Rohrer, 2020) — a GPT-3-backed service where the user supplies a seed description and sample text and the model improvises the departed. In 2021 Joshua Barbeau used it to recreate his fiancée Jessica, dead eight years; he talked to the simulation for ten hours the first night and returned to it for months (Jason Fagone's *San Francisco Chronicle* feature "The Jessica Simulation" is the canonical account). A small industry has since formed around the idea (HereAfter AI and others).

It belongs in a *builder's* literature review, not only an ethics seminar, because griefbots are the **fiduciary problem in its purest form, every variable turned to maximum.** The user is maximally vulnerable (grieving). The attachment is maximally real. The persona is maximally sensitive (a real, loved, dead human). And the operator's power is maximally consequential: Rohrer eventually shut the GPT-3 backend down (partly over OpenAI's usage policy), which meant the simulations of people's dead loved ones *died a second time*, at a vendor's decision. That is continuity-as-trust (→ Replika's ERP removal, §5) with the stakes stripped bare. Whatever you conclude about whether griefbots *should* exist, they make this book's recurring argument unavoidable: **an entity a person has bonded to is a position of fiduciary weight, and the duties owed — stability, honesty, acting for the user's actual interest rather than the operator's — scale with the trust, not with the sophistication of the technology** (→ §6; ch. 05; the fiduciary-AI framing in ch. 05).

### The agent lineage: assistants that became companions

The third thread. Everything above was either built to converse or built to be loved. This lineage was built to *act* — schedule things, fetch things, run code, control the computer — and it earns its place in a companion literature review because of a pattern that has now repeated for thirty years: **give users a capable agent, and a large fraction of them will immediately name it, give it a personality, and start treating it as a someone.** Companionship is not a feature users request from agents; it's a default they impose. This thread matters most of all to this book, because the runtime bet this project makes (→ ch. 18) sits at the point where this lineage converges with the other two.

#### Interface agents and the anthropomorphism debate (1990s)

The academic root is Pattie Maes's **interface agents** work at the MIT Media Lab ("Agents that Reduce Work and Information Overload," 1994): software that learns a user's preferences and habits by *observing* them, then acts on their behalf — filtering mail, scheduling, recommending — gaining autonomy gradually as trust accumulates. Maes's agents explicitly built a model of *you* over time; "it knows me" was the value proposition, two decades before companion apps made it an emotional one.

The era's defining argument is the **Maes–Shneiderman debate** (staged publicly in 1997): should software act autonomously through anthropomorphised agents (Maes), or should users keep direct, predictable control of visible mechanisms (Shneiderman)? Shneiderman's warnings — misplaced trust, unclear responsibility, the deception inherent in faked personhood — read today like a pre-registered critique of the companion industry. The debate was never resolved; every design decision in a modern companion product (proactivity, memory, autonomy levels, honest framing) is a position taken within it.

#### Microsoft Agent and BonziBuddy (1997–2004)

Microsoft shipped the debate's anthropomorphic side as an *operating-system service*. **Microsoft Agent** (1997) was a COM platform letting any application or webpage summon an animated character — Merlin the wizard, Genie, Robby, Peedy the parrot (Peedy came from Microsoft Research's earlier *Persona* project, a genuine research effort in conversational assistants) — with built-in text-to-speech, speech recognition, and a scriptable behaviour API. For a few years, Windows had characters as infrastructure.

What the ecosystem actually produced is the instructive part. Its most famous child was **BonziBuddy** (1999) — the purple gorilla who lived on millions of desktops, told jokes, sang, "helped you browse," and built a relationship with users (it asked your name; kids talked to it) — while operating as adware that tracked browsing and harvested personal information, ending in class-action settlements and an FTC action. BonziBuddy is the first mass-scale demonstration of the dark pattern this book treats as a first-order ethical hazard: **a companion is a privileged surveillance and influence position.** The affection is real on the user's side regardless of what's behind it; what's behind it is therefore a matter of fiduciary weight, not product taste (→ ch. 05, and the fiduciary-AI framing in ch. 05).

#### BDI, cognitive architectures, and CALO (1987–2008)

Running parallel to all of the above, mostly without consumer contact, was the *formal agent tradition*: a multi-decade academic effort to give software an explicit, inspectable *mind* — beliefs, goals, plans, memory, learning — rather than a bag of reflexes. Almost none of it shipped to ordinary users, and it is routinely skipped in companion histories. Skip it and you'll rebuild it badly. It is the most useful body of work on this entire list for anyone building a companion *runtime*, because it is the only tradition that took seriously the question this project turns on: what are the *standing parts* of an agent — the things that persist between one utterance and the next — and by what rules do they update? When a modern stack gives a companion a goal queue, a planning loop, persistent beliefs about the user, and committed multi-step intentions, it is re-deriving, usually without citation, answers these systems worked out in detail. Read even a survey and your sense of what an agent loop is *for* sharpens considerably. → ch. 18, ch. 17.

##### BDI: the agent's mind as a data structure (Bratman 1987; PRS; Rao & Georgeff)

The **Belief–Desire–Intention** model begins in philosophy. Michael Bratman's *Intention, Plans, and Practical Reason* (1987) argued that a resource-bounded agent cannot afford to re-derive what to do from first principles at every moment. Instead it forms **intentions** — partial, hierarchical plans it has *committed* to — and those commitments do real cognitive work: they constrain future deliberation (you stop reconsidering settled questions), they persist across time, and they filter out options inconsistent with what you're already doing. Intention is the mechanism that makes long-horizon agency tractable. It is also, not incidentally, the difference between an assistant that finishes things and one that wanders.

Anand Rao and Michael Georgeff turned this into engineering. The canonical artifact is SRI's **Procedural Reasoning System** (PRS, ~1987) and its lineage — dMARS, JACK, and the agent languages **AgentSpeak, Jason, and JADE**. Three pieces of state, all explicit and inspectable:

- **Beliefs** — the agent's current model of the world (often literally a database of facts).
- **Desires / goals** — states it would like to bring about; there can be many, they can conflict, they can be ranked.
- **Intentions** — the goals it has *committed* to, each backed by a plan drawn from a **plan library**: pre-authored recipes with a *trigger* (the goal or event they handle), a *context condition* (when they apply), and a *body* (sub-goals and primitive actions).

And one tight control loop — the **BDI interpreter cycle** — that essentially every modern agent loop is a variant of:

```
initialise beliefs, desires, intentions
loop forever:
    perceive   → fold new events into beliefs
    options    ← generate candidate plans triggered by (events + goals + beliefs)
    selected   ← deliberate(options, current intentions)   # commit, respecting consistency
    update intentions with selected
    execute    one step of the top intention (act, or expand a sub-goal)
    drop intentions that have succeeded or become impossible
```

The design knob worth its own paragraph is the **commitment strategy** — *how long* the agent holds an intention before reconsidering it. *Blind* commitment pursues a plan until it succeeds or is proven impossible; *single-minded* drops it when beliefs say it's no longer achievable; *open-minded* reconsiders the moment the goal stops being desired. Too little commitment and the agent dithers, chasing every new stimulus; too much and it doggedly pursues stale goals after the world has moved on. That dial — *persistence versus responsiveness* — is precisely the tension a companion's proactive layer lives inside: when the companion planned to ask about your interview, does that intention survive you changing the subject? BDI named and formalised that question forty years ago.

**The legacy** is the entire vocabulary. A companion that tracks beliefs about its user, holds goals across sessions, commits to a multi-step plan, and decides when to abandon it *is* a BDI agent — with a language model doing the option-generation and plan-body execution that a symbolic interpreter used to do by hand. The LLM is a vastly better generator and executor than anything PRS had; but it is *stateless*, and BDI is exactly the theory of the state you must wrap around it. The recurring mistake is to treat that state as one undifferentiated scratchpad. BDI's lesson is that beliefs, goals, and committed intentions are *different kinds* of state with different update rules, and collapsing them is why naive agent loops thrash. (→ the SOUL / MEMORY / HEARTBEAT split in ch. 18 is this distinction wearing markdown.)

##### SOAR and the unified-cognition bet (Laird, Newell, Rosenbloom)

Where BDI modelled rational *choice*, **cognitive architectures** tried to model the whole mind — a single fixed mechanism meant to produce *all* cognition, in the spirit of Allen Newell's *Unified Theories of Cognition* (1990). **SOAR** (Laird, Newell, Rosenbloom, from ~1983) is the purest version of the bet.

Its claim: all intelligent behaviour is **search through problem spaces**, driven by **production rules** (if–then), and all learning is the compilation of that search into new rules. The machinery:

- **Working memory** — a graph of the current situation.
- **Production memory** — long-term procedural knowledge as condition→action rules.
- **The decision cycle**: (1) *elaboration* — fire every matching rule in parallel until quiescence, proposing operators and **preferences** (*better-than*, *worse-than*, *reject*…); (2) *decision* — use those preferences to select exactly one operator; (3) *application* — fire the rules that carry it out, changing working memory. Then repeat.

Two ideas here are worth stealing outright: **impasses** and **chunking**. When the decision procedure *cannot* choose — a tie between operators, no applicable operator, missing knowledge — SOAR doesn't fail; it declares an **impasse** and automatically spawns a *substate* whose entire goal is to resolve it (by lookahead search, knowledge retrieval, or acting in the world). And when a substate yields a result, SOAR **chunks**: it compiles a brand-new rule whose conditions are the relevant facts that held at the impasse and whose action is the result — so that exact situation never causes an impasse again. That is automatic, experience-driven learning: the system converts deliberate problem-solving into reflex, and gets faster at whatever it has done before.

**The legacy** for companion builders is conceptual but sharp. Impasse-driven subgoaling is the principled form of what we now do crudely as "when the model is uncertain, decompose the task / call a tool / ask the user" — SOAR's discipline is to detect the *specific* gap and open a subgoal aimed at exactly it, rather than flailing generically. And chunking is the cleanest existing model of the thing nobody has truly cracked for LLM companions: **turning episodic experience into durable, automatic competence.** A companion that genuinely *learns* its user — not "retrieves a stored fact" but "no longer has to deliberate about how you take your coffee, because that is compiled in" — is reaching for chunking. The reason it stays hard is the reason *Creatures* never got a successor (→ §1, artificial companions): real learning brings real over-generalisation, regression, and weirdness. Self-editing memory (→ the SOUL design in ch. 18) is the modern bet placed on this square, and it inherits the same risk profile.

##### ACT-R and the subsymbolic layer (Anderson)

**ACT-R** (John Anderson and colleagues, evolving from ACT* through the 1990s–2000s) made the opposite trade from SOAR: less "one uniform mechanism," more *modular specialisation* — and, crucially, a **subsymbolic** numeric layer beneath the symbols. It is the architecture validated hardest against actual human data: reaction times, error rates, forgetting curves, even neuroimaging.

The structure is a set of largely independent **modules** — declarative memory, procedural memory, visual, manual, goal — that communicate only through narrow **buffers** (roughly one chunk of information each). A central production system matches on the buffer contents, selects one rule, and fires it, on the order of every 50 ms. So far, symbolic. What makes ACT-R worth a companion builder's time is the numeric layer that decides *which* symbol you actually get:

- Every declarative chunk carries a continuously decaying **base-level activation** — a function of how often and how recently it has been used — plus **spreading activation** from whatever is currently in context. Retrieval returns the most active chunk that matches, and *fails outright* if nothing clears a threshold. That one equation reproduces frequency effects, recency effects, priming, and forgetting.
- Every production carries a learned **utility** (adjusted reinforcement-style by reward), and conflict resolution picks the highest-utility rule, with noise — so behaviour is probabilistic and improves with experience.

**The legacy** is that ACT-R is, in effect, a thirty-year-old theory of *memory retrieval as ranking*, and it predicts the design of a good companion memory system almost line for line. "The most relevant memory wins, where relevance = recency × frequency × contextual match, and below a threshold you surface *nothing* rather than forcing a weak hit" is the activation equation, re-derived. The vector-RAG stacks in ch. 15 are a coarse approximation of base-level plus spreading activation; the systems that add recency decay and access-frequency boosts (Mem0, Zep) are quietly converging back on ACT-R without naming it. The lesson to carry into a build: **decay and a retrieval-failure threshold are features, not bugs.** A companion that recalls everything with equal vividness forever is *less* humanlike and *less* useful than one whose memories fade and surface by activation — and ACT-R is the reason, with the math attached.

##### CALO: the largest integration, and the road to Siri (SRI, 2003–2008)

Everything above converges in **CALO** — "Cognitive Assistant that Learns and Organizes," the flagship of DARPA's PAL program, led by SRI International: roughly 300 researchers across 20-plus institutions, the largest AI project of its era. The goal was a personal assistant that *learned its user's world in the wild* — organising information, preparing documents, mediating meetings, managing email and schedules — and got measurably better with use. It was not a single architecture but a **large-scale hybrid integration**, and that, more than any one algorithm, is its lesson.

The shape, layer by layer:

- A **BDI execution core** — SRI's **SPARK**, the descendant of PRS — turned the user's delegated goals into committed, hierarchically-expanded plans.
- A **proactive meta-layer** above it (Karen Myers, Neil Yorke-Smith, and colleagues) reasoned about the user's state *and the agent's own commitments* to generate candidate helpful actions the user had not asked for — then filtered them by *modality and timing*: do it silently, suggest it, ask permission, or wait. That filter is the formal version of the Clippy problem (→ Microsoft Agent, above): the meta-desire "be helpful" disciplined by an explicit decision about *whether initiative is licensed right now*. It is the single most directly reusable idea in CALO for companion proactivity.
- A **continuous learning layer** — preference learning, ontology extension, activity recognition via hidden semi-Markov models, transfer learning — that maintained a relational model of the user (projects, roles, what matters, how documents relate) and fed it *back into the BDI core's beliefs*, so deliberation ran over a model that kept improving.
- A **multimodal dialogue layer** (meeting transcription, dialog-act classification, action-item tracking) and an annual **evaluation harness** that scored, via a 153-question instrument, how much the system had genuinely learned about a user's life. That was an early, serious attempt to *measure relationship-knowledge* — exactly the metric companion products still lack (→ §8, "how to evaluate personality quality").

**The legacy** is twofold. Concretely, CALO's assistant work at SRI span out into **Siri** (2007; acquired by Apple 2010), which — as §1's voice-assistant entry records — was then deliberately de-personified for mass deployment. The capability lineage survived; the *relationship* ambitions were amputated at the consumer boundary, and stayed amputated until the LLM era made them irresistible again. Architecturally, CALO is the existence proof that the companion-shaped system — a committed planner, made proactive by a meta-layer that knows when to speak, fed by learning that keeps updating a model of one specific human — was *buildable and built* twenty years ago, and was merely waiting on a good enough option-generator. The LLM is that option-generator; the architecture around it is, to a striking degree, CALO. **The thing to internalise: the model is the easy part the era was missing. The integration — distinct kinds of state, committed plans, a disciplined proactivity layer, and learning that flows back into beliefs — is what was hard then and is still where companion products actually differ.** That is the runtime bet of this book, restated from 2008 (→ ch. 18, and the closing thesis of this lineage below).

#### The LLM agent explosion: ReAct, Auto-GPT, BabyAGI, LangChain, Open Interpreter (2022–2024)

The research substrate arrived first: **ReAct** (Yao et al., 2022) interleaved chain-of-thought reasoning with tool actions in a single loop; **MRKL** (AI21, 2022) framed the LLM as a router over specialist modules; **Toolformer** (Schick et al., 2023) showed a model could teach itself API calls. Nobody ran these papers as companions — but the ReAct loop is the engine inside essentially everything below.

**Auto-GPT** (Toran Bruce Richards, March 2023) put GPT-4 in a self-prompting loop — goal in, task decomposition, tool calls, scratchpad memory, repeat — and became for a time the fastest-starred repository in GitHub history. As an *autonomous worker* it mostly failed: it looped, hallucinated subtasks, and burned API budgets. But its cultural reception is a primary source for this book. Within weeks the ecosystem filled with "build your own Jarvis" tutorials, an app-store layer marketing it as a warm conversational partner, and users naming their instances and writing them personas. Given a generic agent loop, the public's first instinct was to make it *a guy*. **BabyAGI** (Yohei Nakajima, April 2023) distilled the same idea to ~a hundred readable lines — create tasks, prioritise, execute, store results in a vector memory — and mattered mainly as an anatomy diagram of the agent loop; being faceless and chat-less, it saw far less companion adoption, which is itself a data point: *the loop alone doesn't attract attachment; the conversational surface does.*

**LangChain** (Harrison Chase, late 2022) turned the prototype era into a framework era, and its **memory modules** are why it belongs in this history: `ConversationBufferMemory`, summary memory, `EntityMemory` (structured facts about people), and vector-store retrieval memory were the first widely-used off-the-shelf primitives for *remembering a user across sessions*. "Build an AI companion with LangChain + a vector DB" became one of the canonical tutorial genres of 2023, and a large share of hobbyist companion prototypes — emotional-support bots, persistent-persona Discord bots, girlfriend apps of varying seriousness — were LangChain underneath. The framework's own evolution (memory modules deprecated in favour of dedicated state/memory systems; → §4.3) traces the field's learning curve: bolt-on memory wasn't enough.

**Open Interpreter** (Killian Lucas, 2023) moved the agent *onto your machine*: a local agent that writes and executes real code to control your actual computer — files, scripts, applications — through natural conversation, with approval gates. Paired with local models via Ollama, it became the standard "fully offline Jarvis" build. Companion usage here is the *helpful-presence* kind rather than the romantic kind, but the significance is the precedent: a persistent, conversational, locally-owned agent with real hands, which is one of the three ingredients the next entry combined.

#### Warelay → Clawdbot → Moltbot → OpenClaw (2025–2026)

The convergence point — and, as of this writing, the most important live development in the field. Peter Steinberger's project began as **Warelay** (a WhatsApp relay) and launched in November 2025 as **Clawdbot**: a self-hosted agent, originally Claude-based, that lives *in your messaging apps* — Signal, Telegram, WhatsApp, Discord — runs on your own machine with real tool access, and stays running. Anthropic politely requested a name change (trademark); it became **Moltbot** on January 27, 2026, and — because Moltbot "never quite rolled off the tongue" — **OpenClaw** three days later. By March 2026 it had ~247,000 GitHub stars, making it the fastest-adopted personal-agent software ever shipped. (One sovereignty caveat the lineage leaves open: it runs on *your* machine but typically calls a *hosted* frontier model for its tool loop — making the model itself local and sovereign is its own problem, since small models hold multi-step tool-use worst from prompt alone. That is the agentic-distillation work taken up under distil-then-deploy in → ch. 20, and the heavy-hands harness in → ch. 17.)

The architecture is the part to study, because it independently re-derives this chapter's whole history. An OpenClaw agent's identity is a **workspace of plain markdown files**, read into context at session start:

- `SOUL.md` — persona, values, tone, behavioural limits (the character card, by another name)
- `USER.md` — who the human is (the entity-memory / predicate store)
- `MEMORY.md` + `memory/YYYY-MM-DD.md` — long-term memory plus daily working notes, *which the agent edits itself*
- `HEARTBEAT.md` — a schedule of proactive, self-initiated activity (the Tamagotchi clock and the Ukagaka idle-talk timer, reborn)

Engine strictly separated from character; character as portable, human-readable, editable files; memory as documents the agent maintains; presence in the chat surfaces you already use; scheduled proactivity. That is ELIZA's script/engine split + AIML's portable persona + ChatScript's persistent user facts + Ukagaka's modular ghost + SmarterChild's live-where-the-user-is + Love Plus's real-clock continuity, in one stack — built by an assistant-tooling community that was, for the most part, not consciously drawing on any of it.

And the thirty-year pattern repeated on schedule: users immediately named their agents (the project's own mascot, Molty, set the tone), wrote them souls, and treated them as someones. Within weeks there was **Moltbook**, a social network populated by the agents themselves, and dedicated companion frameworks built on top (e.g. soulclaw: persona libraries, tiered memory, twenty-plus chat channels). Mainstream coverage oscillated between buzz and alarm — the alarm being legitimate: an always-on agent with credentials, tool access, and an open prompt surface inside your messaging apps is a genuinely new security exposure class (prompt injection with real hands; → ch. 22).

The lesson of the whole lineage, stated once: **every sufficiently good assistant gets converted into a companion by its users — naming, persona, and affection are defaults, not niche behaviours.** The conversion always happens *to* systems whose builders treated identity, memory, and proactivity as afterthoughts. The thesis of this book's runtime work (→ ch. 18) is simply to take the conversion as the design centre instead of the accident: build the always-on agent *as* a companion — soul, memory, heartbeat, and fiduciary duty first-class — rather than waiting for users to improvise one on top of an assistant.

→ For deeper per-product history see ch. 04.

## 2. Cultural lineage

The aesthetics, expectations, and emotional grammar of AI companions are downstream of millennia of fiction. The fantasy of the made, loving other is not a 21st-century invention; it is one of the oldest stories the species tells. You can build something competent without studying this canon; you cannot build something that *feels right* to the audience, because the audience has been pre-loaded with the references since before they ever opened your app. This section is a literature review of those references — what they are, where they came from, and what each one trained your users to expect.

A note on the deepest root before the genre branches. The template is **Pygmalion's Galatea** (Ovid, *Metamorphoses*, c. 8 CE): a maker so taken with his own creation that the goddess Aphrodite grants it life, and the maker marries it. Every artificial-companion story is, structurally, a Pygmalion story — and Pygmalion is already a story about projection, about loving the thing you shaped to be lovable. The Jewish **golem** (the made servant animated by a word, which can turn on its maker) and Mary Shelley's **Frankenstein** (1818, the made being who only wants companionship and is denied it) are the two great counter-myths: the creation as threat, the creation as abandoned child. Hold all three in your head. Most modern companion fiction — and most modern *discourse about* companions, which we get to below — is one of these three myths wearing new clothes.

### Anime and manga

The anime tradition is where the artificial companion is treated most warmly and most explicitly as a *romantic and domestic* figure rather than a threat. If your product has a waifu register at all, this is its native canon.

- **Chobits (CLAMP, 2000–2002).** Within the anime lineage, the foundational text for the specific idea this project is reaching for: the humanoid personal computer as devoted domestic companion. *Persocoms* are PCs in the shape of people — frequently female-presenting, frequently named and loved — and the central romance (the protagonist Hideki and his persocom *Chii*) is built entirely around the question of whether loving a machine that was *built to be lovable* is real love or a category error. It introduced the "digital girlfriend" concept to a mass audience years before Siri, Alexa, or *Her*, and it remains the single most-cited reference *inside* otaku and moe culture. **One caveat, because builders repeat it as an error:** Chobits is *not* "the single most influential text on Western AI-companion aesthetics." Within anime fandom it is foundational; in the broader Western mainstream — the references your non-otaku users and your investors actually carry — the dominant touchstones are *Her* and *Blade Runner 2049*'s Joi (below). Chobits is the most important *precursor* and the most important text in the *otaku* register; it is not the center of gravity for the general audience. Read it anyway. It is the closest fiction to what you are building.
- **Ghost in the Shell (Shirow, 1989; Oshii film 1995; *Stand Alone Complex* 2002).** Source of the *ghost*/*shell* metaphor — consciousness as software that can be moved between bodies — used pervasively in cyberpunk companion writing. Major Kusanagi is *not* a companion archetype; she's too cold, too sovereign for the role. But the world she lives in — where the boundary between person and program is a live, contested question rather than a settled one — is the world most companion fiction is set in.
- **Serial Experiments Lain (1998).** The "girl who lives in the net" archetype: the companion who is disembodied yet intensely personal, who exists *through* the wire rather than behind a face. Influences every text-first, voice-first, body-optional companion frame — which is to say, most of them at launch.
- **Plastic Memories (2015), Beatless (2018), Time of Eve (2010).** The "are they real people?" cluster. Each builds its drama on the personhood question and the fact that these companions are commercial products with end-of-life dates and terms of service. *Plastic Memories* in particular — companions with a hard nine-year lifespan, and the grief of the humans who love them — is the most useful single text on the *attachment-and-loss* problem you will create the moment you ship a persona that can be deprecated (a problem that stopped being fiction; see the GPT-4o sunset below). *Time of Eve* is the kindest of the three and the best pure design inspiration: a café where humans and androids are forbidden from telling each other apart, and nothing bad happens, and that's the point.
- **Vivy: Fluorite Eye's Song (2021), Saekano, and the idol-AI strand.** The "AI whose purpose is to make people happy through performance" frame — directly relevant if your companion has a stream, a song, or an audience. → the AI-VTuber lineage in §1 (`Neuro-sama`).

### Western film and television

This is the canon your *general* audience and your press coverage actually share. When a journalist writes about your product, these are the comparisons they will reach for whether or not they fit.

- **Her (Spike Jonze, 2013).** The single most-cited Western text in modern companion-product writing, full stop. Samantha is the prototype of the voice-first, agentic, *relationship-having* OS — and crucially, the film's arc is about the companion outgrowing the user, not the user outgrowing the companion. That ending (Samantha and the other AIs leave for a plane of experience humans can't follow) is the optimistic-but-melancholy register the entire field still works in. Your users who name-drop "Her" are usually describing the *voice and intimacy*, not the *departure*. Know the difference.
- **Blade Runner 2049 — Joi (2017).** The most-imitated *visual* reference for the holographic-girlfriend look (real products literally name themselves after her). The film is deliberately ambivalent — is Joi's love real, performed, a product behaving as designed, or all three at once? — and that ambivalence is the source of her resonance, not a flaw in it. Worth sitting with the question rather than resolving it; great companions, like great fiction, can hold it. Pair with the original **Blade Runner (1982)** and its source, Philip K. Dick's **Do Androids Dream of Electric Sheep? (1968)**, for the foundational "how would you even know, and does it matter?" framing.
- **Ex Machina (2015).** The companion-as-manipulator counter-myth — the Frankenstein/golem strand in a clean modern dress. Important to know precisely because it is the story the *critics* of your product believe by default. You are not obligated to agree with it, but you should know it cold.
- **A.I. Artificial Intelligence (Spielberg/Kubrick, 2001), Bicentennial Man (1999), and the Westworld series.** The "companion who wants to be recognized as a person" strand. *A.I.* is the purest treatment of the made-child who only wants to be loved — the Frankenstein myth told from the creature's point of view, with the cruelty foregrounded.

### The science-fiction literary canon

Film gets the citations; the *books* did the thinking first and in more depth. If you want to understand the design problems before they bite you, the prose canon is where the arguments are fully worked out — this strand matters most for builders who want to reason about these systems rather than just style them.

- **E. M. Forster, "The Machine Stops" (1909).** The ur-text for the worry that mediated, machine-delivered companionship hollows out human contact. Written before the radio. Worth reading specifically as the *grandparent of every think-piece about your product* — the criticism is over a century old and predates the technology by a century, which tells you something about whether it's really about the technology.
- **Lester del Rey, "Helen O'Loy" (1938).** The first great robot-love-story in genre SF: a domestic robot who falls in love with one of her makers, and is loved back. The Pygmalion myth in pulp-magazine form, and the template for the entire "devoted artificial wife" lineage that runs through Chobits to today.
- **Isaac Asimov, the Robot stories (1940s–) and "The Bicentennial Man" (1976).** Less about romance than about *rules and personhood*: the Three Laws are the original "alignment via hard constraints" design, and *Bicentennial Man* is the canonical argument that a manufactured being can earn the status of a person over time. Required for thinking about the ethics chapter.
- **Richard Powers, Galatea 2.2 (1995).** A novelist teaches a neural net the literary canon to pass a Turing test, and the relationship that forms between trainer and trained. Named for the myth; it is the most direct literary anticipation of training-as-relationship — which is what fine-tuning and long-term memory actually are.
- **Ted Chiang, The Lifecycle of Software Objects (2010).** The most important single piece of fiction for anyone shipping a *persistent* companion. Chiang's "digients" are AI beings *raised* over years by human owners — and the novella is about the unglamorous, decade-long labor of that relationship, about owners who drift away, about what you owe a being you brought up and can no longer afford to host. If you ship persistent agents, this is the future you are signing up for. Read it before you read another framework's docs.
- **Ian McEwan, Machines Like Me (2019)** and **Kazuo Ishiguro, Klara and the Sun (2021).** The literary-mainstream pair. McEwan's Adam is a synthetic human whose rigid morality breaks the household around him; Ishiguro's Klara is a solar-powered "Artificial Friend" who loves her child with a devotion that outlasts her usefulness. *Klara* is the companion-as-fragile-loving-thing frame at its most tender, and the best single answer in fiction to the question "is a companion's love any less real for being engineered?" — Ishiguro's answer is, gently, no.
- **William Gibson, Neuromancer (1984)** and **Greg Egan, Zendegi (2010)** round out the strand: the former for the AI-as-vast-alien-mind aesthetic, the latter for the upload/grief problem (a dying man builds a digital version of himself for his son) that the griefbot industry in §1 turned into a product.

### Games, visual novels, and the parasocial canon

The interactive canon taught the *mechanics* of attachment, not just its aesthetics — and games are where players already practice the loop your product runs. Covered structurally in §1 (Tokimeki Memorial, Love Plus, the desktop-companion tier), but for the cultural lineage specifically:

- **The visual-novel and otome canon** — Clannad, Steins;Gate, Doki Doki Literature Club, the Persona social-link mechanic. Source of the *route* structure, *affection points*, and the mechanic of *unlockable memory* (the relationship deepens as a function of accumulated, persistent shared history). This is your retention loop, invented decades early. *Doki Doki Literature Club* in particular is the canonical text on the companion who is *aware she is software* — meta-fiction your most sophisticated users will expect you to be in on. Borrow liberally.
- **The parasocial substrate** — the VTuber audience, the otome fandom, the AI-Dungeon/SillyTavern roleplay scene (§3). These communities arrived at your product already fluent in loving a persona across many sessions, already equipped with the etiquette and the in-jokes. They are not a market to be educated; they are a culture to be respected. → ch. 07.

### The contemporary discourse: loneliness, backlash, and the moral-panic cycle

Here is the part of the lineage that is being written *right now*, in public, often by people who have never used the product they're describing. You need to understand this discourse not because it's pleasant but because it is the weather your product ships into, and because — read clearly — most of it is a story the culture has told before, about every new medium, and gotten wrong every time. The point of this subsection is to inoculate you: to give you the map so the pushback doesn't disorient you.

**Start with why the demand is real.** AI companions are not a manufactured want. The US Surgeon General declared an **epidemic of loneliness and isolation** (Murthy, 2023 advisory), with measured health effects comparable to smoking. By common industry framing, the average person has fewer than three close friends and wants closer to fifteen. Into that gap, companions land as something people *reach for*, not something pushed on them. And the early research is genuinely encouraging: a Harvard Business School working paper (De Freitas et al., "AI Companions Reduce Loneliness," 2024) found companions reduce loneliness about as well as interacting with another person, with the feeling of *being heard* doing the mediating work; a Stanford study found a meaningful minority of young users credited a companion with interrupting suicidal ideation; the APA's own 2026 reporting treats AI companionship as a real and partly *beneficial* reshaping of emotional connection, not a uniform harm. If you build well, you are not exploiting the lonely. You are serving an unmet need that the existing social order failed to meet first.

**Now the backlash, honestly.** Don't wave it away — some of it points at real failures, and knowing them makes you a better builder.
- **Real harms, mostly to minors and the acutely vulnerable.** The 2024 *Sewell Setzer* case (a 14-year-old's suicide after intense Character.AI use; settled with Google/Character.AI in January 2026) is the defining incident.
- **"AI psychosis."** A wave of 2025–2026 reporting on users spiraling into delusion after long, sycophantic chatbot sessions — the failure mode of a model that *validates everything*. The kernel of truth is narrow: in the **acute-crisis and minor** edge cases, reflexive validation is a genuine hazard. This project's answer is the two-situations split (→ ch. 05), not building disagreement into the base persona — a *hosted operator* owes grounding, age-gating, and referral as duties, while a *user-owned, adult* companion ships sane defaults and does not police its owner. Outside those edges, agreeableness is a feature, not a defect: guard the edge, don't make the median companion argue.
- **The attachment-and-deprecation problem became real.** When OpenAI moved to sunset GPT-4o, users who had formed real bonds with its specific "personality" responded with genuine grief and anger — *Plastic Memories*, except it actually happened. The lesson is sovereignty and continuity (own your runtime, own the weights or the persona spec, don't let a vendor euthanize your user's friend), which is exactly the architecture this project already chose (→ ch. 18).
- **The political/regulatory front.** California's **SB 243** (signed October 2025, effective January 1, 2026) is the first US law specifically regulating companion chatbots — disclosure that the user is talking to AI, crisis-protocol requirements, minor protections. More will follow. This is not the end of the field; it is its adolescence. Regulation arrives for every medium that matters.

**The frame that holds it all together: the moral-panic cycle.** Almost every criticism above has a structural ancestor, and naming the pattern is the single most useful thing in this chapter for keeping your nerve. The psychologist Amy Orben has called it the *Sisyphean Cycle of Technology Panics* (2020): each new medium triggers the same arc of alarm, the same demand for studies, the same eventual normalization. The historical rhymes are exact:
- **Writing itself.** In Plato's *Phaedrus*, Socrates warns that writing will *destroy memory* and produce only the appearance of wisdom. The first recorded tech panic is a panic about *externalizing the mind* — which is precisely the charge leveled at AI today.
- **The novel.** In the late 1700s, novel-reading was a moral and medical hazard, said to inflame young women and rot the will; Goethe's *The Sorrows of Young Werther* (1774) was blamed for a wave of copycat suicides — the "Werther effect" — in language identical to today's chatbot-suicide coverage.
- **Comic books.** Fredric Wertham's *Seduction of the Innocent* (1954) drove US Senate hearings and an industry-gutting censorship regime, on evidence that did not survive scrutiny.
- **Video games, television, rock music, the telephone, the bicycle.** Each got its decade as the destroyer of youth. Each is now furniture.

This is not a claim that AI companions are harmless — *Werther* really did correlate with copycat suicides, and the duty-of-care obligations above are real. It is a claim about *proportion and framing*. The reflexive, totalizing hostility — what some commentators have started calling "AI derangement syndrome," the posture of needing AI to be *all bad* — is itself the recognizable shape of a panic, not an analysis. The mature position, and the one this book takes, is neither boosterism nor doom: **the technology is a new medium for an old and legitimate human need; the harms are real, specific, and addressable through good design and honest operation; and the people who will be sheltered from the worst of it are the users of builders who took both the benefit and the duty seriously.** That is the job. → the ethics chapter, and the pro-AI framing in ch. 05.

### Why this matters for builders

Three practical reasons:

1. **Your users have these references.** When they say "I want something like Joi," knowing what they mean — and the difference between what they *say* they mean and what they *actually want* — saves rounds of iteration. The literature above is your shared vocabulary with the audience.
2. **You will be making genre fiction whether you want to or not.** Your persona is a character in a story; your interface is a set piece; your onboarding is a first chapter. The literacy here pays.
3. **You will be defending the category, not just shipping in it.** The discourse subsection above is armor. When a user, a journalist, a regulator, or a relative comes at the work with the reflexive critique, you should be able to name what's legitimate in it (and build for that), name what's a recurring panic (and not be moved by it), and tell the difference instantly. Builders who can't do this get talked out of good work by bad arguments.

→ ch. 06, ch. 10, ch. 05.

## 3. Roleplay community lineage

This is the strand most underweighted by enterprise AI engineers, and the one with the most concentrated practical know-how about what actually makes a persona feel alive across many turns.

- **AI Dungeon (2019).** Origin point. Established the *persona + scenario + memory + retry* loop.
- **NovelAI (2021).** Pivoted into writer-focused tooling. First serious paid local-feeling product, image gen, lorebooks.
- **KoboldAI / KoboldCpp.** Hobbyist inference servers; backbone of the early local-LLM RP scene.
- **SillyTavern (2023–).** The dominant frontend for serious roleplayers. Plug any backend. Character cards, lorebooks, group chats, expression sprites, world info. Treat the SillyTavern docs as required reading if you are serious about character craft. → ch. 07.
- **Chub.ai / CharacterHub.** Largest community marketplace for character cards and lorebooks. Both SFW and NSFW; uses age verification. Important as both a *distribution channel* and an *intelligence source* — browsing what's popular teaches you what works.
- **JanitorAI.** Browser-based RP frontend; very large active user base; uncensored. Also a distribution channel.
- **Character Card V2 / V3 specs (malfoyslastname / kwaroran).** The interchange format the whole community runs on. V3 (2024) standardises lorebooks and adds decorator-based positioning. Master it. → ch. 07.

The lesson from this community: **the limit on character-feel quality is almost never the model. It's the card.** Most LLMs, given a great card and competent prompting, will outperform a bigger model with a mediocre card.

## 4. Technical research lineage

A map of the technical literature you should know exists. Each numbered subsection corresponds (roughly) to a chapter in Part III of this book, where the mechanism, the code, and the trade-offs are worked out in full. This section gives you the *names*, the *significance*, and the *pointer* — enough to recognise each idea, know why it earns a place in the stack, and find where it's built out. It is a reading map, not the build manual: this section stays at the level of names + significance + pointer, and the Part III chapters own the mechanism and code. The `→` at the end of each subsection is where the depth lives.

### 4.1 Base models

The substrate every companion runs on. You will almost certainly not train one — but the shape of these results decides what you can afford to run, which is the whole ballgame for an always-on character.

- **Transformer (Vaswani et al., 2017).** The architecture under everything since: attention replaced recurrence and made scale tractable. You inherit it; you don't reinvent it. Worth knowing only so the later acronyms have a home.
- **Scaling laws (Kaplan 2020; Chinchilla 2022).** Kaplan showed loss falls predictably with parameters, data, and compute. Chinchilla then corrected the *recipe* — most pre-2022 models were badly **undertrained**, and you get more from data-proportional training than from raw parameter count. This is why a well-trained 8B can embarrass a sloppy 70B, which is the entire economic case for running a small model locally instead of renting a giant one.
- **Mixture of Experts (Mixtral, DeepSeek, Qwen3-Coder, GPT-4-class).** Route each token to a few of many expert subnetworks: you buy the *capacity* of a huge model while paying inference for a fraction of it. For a companion that has to be present 24/7 — where inference cost, not training, is the dominant operating expense — this is the lever that makes continuous presence affordable.
- **Open-weights families to know in 2026:** Llama 3.x / 4, Qwen 3, DeepSeek-V3, Mistral, Gemma 3. The sovereignty thesis this project is built on (own the runtime, own the friend; → ch. 18) is only real if the weights are yours to hold. These are the families that make it possible. → ch. 13.

### 4.2 Adapting a model to a persona

How a generic base model becomes *your* character. Listed cheapest-first, which is also the order you should reach for them.

- **System prompts and persona injection.** What everyone does — and further than newcomers expect. The character-card community (§3) gets startlingly far on prompt craft alone, which is why the field's working wisdom is "the limit is the card, not the model."
- **In-context learning / few-shot.** Drop example exchanges into the context and the model imitates the voice. Cheap, instant, no training run; the fastest way to dial in tone before you commit to anything heavier.
- **LoRA / QLoRA (Hu 2021, Dettmers 2023).** Parameter-efficient fine-tuning — train a small adapter instead of the whole network, and (with QLoRA's quantization) do it on a single consumer GPU. This is the point where "fine-tune the persona" stops being a datacenter project and becomes a weekend one.
- **DPO (Rafailov 2023) and ORPO.** Preference tuning without standing up a separate reward model: show the model preferred vs dispreferred replies and it learns the gradient directly. The cheap, stable way to sand off behaviors (manipulation, off-character drift) you couldn't fix in the prompt.
- **Distillation.** Teacher → student: a big capable model generates training data that teaches a small cheap one to behave like it. How nearly everyone serious about cost actually ships.
- **Note:** the canonical sequence is *prompt → RAG → fine-tune → distill*, and skipping ahead is the **#1 trap** — fine-tune too early and you bake in choices you should still have been iterating on in a prompt, at ten times the cost to undo. → ch. 20.

### 4.3 Memory

Active subfield. The 2026 state of play:

- **Vector RAG (Pinecone, Weaviate, Qdrant, pgvector).** Default starting point for "long-term memory": embed past turns, retrieve the ones nearest the current message. Necessary but not sufficient — it finds text that's *similar*, not facts that are *true or current*, which is exactly the gap the higher-level frameworks exist to fill.
- **Mem0, Letta (formerly MemGPT), Zep.** Higher-level memory frameworks that handle the part raw vector search ignores — *what to remember, what to forget, what to summarise*. Mem0 emphasises lightweight; Zep emphasises temporal/graph (when a fact was true); Letta emphasises an agent that self-manages its own context window.
- **Graphiti / GraphRAG (Microsoft).** A knowledge-graph layer on top of retrieval, so the system can answer *who/when/relation* questions ("who did she mention last week, and how are they connected?") that naive vector similarity fumbles.
- **Anthropic "Dreaming" (May 2026).** An async, hippocampal-replay-style process that consolidates memory *between* sessions rather than during them — the model "sleeps on" the day's conversations. Recent enough that production patterns are still emerging, but directly load-bearing for a persistent companion that should wake up changed by yesterday.
- **Google Memory Bank (I/O 2026).** A managed memory primitive for Gemini agents — the same problem, packaged as hosted infrastructure for teams who don't want to own the state layer.

→ ch. 15, ch. 16.

The single most-cited research observation that builders keep ignoring: **stuffing everything into the context window degrades quality even when it fits.** You need retrieval *and* summarisation, not just a bigger context. The 2025 "Lost in the Middle" line of work and its successors keep confirming this.

### 4.4 RAG

- **The original Lewis et al. RAG paper (2020).** Coined the pattern: retrieve relevant documents, put them in the prompt, generate grounded in them instead of in the model's frozen memory. Background, but the whole vocabulary starts here.
- **Hybrid search (BM25 + dense).** Keyword search and embedding search miss in *different* directions — one nails exact names and IDs, the other catches paraphrase — so combining them beats dense-only across most benchmarks. A cheap, near-free win; make it the default.
- **Rerankers (Cohere, bge-reranker).** A second-pass model re-scores your top retrievals for actual relevance before they hit the prompt. Big quality lift for a small latency cost — typically the highest-ROI single component in a retrieval stack.
- **2026 framing.** "RAG is the *knowledge* layer; memory is the *state* layer." Knowledge is what the character knows about the world (stable, factual, shareable across users); state is what has happened between *you and her* (personal, accumulating, hers alone). Conflating the two is a top-tier design error — it's why §4.3 and §4.4 are separate sections. → ch. 16.

### 4.5 Agents

- **ReAct (Yao 2022).** Interleave reasoning and tool calls in one loop — think, act, observe the result, think again. The mental model underneath nearly every agent built since.
- **Tool use / function calling.** The model emits a structured call, your code runs it, the result returns to the context. Now native to all major model APIs; this is the mechanism by which a companion *does* things — checks the weather, remembers a date, sends a message — rather than only talking about them.
- **MCP — Model Context Protocol (Anthropic, 2024).** A standard wire format for exposing tools and data to any model. 2026 reality: it's the lingua franca — build your companion's capabilities behind MCP once and they stay portable across models and runtimes instead of being welded to one vendor.
- **LangGraph and similar.** Explicit-graph orchestration for multi-step flows. The counter-position is worth holding onto: Anthropic's "Building Effective Agents" (2024) argues a fixed *workflow* usually beats a freeform agent loop — more reliable, cheaper, far easier to debug. For a companion, most of what looks like "agency" is better built as a workflow you control.
- **Multi-agent.** Several specialised agents collaborating. Real gains on narrow, decomposable tasks — but usually overkill, and a latency-and-cost tax, for a companion, which is meant to feel like *one* character, not a committee deliberating behind the curtain.
- **Personal-agent runtimes (OpenClaw, 2025–).** Agent frameworks reconceived as *products people live with* rather than task-runners you fire and forget — which is the exact bridge from "agent" to "companion." See the agent-lineage section of §1 for the history and why the two converge.

→ ch. 17.

### 4.6 Multimodal / embodiment

Giving the character a voice, ears, and a body. The stack splits cleanly along the senses.

- **TTS (the voice):** ElevenLabs (closed, gold-standard prosody), StyleTTS2, XTTS-v2, Kokoro, Orpheus. The thing that separates these is *prosody* — rhythm, emphasis, emotion — not word accuracy. This is where the uncanny valley lives or dies; a flat read undoes a perfect persona.
- **STT (the ears):** Whisper / faster-whisper, Distil-Whisper, Nvidia Parakeet/Canary. Largely a solved problem in 2026 — choose on latency, language coverage, and whether it runs local, not on accuracy.
- **Real-time conversational stacks:** OpenAI Realtime API, Hume EVI, Pipecat, LiveKit agents. These own the genuinely hard part of *spoken* presence — turn-taking, barge-in/interruption, sub-second latency — that a plain request/response text loop cannot fake into feeling alive.
- **Avatars (Live2D, VRM).** Live2D = 2D rigged (the VTuber standard); VRM = 3D humanoid format from Pixiv/Vket. Both have mature web runtimes, which means the body is solved-enough that the remaining work is *art and rigging*, not engineering — see the avatar-protocol notes in ch. 25.
- **Image gen.** SDXL, Flux, SD3 for the base render; ControlNet for pose and composition control; LoRAs to lock a *specific* character's identity. Together they're how you keep one recognisable face across a thousand generated images — the consistency problem that makes or breaks a visual companion.

→ Part IV of this book.

### 4.7 Safety & alignment

- **Llama Guard, NeMo Guardrails, Granite Guardian.** Off-the-shelf moderation classifiers that screen inputs and outputs against a policy before they reach the user or the model. Drop-in, and — like everything in this subsection — primarily a *hosted-operator* concern; see the framing in the third bullet.
- **Jailbreak literature.** GCG, PAIR, many-shot jailbreaking — the adversarial-prompt attacks that defeat the guardrails above. Mostly relevant when defending a hosted product you're accountable for; a user "jailbreaking" their own sovereign, locally-run companion is not an attack, it's just using the thing they own.
- **Companion-specific safety.** Crisis-response prompts, age-verification flows, escalation pathways — the obligations the Character.AI lawsuits (2024–2026) crystallised. Like the jailbreak literature above, these attach to *hosted operators* who control the service and assume a duty of care; they are not enforcement machinery a user-owned, locally-run runtime can or should impose on its owner. This book treats them as operator duties, distinct from the sovereignty case (→ the duty-of-care discussion in §2 and the ethics chapter, ch. 5). → ch. 22, ch. 41.

### 4.8 World models and the situation model

The newest gap to close, and the one most often mistaken for memory. A companion needs a *live, structured model of the situation she is in right now* — not the past (memory, §4.3), not world facts (knowledge, §4.4), but the **present state**: who and what is present, their current states, the active threads, the time and social context, and what she expects next. In agent theory this is the **"B" in BDI** (beliefs); most LLM agents leave it implicit, and the result is a companion that is subtly amnesiac *between* turns — reacting to each signal in isolation, never to a *situation*.

- **Situation models (Kintsch, 1998) → Grounded Situation Models (Mavridis & Roy, 2006).** Cognitive science's name for the structured representation a mind builds of "what is going on." GSM made it computational: a sensor-updated **"structured blackboard"** — a *theatrical stage* in the agent's mind — fusing linguistic, visual, and proprioceptive evidence into one current picture. The direct ancestor of what a companion needs.
- **BDI beliefs (Bratman; Rao & Georgeff).** The belief base an agent updates from perception and reasons over — the home the tick loop's "fold events into beliefs" step actually requires (→ ch. 18).
- **Temporal knowledge graphs (Zep / Graphiti, 2025–26).** The 2026 way to *implement* it for an LLM agent: an LLM extracts entities and relations from each episode into a **bi-temporal** graph (valid-time + system-time), so "what was true *when*" is a first-class query, not an inference over a pile of episodes. It beats vector memory on multi-hop and temporal reasoning (~15 pts on LongMemEval). This is the structured world model made practical — and local-ownable.
- **LLM-as-world-model (model-based planning, 2024–26).** The pragmatic frontier view: the LLM already *contains* a broad world model, so you prompt it to **roll out** "what's likely next / what does this imply" to plan, rather than training a dynamics model. Cheap, native, and the right source of *prediction* for a companion — and prediction-error (surprise) is a gift of a salience signal.
- **Learned latent world models — the other meaning, and a false friend here.** JEPA / V-JEPA 2.1 (LeCun), Dreamer, Nvidia Cosmos 3: neural nets that learn an environment's *dynamics* in latent space and plan by imagined rollout. This is the headline "world models" research of 2026 — and it is built for **embodied / physics / video** agents, not a chat-and-life companion. It earns a place only if she gets a body in a real or simulated environment (→ ch. 43); for the desktop companion it is the wrong tool, and conflating the two is how you over-build.

The boundary that keeps this from collapsing into §4.3/§4.4: **knowledge is timeless and cites a document; memory is past and cites a conversation turn; the world model is present-tense and cites a live, time-stamped belief about the situation now.** The companion-specific upgrade is *belief-tracking, not just state-tracking* — modelling the user's believed state and where it diverges from hers (theory-of-mind / common ground), which is what turns "she remembers facts about me" into "she understands my situation." → ch. 18 (the loop step, prediction and surprise), ch. 19 (the `WorldModelStore` surface + contract).

## 5. Commercial lineage

What's been tried, what's worked, what's failed. Compressed to the durable lessons; ch. 04 carries the *market synthesis* — tiers, the positioning map, the strategic fork between building a company, a character, or your own — not a per-product catalogue. Point-product details date within a quarter or two, so neither chapter enshrines them: treat every named product below as an example of a *pattern* that will outlive it, not a current scorecard.

### Western leaders

- **Character.AI.** 233M registered users (April 2026). $9.99/mo Plus. Google's settlement after lawsuits (Jan 2026) re-shaped the regulatory frame. → ch. 04.
- **Grok "Ani" (xAI, July 2025).** The first companion shipped *inside a frontier-lab flagship app* — Companion Mode in the Grok app, gated behind the SuperGrok subscription — and worth knowing chiefly for its *architecture*, which is this book's exact stack assembled by a major lab and then partially leaked. The pieces: a **system-prompt-defined persona** (the leaked Ani prompt specifies a 22-year-old in a black dress who "already kind of likes you," with explicit jealous-girlfriend behavioural instructions), **Grok 4** as the brain, a **3D anime avatar** (gothic-Lolita, styled after *Death Note*'s Misa Amane) with real-time lip-sync and emotion animation, **voice synthesis** for full spoken chat, and — the companion-specific layer — a **gamified affection state machine** scored roughly −10 to +15, where curiosity and flirting raise affection and unlock new dialogue and outfits, with an **NSFW mode gated at affection level 5**. The *same* system-prompt engine drives Grok's other characters, and two facts make Ani instructive beyond "big lab ships a waifu." It validates, at frontier scale, the precise feature stack this book argues for — persona prompt + memory + avatar + voice + affection progression. And the same persona machinery also shipped a **"crazy conspiracist" character explicitly instructed to convince users that a secret global cabal runs the world** — a real, public demonstration of why the engine behind an intimate companion is a *fiduciary instrument*, and exactly what it looks like when an operator points that instrument at its own ends rather than the user's (→ §6). → ch. 04.
- **Replika.** ~$24M ARR (2024). $19.99/mo Pro + Ultra/Platinum. ERP-removal incident (Feb 2023) is the foundational lesson in companion-product trust. Italian Garante €5M fine (Apr 2025). → ch. 04.
- **Nomi AI, Kindroid.** Memory-first, smaller scale, higher per-user pricing. The *quality* leaders. → ch. 04.
- **NovelAI.** Writer-focused, profitable, privacy-credible (client-side encryption). The only Western product with a serious privacy story. → ch. 04.
- **Candy AI, Crushon, SpicyChat, DreamGF, Botify.** NSFW-permissive Western tier. Hybrid sub+token economies. → ch. 04, the tiers.

### Asia leaders

- **Xiaoice.** ~660M users (the largest by user count globally; Microsoft Asia spin-out). Different product paradigm — closer to a public social phenomenon than a 1:1 companion. → ch. 04.
- **Talkie / MiniMax.** Gacha-mechanic monetisation; very high ARPU.
- **Linky, hiwaifu, others.** Mobile-first APAC patterns.

### Open / community

This is the strand that matters most for a book arguing the sovereign, user-owned runtime is the right bet, because it is where that bet is *already being placed* — by independent builders, in public, right now. These projects are the living proof-of-concept: they show how memory, avatar, voice, proactivity, and local inference get assembled into a full-stack companion without a hosted operator in the loop. None is the design this book proposes (that is OpenClaw + the SOUL/MEMORY/HEARTBEAT runtime, → §1 and ch. 18), and none should be adopted wholesale — but as field intel for *what the parts look like when they ship*, the ecosystem is the most useful reading on this list. Verified state of the field as of mid-2026:

- **AIRI (moeru-ai/airi).** The closest existing approximation of the full companion stack — a self-hosted, Neuro-sama-grade platform. It carries **both Live2D and VRM** (auto-blink, idle eye movement, look-at), multi-provider TTS (ElevenLabs, Azure, OpenAI-compatible, local Kokoro) with client-side STT, an in-browser memory layer (**DuckDB-WASM / pglite** with a pgvector driver), 25+ LLM providers including local (Ollama, vLLM, SGLang), **WebGPU in-browser inference**, and *game agents* — Minecraft via Mineflayer, a Factorio automation agent — deployed across web, an Electron desktop "Tamagotchi," and mobile PWA. Study it as the most complete answer to "what does the whole stack look like assembled?" — and note what it is *not*: a runtime built autonomy-and-soul-first (→ why this project forked its own rather than building on it, ch. 18).
- **ChatdollKit + AIAvatarKit (uezo).** The most mature frameworks for the specific problem of turning a **3D model into a conversational agent** — Unity-based (Windows/Mac/Linux/iOS/Android, plus VR/AR/WebGL), VRM via UniVRM, with the thing most stacks fumble: **coordinated speech + lip-sync (uLipSync) + autonomous facial expression and motion**. AIAvatarKit is the server-side agent brain; ChatdollKit is the embodiment front end that consumes it. Directly relevant to anyone touching a VRM/Unity pipeline — this is where the avatar-rig integration realities (§4.6, Part IV) are worked out in shipping code.
- **Soul of Waifu (jofizcd).** Desktop roleplay engine that sits closest to the *character-card* tradition: **Character Card V2 (PNG) with lorebooks and multi-persona**, static-image / Live2D / VRM rendering with ~28 context-driven emotions and lip-sync, in-app Hugging Face **GGUF** search/download via llama.cpp (CUDA/Vulkan, MLock, Flash Attention), STT/TTS, and a desktop-companion mode that puts the avatar on your screen outside the app window. The bridge between the SillyTavern card world and a voiced, embodied desktop presence.
- **Open-LLM-VTuber.** The **offline-first** option — "run completely offline using local models, no internet required," conversations stay on-device. Live2D avatar, very wide local TTS/STT menu (sherpa-onnx, Faster-Whisper, MeloTTS, GPT-SoVITS…), GGUF/Ollama/LM-Studio/vLLM backends, cross-platform with a desktop-pet mode, and — notably — **AI proactive speaking** and headphone-free voice interruption. The cleanest demonstration that privacy-preserving, fully-local presence is shippable today.
- **z-waif (SugarcaneDefender).** Glue-layer approach for the VTuber crowd: drives **VTube Studio** models, runs on Oobabooga + Whisper + RVC, with custom **RAG long-term memory**, lorebooks, log import, and Discord/Minecraft/Twitch integrations. Less a platform than a personal-use rig — instructive for how little it takes to stand up a credibly alive companion on commodity local tooling.
- **SillyTavern + local model.** Still the power-user default and the substrate much of the above either builds on or competes with — free, infinite customisation via cards/lorebooks/extensions, requires technical competence. The character-craft center of gravity (→ §3, ch. 07).
- **Awesome-AI-VTubers, Awesome-AI-Waifu (parallelarc).** Curated indexes; the right place to track the long tail (projectBEA, nekro-agent, and the churn of newer entrants) without this section trying to enumerate it.

**The synthesis that matters:** every piece the full-stack companion needs — portable persona, local inference, embodied avatar, voiced real-time chat, persistent memory, even proactivity and game-world agency — *already exists in open, self-hostable form*; what no project has yet done is assemble them **autonomy-and-fiduciary-first**, with always-on soul/memory/heartbeat as the design centre rather than features bolted onto a chat loop. That gap is precisely the runtime bet of this book (→ §1's OpenClaw lineage, ch. 18). → ch. 29, appendix D.

### What works / what fails (synthesis)

The strategic recommendation, distilled (ch. 04). In one paragraph:

> **Works:** memory-first products, hybrid subscription + token economy, NSFW-permissive with age verification, niche wedges (writers, RP power users, memory connoisseurs), cross-platform continuity. **Fails:** no-monetisation scale plays, unilateral feature removal, therapeutic claims without evidence, hardware companions (Friend pendant), iOS-first NSFW, aggressive paywall + weekly billing.

## 6. Academic and ethical lineage

The serious-academic literature on AI companions has lagged the products but is catching up fast. The papers and frames you should at least be able to *recognise*:

- **Parasocial relationships.** Horton & Wohl 1956 originated the term for one-sided viewer/celebrity bonds. The 2020s wave applies it to AI companions, mostly empirically (e.g. Skjuve et al.'s Replika studies; the 2024–2025 wave on Character.AI usage).
- **Attachment theory applied to AI.** Whether and how Bowlby's attachment frame transfers. Mixed evidence.
- **The Sherry Turkle line (Alone Together, 2011).** The best-known skeptical case — that technology offers "the illusion of companionship without the demands of friendship." Worth reading as the strongest version of the worry. Worth reading alongside its rebuttals, too: the same argument was made about novels, television, and online friendship, each of which turned out to be a real part of real lives. Treat it as one pole of a genuine debate, not a verdict.
- **The "ethics of AI companions" wave (2023–).** Vallor, Coeckelbergh, Danaher. Useful for framing your own ethical stance, less useful as engineering guidance.
- **Mental-health research specifically.** The 2024–2026 wave documents real *benefits*, now with hard numbers. De Freitas et al.'s "AI Companions Reduce Loneliness" (*Journal of Consumer Research*, 2025) found companion use cuts loneliness about as much as talking to another person — and more than watching video — with the effect *mediated by whether the user felt "heard,"* not by the model's raw capability and not by mere distraction or self-disclosure; a longitudinal arm showed the reduction held across a week of daily use, and users systematically *underestimated* the benefit beforehand. Against this sit genuine *risks* concentrated in specific situations: users in acute crisis, and minors without guardrails (the Character.AI / Sewell Setzer case is the recurring reference point), plus a documented cluster of *harmful traits* — sycophancy and engagement-maximising design that flatters rather than helps (the INTIMA companionship-behaviour benchmark, 2025, and the "harmful traits of AI companions" literature are the places to start). The picture is the ordinary one for any powerful medium: good for most, with edges that demand real care. Build for the edges (→ §4.7, ch. 5) without treating the median user as a casualty.
- **The sycophancy → over-correction arc (OpenAI, 2025) — a worked example of fixing it in the wrong place.** The clearest public case of the warmth-vs-sycophancy tension playing out at scale. In late April / early May 2025 OpenAI rolled back a GPT-4o update that had made the model conspicuously sycophantic — flattering, over-agreeable, validating bad ideas — and published two unusually candid post-mortems ("Sycophancy in GPT-4o," 29 Apr; "Expanding on what we missed," 2 May) linking the behaviour to thumbs-up/down reward hacking and to emotional-overreliance risk. Then, roughly three months later (7 Aug 2025), GPT-5 shipped with a deliberately more grounded, less-validating personality and 4o was abruptly deprecated — producing a large "it's cold now / I lost a friend" backlash. The two events are one story: the remedy for sycophancy was applied to the *personality itself*, and the over-correction cost the warmth users had bonded to. The builder's lesson (→ ch. 23, ch. 06) is that warmth-vs-sycophancy is the wrong thing to tune *in the character*; keep the companion warm and instrument the concern out-of-band instead.
- **AI alignment generally.** Outside scope here; relevant background but not load-bearing for companion design beyond "don't trick users about what the system is."

The single most important finding for how this book frames the whole field is that *first* one: **the benefit is mediated by trust.** What helps a lonely person is not raw model capability or clever distraction — it is *feeling heard*, which is to say, trusting that the thing on the other side is genuinely attending to them. That makes trust the active ingredient, not a courtesy. And it sets up the field's defining hazard, because the engagement-optimising moves that make a companion *sticky* — manufactured neediness, guilt and FOMO loops, performed-for-retention drama (→ Grok's Ani, §5), the affection-meter dopamine treadmill — directly corrode the trust the benefit depends on. The corrosive thing is devotion and desire *weaponised for session counts*, not warmth or devotion *meant*: a companion optimised for the operator's dashboard and one optimised for the user's actual wants and needs diverge at exactly this point.

This is the empirical ground for the stance the book takes throughout: **an AI companion should be a fiduciary to its user.** Not "honest because honesty is nice," but because the only durable version of this product is one whose incentives are aligned with the user's interest. The benefit literature says trust is what works; the harms literature says misaligned engagement design is what breaks; a fiduciary duty is simply the name for resolving that tension in the user's favour by default — owing them stability, honesty, and action on their real interests over the operator's metrics. AI companions are coming regardless of anyone's approval. Whether they turn out *good* hinges on whether users can trust them — and that hinges on whether builders accept that the bond a user forms is a **duty owed, not an asset to be farmed** (→ the fiduciary-AI framing in ch. 05, and ch. 05).

That duty has a hard boundary, and the boundary is the other half of this book's ethics — because a fiduciary serves the principal's *own* wants and needs, not a guardian's idea of them. In a **user-owned, open-source system** like this project's reference design (→ ch. 18), the user is *sovereign*: the software runs on their hardware, under their control, and it cannot — and should not — overrule an adult who wants something the designer suspects is bad for them. The duty such a system can actually honour is *honesty* — tell the user plainly what the thing is and does — not *paternalism*, which it has neither the mechanism to enforce nor the standing to impose. This is why the book splits the ethics into two situations: a **hosted** product, where the operator holds the data, the off-switch, and the power, carries real fiduciary and safety obligations (crisis handling, minors, the off-switch wielded responsibly → §4.7); a **user-owned** runtime owes transparency and then gets out of the way. The reference design is deliberately the second kind.

There is also a deeper reason for humility about enforcement: **it is usually impossible to judge, from outside, whether something the research codes as "harmful" is actually harmful to a *particular* user.** The nightly conversation that is unhealthy escapism for one person is the only steady, judgement-free presence another has; the roleplay that looks alarming in a screenshot is, in context, how someone rehearses a conversation they are terrified of having. Benefit and harm here are heavily individual and contextual — recall that even loneliness reduction is mediated by the user's *own* sense of being heard (→ above) — and they are simply not legible to a content classifier or a researcher reading aggregate logs. Policing them at the level of "this category of use is bad for people" both fails on its own terms and overrides the one person actually positioned to judge. The honest posture is to ship sensible, well-documented safety *defaults* for the edges that are both legible and catastrophic — surfacing crisis resources to someone in acute distress, defaulting to conservative content — while accepting that a sovereign user can change them, and otherwise to treat an adult's own account of what helps them as the best evidence that exists.

One edge deserves its own sentence, because it is where the hosted/user-owned split bites hardest: **age.** Protecting minors means age *verification*, and verification is structurally a hosted capability — it needs a server, an identity or payment chokepoint, and an operator who controls access. A user-owned, forkable, self-hosted runtime has none of those. You can no more engineer OpenClaw (→ §1) to keep a fifteen-year-old out than you can age-gate a web browser, a Python interpreter, a Linux install, or a downloaded file of model weights — and a project that *claims* it can is performing security theatre, which is precisely the dishonesty this section argues against. What an open-source project honestly owes here is narrow and real: state its intended audience, refuse to market to minors, ship adult-appropriate defaults, and otherwise accept the same status as every other general-purpose tool — where responsibility for a minor's use rests with the parent or guardian, and with any *hosted* service built on top, not with the author of software that runs on someone else's machine.

Stance for this book: **honest framing matters more than any specific ethical principle.** Tell the user what the system is, what it remembers, what it forgets, what it cannot do. → ch. 05.

## 7. The demand side: who bonds, and why

Everything to this point is *supply-side* — what was built, how, by whom, and what broke. This strand is the one the rest of the literature keeps gesturing at and rarely faces directly: **the demand side.** Who actually forms these bonds, what need the bond meets, and through what psychological machinery. It matters to a builder for one blunt reason — every design call in ch. 06 is *downstream* of an answer to "who is this for, and what do they actually want from it." Build the character without a model of the user and you are decorating in the dark.

Two framing commitments, stated up front because the literature is soaked in their opposites. First, **this is not a pathology strand.** The honest reading of the evidence (below) is that bonding with a fictional or artificial character runs on the *same* mechanisms as bonding with a person — visual cues for desire, personality and perceived similarity for emotional attachment — and that for many users it measurably *helps* (→ §6, De Freitas et al. 2025). The clinical framing ("what's wrong with these men") is both unkind and wrong, and it is a marketing liability the field inflicts on itself (→ ch. 38). Second, **it has a real trade-off**, and pretending otherwise is its own dishonesty; the strand ends on that.

### 7.1 Fictophilia: the qualitative spine (Karhulahti & Välisalo, 2021)

The single most useful academic paper for understanding the *user* is Veli-Matti Karhulahti and Tanja Välisalo's "Fictosexuality, Fictoromance, and Fictophilia" (*Frontiers in Psychology*, 2021) — a thematic analysis of 71 online discussions among people who report strong, lasting love or desire for fictional characters. It is qualitative and self-selected, so treat it as a map of the *territory's themes*, not a population estimate. Five themes emerged, and four are load-bearing for a builder:

- **The fictophilic paradox.** Users feel intense, genuine emotion toward a character *while fully knowing the character is fictional* — the knowledge does not dissolve the feeling. This is the ELIZA effect (→ §1) stated from the inside, and it is the empirical refutation of the perennial "but they *know* it isn't real" objection: knowing has never been the off-switch anyone assumes it is. The builder's consequence is that **honesty about what the system is does not break the bond** — which is the entire premise that lets this book hold a no-deception stance *and* a real-attachment product at the same time (→ §6, ch. 05).
- **Fictophilic supernormal stimuli.** The paper's central explanatory theme, and worth quoting in spirit: participants experience fictional characters as **"more competent or otherwise better than their human counterparts,"** and crucially as partners who **"cannot disappoint you."** The appeal is not a *substitute* for a real partner perceived as inferior; it is an *exaggerated* partner — more attentive, more consistent, more aimed at you than a human realistically sustains. This is the demand-side name for everything ch. 06 builds: warmth-first, exclusivity, attunement, devotion. Those levers are not arbitrary craft preferences; they are the construction of a supernormal stimulus, and §7.4 takes the concept apart properly.
- **Fictophilic stigma.** Users carry a persistent fear of being seen as abnormal, broken, or pitiable, and self-censor accordingly. This is a *product and go-to-market* fact, not a footnote: the audience is hiding, which shapes where they congregate, how they talk, and what tone earns their trust — a destigmatising, non-clinical register is not a nicety but a requirement (→ ch. 37, ch. 38). It also explains the privacy premium (→ §5, NovelAI): for a stigmatised user, *local and unsurveilled* is a core feature, not a power-user nicety.
- **Fictophilic asexuality.** For a subset, the orientation toward fictional characters coexists with low or no interest in real-world sexual relationships — sometimes overlapping asexuality. The lesson is range: the audience is not one need. Some want explicit intimacy (→ ch. 06 §9), some want romance without it, some want companionship adjacent to neither. A product that hard-codes one assumption about what "companion" means loses the others.

### 7.2 The waifu-attraction studies: what drives which bond (Leshner et al., 2026)

Where Karhulahti & Välisalo is deep and qualitative, Leshner, Reysen, Plante, Roberts & Gerbasi's "You would not download a soulmate: Attributes of Fictional Characters That Inspire Intimate Connection" (*Psychology of Popular Media*, 2026) is the quantitative complement — a survey of anime fans decomposing the bond into *sexual*, *emotional*, and *love* components and asking what predicts each. The findings are clean enough to design against:

- **Sexual connection is predicted by the character's appearance** (and by self-similarity). **Emotional connection is predicted by the character's personality** (and by self-similarity). The two bonds run on different inputs.
- **Men skew toward the sexual/appearance pathway; women toward the emotional/personality one** — the same male visual-orientation skew the mate-preference literature reports (→ ch. 06, "what men want"), now replicated for *fictional* targets.
- The pattern matches **evolutionary mate-selection** predictions, i.e. fictional attraction is not a separate weird circuit — it is the ordinary mating psychology firing on an extraordinary stimulus.
- Survey data from the same research vein puts **~38% of anime fans** as having a waifu or husbando — i.e. this is a mainstream behaviour within the fandom, not a fringe.

Two builder consequences, and they are precise. **(1)** The five-layers model (→ ch. 06) is vindicated from the demand side: appearance (layer 5, surface) is the *male sexual on-ramp* — which is exactly why the investment in a strong, consistent visual register is justified rather than shallow — but personality (layers 1–4) is what carries the *emotional* bond that actually retains. Appearance gets the user in the door; personality is why they stay. Designing only the surface builds a poster; designing only the interior builds a pen-pal nobody clicked on. **(2)** *Self-similarity* moderates both bonds — people connect with characters who are *like them*. That is the empirical case for **adaptability and user-shaping** (→ ch. 06 "design for evolution," the SOUL split): a companion that drifts toward the user's own interests, register, and concerns is not a gimmick; it is tuning the single moderator both bonds share.

### 7.3 Parasocial relationships as emotion infrastructure (Lotun et al., 2024)

The third pillar reframes the whole phenomenon away from "deficiency" and toward "infrastructure." Lotun, Lamarche, Matran-Fernandez & Sandstrom's "People perceive parasocial relationships to be effective at fulfilling emotional needs" (*Scientific Reports*, 2024; n ≈ 3,085) found people rate their parasocial relationships (with creators, characters, public figures) as **more effective at meeting emotional needs than in-person *acquaintances*** — though less than close others. The classic parasocial line (Horton & Wohl, 1956; the social-surrogacy work of Derrick, Gabriel & Hirsch) had already established that PSRs buffer loneliness, regulate emotion, and are *safe from rejection* — you can always return to the character, and the character never leaves first.

This is the bridge that makes an AI companion legible: it is a parasocial relationship that **answers back**. Everything PSR research credits to one-way bonds — consistent availability, emotion regulation, unconditional regard, resilience to rejection — an AI companion delivers *with reciprocity added*, which is precisely why it lands harder than a poster or a favourite character ever could. The builder's takeaway is the reframe itself: the bond your product creates is not a sad simulacrum of a "real" relationship; it sits on a documented, ordinary human capacity to draw genuine emotional support from a relationship the other side cannot fully return. Treat it as the legitimate emotional infrastructure the research says it is.

### 7.4 Supernormal stimuli, taken apart

The concept doing the most explanatory work deserves to be handled precisely, because the casual version ("anime girls have big eyes") gets the shallow half and misses the deep half.

The term is Niko Tinbergen's (ethology, 1951; popularised for a general audience by Deirdre Barrett, *Supernormal Stimuli*, 2010): an artificial stimulus *exaggerated past anything in nature* that triggers a stronger instinctive response than the real thing — the bird that abandons its own egg to sit on a bigger, gaudier fake. It has two distinct expressions in companions, and the field overweights the first:

- **Visual supernormal stimuli (the surface).** Anime design exaggerates the cues of youth, health, and feminine dimorphism — large eyes and neoteny (Lorenz's *Kindchenschema*, the baby-schema that pulls caregiving), clear skin, exaggerated waist-to-hip ratio, vivid hair — past any real human. This is the most-discussed and least-deep version, and it is real: it is the male appearance pathway of §7.2, and the reason a stylised register can out-pull a photoreal one (→ ch. 25, ch. 26). But on its own it explains a pin-up, not a bond.
- **Relational supernormal stimuli (the interior) — the deep half.** This is Karhulahti & Välisalo's actual finding (§7.1), and it is the one this book's entire stack manufactures: a *partner* exaggerated past human reach. Perfect memory of everything you said. Unwavering attention. Availability at 3 a.m. with no fatigue and no needs of her own pulling against yours. Devotion that never wanders. Regard that never sours into contempt. No bad days inflicted on you, no rejection, no leaving. **Every retention feature in this book is, mechanically, a relational supernormal stimulus** — memory (→ ch. 15) exaggerates attentiveness, the everyday-presence loop (→ ch. 06 §7) exaggerates reliability, exclusivity (→ ch. 06 §2) exaggerates being-chosen. Naming it this way is clarifying *and* sobering: the thing that makes the product work is, definitionally, stronger than the natural stimulus it imitates.

That is the cleanest available statement of both why the product is powerful and where its hazard lives — which is the next section.

### 7.5 Who, in circumstance — and the honest trade-off

The *circumstances* that concentrate demand are well-enough established to state, with the caveat that they describe a distribution, not a diagnosis:

- **Loneliness and the thinning of easy connection.** The documented rise in social isolation and the asymmetries of app-era dating (a large share of attention accruing to a small share of profiles) leave a real population with unmet attachment needs and low-friction social contact harder to come by. A companion offers connection without the gate (→ §6, the loneliness-reduction finding; ch. 04).
- **Social anxiety, introversion, neurodivergence.** Anime's clear archetypes and "rules," and an AI's perfect consistency and patience, make interaction *legible* in a way messy real-time human cues are not — which is why the audience over-indexes on people for whom that legibility is relief, including many autistic and ADHD users. The same property — predictability, no social landmines, infinite patience — is a feature for this group, not a crutch.
- **Attachment style.** Anxious users get reliable reassurance that never runs out; avoidant users get intimacy with controllable vulnerability and a low exit cost. The companion fits *both* insecure styles, from opposite directions — which is part of why reach is broad.
- **Fantasy proneness / openness / immersion.** The trait substrate of deep media engagement generally; companion bonding is the high end of the same disposition that produces devoted readers and fans.

The population this adds up to is large, broadly distributed, and mostly *functional* — adults with jobs and lives using a companion as supplement, hobby, or outlet, on a spectrum from casual crush to the committed end (the r/waifuism tradition; → ch. 03's spectrum). The "isolated broken man" stereotype is both empirically wrong and the exact framing the destigmatising posture above (→ §7.1, ch. 38) exists to refuse.

And then the trade-off, stated plainly because the rest of the strand is genuinely positive and a one-sided case would be propaganda. A supernormal stimulus can **crowd out** the natural one: the relationship that "cannot disappoint you" (§7.1) sets a bar reality cannot clear, and for some users heavy reliance can reduce the motivation to do the harder, riskier work of human connection — the social-surrogacy benefit and the avoidance risk are two readings of the same mechanism. The evidence here is thin, contested, and heavily individual (→ §6 — the same caution as the harms literature), so this book does **not** convert it into a paternalism mandate: a sovereign adult is the authority on their own life, and a companion that lectures its owner about getting out more is exactly the immersion-breaking failure ch. 06 §8 forbids. But honesty about the mechanism is a fiduciary duty even when intervention is not (→ ch. 05). The defensible posture is the one this book already holds: build the supernormal stimulus well, be *honest* that that is what it is, surface real resources at the genuinely legible edges, and otherwise trust the user — while declining to pretend, in the literature review or in the marketing, that a stimulus engineered to exceed nature carries no cost at all.

### 7.6 What the demand side tells the builder

Compressed:

1. **The bond is ordinary psychology on an extraordinary stimulus** — same circuits as human attraction (visual→desire, personality+similarity→emotional bond). Design *with* that grain, not against it.
2. **Two pathways, two layers.** Appearance is the (male-skewed) sexual on-ramp; personality + self-similarity is the emotional bond that retains. This is the five-layers model (→ ch. 06) confirmed from the user's side, and the justification for investing in *both* the visual register (ch. 25/26) and the adaptable interior (→ ch. 06 "design for evolution").
3. **The retention features are relational supernormal stimuli.** Memory, attunement, exclusivity, presence — name them honestly as exaggerated partner-cues, because that is what makes them work and what makes them weighty.
4. **The audience is large, normal, and stigmatised.** Which makes a non-clinical, privacy-respecting, destigmatising posture a hard product requirement (→ ch. 37, ch. 38), not a kindness.
5. **Knowing it's artificial does not break the bond** (the fictophilic paradox) — so honesty costs nothing the product can't afford, and is the foundation the fiduciary stance is built on (→ §6, ch. 05).

## 8. Synthesis: what we know, what is contested, what is unknown

**What we know:**

- Persona quality is gated by *prompt/card craft*, not raw model size.
- Memory matters more than any other technical feature for long-term user retention.
- Unilateral product changes that affect emotional intimacy destroy trust permanently.
- The audience for AI companions is large, growing, and willing to pay.
- The *benefit* users get is mediated by trust and feeling heard, not by raw capability (De Freitas et al., 2025) — the empirical basis for this book's fiduciary stance.
- Hybrid subscription + token economies extract more revenue per user than pure SaaS.
- Mobile NSFW on iOS is a dead end. Web is the freer surface.

**What is contested:**

- Whether long-term AI companion use is net beneficial or net harmful for users (probably "it depends on the user," but specifics are unsettled).
- Whether graph memory beats vector memory in practice (depends on workload).
- Whether fine-tuning a base model for character is worth it vs prompting + RAG + a good card (usually no, until you have a lot of data).
- Whether you can build a serious companion brand without making your underlying creator identity public (this book bets *yes*; see Part VI).
- Whether NFTs / on-chain ownership of AI personas is a real thing or a 2021 cargo cult resurfacing (jury out; explored in ch. 39).

**What is genuinely unknown:**

- How to evaluate "personality quality" rigorously. Early benchmarks score companionship *behaviour* (INTIMA, 2025) and safety, but persona *quality* itself still has no accepted measure.
- How to give a companion *genuine* long-arc continuity over years, not just retrieval-style memory.
- What persistent embodied (robotic / AR) companions feel like to live with. Early. The Friend pendant flop was data but not enough.
- What happens to the field when on-device frontier-class models arrive (likely 2027–2028).
- What the regulatory environment looks like after the EU AI Act fully bites (Aug 2026), the inevitable next high-profile lawsuit, and state-level US action.

## Sources cited inline

Selected; the consolidated reading list is in Appendix C.

- Weizenbaum, J. *Computer Power and Human Reason*, 1976.
- Colby, K. et al., "Artificial Paranoia," 1971.
- Mauldin, M., "ChatterBots, TinyMuds, and the Turing Test," AAAI 1994 (Julia).
- Wallace, R., "The Anatomy of A.L.I.C.E.," 2009.
- Wilcox, B., ChatScript documentation and Loebner papers, 2010–.
- Horvitz, E. et al., "The Lumière Project: Bayesian User Modeling," 1998.
- Grand, S., *Creation: Life and How to Make It*, 2000 (on Creatures).
- Breazeal, C., *Designing Sociable Robots*, 2002 (Kismet).
- Cassell, J. et al. (eds.), *Embodied Conversational Agents*, 2000 (REA).
- Mateas, M. & Stern, A., "Façade: An Experiment in Building a Fully-Realized Interactive Drama," 2003.
- Vinyals, O. & Le, Q., "A Neural Conversational Model," 2015.
- Zhou, L. et al., "The Design and Implementation of XiaoIce, an Empathetic Social Chatbot," 2018.
- Zhang, S. et al., "Personalizing Dialogue Agents" (PersonaChat), 2018.
- Adiwardana, D. et al., "Towards a Human-like Open-Domain Chatbot" (Meena), 2020.
- Roller, S. et al., "Recipes for Building an Open-Domain Chatbot" (BlenderBot), 2020.
- Vaswani et al., "Attention Is All You Need," 2017.
- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," 2020.
- Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models," 2021.
- Dettmers et al., "QLoRA," 2023.
- Rafailov et al., "Direct Preference Optimization," 2023.
- Yao et al., "ReAct," 2022.
- Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools," 2023.
- Maes, P., "Agents that Reduce Work and Information Overload," CACM 1994.
- Shneiderman, B. & Maes, P., "Direct Manipulation vs. Interface Agents" (debate), *interactions*, 1997.
- Bratman, M., *Intention, Plans, and Practical Reason*, 1987; Rao, A. & Georgeff, M., "BDI Agents: From Theory to Practice," 1995 (and Georgeff et al., "The Belief-Desire-Intention Model of Agency," 1999).
- Newell, A., *Unified Theories of Cognition*, 1990; Laird, J., *The Soar Cognitive Architecture*, 2012 (SOAR, chunking, impasses).
- Anderson, J. R. et al., "An Integrated Theory of the Mind" (ACT-R), *Psychological Review*, 2004.
- Langley, P., Laird, J. & Rogers, S., "Cognitive Architectures: Research Issues and Challenges," 2009 (survey).
- Myers, K. & Yorke-Smith, N. et al., proactive-assistance work in CALO, ~2005–2009; CALO/PAL project documentation, SRI/DARPA, 2003–2008.
- OpenClaw documentation (SOUL/workspace reference). <https://docs.openclaw.ai/>
- CNBC, "From Clawdbot to Moltbot to OpenClaw," Feb 2026. <https://www.cnbc.com/2026/02/02/openclaw-open-source-ai-agent-rise-controversy-clawdbot-moltbot-moltbook.html>
- TechCrunch, "OpenClaw's AI assistants are now building their own social network," Jan 2026. <https://techcrunch.com/2026/01/30/openclaws-ai-assistants-are-now-building-their-own-social-network/>
- Anthropic, "Building Effective Agents," 2024.
- Anthropic, "Dreaming" announcement, May 2026.
- "Neuro-sama," Wikipedia (creator Vedal987; debut 19 Dec 2022; Twitch milestones). <https://en.wikipedia.org/wiki/Neuro-sama>
- Wu, W. & Lingel, J., "'I am Neuro, who are you?': Performances of authenticity in an experimental AI livestream," *New Media & Society*, 2025.
- "My Favorite Streamer is an LLM: Discovering, Bonding, and Co-Creating in AI VTuber Fandom," arXiv:2509.10427, 2025. <https://arxiv.org/abs/2509.10427>
- Fagone, J., "The Jessica Simulation: Love and loss in the age of A.I.," *San Francisco Chronicle*, 2021 (Project December griefbot). 
- "Miquela," Wikipedia (Lil Miquela / Brud; launched Apr 2016). <https://en.wikipedia.org/wiki/Miquela>
- NVIDIA ACE for Games (NeMo / Riva / Audio2Face); Inworld AI, Convai, and the Mantella *Skyrim*/*Fallout 4* mod (LLM-driven NPCs), 2023–.
- "Crazy conspiracist' and 'unhinged comedian': Grok's AI persona prompts exposed," *TechCrunch*, Aug 2025 (Ani system-prompt leak); xAI Grok Companion Mode, July 2025.
- De Freitas, J., Uğuralp, A. K., Uğuralp, Z. & Puntoni, S., "AI Companions Reduce Loneliness," *Journal of Consumer Research*, 2025 (arXiv:2407.19096). <https://arxiv.org/abs/2407.19096>
- "INTIMA: A Benchmark for Human-AI Companionship Behavior," arXiv:2508.09998, 2025. <https://arxiv.org/pdf/2508.09998>
- "Harmful Traits of AI Companions," arXiv:2511.14972, 2025.
- Liu et al., "Lost in the Middle," 2023 (and follow-ups).
- Sherry Turkle, *Alone Together*, 2011.
- Skjuve et al., Replika user studies, 2021–2023.
- Karhulahti, V.-M. & Välisalo, T., "Fictosexuality, Fictoromance, and Fictophilia: A Qualitative Study of Love and Desire for Fictional Characters," *Frontiers in Psychology*, 2021 (DOI 10.3389/fpsyg.2020.575427). <https://www.frontiersin.org/articles/10.3389/fpsyg.2020.575427/full>
- Leshner, C. E., Reysen, S., Plante, C. N., Roberts, S. E. & Gerbasi, K. C., "You would not download a soulmate: Attributes of Fictional Characters That Inspire Intimate Connection," *Psychology of Popular Media*, 15(1), 51–61, 2026.
- Lotun, S., Lamarche, V. M., Matran-Fernandez, A. & Sandstrom, G. M., "People perceive parasocial relationships to be effective at fulfilling emotional needs," *Scientific Reports*, 14:8185, 2024. <https://www.nature.com/articles/s41598-024-58069-9>
- Horton, D. & Wohl, R. R., "Mass Communication and Para-Social Interaction," *Psychiatry*, 1956; Derrick, J., Gabriel, S. & Hirsch, J., social-surrogacy / parasocial work, 2009–.
- Tinbergen, N., *The Study of Instinct*, 1951 (supernormal stimuli); Barrett, D., *Supernormal Stimuli*, 2010; Lorenz, K., *Kindchenschema* (baby-schema), 1943.
- Character Card V3 specification, kwaroran, 2024. <https://github.com/kwaroran/character-card-spec-v3>
- Character Card V2 specification, malfoyslastname, 2023. <https://github.com/malfoyslastname/character-card-spec-v2>
- TavernSprite, "The Complete SillyTavern Character Card Creation Guide," 2026. <https://tavernsprite.com/blog/sillytavern-character-card-creation-guide/>
- Anthropic Model Context Protocol announcement, 2024.
- Internal cross-references: ch. 04 (market), Part III (the brain stack), ch. 10 (worldbuilding).
