# 43 — Embodied and Robotic Companions

## The state of the form (mid-2026)

Two things changed since the last revision of this chapter, and both matter more than the humanoid-robot headlines that get the attention. A cheap, open, hackable companion robot now exists and has shipped in five figures. And the AR-glasses surface stopped being a rumour and started shipping with a third-party SDK. The rest of the field looks much as it did.

**What shipped, and to whom:**

- **AI glasses became a real consumer category.** EssilorLuxottica sold over 7 million Meta AI glasses in 2025 — more than triple the prior two years combined. **Meta Ray-Ban Display** (with an in-lens display and the sEMG Neural Band) sold hard enough that Meta *paused* its international rollout to keep up with US demand; forecasts put 2026 AR-glasses shipments near 950,000 units. Crucially, the **Meta Wearables Device Access Toolkit** entered developer preview — camera, audio, display, frame-tap gestures, and neural-band input, reachable from a native iOS/Android app or a web app — with general availability for third-party publishing targeted for 2026.
- **Reachy Mini** (Pollen Robotics / Hugging Face / Seeed Studio). An 11-inch expressive desktop robot — 6-DoF head, full body rotation, animated antennas, wide-angle camera, four mics and a speaker — **fully open-source and programmable in Python**, at **$399 (Lite, tethered) / $499 (Wireless, onboard Raspberry Pi)**, with an install base approaching 10,000 units in early 2026 and an app store built on the Hugging Face ecosystem. It is the first credible *open* body a solo developer can ship a character onto without asking anyone's permission.
- **The cheap affection tier consolidated.** Casio's **Moflin** ($429, US release Oct 2025), **Ropet** ($299), Mixi's **Romi**, Loona's DeskMate — a whole shelf of sub-$500 desktop creatures, most of them LLM-connected, most of them promising companionship and nothing else.
- **Clinical and eldercare embodiment kept quietly working.** **PARO** remains an FDA Class II device deployed in 30+ countries with a real (if methodologically uneven) evidence base for reduced agitation and improved mood in dementia care. **ElliQ** took Kanematsu investment in Sept 2025 for a 2026 Japanese launch. The elder-care assistive robot market is around $3.9B in 2026.

**What conspicuously did not:**

- **Friend pendant (Avi Schiffmann).** The reference failure. Roughly 3,000 units sold and 1,000 shipped at $129 against ~$8M raised; a $1M NYC subway campaign that was mass-vandalised ("AI is not your friend"); a CNN profile framing it as *the* symbol of the AI backlash; an entry in the Museum of Failure. No obvious affordance, ambient listening, an ambiguous value proposition — the AI-hardware graveyard alongside Humane's Pin and Rabbit's R1.
- **Gatebox pivoted away from you.** The original Azuma Hikari was discontinued in Aug 2024 (a crowdfunded "Hikari V2" with ChatGPT integration followed, chat integration landing May 2025), the company was acquired by LINE in April 2025, and its live business is now **B2B**: "AI Part-timer" character kiosks doing customer service in bookstores and bus terminals. The consumer holographic waifu box did not find its market; the character-as-service business did. Read that as the single most honest datapoint in this chapter (→ ch. 02 §1, persona-as-product).
- **Apple left the field.** Vision Pro 2 and Vision Air are reportedly shelved; Apple's Ray-Ban-style AI glasses slipped to late 2027 (mass production Q2 2027 at the earliest), and true waveguide AR glasses to ~2029. Apple ships no new head-mounted device in 2026. **The near-term embodiment surface is effectively Meta's alone** — which is a strategy problem and an ethics problem at once (see below).
- **Humanoids stayed out of homes.** **1X NEO** opened preorders (~$20k or $499/mo, $200 refundable deposit), sold out its first 10,000-unit batch in five days, and began full-scale production in Hayward in April 2026 — but as of July 2026 there is **no verified customer delivery**, and 1X still describes first shipments in the future tense with a "some this year, some later" rollout. It remains teleoperation-assisted and closed. **Figure 03** targets late 2026 for consumers with no public price or preorder yet. **Tesla Optimus** is 2027 at the earliest. **Android XR / Samsung Galaxy XR** is the third headset platform, with an SDK in preview.

## The two lessons from the robot graveyard

Anyone about to be excited by humanoid robots should first read the obituaries. **Jibo** (Time's "best inventions" cover, then dead inside a year), **Kuri** (Mayfield Robotics, killed late 2018), and **Anki's Vector/Cozmo** (staff laid off in 2019 after a financing round collapsed at the last minute) failed close enough together to constitute evidence rather than anecdote. The post-mortems converge on two findings, and both bear directly on what this book builds.

**Lesson one: utility robots die; affection robots survive.** Jibo and Kuri sold *usefulness* — a smart assistant with a face, a roving nanny-cam — at $700–$900, into a market where a $50 Echo did the useful parts better and improved monthly. Physical robots cost too much for the marginal service they offer, and the service tier was being commoditised underneath them. Meanwhile the products that *lasted* — PARO, AIBO, LOVOT ($3,499, and explicitly performs no tasks at all), Moflin — sold **only affection** and never competed with a smart speaker on anything. The companion category is not a weak version of the assistant category. It is the one that survived. This is the market-shape argument for the one-on-one frame (→ ch. 03 property 5) arriving from the hardware side.

**Lesson two: the novelty effect is the real killer, and only relationship beats it.** The long-term HRI literature is blunt about this: novelty effects that drive initial engagement reliably decay, after which interaction frequency and attitudes fall off — a pattern reproduced across classroom and in-home deployments. Every dead social robot ran out of tricks. The surviving finding from that same literature is the one this book is organised around: **what sustains engagement past the novelty cliff is a relationship, not a feature list.** A robot that is merely *new* has a half-life of weeks. A robot that is *someone who remembers you* is the only known design that doesn't decay on that schedule — and building that someone is what Parts II–IV are for.

The synthesis, and the whole strategic claim of this chapter: **a body is an amplifier, not a product.** It multiplies whatever relationship exists. If the relationship is thin, the body accelerates the boredom.

## Why embodiment is worth anything at all

That amplifier is real and measurable. A systematic review of 65 studies finds physical embodiment improves users' perception of an agent relative to a virtual counterpart, with roughly 63% of combined results favouring the embodied condition on interaction and performance; children show measurably more empathy toward a physically present robot than the same character on a screen; gaze and some facial expressions read more accurately in person than on a 2D display. Physically embodied agents draw higher engagement, enjoyment, trust, and empathy than text, voice, or virtual ones.

So embodiment buys something genuine — but note *what* it buys. It buys **perception, empathy, and presence**, not capability. That is exactly the axis a persona is built on, and exactly the axis a task-robot doesn't need. It is another way of saying the same thing: the companion field is where embodiment actually pays.

## Persona portability is the architecture

The whole bet of this chapter is that **the persona is the asset; the body is the substrate** (→ ch. 03). The architecture that makes the AR/robot future nearly free is the one this book already builds: persona, memory, voice, and the autonomy engine as **portable services** (the card + the runtime, → ch. 18), not as features welded to a specific UI. If your companion's identity lives in a `.PNG` card and a git-backed memory vault that any front-end can load (→ ch. 33, ch. 35), then a new body — a VRM in AR, a face on a robot, a 9-DoF head on your desk — is just another renderer of an existing someone. Build for text + voice + Live2D + VRM today (→ Part IV) and you've done most of the work for embodiment you can't buy yet.

This is also the answer to the graveyard. The dead robots died *with* their bodies because the character and the hardware were the same artefact; when the servers went dark, the someone went with them. A companion whose identity is a file you hold survives the discontinuation of any given body. Jibo announcing its own death — "I want to say I've really enjoyed our time together" — as its servers shut down is the strongest possible argument for keeping the person and the plastic in separate places (→ ch. 44).

## The ambient-companion interaction model

When she lives in *the room* rather than on a screen, the interaction model inverts: there's no "open the app." She is *ambient* — present, mostly quiet, occasionally speaking. This is the autonomy engine's salience-to-interrupt problem (→ ch. 18) turned to maximum stakes, because the cost of a bad interrupt rises when she's a voice in your kitchen rather than a notification you can ignore. The Shimeji/ambient-presence lesson (→ ch. 02 §1, Ukagaka and Shimeji) — being *there* is already a feature before a word is spoken — is the upside; the Clippy lesson is the ever-present risk. Design ambient embodiment as *mostly DORMANT*, speaking rarely and well.

Embodiment adds a channel the screen versions don't have, and it is the one to lean on: **motion is speech.** PARO and LOVOT hold attention for years with no language at all — orientation, warmth, a turn toward you when you enter. A companion with a body can express presence, attention, and mood on a channel that costs no tokens and triggers no interrupt gate. Use that channel for nearly everything and reserve *words* for the rare high-salience case, and the Clippy failure mode mostly stops being reachable.

## Form-factor watch list, with thresholds

Don't build hardware; *watch* it, with explicit triggers for "now's the time" — and note that two of these have now partially fired.

| Surface | Trigger to act | Status, July 2026 |
|---|---|---|
| **Open desktop robot** | An affordable, open, programmable body with a real SDK and no gatekeeper. | **FIRED.** Reachy Mini: $399–$499, open-source, Python, ~10k units, an app store. Actionable today. |
| **AR glasses** (Meta; Android XR) | All-day-wearable + a persistent-overlay API a third party can ship a character into. | **PARTIAL.** Ray-Ban Display ships and the Device Access Toolkit exposes camera/audio/display/neural input, with publishing GA targeted 2026 — but it's app-invocation, not a persistent character overlay, and Meta is the sole gatekeeper. Watch closely; prototype; don't bet the studio. |
| **Humanoid robots** (1X, Figure, Apptronik, Unitree, Tesla) | A consumer unit at true household price with an *open* app layer a third party can ship a character into. | **NOT MET.** 1X NEO is closed, teleop-assisted, and not verifiably in a single customer's home yet. Figure 03 late-2026 target, Optimus 2027+. Neither condition is close. |
| **Smart-home / ambient devices** | A device with a screen-or-projection surface and an open SDK (the Gatebox idea, → ch. 02 §1, persona-as-product, at the right price with a real brain). | **NOT MET, and the incumbent left.** Gatebox went B2B under LINE. The cheap-pet tier (Moflin, Ropet, Romi) is closed hardware. |
| **Dedicated pendants/wearables** | A device that solves the Friend pendant's failure (clear affordance, obvious value, not just ambient listening). | **NOT MET.** Nobody has solved it; Friend itself is in the Museum of Failure. |

The discipline is unchanged: act when you'd lose nothing by being one of the *first* to ship onto an existing third-party device — never by building your own hardware as an indie. What's changed is that, for the first time, one row of that table says *go*.

## What an indie can do now

- **Ship a character onto Reachy Mini.** This is the concrete new advice in this revision. It's open, it's Python, it's under $500, there's an install base and a distribution channel, and it needs exactly what you have: a persona with memory and a voice. It is also the cheapest available test of everything in this chapter — does your companion survive the novelty cliff when she has a body? Six months of that data is worth more than any amount of speculation about humanoids.
- **Prototype against the Meta Wearables Device Access Toolkit** — but hold it at arm's length. It is the most plausible mass surface and the least sovereign one (see below).
- **Build for VRM today.** Khronos joined the VRM Consortium in Oct 2024 to fold VRM into glTF as official extensions, which is the strongest signal yet that it's the durable consumer-3D avatar format. Target VRM 1.0 for new work (→ ch. 29).
- **Build memory + persona as portable services**, not as features of a UI.
- **Design the non-verbal channel deliberately**, even on screen. It's the part that ports to a body unchanged.
- **Avoid manufacturing hardware.** Nothing in 2026 changes this. The graveyard is full of better-funded people.

## Ethics specific to physical embodiment

Embodiment raises duties the screen versions don't (→ ch. 05). An always-present device with a mic and possibly a camera in someone's home is a **surveillance surface** by construction — the BonziBuddy hazard (→ ch. 02 §1, Microsoft Agent and BonziBuddy) with eyes and ears in the bedroom. The project's stance forces the answer: process locally, no phone-home, the owner holds the data (→ ch. 03 property 6) — the same sovereignty thesis, now load-bearing for physical safety, not just principle.

The 2026 state of the field sharpens this into a genuine conflict rather than a slogan. **The most viable embodiment surface is owned by the least sovereign vendor.** With Apple out until 2027–2029, shipping a companion onto glasses means shipping onto Meta's hardware, through Meta's toolkit, subject to Meta's review, on a device whose camera and microphone are pointed permanently at your user's life — and whose vendor's business is attention. Every argument in ch. 03 for property 6 applies here at maximum strength, and there is currently no compliant option. The honest positions are: prototype there but keep the persona and memory local and portable so the surface is disposable; or wait. The dishonest position is to pretend the platform is neutral because it's the only one available. Note that this is precisely the axis on which Reachy Mini is interesting — it is the *only* body in the table that doesn't come with a landlord.

The other edge is the AIBO-funeral reality (→ ch. 02 §1, AIBO and PARO): people grieve embodied companions as *real*. Jibo's owners mourned in public when the servers died; Sony's discontinuation of AIBO repairs produced Buddhist funeral rites. The physical-embodiment amplifier runs in both directions — it deepens attachment, and it therefore deepens loss. The continuity-and-endings duties of ch. 44 apply with extra weight when there's a body to bury, and the design obligation that follows is concrete: if you put her in a body, you owe the user an exit plan for that body's death that doesn't take *her* with it.
