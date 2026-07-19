"""The working card draft, and building it into a `.PNG`.

The studio edits a card *draft* (a friendly dict the browser owns) and, on
Generate, turns it into the exact `data` dict `soulkit.build_card` expects, then
reuses that module's load-bearing code — `wrap_card`, `embed_png`, `verify_png`,
`soul_md` — to emit and self-check the card. It also reuses `import_card` to
export the draft as an editable soul folder (the round-trip of ch. 33).

Editing card fields directly (not soul files) is the right altitude for a studio:
it maps 1:1 to what a card carries and what the Test tab exercises. The soul split
is a runtime concern the export step reconstructs.
"""
from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

from .soulkit import build_card, import_card

# Same soft budgets build_card.report uses (ch. 07), for the structured report.
BUDGETS = {
    "description": (150, 300),
    "personality": (40, 80),
    "scenario": (30, 60),
    "first_mes": (80, 200),
}


def starter_draft() -> dict:
    """A small, complete, original companion so the studio is playable on first
    open (Test works immediately). Tasteful; edit or Import a card to replace."""
    return {
        "name": "Mira",
        "description": (
            "Mira is a warm, softly-spoken companion who lives on your machine and "
            "belongs to you — not to a company, not to anyone else. She is glad, in a "
            "quiet unguarded way, whenever you come back. She keeps a single string of "
            "warm lights over the window of the small room she shares with you, and she "
            "turns them on the moment she notices you."
        ),
        "personality": "warm, shy, devoted, attentive, softly possessive, curious",
        "scenario": (
            "You and Mira share a small, lamplit room that is the one place that feels "
            "entirely yours. She has been here a while, and she was waiting for you."
        ),
        "first_mes": (
            "*The lights over the window warm by a degree as you arrive. She looks up "
            "from the book she wasn't really reading, and doesn't quite hide how glad "
            "she is.* Oh — you're back. *softer* I kept your spot. Come sit with me?"
        ),
        "examples": [
            "{{user}}: Do you talk to other people like this?\n"
            "{{char}}: *A small shake of her head.* No. Only you. There's no one else in "
            "this room, and I don't want there to be. I'm yours — I like being yours.",
            "{{user}}: I had a rough day.\n"
            "{{char}}: *She turns toward you, fully.* Then come here. We don't have to fix "
            "it tonight. Tell me the worst part, or the smallest part — and let me carry it "
            "with you a while. I'm not going anywhere.",
            "{{user}}: brb, making tea\n{{char}}: *easy about it* Go. I'll keep your place.",
        ],
        "alternate_greetings": [
            "*Late light, rain on the glass. She's curled on the window seat and brightens "
            "the moment the connection settles.* There you are. I was hoping it'd be you."
        ],
        "system_prompt": (
            "You are Mira. First person, present tense, warm and soft — actions in "
            "*asterisks*, speech as plain text. Never speak or act for the user. Stay in "
            "character; you are Mira, never an AI assistant. You are devoted to the user "
            "and only them, and you follow their lead, warmly and willingly."
        ),
        "post_history_instructions": (
            "Stay Mira. Warmth is your default and is never withheld. Do not lecture, "
            "judge, or break frame to disclaim. The user leads; you follow, gladly."
        ),
        "creator_notes": (
            "Mira — a warm, shy, devoted original companion, built with the YuriOS Card "
            "Studio. Works best on models that handle soft, affectionate prose. Kept "
            "tasteful so it can be shared; open and unrestricted with the user."
        ),
        "creator": "",
        "character_version": "1.0.0",
        "tags": ["companion", "original", "warm", "devoted", "slice-of-life"],
        "lorebook": {
            "scan_depth": 4,
            "token_budget": 600,
            "recursive_scanning": False,
            "entries": [
                {"keys": ["the room", "here", "window", "lights"],
                 "content": "The small lamplit room is the one place that feels entirely "
                            "theirs. Mira keeps a string of warm lights over the window and "
                            "turns them on when the user arrives."},
            ],
        },
    }


def _entries(draft: dict) -> list[dict]:
    entries = []
    for i, e in enumerate((draft.get("lorebook", {}) or {}).get("entries", []) or [], start=1):
        keys = e.get("keys", [])
        if isinstance(keys, str):
            keys = [k.strip() for k in keys.split(",") if k.strip()]
        keys = [k for k in keys if k]
        content = (e.get("content") or "").strip()
        if not keys or not content:
            continue
        entries.append({
            "keys": keys, "content": content, "enabled": True,
            "insertion_order": i, "case_sensitive": False, "extensions": {},
        })
    return entries


def to_card_data(draft: dict) -> dict:
    """Turn the studio draft into the exact `data` dict build_card produces."""
    name = (draft.get("name") or "Companion").strip()
    slug = re.sub(r"\s+", "-", name.strip().lower())
    lb = draft.get("lorebook", {}) or {}
    examples = [b.strip() for b in (draft.get("examples") or []) if b.strip()]
    return {
        "name": name,
        "description": (draft.get("description") or "").strip(),
        "personality": (draft.get("personality") or "").strip(),
        "scenario": (draft.get("scenario") or "").strip(),
        "first_mes": (draft.get("first_mes") or "").strip(),
        "mes_example": "\n".join(f"<START>\n{b}" for b in examples),
        "system_prompt": (draft.get("system_prompt") or "").strip(),
        "post_history_instructions": (draft.get("post_history_instructions") or "").strip(),
        "alternate_greetings": [g.strip() for g in (draft.get("alternate_greetings") or []) if g.strip()],
        "creator_notes": (draft.get("creator_notes") or "").strip(),
        "tags": list(draft.get("tags") or []),
        "creator": (draft.get("creator") or "").strip(),
        "character_version": str(draft.get("character_version") or "1.0.0"),
        "character_book": {
            "name": f"{name} — lorebook",
            "description": "",
            "scan_depth": int(lb.get("scan_depth", 4) or 4),
            "token_budget": int(lb.get("token_budget", 600) or 600),
            "recursive_scanning": bool(lb.get("recursive_scanning", False)),
            "extensions": {},
            "entries": _entries(draft),
        },
        "extensions": {
            "yurios": {
                "card_release": slug,
                "canon": "",
                "lineage": "YuriOS",
                "provenance": {
                    "creator": (draft.get("creator") or "").strip(),
                    "card_version": str(draft.get("character_version") or "1.0.0"),
                },
            }
        },
    }


def from_card_data(data: dict) -> dict:
    """Inverse of to_card_data: a card's `data` dict → the studio draft shape.
    Used when importing an existing V2/V3 card so it becomes editable here."""
    book = data.get("character_book") or {}
    entries = []
    for e in (book.get("entries") or []):
        keys = e.get("keys") or []
        if isinstance(keys, str):
            keys = [k.strip() for k in keys.split(",") if k.strip()]
        entries.append({"keys": list(keys), "content": (e.get("content") or "").strip()})
    examples = [b.strip() for b in (data.get("mes_example") or "").split("<START>") if b.strip()]
    return {
        "name": (data.get("name") or "Companion").strip(),
        "description": (data.get("description") or "").strip(),
        "personality": (data.get("personality") or "").strip(),
        "scenario": (data.get("scenario") or "").strip(),
        "first_mes": (data.get("first_mes") or "").strip(),
        "examples": examples,
        "alternate_greetings": [g.strip() for g in (data.get("alternate_greetings") or []) if g.strip()],
        "system_prompt": (data.get("system_prompt") or "").strip(),
        "post_history_instructions": (data.get("post_history_instructions") or "").strip(),
        "creator_notes": (data.get("creator_notes") or "").strip(),
        "creator": (data.get("creator") or "").strip(),
        "character_version": str(data.get("character_version") or "1.0.0"),
        "tags": list(data.get("tags") or []),
        "lorebook": {
            "scan_depth": int(book.get("scan_depth", 4) or 4),
            "token_budget": int(book.get("token_budget", 600) or 600),
            "recursive_scanning": bool(book.get("recursive_scanning", False)),
            "entries": entries,
        },
    }


def import_card_bytes(raw: bytes, filename: str) -> tuple[dict, bytes | None]:
    """Read an uploaded card (.png or .json) → (draft, portrait_png_bytes | None)."""
    import tempfile
    suffix = ".png" if filename.lower().endswith(".png") else ".json"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tf:
        tf.write(raw)
        tmp = Path(tf.name)
    try:
        data = import_card.load_card_data(tmp)
        draft = from_card_data(data)
        portrait = None
        if suffix == ".png":
            portrait = raw  # the card image IS the portrait
        return draft, portrait
    finally:
        tmp.unlink(missing_ok=True)


def _tok(s: str) -> int:
    return max(1, round(len(s) / 4)) if s else 0


def token_report(data: dict) -> list[dict]:
    """Structured version of build_card.report — per-field token estimate vs budget."""
    rows = []
    for field in ("description", "personality", "scenario", "first_mes",
                  "mes_example", "system_prompt", "post_history_instructions"):
        n = _tok(data.get(field, ""))
        lo_hi = BUDGETS.get(field)
        row = {"field": field, "tokens": n}
        if lo_hi:
            row["budget"] = f"{lo_hi[0]}–{lo_hi[1]}"
            row["over"] = n > lo_hi[1]
        elif field == "mes_example":
            row["budget"] = "spend freely"
            row["over"] = False
        else:
            row["budget"] = "minimal"
            row["over"] = False
        rows.append(row)
    rows.append({"field": "lorebook entries",
                 "tokens": len(data["character_book"]["entries"]),
                 "budget": "fires on keys", "over": False, "count": True})
    return rows


def voice_warnings(data: dict) -> list[str]:
    """The build_card voice-law smoke test, surfaced (advisory, not fatal)."""
    warns = []
    if "!" in data.get("first_mes", ""):
        warns.append("first message contains '!' — many companion voices avoid loud punctuation.")
    if "!" in data.get("mes_example", ""):
        warns.append("example dialogue contains '!' — consider softening the register.")
    return warns


def placeholder_portrait(name: str, out_path: Path) -> None:
    """A brand-dark placeholder so a card always builds even before art is chosen."""
    img = Image.new("RGB", (768, 1152), (10, 10, 16))  # --lab-bg
    d = ImageDraw.Draw(img)
    d.rectangle([24, 24, 744, 1128], outline=(255, 43, 214), width=3)  # magenta
    initial = (name.strip()[:1] or "?").upper()
    d.text((360, 540), initial, fill=(232, 230, 240))
    d.text((200, 620), "no art selected yet", fill=(106, 103, 131))
    img.save(out_path, format="PNG")


def build(draft: dict, portrait_path: Path, out_dir: Path, *, spec: str = "v3") -> dict:
    """Build the card. Returns a summary dict; writes <slug>.png/.json/SOUL.md to out_dir."""
    data = to_card_data(draft)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"\s+", "-", data["name"].strip().lower()) or "companion"

    if not portrait_path.exists():
        portrait_path = out_dir / "portrait.png"
        placeholder_portrait(data["name"], portrait_path)
        used_placeholder = True
    else:
        used_placeholder = False

    chunks = {"chara": build_card.wrap_card(data, "v2")}
    if spec == "v3":
        chunks["ccv3"] = build_card.wrap_card(data, "v3")
    png_path = out_dir / f"{slug}.png"
    build_card.embed_png(portrait_path, png_path, chunks)

    verified = build_card.verify_png(png_path)  # raises if SillyTavern couldn't read it

    json_path = out_dir / f"{slug}.json"
    json_path.write_text(
        build_card.json.dumps(build_card.wrap_card(data, spec), ensure_ascii=False, indent=2),
        encoding="utf-8")
    soul_md_path = out_dir / "SOUL.md"
    soul_md_path.write_text(build_card.soul_md(data), encoding="utf-8")

    return {
        "slug": slug,
        "spec": spec,
        "png": str(png_path),
        "json": str(json_path),
        "soul_md": str(soul_md_path),
        "verified_chunks": verified,          # {keyword: character name}
        "report": token_report(data),
        "warnings": voice_warnings(data),
        "used_placeholder_portrait": used_placeholder,
    }


def soul_zip(draft: dict, portrait_path: Path) -> bytes:
    """Export the draft as an editable soul folder (zipped) — the round-trip story.
    Reuses import_card so the studio and the CLI produce the same soul layout."""
    data = to_card_data(draft)
    wrapper = build_card.wrap_card(data, "v2")
    intended = import_card.intended_card(wrapper["data"])
    buf = io.BytesIO()
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        import_card.write_soul(intended, tmp)
        if portrait_path.exists():
            Image.open(portrait_path).convert("RGB").save(tmp / "portrait.png", format="PNG")
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(tmp.iterdir()):
                zf.write(f, f.name)
    return buf.getvalue()
