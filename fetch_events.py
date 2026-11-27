#!/usr/bin/env python3
"""Pull upcoming Lucky Dog Racing League events into events.json.

- Reads the public Events Calendar REST feed (upcoming events only).
- Keeps any manual fields you add to events.json (youtubeId, publishAt, note)
  so re-running never wipes them.
- Prints a summary of what is new / changed / removed.

Usage:  python3 fetch_events.py
Needs only Python 3.8+ (standard library).
"""
import html
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

FEED = "https://www.racelucky.com/wp-json/tribe/events/v1/events?per_page=50"
OUT = Path("events.json")
MANUAL_FIELDS = ("youtubeId", "publishAt", "note")  # you edit these by hand
SOURCE_FIELDS = ("title", "start", "end", "venue", "city", "state", "url")


def get_json(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "event-sync/1.0 (personal site update)"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_all(url=FEED):
    events = []
    while url:
        data = get_json(url)
        events.extend(data.get("events", []))
        url = data.get("next_rest_url")
    return events


def normalize(e):
    venue = e.get("venue") or {}
    if isinstance(venue, list):  # the API returns [] when there is no venue
        venue = {}
    return {
        "id": e["id"],
        "title": html.unescape(e.get("title", "")).strip(),
        "start": e["start_date"].replace(" ", "T"),  # local to the venue
        "end": e["end_date"].replace(" ", "T"),
        "venue": html.unescape(venue.get("venue", "")),
        "city": venue.get("city", ""),
        "state": venue.get("stateprovince") or venue.get("state", ""),
        "url": e.get("url", ""),
    }


def merge(new_events, old_events):
    old_by_id = {o["id"]: o for o in old_events}
    merged, added, changed = [], [], []
    for n in new_events:
        old = old_by_id.pop(n["id"], None)
        if old is None:
            added.append(n["title"])
        else:
            if any(old.get(k) != n[k] for k in SOURCE_FIELDS):
                changed.append(n["title"])
            for k in MANUAL_FIELDS:  # carry over your hand-entered fields
                if k in old:
                    n[k] = old[k]
        merged.append(n)
    removed = [o["title"] for o in old_by_id.values()]
    merged.sort(key=lambda x: x["start"])
    return merged, added, changed, removed


def main():
    old = []
    if OUT.exists():
        old = json.loads(OUT.read_text()).get("events", [])
    try:
        raw = fetch_all()
    except Exception as exc:  # never overwrite good data with a failed run
        sys.exit(f"Fetch failed, events.json left unchanged: {exc}")
    if not raw:
        sys.exit("Feed returned 0 events; leaving events.json unchanged.")

    merged, added, changed, removed = merge([normalize(e) for e in raw], old)
    OUT.write_text(
        json.dumps(
            {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "events": merged},
            indent=2, ensure_ascii=False,
        )
    )
    print(f"{len(merged)} upcoming events saved to {OUT}")
    for label, items in (("NEW", added), ("CHANGED", changed), ("REMOVED", removed)):
        for title in items:
            print(f"  {label}: {title}")


if __name__ == "__main__":
    main()