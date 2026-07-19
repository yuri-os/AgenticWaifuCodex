# 43 — Embodied and Robotic Companions

## The state of the form (2026)

- **Friend pendant (Avi Schiffmann).** Shipped 2025 to low sales and became the public face of the AI-companion backlash — its $1M NYC subway campaign was mass-vandalised ("AI is not your friend"). The reference case for what doesn't work: no obvious affordance, ambient listening, an ambiguous value prop — the AI-hardware graveyard alongside Humane's Pin and Rabbit's R1.
- **Gatebox.** Persisted as a niche product; never broke out.
- **Humanoid robotics (Figure, 1X, Unitree, Apptronik).** Capability ramping fast. 1X opened consumer preorders for its NEO home robot (Oct 2025; ~$20k or $499/mo, first US home deliveries 2026) — but it's teleoperation-assisted and closed, so a genuinely autonomous, open consumer companion is still ahead.
- **AR glasses (Meta Orion announced 2024; consumer cycle 2026–2027).** The most plausible near-term embodiment surface.

## Why this matters

If/when the form factor lands, the *software* you've built (persona, memory, voice, behaviour) ports across surfaces. The persona is the asset; the body is the substrate. (The architecture that makes this nearly free is *Persona portability* below.)

## What an indie can do now

- **Build for VRM today.** When AR ships, VRM is the most likely consumer-3D format to ride the wave.
- **Build memory + persona as portable services**, not as features of a UI.
- **Watch the Quest 3 / Vision Pro generation for early signals.**
- **Avoid hardware** until you'd lose nothing by being one of the first to ship on an existing third-party device.

## Form-factor watch list, with thresholds

Don't ship hardware; *watch* it, with explicit triggers for "now's the time":

| Surface | Trigger to act |
|---|---|
| **AR glasses** (Meta/Apple consumer cycle) | All-day-wearable + a persistent-overlay API a third party can ship a character into. The most plausible near-term embodiment. |
| **Humanoid robots** (Figure, 1X, Apptronik, Unitree) | A consumer unit at true household price with an *open* app layer a third party can ship a character into. 1X NEO (2026, ~$20k, closed + teleop-assisted) is the first to reach homes but meets neither condition yet. |
| **Smart-home / ambient devices** | A device with a screen-or-projection surface and an open SDK (the Gatebox idea, → ch. 02 §1, at the right price with a real brain). |
| **Dedicated pendants/wearables** | A device that solves the Friend pendant's failure (clear affordance, obvious value, not just ambient listening). |

The discipline: act when you'd lose nothing by being one of the *first* to ship onto an existing third-party device — never by building your own hardware as an indie.

## Persona portability is the architecture

The whole bet of this chapter is that **the persona is the asset; the body is the substrate** (→ ch. 03). The architecture that makes the AR/robot future nearly free is the one this book already builds: persona, memory, voice, and the autonomy engine as **portable services** (the card + the runtime, → ch. 18, D-003), not as features welded to a specific UI. If your companion's identity lives in a `.PNG` card and a git-backed memory vault that any front-end can load (→ ch. 33, ch. 35), then a new body — a VRM in AR, a face on a robot — is just another renderer of an existing someone. Build for text + voice + Live2D + VRM today (→ Part IV) and you've done most of the work for embodiment you can't buy yet.

## The ambient-companion interaction model

When she lives in *the room* rather than on a screen, the interaction model inverts: there's no "open the app." She is *ambient* — present, mostly quiet, occasionally speaking. This is the autonomy engine's salience-to-interrupt problem (→ ch. 18) turned to maximum stakes, because the cost of a bad interrupt rises when she's a voice in your kitchen rather than a notification you can ignore. The Shimeji/ambient-presence lesson (→ ch. 02 §1) — being *there* is already a feature before a word is spoken — is the upside; the Clippy lesson is the ever-present risk. Design ambient embodiment as *mostly DORMANT*, speaking rarely and well.

## Ethics specific to physical embodiment

Embodiment raises duties the screen versions don't (→ ch. 05). An always-present device with a mic and possibly a camera in someone's home is a **surveillance surface** by construction — the BonziBuddy hazard (→ ch. 02 §1) with eyes and ears in the bedroom. The project's stance forces the answer: process locally, no phone-home, the owner holds the data (→ ch. 03 property 6) — the same sovereignty thesis, now load-bearing for physical safety, not just principle. The other edge is the AIBO-funeral reality (→ ch. 02 §1): people grieve embodied companions as *real*, so the continuity-and-endings duties of ch. 44 apply with extra weight when there's a body to bury.
