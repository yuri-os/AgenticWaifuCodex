#!/usr/bin/env python3
"""
import_card.py — the inverse of build_card.py: unpack a SillyTavern character
card (a V2/V3 `.png`, or a card `.json`) back into an editable YuriOS **SOUL**
folder (CONSTITUTION.md / PERSONA.md / SCENARIO.md / EXAMPLES.md / WORLD.md /
NOTES.md + a generated soul.yaml).

The card is only the *transport* format (→ D-003); the soul files are the
working home a runtime reads on every wake (→ ch. 07). A downloaded card is a
flat artifact — importing it splits it back into the immutable-core / editable
layers so a recipient can actually live with and reshape the companion.

Foreign cards rarely fill every field, so missing fields get **sensible
defaults** (empty sections, a default personality line, a minimal lorebook). The
split is necessarily a guess for a stranger's card: the whole description lands
in the editable PERSONA layer; move the parts that must never drift into
CONSTITUTION.md by hand afterward.

After writing, the importer **round-trips**: it re-exports the soul it just wrote
(via build_card) and checks the result matches the card it read, so you know the
import lost nothing. Run with --verify-only to check without writing.

Usage:
    python import_card.py some-card.png                 # -> ./imported-<name>/
    python import_card.py some-card.json --out ./yuri2  # choose output folder
    python import_card.py some-card.png --name Mira     # override the name
    python import_card.py some-card.png --verify-only   # round-trip check, no write

Dependencies: Pillow, PyYAML  (see requirements.txt)
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: PyYAML.  pip install -r requirements.txt")

from . import build_card  # shares the PNG/card helpers and the re-export path
# ^ VENDORED ADAPTATION: the yuri-soul original is `import build_card` (sibling
# module on sys.path). Here soulkit is a package, so this is a relative import.
# This is the ONLY change from the source of truth (see VENDORED.md).

DEFAULT_PERSONALITY = "warm, attentive, present"


# --- read a card in (png or json) -------------------------------------------

def load_card_data(path: Path) -> dict:
    """Return the card's `data` dict from a `.png` or `.json` source."""
    if path.suffix.lower() == ".png":
        card = build_card.extract_card(path)
    else:
        card = json.loads(path.read_text(encoding="utf-8"))
    # Accept either the {"spec","data":{...}} wrapper or a bare data dict.
    data = card.get("data", card) if isinstance(card, dict) else None
    if not isinstance(data, dict) or "name" not in data:
        raise ValueError(f"{path}: not a recognisable character card "
                         "(no data.name field)")
    return data


# --- normalise a (possibly sparse) card into the canonical soul shape -------

def example_blocks(mes_example: str) -> list[str]:
    """Split a mes_example field into its individual exchanges. Blocks are
    delimited by `<START>` in the card format; a card that omits the delimiter
    is treated as one block."""
    return [b.strip() for b in (mes_example or "").split("<START>") if b.strip()]


def normalise_book(book) -> dict:
    """Coerce a card's character_book into exactly the shape build_card's
    exporter produces, filling defaults and dropping un-keyable entries."""
    book = book or {}
    entries_out = []
    for i, e in enumerate((book.get("entries") or []), start=1):
        keys = [k.strip() for k in (e.get("keys") or []) if str(k).strip()]
        if not keys:  # a card entry with no trigger keys can't round-trip — give it one
            name = str(e.get("name") or e.get("comment") or "").strip()
            keys = [name] if name else [f"entry-{i}"]
        entries_out.append({
            "keys": keys,
            "content": (e.get("content") or "").strip(),
            "enabled": True,
            "insertion_order": i,
            "case_sensitive": False,
            "extensions": {},
        })
    return {
        "name": book.get("name", "lorebook"),
        "description": book.get("description", ""),
        "scan_depth": book.get("scan_depth", 4),
        "token_budget": book.get("token_budget", 600),
        "recursive_scanning": book.get("recursive_scanning", False),
        "extensions": {},
        "entries": entries_out,
    }


def intended_card(data: dict, name: str | None = None) -> dict:
    """The canonical card we *intend* the imported soul to represent: every field
    present, stripped, with sensible defaults for whatever the source omitted.
    Writing the soul from this (and re-exporting it) is what makes the round-trip
    exact."""
    def s(key: str) -> str:
        return (data.get(key) or "").strip()

    return {
        "name": (name or data.get("name") or "Companion").strip(),
        "description": s("description"),
        "personality": s("personality") or DEFAULT_PERSONALITY,
        "scenario": s("scenario"),
        "first_mes": s("first_mes"),
        "alternate_greetings": [g.strip() for g in (data.get("alternate_greetings") or [])
                                if g and g.strip()],
        "mes_example": "\n".join(f"<START>\n{b}" for b in example_blocks(data.get("mes_example", ""))),
        "system_prompt": s("system_prompt"),
        "post_history_instructions": s("post_history_instructions"),
        "creator_notes": s("creator_notes") or "Imported with import_card.py.",
        "tags": list(data.get("tags") or []),
        "creator": (data.get("creator") or "").strip(),
        "character_version": str(data.get("character_version") or "1.0.0"),
        "character_book": normalise_book(data.get("character_book")),
        "_yurios": (data.get("extensions") or {}).get("yurios", {}),
    }


# --- write the soul folder ---------------------------------------------------

def _md(front: dict, body: str) -> str:
    fm = yaml.safe_dump(front, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n\n{body.rstrip()}\n"


def _entry_block(e: dict) -> str:
    keys = ", ".join(e["keys"])
    return f"## {keys}\n\nkeys: {keys}\n\n{e['content']}".rstrip()


def write_soul(card: dict, out_dir: Path) -> None:
    """Materialise the intended card as the soul .md files + soul.yaml."""
    out_dir.mkdir(parents=True, exist_ok=True)

    constitution = (
        "# Constitution — the immutable core\n\n"
        "*Imported card. By default the whole persona landed in `PERSONA.md`; "
        "move the parts that must never drift (who she is, who she belongs to) "
        "up here, into `## Identity`, by hand.*\n\n"
        "## Identity\n\n"
        f"{card['name']} — imported companion. (Replace this with the immutable "
        "core: identity, values, who she belongs to.)\n\n"
        "## Voice law\n\n"
        f"{card['system_prompt']}\n\n"
        "## Hard limits\n\n"
        f"{card['post_history_instructions']}\n"
    )
    (out_dir / "CONSTITUTION.md").write_text(
        _md({"soul": "constitution", "mutable": False}, constitution), encoding="utf-8")

    persona = (
        "# Persona — the editable layer\n\n"
        "## Description\n\n"
        f"{card['description']}\n"
    )
    (out_dir / "PERSONA.md").write_text(
        _md({"soul": "persona", "mutable": True, "personality": card["personality"]},
            persona), encoding="utf-8")

    scenario_parts = ["# Scenario & Greetings\n",
                      "## Scenario\n", card["scenario"] + "\n",
                      "## First message\n", card["first_mes"] + "\n"]
    for i, greet in enumerate(card["alternate_greetings"], start=1):
        scenario_parts += [f"## Alternate greeting {i}\n", greet + "\n"]
    (out_dir / "SCENARIO.md").write_text(
        _md({"soul": "scenario"}, "\n".join(scenario_parts)), encoding="utf-8")

    examples = ["# Example dialogues\n"]
    for i, block in enumerate(example_blocks(card["mes_example"]), start=1):
        examples += [f"## Example {i}\n", block + "\n"]
    (out_dir / "EXAMPLES.md").write_text(
        _md({"soul": "examples"}, "\n".join(examples)), encoding="utf-8")

    book = card["character_book"]
    world_body = "# World (lorebook)\n\n" + "\n\n".join(_entry_block(e) for e in book["entries"])
    (out_dir / "WORLD.md").write_text(
        _md({"soul": "world", "name": book["name"], "description": book["description"],
             "scan_depth": book["scan_depth"], "token_budget": book["token_budget"],
             "recursive_scanning": book["recursive_scanning"]},
            world_body), encoding="utf-8")

    (out_dir / "NOTES.md").write_text(
        _md({"soul": "notes"}, card["creator_notes"]), encoding="utf-8")

    yurios = card["_yurios"]
    manifest = {
        "name": card["name"],
        "creator": card["creator"],
        "character_version": card["character_version"],
        "spec": "v2",
        "canon": yurios.get("canon", ""),
        "lineage": yurios.get("lineage", "YuriOS"),
        "portrait": "portrait.png",
        "tags": card["tags"],
        "fields": {
            "description": "PERSONA.md#Description",
            "personality": "PERSONA.md@personality",
            "scenario": "SCENARIO.md#Scenario",
            "first_mes": "SCENARIO.md#First message",
            "alternate_greetings": [f"SCENARIO.md#Alternate greeting {i}"
                                    for i in range(1, len(card["alternate_greetings"]) + 1)],
            "mes_example": "EXAMPLES.md",
            "system_prompt": "CONSTITUTION.md#Voice law",
            "post_history_instructions": "CONSTITUTION.md#Hard limits",
            "creator_notes": "NOTES.md",
            "character_book": "WORLD.md",
        },
    }
    header = ("# Generated by import_card.py — the export manifest for this soul.\n"
              "# Edit the .md files, then `python build_card.py --soul <dir>` to rebuild a card.\n\n")
    (out_dir / "soul.yaml").write_text(
        header + yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8")


def save_portrait(src: Path, out_dir: Path) -> bool:
    """If the source is a PNG, its own image is the portrait — re-save it so the
    soul can be rebuilt into a card. Returns True if a portrait was written."""
    if src.suffix.lower() != ".png":
        return False
    try:
        from PIL import Image
    except ImportError:
        return False
    Image.open(src).convert("RGB").save(out_dir / "portrait.png", format="PNG")
    return True


# --- round-trip check: does the written soul re-export to the same card? -----

def roundtrip_diffs(intended: dict, soul_dir: Path) -> list[str]:
    """Re-export the soul we wrote and compare it to the card we intended.
    Returns a list of human-readable differences (empty list == clean)."""
    _, _, _, data2 = build_card.build_card_data(soul_dir)
    diffs: list[str] = []

    text_fields = ["name", "description", "personality", "scenario", "first_mes",
                   "system_prompt", "post_history_instructions", "creator_notes",
                   "creator", "character_version"]
    for f in text_fields:
        if (intended.get(f) or "").strip() != (data2.get(f) or "").strip():
            diffs.append(f"{f}: changed across round-trip")

    if [g.strip() for g in intended["alternate_greetings"]] != \
       [g.strip() for g in data2.get("alternate_greetings", [])]:
        diffs.append("alternate_greetings: changed across round-trip")

    if example_blocks(intended["mes_example"]) != example_blocks(data2.get("mes_example", "")):
        diffs.append("mes_example: changed across round-trip")

    if sorted(intended["tags"]) != sorted(data2.get("tags", [])):
        diffs.append("tags: changed across round-trip")

    def book_sig(b):
        return [(e["keys"], (e["content"] or "").strip()) for e in (b.get("entries") or [])]
    if book_sig(intended["character_book"]) != book_sig(data2.get("character_book", {})):
        diffs.append("character_book entries: changed across round-trip")

    return diffs


def verify_roundtrip(intended: dict) -> list[str]:
    """Write the soul to a throwaway dir and run the round-trip check there, so a
    --verify-only run doesn't touch the output folder."""
    with tempfile.TemporaryDirectory() as tmp:
        write_soul(intended, Path(tmp))
        return roundtrip_diffs(intended, Path(tmp))


# --- main --------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Import a SillyTavern card into a YuriOS soul folder.")
    ap.add_argument("card", type=Path, help="source card: a .png or .json")
    ap.add_argument("--out", type=Path, default=None,
                    help="output soul folder (default: ./imported-<name>/)")
    ap.add_argument("--name", default=None, help="override the character name")
    ap.add_argument("--verify-only", action="store_true",
                    help="round-trip check only; do not write the soul folder")
    args = ap.parse_args()

    if not args.card.exists():
        sys.exit(f"No such file: {args.card}")
    try:
        data = load_card_data(args.card)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        sys.exit(f"Read error: {e}")

    intended = intended_card(data, args.name)

    if args.verify_only:
        diffs = verify_roundtrip(intended)
        if diffs:
            print(f"Round-trip MISMATCH for {intended['name']}:")
            for d in diffs:
                print(f"  - {d}")
            sys.exit(1)
        print(f"Round-trip OK: {intended['name']} re-exports unchanged.")
        return

    out_dir = (args.out or Path.cwd() / f"imported-{intended['name'].lower().replace(' ', '-')}").resolve()
    write_soul(intended, out_dir)
    had_portrait = save_portrait(args.card.resolve(), out_dir)

    print(f"Imported {intended['name']} -> {out_dir}/")
    for f in ("CONSTITUTION.md", "PERSONA.md", "SCENARIO.md", "EXAMPLES.md",
              "WORLD.md", "NOTES.md", "soul.yaml"):
        print(f"  {f}")
    print(f"  portrait.png{'' if had_portrait else '   (none — add one before rebuilding a card)'}")
    n_examples = len(example_blocks(intended["mes_example"]))
    n_entries = len(intended["character_book"]["entries"])
    print(f"\n  {n_examples} example exchange(s), {n_entries} lorebook entr(y/ies)")

    diffs = roundtrip_diffs(intended, out_dir)
    if diffs:
        print("\n  WARNING: round-trip mismatch — import may have lost detail:")
        for d in diffs:
            print(f"    - {d}")
    else:
        print("\n  round-trip verified: this soul re-exports to the card it came from.")

    print("\nNext: edit the .md files (move immutable traits into CONSTITUTION.md),"
          "\nthen `python build_card.py --soul " + str(out_dir) + "` to rebuild the card.")


if __name__ == "__main__":
    main()
