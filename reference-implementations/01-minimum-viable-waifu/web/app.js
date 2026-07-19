/* The sanctuary client (SPEC §9.1). Vanilla JS, no build step.
   - session persists in localStorage (one person, one thread)
   - assistant tokens stream in via SSE-over-fetch
   - on load: render history, then ask for the continuity greeting (§9.3)
     if this is a fresh visit — the proof it works. */

const $messages = document.getElementById("messages");
const $input = document.getElementById("input");
const $send = document.getElementById("send");
const $status = document.getElementById("status");

const GREETING_GAP_MS = 30 * 60 * 1000; // returning after 30+ min ⇒ she speaks first

// ---- rendering -------------------------------------------------------------

function addMessage(role, text = "") {
  const el = document.createElement("div");
  el.className = `msg ${role}`;
  const who = role === "user" ? "you" : "yuri";
  el.innerHTML = `<div class="who">${who}</div><div class="body"></div>`;
  el.querySelector(".body").textContent = text;
  $messages.appendChild(el);
  $messages.scrollTop = $messages.scrollHeight;
  return el;
}

function addRating(el, turnId) {
  if (!turnId) return;
  const div = document.createElement("div");
  div.className = "rate";
  for (const [label, thumbs] of [["👍", 1], ["👎", -1]]) {
    const b = document.createElement("button");
    b.textContent = label;
    b.title = thumbs === 1 ? "this was her" : "this wasn't her";
    b.onclick = async () => {
      await fetch("/api/rate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ turn_id: turnId, thumbs }),
      });
      div.querySelectorAll("button").forEach(x => x.classList.remove("chosen"));
      b.classList.add("chosen");
    };
    div.appendChild(b);
  }
  el.appendChild(div);
}

function showError(text) {
  const el = document.createElement("div");
  el.className = "error";
  el.textContent = text;
  $messages.appendChild(el);
}

// ---- SSE over fetch ----------------------------------------------------------

async function consumeSSE(response, el) {
  // streams {"token":…}* then {"done":true,"turn_id":…} (§10)
  const body = el.querySelector(".body");
  el.classList.add("streaming");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "", result = null;
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop();
    for (const ev of events) {
      if (!ev.startsWith("data: ")) continue;
      const data = JSON.parse(ev.slice(6));
      if (data.token) {
        body.textContent += data.token;
        $messages.scrollTop = $messages.scrollHeight;
      } else if (data.error) {
        showError(`something broke mid-thought: ${data.error}`);
      } else if (data.done) {
        result = data;
      }
    }
  }
  el.classList.remove("streaming");
  return result;
}

// ---- session ------------------------------------------------------------------

async function getSession() {
  let sid = localStorage.getItem("mvw_session");
  if (sid) {
    const r = await fetch(`/api/session/${sid}/history`);
    if (r.ok) return { sid, history: (await r.json()).messages };
  }
  const r = await fetch("/api/session", { method: "POST" });
  sid = (await r.json()).session_id;
  localStorage.setItem("mvw_session", sid);
  return { sid, history: [] };
}

// ---- the loop -------------------------------------------------------------------

let sessionId = null;
let busy = false;

async function send() {
  const text = $input.value.trim();
  if (!text || busy) return;
  busy = true;
  $input.value = "";
  $input.style.height = "auto";
  addMessage("user", text);
  const el = addMessage("assistant");
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    if (!r.ok) throw new Error(`http ${r.status}`);
    const done = await consumeSSE(r, el);
    if (done) addRating(el, done.turn_id);
  } catch (e) {
    el.classList.remove("streaming");
    showError(`couldn't reach her: ${e.message}`);
  } finally {
    busy = false;
    $input.focus();
  }
}

async function greet() {
  const el = addMessage("assistant");
  try {
    const r = await fetch(`/api/greeting?session_id=${sessionId}`);
    if (!r.ok) throw new Error(`http ${r.status}`);
    const done = await consumeSSE(r, el);
    if (done) addRating(el, done.turn_id);
  } catch (e) {
    el.remove(); // no greeting is better than a broken one
  }
}

async function init() {
  const { sid, history } = await getSession();
  sessionId = sid;
  for (const m of history) {
    const el = addMessage(m.role, m.content);
    if (m.role === "assistant") addRating(el, m.turn_id);
  }
  // continuity greeting (§9.3): first thing shown on a fresh visit must
  // demonstrate memory, unprompted
  const last = history[history.length - 1];
  const fresh = !last || (Date.now() - Date.parse(last.ts)) > GREETING_GAP_MS;
  if (fresh) await greet();
}

$send.onclick = send;
$input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});
$input.addEventListener("input", () => {
  $input.style.height = "auto";
  $input.style.height = Math.min($input.scrollHeight, 9 * 16) + "px";
});

init().catch((e) => {
  $status.textContent = "· unreachable";
  showError(`the sanctuary didn't open: ${e.message}`);
});
