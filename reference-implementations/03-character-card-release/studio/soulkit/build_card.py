#!/usr/bin/env python3
"""
build_card.py — flatten a Yuri SOUL (folder of .md files) into an exportable
V2/V3 character-card PNG for SillyTavern.

The .md files are the working home of the soul (read on every wake at runtime,
split into an immutable CONSTITUTION and an editable PERSONA — D-002). A card is
just the *export* of that soul (D-003): this script reads soul.yaml, assembles
the card fields from the .md files, and writes both a .json and a .png with the
card embedded in a tEXt chunk.

Usage:
    python build_card.py                 # build from ./soul.yaml -> ./dist/
    python build_card.py --spec v3       # export a V3 card (adds ccv3 chunk)
    python build_card.py --out /tmp/out  # choose output dir
    python build_card.py --soul ./        # choose soul folder

Dependencies: Pillow, PyYAML  (see requirements.txt)
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import re
import struct
import sys
import zlib
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: PyYAML.  pip install -r requirements.txt")
try:
    from PIL import Image
except ImportError:
    sys.exit("Missing dependency: Pillow.  pip install -r requirements.txt")


# --- parsing helpers --------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
H2_RE = re.compile(r"^##\s+(.*?)\s*$", re.MULTILINE)


def parse_md(path: Path) -> tuple[dict, str]:
    """Return (frontmatter dict, body) for a soul .md file."""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if m:
        front = yaml.safe_load(m.group(1)) or {}
        body = text[m.end():]
    else:
        front, body = {}, text
    return front, body


def split_sections(body: str) -> dict[str, str]:
    """Map each '## Heading' to the prose beneath it (order preserved)."""
    sections: dict[str, str] = {}
    matches = list(H2_RE.finditer(body))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[m.group(1).strip()] = body[start:end].strip()
    return sections


class Soul:
    """Lazy reader/cache over the soul folder."""

    def __init__(self, folder: Path):
        self.folder = folder
        self._front: dict[str, dict] = {}
        self._sections: dict[str, dict[str, str]] = {}
        self._body: dict[str, str] = {}

    def _load(self, fname: str):
        if fname not in self._front:
            path = self.folder / fname
            if not path.exists():
                raise FileNotFoundError(f"soul references missing file: {fname}")
            front, body = parse_md(path)
            self._front[fname] = front
            self._body[fname] = body.strip()
            self._sections[fname] = split_sections(body)

    def front(self, fname: str) -> dict:
        self._load(fname); return self._front[fname]

    def body(self, fname: str) -> str:
        self._load(fname); return self._body[fname]

    def section(self, fname: str, heading: str) -> str:
        self._load(fname)
        secs = self._sections[fname]
        if heading not in secs:
            raise KeyError(f"{fname}: no '## {heading}' section "
                           f"(have: {', '.join(secs) or 'none'})")
        return secs[heading]

    def sections(self, fname: str) -> dict[str, str]:
        self._load(fname); return self._sections[fname]

    def resolve(self, ref: str) -> str:
        """Resolve a 'FILE#Heading' / 'FILE@key' / 'FILE' reference to text."""
        if "#" in ref:
            fname, heading = ref.split("#", 1)
            return self.section(fname.strip(), heading.strip())
        if "@" in ref:
            fname, key = ref.split("@", 1)
            val = self.front(fname.strip()).get(key.strip())
            if val is None:
                raise KeyError(f"{fname}: no frontmatter key '{key}'")
            return str(val)
        return self.body(ref.strip())

    def resolve_field(self, src) -> str:
        if isinstance(src, list):
            return "\n\n".join(self.resolve(r) for r in src)
        return self.resolve(src)

    def resolve_list(self, src) -> list[str]:
        srcs = src if isinstance(src, list) else [src]
        return [self.resolve(r) for r in srcs]


# --- structured fields ------------------------------------------------------

def build_examples(soul: Soul, fname: str) -> str:
    """Each '## Example ...' block -> one <START> exchange, joined."""
    blocks = [content for heading, content in soul.sections(fname).items()
              if heading.lower().startswith("example")]
    return "\n".join(f"<START>\n{b.strip()}" for b in blocks)


def build_character_book(soul: Soul, fname: str) -> dict:
    """WORLD.md frontmatter + each '## Entry' (with a 'keys:' line) -> lorebook."""
    front = soul.front(fname)
    entries = []
    for order, (heading, content) in enumerate(soul.sections(fname).items(), start=1):
        lines = content.strip().splitlines()
        keys: list[str] = []
        rest = lines
        for i, line in enumerate(lines):
            if line.lower().startswith("keys:"):
                keys = [k.strip() for k in line.split(":", 1)[1].split(",") if k.strip()]
                rest = lines[:i] + lines[i + 1:]
                break
        if not keys:  # a section without keys isn't a lorebook entry; skip it
            continue
        entries.append({
            "keys": keys,
            "content": "\n".join(rest).strip(),
            "enabled": True,
            "insertion_order": order,
            "case_sensitive": False,
            "extensions": {},
        })
    return {
        "name": front.get("name", "lorebook"),
        "description": front.get("description", ""),
        "scan_depth": front.get("scan_depth", 4),
        "token_budget": front.get("token_budget", 600),
        "recursive_scanning": front.get("recursive_scanning", False),
        "extensions": {},
        "entries": entries,
    }


# --- card assembly ----------------------------------------------------------

def build_data(soul: Soul, manifest: dict, slug: str) -> dict:
    f = manifest["fields"]
    data = {
        "name": manifest["name"],
        "description": soul.resolve_field(f["description"]),
        "personality": soul.resolve_field(f["personality"]),
        "scenario": soul.resolve_field(f["scenario"]),
        "first_mes": soul.resolve_field(f["first_mes"]),
        "mes_example": build_examples(soul, f["mes_example"]),
        "system_prompt": soul.resolve_field(f["system_prompt"]),
        "post_history_instructions": soul.resolve_field(f["post_history_instructions"]),
        "alternate_greetings": soul.resolve_list(f.get("alternate_greetings", [])),
        "creator_notes": soul.resolve_field(f["creator_notes"]),
        "tags": manifest.get("tags", []),
        "creator": manifest.get("creator", ""),
        "character_version": str(manifest.get("character_version", "1.0.0")),
        "character_book": build_character_book(soul, f["character_book"]),
        "extensions": {
            "yurios": {
                "card_release": slug,
                "canon": manifest.get("canon", ""),
                "lineage": manifest.get("lineage", "YuriOS"),
                "provenance": {
                    "creator": manifest.get("creator", ""),
                    "card_version": str(manifest.get("character_version", "1.0.0")),
                },
            }
        },
    }
    return data


def wrap_card(data: dict, spec: str) -> dict:
    if spec == "v3":
        return {"spec": "chara_card_v3", "spec_version": "3.0", "data": data}
    return {"spec": "chara_card_v2", "spec_version": "2.0", "data": data}


def _text_chunk(keyword: str, text: str) -> bytes:
    """Build a PNG `tEXt` chunk (length + type + keyword\\0text + CRC32)."""
    body = keyword.encode("latin-1") + b"\x00" + text.encode("latin-1")
    return (struct.pack(">I", len(body)) + b"tEXt" + body
            + struct.pack(">I", zlib.crc32(b"tEXt" + body) & 0xFFFFFFFF))


def embed_png(portrait: Path, out_png: Path, cards: dict[str, dict]):
    """Write the portrait with each card JSON in a base64 `tEXt` chunk.

    SillyTavern reads ONLY `tEXt` chunks (keyword 'chara' for V2, 'ccv3' for
    V3). We write the chunk bytes by hand and splice them in right after IHDR,
    rather than relying on Pillow's PngInfo — some Pillow versions emit `iTXt`,
    which SillyTavern's parser ignores ("no text chunks"). base64 is ASCII, so
    it is always latin-1 safe for a tEXt chunk.
    """
    buf = io.BytesIO()
    Image.open(portrait).convert("RGB").save(buf, format="PNG")
    png = buf.getvalue()
    ihdr_end = 8 + 4 + 4 + 13 + 4  # sig + (len + "IHDR" + 13 data + CRC) = 33
    chunks = b"".join(
        _text_chunk(kw, base64.b64encode(
            json.dumps(card, ensure_ascii=False).encode("utf-8")).decode("ascii"))
        for kw, card in cards.items()
    )
    out_png.write_bytes(png[:ihdr_end] + chunks + png[ihdr_end:])


def verify_png(out_png: Path) -> dict[str, str]:
    """Re-parse the file the way SillyTavern does: tEXt chunks only, CRC-checked,
    base64 -> JSON. Returns {keyword: character name}. Raises on any failure."""
    data = out_png.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    found: dict[str, str] = {}
    off = 8
    while off < len(data):
        (length,) = struct.unpack(">I", data[off:off + 4])
        ctype = data[off + 4:off + 8]
        body = data[off + 8:off + 8 + length]
        (stored_crc,) = struct.unpack(">I", data[off + 8 + length:off + 12 + length])
        if ctype == b"tEXt":
            if zlib.crc32(ctype + body) & 0xFFFFFFFF != stored_crc:
                raise ValueError("tEXt CRC mismatch — SillyTavern would reject this")
            keyword, _, text = body.partition(b"\x00")
            card = json.loads(base64.b64decode(text))
            found[keyword.decode("latin-1")] = card["data"]["name"]
        off += 12 + length
    if not found:
        raise ValueError("no tEXt chunks present — SillyTavern would reject this")
    return found


def extract_card(png_path: Path) -> dict:
    """Read a character card back out of a PNG's tEXt chunks (the inverse of
    embed_png). Returns the full card wrapper ({"spec", "spec_version", "data"}),
    preferring a V3 'ccv3' chunk over the V2 'chara' chunk when both are present.
    Used by import_card.py and the round-trip check.
    """
    raw = png_path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{png_path}: not a PNG")
    chunks: dict[str, dict] = {}
    off = 8
    while off + 8 <= len(raw):
        (length,) = struct.unpack(">I", raw[off:off + 4])
        ctype = raw[off + 4:off + 8]
        body = raw[off + 8:off + 8 + length]
        if ctype == b"tEXt":
            keyword, _, text = body.partition(b"\x00")
            try:
                chunks[keyword.decode("latin-1")] = json.loads(base64.b64decode(text))
            except (ValueError, json.JSONDecodeError):
                pass  # not a card chunk (e.g. a plain caption) — skip
        if ctype == b"IEND":
            break
        off += 12 + length
    for kw in ("ccv3", "chara"):
        if kw in chunks:
            return chunks[kw]
    raise ValueError(f"{png_path}: no character-card tEXt chunk (chara/ccv3) found")


# --- OpenClaw / Hermes single-file SOUL export ------------------------------

def soul_md(data: dict, manifest: dict | None = None) -> str:
    """Flatten card data into a single OpenClaw/Hermes-style `SOUL.md`.

    A foreign single-file compatibility target (→ ch. 07): the soul's split into
    CONSTITUTION/PERSONA is a YuriOS-runtime concern; runtimes that want one flat
    file get everything the card carries laid out as readable Markdown.
    """
    name = data.get("name", "Companion")
    version = str((manifest or {}).get("character_version",
                                       data.get("character_version", "1.0.0")))
    out = ["---", f"name: {name}", f"version: {version}",
           "format: openclaw-soul", "---", "", f"# {name}", ""]

    def section(title: str, body) -> None:
        body = (body or "").strip()
        if body:
            out.extend([f"## {title}", "", body, ""])

    section("Description", data.get("description"))
    section("Personality", data.get("personality"))
    section("Scenario", data.get("scenario"))
    section("First message", data.get("first_mes"))
    for i, greet in enumerate(data.get("alternate_greetings") or [], start=1):
        section(f"Alternate greeting {i}", greet)
    section("Example dialogue", data.get("mes_example"))
    section("System prompt", data.get("system_prompt"))
    section("Hard limits", data.get("post_history_instructions"))

    entries = (data.get("character_book") or {}).get("entries") or []
    if entries:
        out.extend(["## World & lore", ""])
        for e in entries:
            keys = ", ".join(e.get("keys", [])) or "entry"
            out.extend([f"### {keys}", "", (e.get("content") or "").strip(), ""])

    section("Notes", data.get("creator_notes"))
    return "\n".join(out).rstrip() + "\n"


# --- token report (approx, chars/4) against ch.07 budgets -------------------

BUDGETS = {  # (low, high) soft guidance from book ch.07
    "description": (150, 300),
    "personality": (40, 80),
    "scenario": (30, 60),
    "first_mes": (80, 200),
}


def report(data: dict):
    def tok(s: str) -> int:
        return max(1, round(len(s) / 4)) if s else 0
    print("\n  field                approx tokens   ch.07 budget")
    print("  " + "-" * 52)
    for field in ("description", "personality", "scenario", "first_mes",
                  "mes_example", "system_prompt", "post_history_instructions"):
        n = tok(data[field])
        lo_hi = BUDGETS.get(field)
        note = ""
        if lo_hi:
            lo, hi = lo_hi
            note = f"{lo}-{hi}"
            if n > hi:
                note += "  (over)"
        elif field == "mes_example":
            note = "spend freely"
        else:
            note = "minimal"
        print(f"  {field:<28}{n:>6}   {note}")
    n_entries = len(data["character_book"]["entries"])
    print(f"  character_book              {n_entries:>3} entries   (fires on keys)")


# --- main -------------------------------------------------------------------

def build_card_data(soul_dir: Path, spec: str | None = None, name: str | None = None):
    """Load a soul folder + its manifest and assemble the card data dict.

    Returns (manifest, spec, slug, data). Shared by the CLI and by
    import_card.py's round-trip check (it re-exports an imported soul and
    compares the result to the original card).
    """
    manifest_path = soul_dir / "soul.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No soul.yaml in {soul_dir}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if name:
        manifest["name"] = name
    spec = spec or manifest.get("spec", "v2")
    soul = Soul(soul_dir)
    slug = manifest["name"].strip().lower().replace(" ", "-")
    data = build_data(soul, manifest, slug)
    return manifest, spec, slug, data


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Build a Yuri character card from the SOUL.")
    ap.add_argument("--soul", type=Path, default=here, help="soul folder (default: script dir)")
    ap.add_argument("--out", type=Path, default=None, help="output dir (default: <soul>/dist)")
    ap.add_argument("--spec", choices=["v2", "v3"], default=None, help="card spec (default: manifest)")
    ap.add_argument("--name", default=None, help="override character name")
    args = ap.parse_args()

    soul_dir = args.soul.resolve()
    try:
        manifest, spec, slug, data = build_card_data(soul_dir, args.spec, args.name)
    except (FileNotFoundError, KeyError) as e:
        sys.exit(f"Build error: {e}")

    # validate against the immutable voice law as a smoke test
    if "!" in data["first_mes"] or "!" in data["mes_example"]:
        print("  WARNING: exclamation mark found — violates Yuri's voice law.")

    out_dir = (args.out or (soul_dir / "dist")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    card = wrap_card(data, spec)
    json_path = out_dir / f"{slug}.json"
    json_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")

    soul_md_path = out_dir / "SOUL.md"
    soul_md_path.write_text(soul_md(data, manifest), encoding="utf-8")

    portrait = soul_dir / manifest.get("portrait", "portrait.png")
    if not portrait.exists():
        sys.exit(f"Portrait not found: {portrait}")

    chunks = {"chara": wrap_card(data, "v2")}
    if spec == "v3":
        chunks["ccv3"] = wrap_card(data, "v3")
    png_path = out_dir / f"{slug}.png"
    embed_png(portrait, png_path, chunks)

    try:
        verified = verify_png(png_path)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        sys.exit(f"Build wrote {png_path} but self-verification failed: {e}")

    print(f"Built {manifest['name']} ({spec}) from {soul_dir.name}/")
    print(f"  -> {png_path}")
    print(f"  -> {json_path}")
    print(f"  -> {soul_md_path}  (OpenClaw/Hermes single-file SOUL)")
    report(data)
    chunk_list = ", ".join(f"{kw} ({name})" for kw, name in verified.items())
    print(f"\n  verified SillyTavern-readable tEXt chunk(s): {chunk_list}")
    print(f"\nImport THIS file in SillyTavern (not portrait.png):"
          f"\n  Characters -> Import Character -> {png_path}")


if __name__ == "__main__":
    main()
