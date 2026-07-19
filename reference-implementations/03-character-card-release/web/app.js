/* YuriOS Card Studio — SPA front-end. Vanilla JS, no build step. */
"use strict";

const S = { draft:null, settings:null, principles:[], fieldPrinciples:{}, hasPortrait:false };
let testHistory = [];

// ---- tiny helpers ----------------------------------------------------------
const $ = (sel, root=document) => root.querySelector(sel);
const $$ = (sel, root=document) => [...root.querySelectorAll(sel)];
function el(tag, attrs={}, ...kids){
  const n = document.createElement(tag);
  for (const [k,v] of Object.entries(attrs)){
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined) n.setAttribute(k, v);
  }
  for (const kid of kids.flat()) if (kid !== null && kid !== undefined)
    n.append(kid.nodeType ? kid : document.createTextNode(kid));
  return n;
}
async function api(path, opts={}){
  const res = await fetch(path, {headers:{"Content-Type":"application/json"}, ...opts});
  if (!res.ok){
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch(_){}
    throw new Error(msg);
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res;
}
const getJSON = (p) => api(p);
const postJSON = (p, body) => api(p, {method:"POST", body:JSON.stringify(body)});

function toast(msg, kind=""){
  const t = $("#toast"); t.textContent = msg; t.className = "toast " + kind;
  clearTimeout(t._h); t._h = setTimeout(()=>{ t.className = "toast hidden"; }, 3200);
}

// ---- autosave --------------------------------------------------------------
let saveTimer = null;
function markDirty(){
  $("#save-state").textContent = "saving…"; $("#save-state").className = "save-state saving";
  clearTimeout(saveTimer);
  saveTimer = setTimeout(async ()=>{
    try { await postJSON("/api/draft", S.draft);
      $("#save-state").textContent = "saved"; $("#save-state").className = "save-state"; }
    catch(e){ $("#save-state").textContent = "save failed"; }
  }, 500);
}

// ---- modal -----------------------------------------------------------------
function showModal(title, bodyNode, actions){
  $("#modal-title").textContent = title;
  const body = $("#modal-body"); body.innerHTML = ""; body.append(bodyNode);
  const act = $("#modal-actions"); act.innerHTML = "";
  for (const a of actions) act.append(a);
  $("#modal").classList.remove("hidden");
}
function closeModal(){ $("#modal").classList.add("hidden"); }

// ============================================================================
//  DESIGN TAB
// ============================================================================
const TEXT_FIELDS = [
  ["name", "Name", "input", "Who she is. One name."],
  ["personality", "Personality", "textarea", "A short summary line — specific traits, not categories (→ ch.06 §4)."],
  ["description", "Description", "textarea", "The always-present identity block, injected every turn. Enact, don't describe (→ ch.06 §5)."],
  ["scenario", "Scenario", "textarea", "The setting the two of you share."],
  ["first_mes", "First message", "textarea", "The opening scene the reader sees. Warm; withhold the backstory (→ ch.06 §6)."],
  ["system_prompt", "System prompt / voice law", "textarea", "How she speaks and behaves. Routed to the card's system_prompt."],
  ["post_history_instructions", "Hard limits", "textarea", "The never-drift rules, placed closest to the model's next token."],
  ["creator_notes", "Creator notes", "textarea", "The in-card README a runtime shows on import."],
];

function assistBar(field){
  const mk = (label, mode, title) => el("button", {class:"ghost", title,
    onclick:()=>runAssist(field, mode)}, label);
  return el("div", {class:"assist-btns"},
    mk("✎ improve","improve","Rewrite this field stronger against the ch.06 principles"),
    mk("✦ draft","draft","Draft this field from scratch"),
    mk("? suggest","suggest","Get concrete suggestions (advice only)"));
}

function textField([key,label,kind,hint]){
  const input = kind === "input"
    ? el("input", {type:"text", value:S.draft[key]||""})
    : el("textarea", {}, S.draft[key]||"");
  input.addEventListener("input", ()=>{ S.draft[key] = input.value; markDirty(); });
  input.dataset.field = key;
  const wrap = el("div", {class:"field"},
    el("div", {class:"field-head"},
      el("label", {}, label),
      key==="name" ? el("span",{}) : assistBar(key)),
    input,
    el("div", {class:"meta hint", style:"margin:6px 0 0"}, hint));
  return wrap;
}

function listEditor(key, label, hint, itemLabel){
  // key -> array of strings (examples, alternate_greetings)
  const container = el("div", {class:"field"});
  const items = el("div");
  function rerender(){
    items.innerHTML = "";
    (S.draft[key]||[]).forEach((val, i)=>{
      const ta = el("textarea", {}, val);
      ta.addEventListener("input", ()=>{ S.draft[key][i] = ta.value; markDirty(); });
      const del = el("button", {class:"ghost del", title:"remove",
        onclick:()=>{ S.draft[key].splice(i,1); markDirty(); rerender(); }}, "✕");
      items.append(el("div", {class:"list-item"}, ta, del));
    });
  }
  container.append(
    el("div", {class:"field-head"}, el("label", {}, label),
      key==="mes_example" ? assistBarForExamples() : el("span",{})),
    el("div", {class:"meta hint", style:"margin:0 0 8px"}, hint),
    items,
    el("button", {class:"secondary", onclick:()=>{
      (S.draft[key] = S.draft[key]||[]).push(""); markDirty(); rerender(); }}, "+ add "+itemLabel));
  rerender();
  return container;
}

function assistBarForExamples(){
  return el("div", {class:"assist-btns"},
    el("button", {class:"ghost", title:"Draft a new example exchange",
      onclick:()=>runAssist("mes_example","draft")}, "✦ draft an example"));
}

function lorebookEditor(){
  const lb = S.draft.lorebook = S.draft.lorebook || {scan_depth:4, token_budget:600, recursive_scanning:false, entries:[]};
  const container = el("div", {class:"field"});
  const items = el("div");
  function rerender(){
    items.innerHTML = "";
    lb.entries.forEach((e, i)=>{
      const keys = el("input", {type:"text", placeholder:"trigger keys, comma-separated",
        value:Array.isArray(e.keys)?e.keys.join(", "):(e.keys||"")});
      keys.addEventListener("input", ()=>{ e.keys = keys.value.split(",").map(s=>s.trim()).filter(Boolean); markDirty(); });
      const content = el("textarea", {placeholder:"what she knows / the world fact"}, e.content||"");
      content.addEventListener("input", ()=>{ e.content = content.value; markDirty(); });
      const del = el("button", {class:"ghost", title:"remove entry",
        onclick:()=>{ lb.entries.splice(i,1); markDirty(); rerender(); }}, "✕ remove entry");
      items.append(el("div", {class:"field", style:"background:var(--lab-bg-3)"},
        keys, el("div",{style:"height:6px"}), content, el("div",{style:"height:6px"}), del));
    });
  }
  container.append(
    el("div", {class:"field-head"}, el("label", {}, "Lorebook (fires on keys)"),
      el("div", {class:"assist-btns"},
        el("button",{class:"ghost", title:"Draft a lorebook entry",
          onclick:()=>runAssist("lorebook","draft")}, "✦ draft entry"))),
    el("div", {class:"meta hint", style:"margin:0 0 8px"},
      "World facts loaded only when a key is mentioned. Keep it sparse; let reveals be earned (→ ch.08, ch.38)."),
    items,
    el("button", {class:"secondary", onclick:()=>{
      lb.entries.push({keys:[], content:""}); markDirty(); rerender(); }}, "+ add entry"));
  rerender();
  return container;
}

function metaRow(){
  const mk = (key, label, type="text") => {
    const inp = el("input", {type, value:S.draft[key]||""});
    inp.addEventListener("input", ()=>{ S.draft[key] = inp.value; markDirty(); });
    return el("div", {}, el("label", {class:"meta"}, label), inp);
  };
  const tags = el("input", {type:"text", value:(S.draft.tags||[]).join(", ")});
  tags.addEventListener("input", ()=>{ S.draft.tags = tags.value.split(",").map(s=>s.trim()).filter(Boolean); markDirty(); });
  return el("div", {class:"field"},
    el("div", {class:"row"}, mk("creator","Creator"), mk("character_version","Version")),
    el("div", {style:"height:10px"}),
    el("div", {}, el("label", {class:"meta"}, "Tags (comma-separated)"), tags));
}

function principlesPanel(){
  const ul = el("ul");
  for (const p of S.principles)
    ul.append(el("li", {}, el("b", {}, p.title+": "), p.rule+" ", el("span", {class:"do"}, "→ "+p.do)));
  return el("details", {class:"principles"},
    el("summary", {}, "Character-design principles (ch. 06) — the recipe"), ul);
}

function renderDesign(){
  const root = $("#tab-design"); root.innerHTML = "";
  root.append(
    el("h2", {}, "Design the character"),
    el("p", {class:"hint"}, "Edit the fields. Use ✎/✦/? for AI help grounded in the book's design principles. Everything autosaves."),
    principlesPanel(),
    ...TEXT_FIELDS.map(textField),
    listEditor("examples","Example dialogue","The highest-ROI field — the model imitates shown voice. One behaviour per exchange (→ ch.06 §5).","example"),
    listEditor("alternate_greetings","Return greetings","Shown when she's met the user before (alternate greetings).","greeting"),
    lorebookEditor(),
    metaRow());
}

async function runAssist(field, mode){
  const current = field==="mes_example" || field==="lorebook" ? "" : (S.draft[field]||"");
  const loading = el("div", {}, el("span", {class:"spinner"}), " thinking…");
  showModal("Assistant · "+field, loading, [el("button", {class:"ghost", onclick:closeModal}, "Cancel")]);
  try {
    const {suggestion} = await postJSON("/api/assist", {field, current, mode, draft:S.draft});
    const body = el("div", {}, suggestion);
    const actions = [];
    if (mode !== "suggest"){
      if (field === "mes_example")
        actions.push(el("button", {class:"primary", onclick:()=>{
          (S.draft.examples = S.draft.examples||[]).push(suggestion.trim()); markDirty(); closeModal(); renderDesign(); toast("added example","ok"); }}, "Add as example"));
      else if (field === "lorebook")
        actions.push(el("button", {class:"primary", onclick:()=>{
          const lb = S.draft.lorebook; lb.entries.push({keys:[], content:suggestion.trim()}); markDirty(); closeModal(); renderDesign(); toast("added entry","ok"); }}, "Add as entry"));
      else
        actions.push(el("button", {class:"primary", onclick:()=>{
          S.draft[field] = suggestion.trim(); markDirty(); closeModal(); renderDesign(); toast("field updated","ok"); }}, "Use this"));
    }
    actions.push(el("button", {class:"secondary", onclick:()=>{ navigator.clipboard?.writeText(suggestion); toast("copied","ok"); }}, "Copy"));
    actions.push(el("button", {class:"ghost", onclick:closeModal}, "Dismiss"));
    showModal("Assistant · "+field+" ("+mode+")", body, actions);
  } catch(e){
    showModal("Assistant", el("div", {}, "Error: "+e.message), [el("button", {class:"ghost", onclick:closeModal}, "Close")]);
  }
}

// ============================================================================
//  ART TAB
// ============================================================================
let artCandidates = [];
function renderArt(){
  const root = $("#tab-art"); root.innerHTML = "";
  const promptSeed = "anime portrait, " + (S.draft.personality || "") +
    ". soft warm lighting, 2.5D anime style, detailed, single character, upper body";
  const promptBox = el("textarea", {}, promptSeed);
  const grid = el("div", {class:"art-grid"});
  const current = el("div", {class:"portrait-current"});
  function refreshCurrent(){
    current.innerHTML = "";
    if (S.hasPortrait){
      current.append(
        el("img", {src:"/api/portrait?ts="+Date.now(), alt:"selected portrait"}),
        el("div", {}, el("div", {class:"badge good"}, "portrait selected"),
          el("div", {style:"height:8px"}),
          el("button", {class:"ghost", onclick:async ()=>{ await fetch("/api/portrait",{method:"DELETE"}); S.hasPortrait=false; refreshCurrent(); toast("portrait cleared"); }}, "clear portrait")));
    } else {
      current.append(el("div", {class:"badge warn"}, "no portrait yet — generate or upload one; a placeholder is used until then"));
    }
  }
  const genBtn = el("button", {class:"primary", onclick:async ()=>{
    grid.innerHTML = ""; grid.append(el("div", {}, el("span",{class:"spinner"})," generating "+ (S.settings.image_count||2) +" candidate(s) via "+S.settings.image_model+"…"));
    try {
      const {images} = await postJSON("/api/image", {prompt:promptBox.value});
      artCandidates = images; renderCandidates();
    } catch(e){ grid.innerHTML = ""; grid.append(el("div",{class:"badge warn"}, "image error: "+e.message)); }
  }}, "✦ Generate art");
  const upload = el("input", {type:"file", accept:"image/*", style:"display:none",
    onchange:(ev)=>uploadPortrait(ev.target.files[0], refreshCurrent)});
  function renderCandidates(){
    grid.innerHTML = "";
    artCandidates.forEach((src, i)=>{
      const cell = el("div", {class:"art-cell", onclick:async ()=>{
        try { await postJSON("/api/portrait", {image:src}); S.hasPortrait=true;
          $$(".art-cell").forEach(c=>c.classList.remove("selected")); cell.classList.add("selected");
          refreshCurrent(); toast("portrait selected","ok"); }
        catch(e){ toast("could not select: "+e.message,"err"); }
      }}, el("span", {class:"tag"}, "#"+(i+1)), el("img", {src, alt:"candidate "+(i+1)}));
      grid.append(cell);
    });
  }
  root.append(
    el("h2", {}, "Art & branding"),
    el("p", {class:"hint"}, "Describe the look, generate candidates through OpenRouter, and pick the one that becomes the card's portrait. Consistency is the identity (→ ch.26)."),
    el("div", {class:"field"},
      el("label", {class:"meta"}, "Image prompt"), promptBox,
      el("div", {style:"height:10px"}),
      el("div", {class:"row"}, genBtn,
        el("button", {class:"secondary", onclick:()=>upload.click()}, "⭱ Upload your own"), upload)),
    grid,
    el("h2", {style:"margin-top:22px"}, "Current portrait"),
    current);
  refreshCurrent();
}
async function uploadPortrait(file, done){
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async ()=>{
    try { await postJSON("/api/portrait", {image:reader.result}); S.hasPortrait=true; done(); toast("portrait set","ok"); }
    catch(e){ toast("upload failed: "+e.message,"err"); }
  };
  reader.readAsDataURL(file);
}

// ============================================================================
//  TEST TAB
// ============================================================================
function renderTest(){
  const root = $("#tab-test"); root.innerHTML = "";
  const log = el("div", {class:"chat"});
  const input = el("textarea", {placeholder:"say something to "+(S.draft.name||"her")+"…"});
  function draw(){
    log.innerHTML = "";
    if (S.draft.first_mes) log.append(msgNode("assistant", S.draft.name||"her", S.draft.first_mes));
    for (const m of testHistory) log.append(msgNode(m.role, S.draft.name||"her", m.content));
    log.scrollTop = log.scrollHeight;
  }
  async function send(){
    const text = input.value.trim(); if (!text) return;
    input.value = ""; testHistory.push({role:"user", content:text}); draw();
    const thinking = msgNode("assistant", S.draft.name||"her", "…"); log.append(thinking); log.scrollTop = log.scrollHeight;
    try {
      await postJSON("/api/draft", S.draft);   // make sure the server tests what you see
      const {reply} = await postJSON("/api/chat", {message:text, history:testHistory, draft:S.draft});
      testHistory.push({role:"assistant", content:reply});
    } catch(e){ testHistory.push({role:"assistant", content:"[error: "+e.message+"]"}); }
    draw();
  }
  input.addEventListener("keydown", (e)=>{ if (e.key==="Enter" && !e.shiftKey){ e.preventDefault(); send(); }});
  root.append(
    el("h2", {}, "Test the card"),
    el("p", {class:"hint"}, "Talk to the character exactly as a runtime would assemble her, before you ship. Uses your OpenRouter chat model."),
    log,
    el("div", {class:"chat-input"}, input, el("button", {class:"primary", onclick:send}, "Send")),
    el("div", {style:"margin-top:8px"},
      el("button", {class:"ghost", onclick:()=>{ testHistory=[]; draw(); }}, "↺ start over")));
  draw();
}
function msgNode(role, name, content){
  return el("div", {class:"msg "+role},
    el("span", {class:"who"}, role==="user" ? "you" : name), content);
}

// ============================================================================
//  GENERATE TAB
// ============================================================================
function renderGenerate(){
  const root = $("#tab-generate"); root.innerHTML = "";
  const specSel = el("select", {}, el("option", {value:"v3"}, "V3 (chara + ccv3)"), el("option", {value:"v2"}, "V2 (chara only)"));
  const out = el("div");
  const importInput = el("input", {type:"file", accept:".png,.json", style:"display:none",
    onchange:(ev)=>importCard(ev.target.files[0])});
  const buildBtn = el("button", {class:"primary", onclick:async ()=>{
    out.innerHTML = ""; out.append(el("div", {}, el("span",{class:"spinner"})," building & self-verifying…"));
    try {
      await postJSON("/api/draft", S.draft);
      const r = await postJSON("/api/build", {draft:S.draft, spec:specSel.value});
      renderReport(out, r);
    } catch(e){ out.innerHTML=""; out.append(el("div", {class:"badge warn"}, "build failed: "+e.message)); }
  }}, "⚙ Generate card");
  root.append(
    el("h2", {}, "Generate the .PNG"),
    el("p", {class:"hint"}, "Flatten the draft into a SillyTavern-ready character card and self-verify it parses. The token report shows where your budget went (→ ch.07)."),
    el("div", {class:"field"},
      el("div", {class:"row"},
        el("div", {}, el("label", {class:"meta"}, "Card spec"), specSel),
        el("div", {style:"display:flex; align-items:flex-end; gap:8px"}, buildBtn,
          el("button", {class:"secondary", onclick:()=>importInput.click()}, "⭱ Import a card"), importInput))),
    out);
}
function renderReport(out, r){
  out.innerHTML = "";
  const chunks = Object.entries(r.verified_chunks||{}).map(([k,v])=>k+" ("+v+")").join(", ");
  const head = el("div", {},
    el("span", {class:"badge good"}, "verified: "+chunks),
    el("span", {class:"badge"}, "spec "+r.spec));
  if (r.used_placeholder_portrait) head.append(el("span", {class:"badge warn"}, "placeholder portrait — pick art in the Art tab"));
  const rows = (r.report||[]).map(row=>el("tr", {},
    el("td", {}, row.field),
    el("td", {class:row.over?"over":""}, String(row.tokens)),
    el("td", {class:row.over?"over":""}, row.budget + (row.over?"  (over)":""))));
  const table = el("table", {class:"report"},
    el("tr", {}, el("th",{},"field"), el("th",{},"~tokens"), el("th",{},"budget")), ...rows);
  const warns = (r.warnings||[]).length
    ? el("div", {class:"badge warn", style:"display:block; margin:8px 0"}, "⚠ "+r.warnings.join("  ·  ")) : el("span");
  out.append(head, table, warns,
    el("div", {class:"row", style:"margin-top:10px"},
      el("button", {class:"primary", onclick:()=>location.href="/api/download/card"}, "⭳ Download .PNG"),
      el("button", {class:"secondary", onclick:()=>location.href="/api/download/soul"}, "⭳ Download editable soul (.zip)")));
}
async function importCard(file){
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async ()=>{
    try {
      const r = await postJSON("/api/import", {filename:file.name, data:reader.result});
      S.draft = r.draft; S.hasPortrait = r.has_portrait || S.hasPortrait;
      renderAll(); toast("imported "+(S.draft.name||"card"),"ok");
    } catch(e){ toast("import failed: "+e.message,"err"); }
  };
  reader.readAsDataURL(file);
}

// ============================================================================
//  SETTINGS TAB
// ============================================================================
function renderSettings(){
  const root = $("#tab-settings"); root.innerHTML = "";
  const s = S.settings;
  const f = {};
  const field = (key, label, type="text", hint="") => {
    const inp = el("input", {type, value:(s[key]??"")}); f[key]=inp;
    return el("div", {class:"field"}, el("label", {class:"meta"}, label), inp,
      hint?el("div",{class:"meta hint", style:"margin-top:6px"},hint):el("span"));
  };
  const keyField = field("openrouter_api_key","OpenRouter API key","password",
    "Resolved from here → OPENROUTER_API_KEY env → the Build #2 .env. Currently: "+(s.has_key?("using "+s.key_source):"NO KEY FOUND"));
  root.append(
    el("h2", {}, "Settings"),
    el("p", {class:"hint"}, "OpenRouter config. Model ids drift — edit freely. Nothing here leaves your machine except calls you make."),
    keyField,
    field("base_url","Base URL"),
    el("div", {class:"row"}, field("assist_model","Assist model (writing help)"), field("chat_model","Chat model (test)")),
    el("div", {class:"row"}, field("image_model","Image model"), field("image_count","Candidates per generate","number")),
    el("div", {class:"row"}, field("temperature","Temperature","number"), field("max_tokens","Max tokens","number")),
    el("div", {class:"field", style:"background:none; border:none; padding:0"},
      el("div", {class:"meta hint", style:"margin-bottom:8px"}, "Text presets: z-ai/glm-5.2 (default, reasoning — keep max tokens ≥2048) · venice/uncensored (free) · thedrummer/cydonia-24b-v4.1 · neversleep/llama-3-lumimaid-70b. Image: google/gemini-2.5-flash-image · google/gemini-3.1-flash-image-preview · bytedance-seed/seedream-4.5"),
      el("button", {class:"primary", onclick:async ()=>{
        const patch = {};
        for (const [k,inp] of Object.entries(f)){
          let v = inp.value;
          if (inp.type==="number") v = parseFloat(v);
          if (k==="openrouter_api_key" && v.includes("…")) continue; // masked, unchanged
          patch[k]=v;
        }
        try { S.settings = await postJSON("/api/settings", patch); renderSettings(); updateKeyBadge(); toast("settings saved","ok"); }
        catch(e){ toast("save failed: "+e.message,"err"); }
      }}, "Save settings")));
}

// ============================================================================
//  SHELL
// ============================================================================
function updateKeyBadge(){
  const b = $("#key-badge");
  if (S.settings.has_key){ b.textContent = "key ✓"; b.className = "key-badge ok"; b.title = "key source: "+S.settings.key_source; }
  else { b.textContent = "no key"; b.className = "key-badge no"; b.title = "set a key in Settings"; }
}
function renderAll(){ renderDesign(); renderArt(); renderTest(); renderGenerate(); renderSettings(); updateKeyBadge(); }

function wireTabs(){
  $$("#tabs button").forEach(btn=>btn.addEventListener("click", ()=>{
    $$("#tabs button").forEach(b=>b.classList.remove("active")); btn.classList.add("active");
    $$(".tab").forEach(t=>t.classList.remove("active"));
    $("#tab-"+btn.dataset.tab).classList.add("active");
  }));
  $("#modal-close").addEventListener("click", closeModal);
  $("#modal").addEventListener("click", (e)=>{ if (e.target.id==="modal") closeModal(); });
}

async function boot(){
  wireTabs();
  try {
    const st = await getJSON("/api/state");
    S.draft = st.draft; S.settings = st.settings; S.principles = st.principles;
    S.fieldPrinciples = st.field_principles; S.hasPortrait = st.has_portrait;
    renderAll();
  } catch(e){ toast("failed to load: "+e.message, "err"); }
}
boot();
