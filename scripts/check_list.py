"""Check data/accomplishments.json for mistakes before they reach the site.

Run it yourself with:   python scripts/check_list.py
GitHub also runs it on every push (see .github/workflows/check-list.yml),
and marks the commit with a red X if anything is wrong.
"""
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

LIST_FILE = Path(__file__).resolve().parent.parent / "data" / "accomplishments.json"
REQUIRED = ["number", "series", "vibe", "title", "proof", "capstone", "status", "added", "retired"]
STATUSES = {"active", "retired"}

problems = []


def problem(msg):
    problems.append(msg)


def is_date(value):
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


# 1. The file has to be valid JSON. A missing comma or quote fails here.
try:
    data = json.loads(LIST_FILE.read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    print(f"The file isn't valid JSON: {e.msg} at line {e.lineno}, column {e.colno}.")
    print("Usually that's a missing or extra comma, or a missing quote, on or just before that line.")
    sys.exit(1)

vibes = {v["key"] for v in data.get("vibes", [])}
series = {s["key"] for s in data.get("series", [])}
items = data.get("accomplishments", [])

# 2. Every entry has every field, with sensible values.
for i, a in enumerate(items):
    label = f"#{a.get('number', '?')} (entry {i + 1} in the file)"
    for field in REQUIRED:
        if field not in a:
            problem(f"{label} is missing the '{field}' field.")
    if not isinstance(a.get("number"), int) or a.get("number", 0) < 1:
        problem(f"{label}: 'number' has to be a whole number, 1 or higher.")
    if a.get("vibe") not in vibes:
        problem(f"{label}: vibe '{a.get('vibe')}' isn't one of {sorted(vibes)}.")
    if a.get("series") not in series:
        problem(f"{label}: series '{a.get('series')}' isn't one of {sorted(series)}. Add it to the series list first.")
    if a.get("status") not in STATUSES:
        problem(f"{label}: status has to be 'active' or 'retired'.")
    if not isinstance(a.get("capstone"), bool):
        problem(f"{label}: capstone has to be true or false (no quotes).")
    if not str(a.get("title", "")).strip() or not str(a.get("proof", "")).strip():
        problem(f"{label}: title and proof can't be blank.")
    if not is_date(a.get("added")):
        problem(f"{label}: 'added' has to be a date like 2026-11-24.")
    if a.get("status") == "retired" and not is_date(a.get("retired")):
        problem(f"{label}: it's retired, so 'retired' needs the date it was retired.")
    if a.get("status") == "active" and a.get("retired") is not None:
        problem(f"{label}: it's active, so 'retired' should be null.")

# 3. Numbers are permanent and unique, retired ones included.
for num, count in Counter(a.get("number") for a in items).items():
    if count > 1:
        problem(f"Number {num} is used {count} times. Every number can only be used once, ever.")

# 4. At most one active capstone per vibe in each series.
caps = Counter((a.get("series"), a.get("vibe")) for a in items if a.get("capstone") and a.get("status") == "active")
for (s, v), count in caps.items():
    if count > 1:
        problem(f"The {v} vibe has {count} active capstones in the {s} series. Only one is allowed.")

if problems:
    print(f"Found {len(problems)} problem(s) in {LIST_FILE.name}:")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)

active = sum(1 for a in items if a.get("status") == "active")
print(f"All good: {len(items)} entries ({active} active), {len(vibes)} vibes, {len(series)} series.")
