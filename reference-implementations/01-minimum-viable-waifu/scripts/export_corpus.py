#!/usr/bin/env python3
"""export_corpus.py — merge ratings into turns and emit a training-ready JSONL
(SPEC §8, → ch. 20, Appendix D).

The logs themselves are append-only and never rewritten: ratings live in the
sidecar keyed by turn id and are merged HERE, at export. Flagged/redacted rows
are subtracted. Output goes next to the corpus, still personal data.

Usage:  python scripts/export_corpus.py  [--corpus ./corpus]  [--out export.jsonl]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def export(corpus_dir: Path, out_name: str = "export.jsonl") -> tuple[int, int]:
    turns_path = corpus_dir / "turns.jsonl"
    ratings_path = corpus_dir / "ratings.jsonl"
    if not turns_path.exists():
        raise SystemExit(f"no {turns_path} — nothing captured yet")

    # last rating per turn wins (a user may change their mind)
    ratings: dict[str, dict] = {}
    if ratings_path.exists():
        for line in ratings_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                ratings[r["id"]] = {"thumbs": r["thumbs"], "by": r.get("by", "user")}

    kept = skipped = 0
    out_path = corpus_dir / out_name
    with out_path.open("w", encoding="utf-8") as out:
        for line in turns_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("flags") or rec.get("redacted"):
                skipped += 1          # exclusions subtract at export (§8.2)
                continue
            if rec["id"] in ratings:
                rec["rating"] = ratings[rec["id"]]
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            kept += 1
    return kept, skipped


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="./corpus")
    ap.add_argument("--out", default="export.jsonl")
    args = ap.parse_args()
    kept, skipped = export(Path(args.corpus), args.out)
    print(f"exported {kept} records ({skipped} excluded) → {args.corpus}/{args.out}")
