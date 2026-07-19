"""The partner model — `USER.md`, her theory of *you* (→ book ch. 15, ch. 31).

This is the second home for memory, and the one that behaves differently on
purpose. The episodic journal (see `store.py`) is *approximate* recall — top-k,
faded by recency, sometimes empty. `USER.md` is the opposite: **small, durable,
and injected into the prompt whole, every turn.** She always knows your name;
she only *sometimes* remembers what you said last Tuesday. Those are different
jobs and they get different storage.

The interesting part is how facts get *in*. After each exchange an extractor
proposes structured ops — add / update / remove a line — and those ops are not
written straight to `USER.md`. A low-confidence claim is **quarantined**: held
aside until a *second* turn corroborates it, and only then promoted. Promotion,
not capture, is the trust boundary. This is the single mechanism that stops a
companion from confidently "remembering" something you said once, sarcastically,
three weeks ago (→ ch. 15, "context poisoning").

Two extractors ship:
  * KeywordExtractor — offline, rule-based. Recognises a handful of patterns
    ("my name is …", "i live in …", "remember that …"). Deterministic, so the
    tutorial's quarantine demo is reproducible with no model. This is a teaching
    stand-in, not how the real build reads you.
  * LLMExtractor     — the real path: one cheap utility-model call per exchange,
    returning the same Op schema as JSON. Wrap any callable that takes messages
    and returns a string. Documented here; not exercised by the offline tests.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

SECTIONS = ("Stable", "Ongoing", "Don't forget")
QUARANTINE_CONFIDENCE = 0.6   # below this, an op waits for a second sighting
UNSCORED_CONFIDENCE = 0.0     # a claim proposed with NO confidence is treated as
                              # UNSURE (→ quarantine), never as certain. Getting
                              # this backwards lets confabulations walk straight in.
CORROBORATION_OVERLAP = 0.5   # token overlap that counts as "the same claim again"


@dataclass
class Op:
    section: str               # Stable | Ongoing | Don't forget
    text: str
    op: str = "add"            # add | update | remove
    confidence: float = UNSCORED_CONFIDENCE


# --- extractors: exchange → proposed ops -------------------------------------

class KeywordExtractor:
    """Offline, deterministic stand-in for the utility model. Emits ops from a
    few hand-written patterns so the quarantine can be demonstrated without a
    network call. Real companions use LLMExtractor; this exists so the tutorial
    runs anywhere."""

    #                 pattern                              section        confidence
    RULES = [
        (re.compile(r"\bmy name is (\w+)", re.I),         "Stable",      0.9),
        (re.compile(r"\bi live in ([\w ]+)", re.I),       "Stable",      0.5),
        (re.compile(r"\bi play (?:the )?(\w+)", re.I),    "Stable",      0.5),
        (re.compile(r"\bremember (?:that )?(.+)", re.I),  "Don't forget", 0.9),
    ]
    TEMPLATES = {
        "Stable": {"name": "their name is {0}",
                   "live": "lives in {0}",
                   "play": "plays {0}"},
    }

    def __call__(self, user_md: str, exchange: str) -> list[Op]:
        # only mine the *user's* half of the exchange
        user_line = exchange.split("\n", 1)[0]
        ops: list[Op] = []
        for pattern, section, conf in self.RULES:
            m = pattern.search(user_line)
            if not m:
                continue
            captured = m.group(1).strip().rstrip(".")
            if "name is" in pattern.pattern:
                text = f"their name is {captured.title()}"
            elif "live in" in pattern.pattern:
                text = f"lives in {captured.title()}"
            elif "i play" in pattern.pattern:
                text = f"plays {captured}"
            else:
                text = captured
            ops.append(Op(section=section, text=text, op="add", confidence=conf))
        return ops


EXTRACT_SYSTEM = """\
Extract only DURABLE facts about the user worth remembering across sessions:
identity, stable preferences, ongoing situations/goals, explicit "remember this".
Ignore ephemeral chit-chat. Return JSON:
{ "ops": [ { "section": "Stable"|"Ongoing"|"Don't forget", "text": string,
            "op": "add"|"update"|"remove", "confidence": 0..1 } ] }
Return {"ops": []} if nothing durable was stated."""


class LLMExtractor:
    """The real extractor: one utility-model call per exchange. `complete` is any
    callable `(messages: list[dict]) -> str` — wire your provider in. Not used by
    the offline tests; here so the tutorial can show the production shape."""

    def __init__(self, complete):
        self._complete = complete

    def __call__(self, user_md: str, exchange: str) -> list[Op]:
        raw = self._complete([
            {"role": "system", "content": EXTRACT_SYSTEM},
            {"role": "user", "content":
                f"Current USER.md:\n\n{user_md}\n\n---\nLast exchange:\n\n{exchange}"},
        ])
        return parse_ops(raw)


def parse_ops(raw: str) -> list[Op]:
    """Tolerant parse of an LLM reply: strip code fences, take the outermost
    JSON object, drop anything malformed. A garbled reply yields [] — never an
    exception, so one bad utility call can't break the turn."""
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < 0:
        return []
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return []
    ops = []
    for o in data.get("ops", []):
        if not isinstance(o, dict) or o.get("section") not in SECTIONS:
            continue
        text = str(o.get("text", "")).strip()
        if not text:
            continue
        # a missing confidence fails safe to UNSCORED (→ quarantine), not certainty
        ops.append(Op(section=o["section"], text=text, op=o.get("op", "add"),
                      confidence=float(o.get("confidence", UNSCORED_CONFIDENCE))))
    return ops


# --- merging ops into USER.md ------------------------------------------------

def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", s.lower()))


def _overlap(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def apply_ops(user_md: str, ops: list[Op]) -> str:
    """Merge, don't blindly append: `update` replaces the closest existing line,
    `remove` drops it, `add` skips near-duplicates. Sections are created on
    demand. This is why USER.md stays small instead of accreting every phrasing
    of the same fact."""
    lines = user_md.splitlines()
    for op in ops:
        header = f"## {op.section}"
        if header not in lines:
            if lines and lines[-1].strip():
                lines.append("")
            lines.extend([header, ""])
        start = lines.index(header) + 1
        end = start
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        bullets = [i for i in range(start, end) if lines[i].lstrip().startswith("- ")]

        def best_match(threshold: float) -> int | None:
            scored = [(i, _overlap(lines[i].lstrip("- ").strip(), op.text))
                      for i in bullets]
            scored = [(i, s) for i, s in scored if s >= threshold]
            return max(scored, key=lambda t: t[1])[0] if scored else None

        if op.op == "remove":
            i = best_match(CORROBORATION_OVERLAP)
            if i is not None:
                lines.pop(i)
        elif op.op == "update":
            i = best_match(0.3)
            if i is not None:
                lines[i] = f"- {op.text}"
            else:
                lines.insert(end, f"- {op.text}")
        else:  # add — skip if an equivalent line already exists
            if best_match(0.8) is None:
                lines.insert(end, f"- {op.text}")
    return "\n".join(lines).rstrip() + "\n"


# --- the quarantine ----------------------------------------------------------

class Quarantine:
    """Low-confidence claims wait here (a JSON file) until a second turn
    corroborates them; only then are they promoted into USER.md.

    triage() returns (apply_now, newly_held):
      * a `remove` is always applied — it is always safe to forget;
      * a claim that matches something already waiting → corroborated → promote;
      * an unmatched claim below the confidence bar → held for next time;
      * an unmatched claim above the bar → applied directly.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.items: list[dict] = []
        if self.path.exists():
            self.items = json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.items, indent=2), encoding="utf-8")

    def triage(self, ops: list[Op]) -> tuple[list[Op], list[Op]]:
        apply_now: list[Op] = []
        held: list[Op] = []
        for op in ops:
            if op.op == "remove":
                apply_now.append(op)
                continue
            match = next((q for q in self.items
                          if q["section"] == op.section
                          and _overlap(q["text"], op.text) >= CORROBORATION_OVERLAP),
                         None)
            if match is not None:           # second sighting — promote
                self.items.remove(match)
                apply_now.append(op)
            elif op.confidence < QUARANTINE_CONFIDENCE:
                self.items.append({"section": op.section, "text": op.text,
                                   "confidence": op.confidence})
                held.append(op)
            else:                           # confident enough on first sighting
                apply_now.append(op)
        self._save()
        return apply_now, held
