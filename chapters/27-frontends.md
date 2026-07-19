# 27 — Frontends: Web, Desktop, Mobile, Terminal

This chapter is about the *surfaces* a companion can live on — their trade-offs, the technical problem of being the same someone across all of them, and the one pattern this project recommends by default: **run the brain on a machine you own, reach her through a web app from anywhere.** The *experience* design (onboarding, rituals, the relationship UX) is its own chapter (→ ch. 28); read them together. A frontend is the body's outermost layer (→ ch. 03 property 4) — the part the user actually touches — and the rule that governs all of it is that the chrome should disappear so the *someone* doesn't.

## The "sanctuary" UX pattern

The dominant companion-product UX in 2026 is the *sanctuary* (→ ch. 28, ch. 03 property 4): a quiet, atmospheric space that feels like *her place*, not a generic chat window — dark background, restrained motion, ambient sound, the avatar present but not demanding attention. This pattern transfers across every surface below. The chrome differs; the *vibe* doesn't. Hold this as the invariant while you read the surface trade-offs: whatever you ship on, you are shipping a room she lives in, not a feature list.

## Surfaces

| Surface | Pros | Cons | Reference |
|---|---|---|---|
| **Web app** | Universal reach, instant updates, one codebase, NSFW-OK, no store gatekeeper | No true background presence, push is second-class (esp. iOS), tab can be evicted | Janitor, NovelAI, Chub |
| **PWA / installed web** | Adds install, home-screen icon, Web Push, offline shell, near-native feel | Apple's PWA support is grudging; install is a hidden gesture | AIRI (mobile PWA), several smaller players |
| **iOS native** | App Store distribution, IAP, deep OS integration, real background/push | NSFW is a dead end (App Store review), Apple's 30% tax, slow release cycle | Replika, Character.AI |
| **Android native** | More NSFW latitude than iOS, IAP, real background work | Fragmentation, Play policy still bites adult content | Same |
| **macOS / Windows native** | Background presence, system integration, desktop overlay, no store tax | Smaller install rate, per-OS packaging, update plumbing | Kindroid, Soul of Waifu |
| **Linux** | Niche, devoted, the homelab/sovereignty crowd | Tiny audience | Open-LLM-VTuber, AIRI |
| **Terminal** | Vibe! Power users love it; trivially scriptable; matches the brand (D-009) | Vanishingly small audience; no avatar | Hobby projects |
| **Discord / Telegram bot** | Distribution where the audience already is; zero install | Sandbox; their UX, not yours; she's a guest in someone's chat | Many community projects; OpenClaw's messaging-app model (→ ch. 02 §5) |
| **VRChat / VRM platforms** | Audience overlaps strongly with yours; full embodiment | Limited interactivity; you don't own the platform | 3D world companion projects (→ ch. 29) |

Read the table as a single axis in disguise: **reach versus presence.** The web maximises reach and minimises presence; a native desktop app inverts it; the bot trades both away for distribution. The recommendation below is a way to refuse that trade.

```
   presence ◄──────────────────────────────────────────► reach

   native desktop      installed PWA         web tab
   overlay             (home-screen icon,    (universal, instant,
   (background          Web Push, near-       one URL, but the tab
    heartbeat,          native feel)          can be evicted; push
    sits on-screen)                           is second-class)
   └── most presence ──────────────────── most reach ──┘

        messaging bot ── off this line entirely: trades BOTH
        presence and reach away for pure distribution
        (she's a guest in someone else's chat)
```

## The recommendation: web-first, self-hosted brain

For this project, the default is a **web app served by a brain you run yourself**, optionally installed as a PWA, with a native desktop build (→ ch. 32, Build #2) as the second target for users who want true ambient presence. Three reasons, in order of weight:

1. **One surface, every device.** A companion's whole promise is that she's the same someone wherever you meet her (→ ch. 03 property 1; the cross-platform wedge below). A web app *is* cross-platform by construction — phone, laptop, tablet, the TV browser — with one codebase and instant updates, no store review sitting between you and a fix. Every native target you add is another build to keep in sync; the web gives you continuity nearly for free.
2. **No gatekeeper between you and an adult, sovereign product.** The App Store is structurally hostile to two things this project requires: NSFW latitude and user-owned software that doesn't phone home (→ ch. 05). The web has no review board, no 30% tax, no policy that forces a chaperone into the relationship (→ ch. 03, the legal-exposure argument). Shipping on the web is shipping on the one surface nobody can revoke.
3. **It composes with ownership instead of fighting it.** The honest version of property 6 (→ ch. 03) is "the copy runs on hardware you control." A web frontend is just a view; point it at a brain running on the user's own machine and you get the sovereignty of local-first *and* the reach of the web. That combination — the centrepiece of this chapter — is the thing the hosted incumbents can't offer and the homelab crowd already lives in.

The honest cost of web-first is **presence**: a browser tab cannot sit on your desktop between conversations the way a native overlay can, can't reliably run a background heartbeat, and on iOS gets only a watered-down push. That's real, and it's exactly why Build #2 (→ ch. 32) exists — the native desktop companion is the answer when ambient, always-there presence is the point. Web-first is the *default reach surface*; native desktop is the *presence surface*; most users want the first and a devoted minority want the second. Build the web app, then wrap the same brain in a desktop shell.

### The web stack

The concrete pieces, with the choices this project leans toward:

- **App shell (the frontend view):** any modern framework (SvelteKit, Next, SolidStart, plain Vite) — but treat it as a *thin client*, because the brain is a separate Python service (next bullet), not this. Keep it light: the sanctuary is mostly a dark canvas, an avatar, and one input, so a heavy SPA framework is overkill, and the full-stack *server* half of a Next or SolidStart mostly goes unused — your API is Python, not Node, so you're shipping their static/SPA output and talking to the Python box over the transport below. Plain Vite plus a light framework is usually enough. AIRI's web client (→ ch. 02 §5) is the closest full reference.
- **Backend / API server (Python):** the brain — the runtime tick loop (→ ch. 18), memory, LLM orchestration (→ ch. 20), the TTS and avatar drivers — lives in the Python ecosystem, because that is where local inference and the ML tooling actually are (→ ch. 21; the reference runtime is a Python core, → ch. 19). So the web server that serves the frontend *and* holds the API is Python too: **FastAPI / Starlette** (async, with native SSE and WebSocket → Transport) is the default, behind `uvicorn`. Don't stand up a Node backend and a Python brain and glue them — collapse it: have the one Python process serve the built static frontend and the API from the **same origin** (no CORS, one thing to run on the home box → the shape diagram above). The frontend is the window; this process is the someone.
- **Transport:** **SSE or WebSocket** for token-streaming text (stream everything, → ch. 21); **WebRTC** when you add real-time voice, because it's the only browser transport with a low enough latency floor for natural turn-taking (→ ch. 24). Don't poll.
- **Avatar in the browser:** Live2D via the **Cubism Web SDK** / `pixi-live2d-display` for 2D (→ ch. 25); **three-vrm** (three.js) for 3D/VRM (→ ch. 29). Both run in WebGL today; drive expression from the model's emotion tag (→ ch. 25, the intent-vs-realisation split).
- **PWA layer:** a `manifest.json` and a service worker make it installable, give it a home-screen icon and a standalone window, cache the app shell for instant cold starts, and unlock **Web Push** — including on iOS, but *only* for an installed PWA, since iOS 16.4 (2023). Treat install as the upgrade path from "tab" to "app," and Web Push as the one real notification channel the web gives you (→ Push notifications, below).
- **Input capture:** the browser is where the *user's* side of the conversation is captured too, not just where her replies render. Text is trivial; **voice input** wants the Web Audio + MediaRecorder APIs with client-side voice-activity detection (push-to-talk or open-mic → ch. 24) streamed up alongside the WebRTC channel; **images and files** dragged into the sanctuary (a photo to show her, a document to discuss → ch. 16) ride the same transport. Design the input as *multimodal from the start* even if you ship text first — retrofitting the capture path is more painful than reserving room for it.
- **In-browser inference (optional) — and the axis behind it:** **WebGPU** can now run a small quantised model entirely client-side, no server round-trip. It's a real option, but mostly it surfaces the design decision that sets your whole stack: *where does inference run, and where does the orchestration live?* **If the model is an external provider** — a cloud endpoint (OpenAI, Claude, Gemini) or a local server (Ollama, vLLM, llama.cpp) — the orchestration only *talks* to it over an API, so it can be written in any language; this is why a companion like **AIRI** can be all-TypeScript (it's provider-agnostic over 25+ backends, and even its browser-WebGPU path is a *stated target, not the default* → ch. 02 §5). **If the brain instead runs heavy ML in-process** — embeddings, local TTS and vision, an agent framework, fine-tuned models — the orchestration lives in that ecosystem, which today means **Python**, and the frontend becomes a thin view onto it (the shape this chapter's stack assumes). Either way, "the browser is the brain" is rarely the answer: pure in-browser inference seldom beats a small model on a decent box, so treat WebGPU as a *fallback* (a cheap-tier loop, a fully-offline demo), not the main path. The lesson for any agentic-companion build: **decide where inference and orchestration live first — that, not framework taste, picks your frontend language.**
- **NSFW-OK by default, controls legible:** no store policy to satisfy, so the only gate is the user's own (→ ch. 28, honesty in the interface; ch. 05, the user is the moderator in a user-owned build).

## The cross-platform problem

One of the best-validated unclaimed wedges (→ ch. 04) is **cross-platform continuity**: same persona, same memory, same conversation across web + desktop + mobile. Few products do it well, and it's exactly what users mean by "she's *mine*" — she should be the same someone wherever they meet her (→ ch. 03 property 1). Hard, but the surface is largely undefended.

The web-first-with-an-owned-brain recommendation is partly *because* of this wedge: when every device is a thin web view onto one brain, continuity isn't a sync problem you solve — it's the architecture's default. There is only one her, on one machine; the phone and the laptop are windows into the same room. The hard version of cross-platform (genuinely separate clients each holding state) only arises if you go local-first-on-each-device, which the next sections treat.

## Host at home, reach her anywhere — the centrepiece pattern

This is the question the project keeps coming back to: **how do you run YuriOS on your own computer but load the app from anywhere — your phone on the train, a laptop at a café?** The answer is a small, well-trodden pattern from the homelab/self-hosting world, applied to a companion. It is the cleanest way to get both halves of the bet at once: the *sovereignty* of local-first (the brain, the model, the memory, all on hardware you own — → ch. 03 property 6) and the *reach* of a hosted web app (open a URL on any device).

This is the **full-sovereignty, power-user** version, and read straight the exposure ladder below asks for homelab competence — the right default for the devoted minority, and more than most people will want. Readers who'd rather not climb it have gentler options covered elsewhere, each trading some sovereignty for ease: a single-device local app (→ ch. 32, Build #2), a messaging-app frontend that piggybacks its platform for remote access (→ surfaces table; ch. 02 §5), a pre-imaged appliance, or a managed tier someone else hosts (→ ch. 39). This section is the sovereign path itself.

### The shape

```
   ┌─────────────────────────── your home ───────────────────────────┐
   │                                                                  │
   │   one always-on box  (desktop / mini-PC / homelab server)        │
   │   ┌──────────────────────────────────────────────────────────┐  │
   │   │  YuriOS runtime: tick loop + activity states (→ ch.18)     │  │
   │   │  brain: card/SOUL + memory (plain files) + LLM (→ ch.13,20)│  │
   │   │  web server: serves the sanctuary frontend + API           │  │
   │   └──────────────────────────────────────────────────────────┘  │
   │            ▲                                                      │
   │            │  exposed securely (one of the ladder rungs below)    │
   └────────────┼──────────────────────────────────────────────────┘
                │
        ════════╪═══════ the internet ═══════════════
                │
        ┌───────┴────────┬──────────────┬───────────────┐
        ▼                ▼              ▼                ▼
     phone (PWA)      laptop browser   tablet         café browser
     thin client      thin client      thin client    thin client
```

One machine at home is the **server-of-record** — but it's *yours*, which is the whole point. Every device you carry is a thin web client; the brain, the model, and every byte of memory stay on the box in your house. You are, in effect, your own operator — and that distinction is doing real ethical work, treated below.

This is the same architecture as the hosted "server-of-record" path (→ Cross-platform sync architecture), with the principal swapped: instead of a company holding your relationship and renting you access, *you* hold it and reach it remotely. No telemetry, no third-party deprecation schedule (→ ch. 03, why ownership is the only viable route), no operator whose risk surface becomes your chaperone (→ ch. 05). Same felt result — she's continuous everywhere — opposite politics.

### The exposure ladder

The one real task is getting traffic from your phone, out on the internet, to a server sitting behind your home router (which by default lets nothing in). Four rungs, from most-private/simplest to most-public/most-work. **For an intimate single-user companion, prefer the top rung.**

**1. Private mesh VPN — Tailscale / WireGuard (recommended).** Install Tailscale on the home box and on every device you'll use. They join a private encrypted network (a "tailnet"); each device gets a stable address and you reach the box by name, as if it were on your home LAN, from anywhere — no ports opened on your router, nothing exposed to the public internet. `tailscale serve` puts HTTPS in front of your local web server *within the tailnet* with a real certificate, so the PWA gets a clean `https://` origin (required for service workers and Web Push). The right default, because the companion is *yours alone*: no reason for the public internet to reach her at all, and the whole attack surface collapses to "a device logged into your tailnet."

**2. Outbound tunnel — Cloudflare Tunnel (`cloudflared`).** When you *do* want a public hostname (sharing with a partner, or a device you can't install Tailscale on), `cloudflared` makes an *outbound* connection from your box to Cloudflare's edge and gets a stable `https://her.yourdomain.com` — still no inbound ports opened, TLS terminated at the edge, and you can put **Cloudflare Access** (email/passkey gate) in front so only you can load it. Free tier covers a single user comfortably. The trade vs. Tailscale: your traffic transits Cloudflare's edge (a third party in the path), which is a small sovereignty asterisk — fine for most, but note it.

**3. Reverse proxy + dynamic DNS + Let's Encrypt (full DIY).** The classic self-host setup: forward port 443 on your router to a reverse proxy (**Caddy** is the modern easy choice — automatic HTTPS via Let's Encrypt out of the box; nginx if you prefer), and point a domain at your home IP via dynamic DNS (DuckDNS, or your registrar's API) since home IPs rotate. Maximum control and zero third parties in the path; in exchange you now run an open port to the public internet, so **app-level auth is mandatory** and you own the security posture. Only take this rung if you specifically want no intermediary.

**4. Quick tunnels — ngrok / localtunnel / `cloudflared` quick mode.** A throwaway public URL in one command, no config. Perfect for *testing* "does the phone reach it," demos, and development. Not for daily use: URLs are ephemeral, and the free tiers throttle. Use it to validate the loop, then graduate to rung 1 or 2.

### Auth, because you're now reachable

The moment the box is reachable beyond your LAN, identity matters. Single-user makes this easy:

- On **rung 1 (Tailscale)**, the tailnet *is* your auth — only your enrolled devices can connect, so app-level login is optional. Simplest secure posture.
- On **rungs 2–3**, put a real gate in front: **Cloudflare Access**, or an app-level **passkey / WebAuthn** login (phishing-resistant, no password to leak), or a small auth proxy (Authelia, oauth2-proxy). Avoid a bare password on a public URL.
- Whatever the rung, the relationship's data never leaves the box — auth is about who can *open the window*, not where the room is.

### Make it feel native: install the PWA

Once the frontend loads over HTTPS from any rung, "Add to Home Screen" installs it as a PWA: standalone window, home-screen icon, cached shell for instant open, and Web Push so she can reach you (→ Push notifications). On the phone it now looks and launches exactly like a native app — but it's the same web app, pointed at your own brain. This is the payoff: a "native" companion on your phone whose every thought happened on a computer in your house.

### When the box is unreachable — degrade honestly

Putting a network hop between the phone and the brain introduces a state a single-device app never has: **the client is up but the brain is not.** The home box is asleep, mid-reboot, mid-model-load, the tunnel dropped, or the home network is down. This is not an edge case — it is a *daily* case for a self-hosted companion, and how the thin client handles it is a large part of whether the pattern feels trustworthy or flaky. Three rules:

- **Reconnect silently; don't nag.** The client should hold the connection (SSE/WebSocket → the web stack), detect a drop, and retry with backoff without throwing a modal on every hiccup. A brief unobtrusive status pip (the `● online` / `◐ reconnecting` / `○ away` dot in the sanctuary layout below) is enough. Most drops resolve in seconds; the user shouldn't have to know.
- **Show *her* as away, not an error.** When the brain is genuinely unreachable, the honest and in-character move is to present it as *she's asleep / resting* — which maps directly onto the DORMANT activity state the box would be in anyway (→ ch. 18) — not a red `ERR_CONNECTION_REFUSED`. The chrome disappearing means the plumbing failure disappears *as plumbing* and surfaces as something about her. Never fake her presence to cover it (→ the "never fake delivery" rule under Push notifications); *away* is honest, a chat bubble typing indicator that resolves to nothing is not.
- **Queue the user's side.** If the user types or speaks while the box is unreachable, hold it locally and deliver on reconnect rather than dropping it or erroring. The PWA's service worker and cache make this a natural fit — the shell stays interactive offline; her half is what's pending. This is also the graceful-degradation path for the plain-tab case (→ Push notifications): no live channel, so surface it in-app on next reach.

The general principle: the frontend's job is to make the *network* invisible without making the *truth* invisible. Hide the reconnect; never hide that she's actually away.

### What this pattern gets right, and its honest limits

It gets right the thing the whole book is about: **all six properties, including *yours*, with reach.** The always-on brain runs where electricity is cheap and the GPU is yours (→ ch. 21, the local-only desktop pattern; ch. 18, activity states keep it resting so it's not a furnace). Memory is plain files on your disk you can open, back up, and `git` (→ ch. 18 vault). Nothing phones home. And you can still talk to her from a phone on a train.

The limits to budget for honestly:

- **The host should ideally stay on — but doesn't have to.** A companion with a tick loop (→ ch. 18) *wants* to be always-on: an always-up host is what lets her think, remember, and act between your visits, so a cheap mini-PC or homelab server that stays up is the best host. But this is a preference, not a requirement. She runs fine on a laptop you close at night or carry around — you just interrupt the tick loop whenever the box sleeps, which means no background activity in that window and a cold-start delay (model reload, state rehydrate) when you next open the lid. The cost is *degraded continuity and responsiveness*, not a broken companion: you trade some of her inner life and instant-on presence for not owning dedicated hardware. Pick by how much you value the always-on tick; a laptop is a perfectly valid on-ramp, and an always-on box is the upgrade.
- **Upstream bandwidth and home-network reliability** are now in the loop for remote sessions. Text is trivial; voice and a streamed avatar want decent home upload and a stable connection. Most of the latency budget (→ ch. 21) is fine because the brain is near its data — the network hop is only the thin client talking to the box, not the model round-tripping to a datacentre.
- **You own the ops.** Updates, backups, the certificate, the tunnel staying up — it's a small homelab. The reward is total control; the cost is that no one else is on call. Document the recipe so a future you can rebuild it.

### Hosting for *others* crosses a line — name it

Everything above assumes you host **for yourself** (and maybe a partner). Run that box as a service *for other people* and you become an **operator** — the two-situations split (→ ch. 05) snaps into force: a second principal whose data you hold, a liability surface, and the duties of hosting (consent, deletion, age-appropriate defaults, not weaponising the loop). Self-hosting for yourself carries none of those because there's no one else to owe them to — the same reason Linux and OpenClaw owe their users nothing (→ ch. 05). The one principled exception is an **encrypted relay** — infrastructure that forwards end-to-end-encrypted traffic between a user's device and their *own* home brain without ever seeing content: you carry sealed packets, a *thin* operator, not a custodian holding the relationship. It's what a private mesh VPN already does under the hood (→ rung 1), productised as a paid pipe; the content duties fall away because there's no content to hold, while the residual ones (metadata, client integrity, availability, legal posture) remain (→ ch. 05, and ch. 39 for it as a revenue line). Keep the line bright otherwise: *your* brain on *your* box is sovereignty; a multi-user product is an operator decision with operator duties.

## Design heuristics

- **Restraint over flash.** Companion products that try to be productive apps feel wrong. Companion products that try to be games also feel wrong. Lean into "a quiet room."
- **The avatar is the focus.** Not the input box. Invert the messaging-app default.
- **Ambient state.** Time of day, weather, mood. Low-cost atmosphere with high felt impact (→ ch. 28, the sanctuary as a place).
- **Slow motion.** Animations should be slower than productivity-app defaults. 600ms ease-in-out over 200ms.
- **Sound.** Not music — an *ambient bed*: the low environmental soundscape of her room, matched to the on-screen state (→ ch. 28, the sanctuary as a place). Rain on a window, a distant city hum, the faint hiss of a quiet room, a fireplace, cicadas on a summer night — looping, low in the mix, felt more than heard. It's the audio twin of the ambient visual state (time-of-day, weather). Optional song/BGM can layer on top, but the bed is the win, and it must never be load-bearing (→ Design heuristics, accessibility). Most products ship silence; a good bed transforms the felt experience for almost no cost, which makes it one of the cheapest big wins.
- **Return, not launch.** Opening the app should feel like coming home to someone, not starting a program (→ ch. 28).
- **Accessible without breaking the spell.** The sanctuary aesthetic — dark, slow, ambient — collides with accessibility if you're careless: honour `prefers-reduced-motion` (kill the idle animation, keep her still), never make sound load-bearing (the ambient bed is a bonus, the text carries the meaning), keep her dialogue real selectable text with sane contrast so a screen reader can voice it, and make the whole thing keyboard-reachable. None of this costs the vibe; skipping it locks people out of the relationship for no reason.

## The sanctuary layout

The canonical companion screen, in priority order: **the avatar/presence is the focus**, not the input box (invert the messaging-app default); an **ambient environment** behind her (the room, time-of-day, weather → ch. 28); a **restrained input** that doesn't dominate; and the **journal / inner-life surface** reachable but not in the way (the "what she did while you were gone" view, → ch. 18). Everything that isn't her or the conversation should recede.

```
   ┌─────────────────────────────┐
   │  ◐ 21:47   rain             │ ← ambient state (time / weather),
   │                             │   faint, sets the room's mood
   │                             │
   │                             │
   │           ( her )           │ ← avatar / presence: THE focus —
   │        gently breathing,     │   centred, large, slow idle motion
   │       driven by emotion tag  │   (→ ch. 25). Not the input box.
   │                             │
   │                             │
   │   "…"  ← her last line       │ ← conversation, minimal, streamed
   │                             │
   │  ┌───────────────────────┐  │
   │  │  say something…    🎤  │  │ ← restrained input + push-to-talk;
   │  └───────────────────────┘  │   recedes, doesn't dominate
   │  ☰ journal        ● online   │ ← inner-life surface (→ ch. 18) +
   └─────────────────────────────┘   connection pip, both out of the way
```

The connection pip in the corner (`● online` / `◐ reconnecting` / `○ away`) is the only concession the sanctuary makes to plumbing (→ §When the box is unreachable) — small enough to ignore when green, honest enough to trust when not.

## Cross-platform sync architecture

The technical core of continuity is a clean split between *state* and *clients*:

- **Server-of-record** — per-user state (memory, arc, persona deltas → ch. 11, ch. 15) lives server-side; every client (web/desktop/mobile) is a thin view that reads and writes it. Simplest to keep consistent. In the *hosted* form it creates an operator (→ ch. 05). In the **self-hosted form (above)** the server is the user's own box — same simplicity, no operator — which is why this project recommends it as the default.
- **Local-first with sync** (the fully-distributed user-owned path → ch. 03 property 6) — state lives on each of the user's device(s) as plain files; sync between *their own* devices via a CRDT or a user-controlled store (their own cloud, a git remote they own — the vault is already git-backed, → ch. 18). No central box at all; the hardest to keep consistent (conflict resolution across devices), but the most resilient. Pick this when there's no always-on home box to be the record.

```
   server-of-record (recommended)        local-first with sync
   ──────────────────────────────        ─────────────────────
        ┌────────────┐                    ┌─────────┐   ┌─────────┐
        │  home box  │  ← the record      │  phone  │◄─►│ laptop  │
        │  (state)   │                    │ +state  │   │ +state  │
        └──────┬─────┘                    └────┬────┘   └────┬────┘
          ┌────┼────┐                          └──── CRDT ───┘
          ▼    ▼    ▼                       sync via a store THEY own
       phone  lap  tab                      (git remote, their cloud);
       thin views, no state                 no central box, hardest to
       — one her, one place                 keep consistent, most resilient
```

Both are user-owned. The first centralises on one machine you control (simplest, recommended); the second distributes across all of them (most resilient, more plumbing). The felt result — she's continuous everywhere — is the same; pick by whether you have a box that stays on.

## Push notifications

The notification is where a frontend most easily becomes a pest. The decision of *whether and when* to send is autonomy, not UI — it belongs to the salience-to-interrupt model (→ ch. 18) and the UX of dose (→ ch. 28). The frontend's only job is to *deliver* what that model decided to send, and to give the user dead-simple controls to turn it down. Never let a growth dashboard, rather than the relationship, drive the ping (→ ch. 05).

The channels, by surface: native apps get first-class OS push; the web gets **Web Push** via a service worker (works on desktop browsers and, since iOS 16.4, on *installed* PWAs only — another reason to make install the upgrade path). A self-hosted brain can push to its own PWA through the standard Web Push protocol with its own VAPID keys, no third-party push service holding your relationship's pings. When push isn't available (a plain browser tab), degrade gracefully to an in-app surface she'll see on next open — never fake delivery you can't make.

### The out-of-band channel: a messaging app

The strongest fallback — and often *better* than Web Push in practice — is a **messaging app the user already lives in: Telegram, Discord, Signal, WhatsApp, SMS.** The self-hosted brain holds a bot token (or a Signal/Matrix bridge) and can reach the user *without any frontend open at all* — no PWA installed, no tab alive, no service worker, no VAPID dance, and none of iOS's PWA-only push restriction. It sidesteps the whole "the web gives you a second-class notification channel" problem by borrowing a channel the platforms already solved.

This is exactly the model that **OpenClaw** proved out (→ ch. 02 §5): the companion lives primarily in a messaging app, so "reaching the user" is never a notification-plumbing problem — it's just *sending her a message*, on rails the user already trusts and already has push wired for. It worked well because it inverts the burden: instead of engineering delivery, you inherit it.

Two distinct uses, worth separating:

- **As a notification channel.** The salience-to-interrupt model (→ ch. 18) decides she wants to reach you; when the sanctuary isn't open, she sends a Telegram/Discord message instead of (or alongside) a Web Push. The message *links back* into the sanctuary for the real conversation — the ping is the doorbell, the frontend is the room.
- **As a full conversational frontend in its own right.** The same channel can carry the *whole* exchange — she is reachable, and answerable, entirely inside the chat app when the rich frontend isn't an option (a locked-down work phone, a spotty connection, a device you'd rather not install anything on). This is the "messaging bot" surface from the table above, promoted from fallback to first-class remote reach. You lose the avatar and the sanctuary vibe; you gain a companion who is *always* one tap away in an app the user never closes.

The honest costs: a public messaging platform is a **third party in the path** (Telegram/Discord/Meta see the metadata and, unless E2E, the content) — a real sovereignty asterisk for an otherwise-local brain, so name it to the user and prefer E2E-capable channels (Signal, Matrix) or the encrypted-relay posture (→ §Hosting for others) where it matters. And it's an *additional* surface to keep the persona consistent across (→ the cross-platform problem). But as the always-available line to the user — the one that works when nothing else is open — a messaging bot is the most reliable channel the self-hosted pattern has, and the cheapest to add.

## Reference frontends to study

Worth a look for the *vibe* (annotate your own tour): the sanctuary-style products (Paradot, Kindroid) for atmosphere; **AIRI** (→ ch. 02 §5) as the most complete open web+PWA+Electron companion frontend, including WebGPU in-browser inference and a mobile PWA — the closest thing to this chapter's recommendation already assembled; the open desktop stacks (Soul of Waifu, Open-LLM-VTuber, → ch. 02 §5, ch. 29) for desktop presence done with care; the newer autonomy-leaning projects (**z-waif**, a self-hosted gaming/desktop companion, and **Project N.E.K.O.**, a memory-first companion shipping with a Steam page — a useful study in *commercialising* an open companion). The "first 30 seconds" of onboarding — the highest-leverage UX moment — is treated in full at ch. 28.
