"""Token use and estimated cost of a shwow-kit work item, read from Claude Code transcripts.

Usage: python cost.py <work-item-slug> [--projects DIR] [--prices FILE]

Subagents are matched by their description, which dispatch and verify start with
"<slug> <slice-or-landing> ". Coordinator sessions are every session that started
one of them, counted whole, so they can include other work done in that session.
"""

import argparse
import collections
import json
import pathlib
import sys

# US$ per million tokens: input, output, cache read, cache write.
# Cache writes are priced at the 1-hour rate (2x input), which Claude Code uses.
# Override with --prices (same shape) or ~/.shwow-kit/prices.json.
PRICES = {
    "claude-fable-5-2": (8.00, 40.00, 0.20, 16.00),
    "claude-opus-5-5": (4.00, 20.00, 0.20, 8.00),
    "claude-opus-5": (5.00, 25.00, 0.50, 10.00),
    "claude-sonnet-5-5": (2.00, 10.00, 0.10, 4.00),
    "claude-sonnet-5": (2.00, 10.00, 0.20, 4.00),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.20),
}


def usage_of(path):
    """Sum token use per model in one transcript file."""
    per_model = collections.defaultdict(collections.Counter)
    first = last = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = e.get("timestamp")
            if ts:
                first = first or ts
                last = ts
            if e.get("type") != "assistant":
                continue
            m = e.get("message") or {}
            u = m.get("usage") or {}
            c = per_model[m.get("model") or "unknown"]
            c["input"] += u.get("input_tokens") or 0
            c["output"] += u.get("output_tokens") or 0
            c["cache_read"] += u.get("cache_read_input_tokens") or 0
            c["cache_write"] += u.get("cache_creation_input_tokens") or 0
    return per_model, first, last


def cost_of(per_model, prices):
    total, unpriced = 0.0, set()
    for model, c in per_model.items():
        p = prices.get(model)
        if not p:
            if sum(c.values()):
                unpriced.add(model)
            continue
        total += (c["input"] * p[0] + c["output"] * p[1] + c["cache_read"] * p[2] + c["cache_write"] * p[3]) / 1e6
    return total, unpriced


def minutes(first, last):
    from datetime import datetime

    if not first or not last:
        return 0
    f = datetime.fromisoformat(first.replace("Z", "+00:00"))
    l = datetime.fromisoformat(last.replace("Z", "+00:00"))
    return round((l - f).total_seconds() / 60)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--projects", default=str(pathlib.Path.home() / ".claude" / "projects"))
    ap.add_argument("--prices")
    a = ap.parse_args()

    prices = dict(PRICES)
    for pf in [pathlib.Path.home() / ".shwow-kit" / "prices.json", a.prices]:
        if pf and pathlib.Path(pf).is_file():
            prices.update({k: tuple(v) for k, v in json.loads(pathlib.Path(pf).read_text()).items()})

    rows, sessions, unpriced = [], set(), set()
    for meta in pathlib.Path(a.projects).glob("*/*/subagents/*.meta.json"):
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        desc = (m.get("description") or "").strip()
        if not desc.lower().startswith(a.slug.lower() + " "):
            continue
        transcript = meta.with_name(meta.name.replace(".meta.json", ".jsonl"))
        if not transcript.is_file():
            continue
        per_model, first, last = usage_of(transcript)
        cost, missing = cost_of(per_model, prices)
        unpriced |= missing
        parts = desc.split()
        rows.append({
            "unit": parts[1] if len(parts) > 1 else "?",
            "agent": (m.get("agentType") or "?").split(":")[-1],
            "model": ", ".join(sorted(per_model)),
            "tokens": sum(sum(c.values()) for c in per_model.values()),
            "minutes": minutes(first, last),
            "cost": cost,
        })
        sessions.add(meta.parent.parent)

    if not rows:
        print(f"No subagents found whose description starts with '{a.slug} '.")
        return 1

    coord_cost = coord_tokens = 0
    for s in sessions:
        main_transcript = s.with_suffix(".jsonl")
        if main_transcript.is_file():
            per_model, _, _ = usage_of(main_transcript)
            c, missing = cost_of(per_model, prices)
            unpriced |= missing
            coord_cost += c
            coord_tokens += sum(sum(x.values()) for x in per_model.values())

    rows.sort(key=lambda r: (r["unit"], r["agent"]))
    print(f"# Cost: {a.slug}\n")
    print("| slice / landing | agent | model | tokens | minutes | est. US$ |")
    print("| --- | --- | --- | --- | --- | --- |")
    for r in rows:
        print(f"| {r['unit']} | {r['agent']} | {r['model']} | {r['tokens']:,} | {r['minutes']} | {r['cost']:.2f} |")
    by_unit = collections.defaultdict(float)
    for r in rows:
        by_unit[r["unit"]] += r["cost"]
    agents_cost = sum(by_unit.values())
    print()
    print("Per slice or landing: " + ", ".join(f"{u} {c:.2f}" for u, c in sorted(by_unit.items())))
    print(f"Subagents: US${agents_cost:.2f}. Coordinator sessions ({len(sessions)}, whole sessions): US${coord_cost:.2f}, {coord_tokens:,} tokens.")
    print(f"Total: US${agents_cost + coord_cost:.2f}. Estimates at API prices; a subscription bills differently.")
    if unpriced:
        print(f"No price for: {', '.join(sorted(unpriced))} (add to ~/.shwow-kit/prices.json).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
