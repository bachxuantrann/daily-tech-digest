#!/usr/bin/env python3
"""Validate one day's digest and add it to the site's data folder.

Usage:
    python3 scripts/publish.py path/to/day.json

What it does:
  1. Validates the JSON against the schema described in README.md.
  2. Sets generated_at from the system clock (any value in the input is ignored)
     and writes it to data/<date>.json (replacing any earlier run for that date).
  3. Adds the date to data/index.json (newest first, no duplicates).

Exit code is 0 on success, 1 if validation fails (nothing is written then).
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_http_url(value):
    try:
        u = urlparse(value)
    except Exception:
        return False
    return u.scheme in ("http", "https") and bool(u.netloc)


def non_empty(value):
    return isinstance(value, str) and value.strip() != ""


def validate(day):
    errors = []
    if not isinstance(day, dict):
        return ["root must be a JSON object"]

    if not (isinstance(day.get("date"), str) and DATE_RE.match(day["date"])):
        errors.append("date must be a string like 2026-10-18")

    if "summary" in day and not isinstance(day["summary"], str):
        errors.append("summary must be a string")

    sections = day.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be a non-empty list")
        sections = []
    for i, sec in enumerate(sections):
        where = f"sections[{i}]"
        if not isinstance(sec, dict):
            errors.append(f"{where} must be an object")
            continue
        if not non_empty(sec.get("title")):
            errors.append(f"{where}.title is required")
        items = sec.get("items")
        if not isinstance(items, list) or not items:
            errors.append(f"{where}.items must be a non-empty list")
            continue
        for j, item in enumerate(items):
            iw = f"{where}.items[{j}]"
            if not isinstance(item, dict):
                errors.append(f"{iw} must be an object")
                continue
            if not non_empty(item.get("title")):
                errors.append(f"{iw}.title is required")
            if not non_empty(item.get("summary")):
                errors.append(f"{iw}.summary is required")
            if "apply" in item and not isinstance(item["apply"], str):
                errors.append(f"{iw}.apply must be a string")
            src = item.get("source")
            if src is not None:
                if not isinstance(src, dict) or not is_http_url(src.get("url", "")):
                    errors.append(f"{iw}.source.url must be an http(s) URL")

    k = day.get("knowledge")
    if k is not None:
        if not isinstance(k, dict) or not non_empty(k.get("title")) or not non_empty(k.get("body")):
            errors.append("knowledge needs title and body")
        elif "example" in k and not isinstance(k["example"], str):
            errors.append("knowledge.example must be a string")

    sources = day.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        sources = []
    for i, s in enumerate(sources):
        if not isinstance(s, dict) or not is_http_url(s.get("url", "")):
            errors.append(f"sources[{i}].url must be an http(s) URL")
        elif not non_empty(s.get("title")):
            errors.append(f"sources[{i}].title is required")

    return errors


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 1

    src = Path(argv[1])
    try:
        day = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read {src}: {exc}")
        return 1

    errors = validate(day)
    if errors:
        print("Validation failed, nothing written:")
        for e in errors:
            print(f"  - {e}")
        return 1

    # The model that writes the JSON has no clock and tends to guess the time,
    # so the publish time always comes from the system clock instead.
    day["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    DATA.mkdir(exist_ok=True)
    date = day["date"]
    (DATA / f"{date}.json").write_text(
        json.dumps(day, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    index_path = DATA / "index.json"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        dates = [d for d in index.get("dates", []) if isinstance(d, str) and DATE_RE.match(d)]
    except (OSError, json.JSONDecodeError):
        dates = []
    if date not in dates:
        dates.append(date)
    dates = sorted(set(dates), reverse=True)
    index_path.write_text(
        json.dumps({"dates": dates}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    items = sum(len(s["items"]) for s in day["sections"])
    print(f"OK: data/{date}.json written ({len(day['sections'])} sections, {items} items); index has {len(dates)} day(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
