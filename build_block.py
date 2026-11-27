#!/usr/bin/env python3
"""Pick which events to show, add YouTube info, and export the Squarespace block.

Reads events.json (made by fetch_events.py), asks you which events to feature,
optionally asks for a YouTube link + publish time for each, then writes
events-block-ready.html: the Squarespace Code Block with those events baked in.

Keep this file, squarespace-events-block.html and events.json in one folder.
Usage:  python3 build_block.py
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "squarespace-events-block.html"
EVENTS = Path("events.json")
OUTPUT = Path("events-block-ready.html")
PUBLISHED = Path("events-published.json")  # what publish.py puts online


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def pretty_range(ev):
    a, b = ev["start"][:10], (ev.get("end") or ev["start"])[:10]
    return a if a == b else f"{a} to {b}"


def parse_selection(text, count):
    if not text:
        return list(range(count))  # Enter = everything
    chosen = []
    for piece in text.replace(" ", "").split(","):
        if piece.isdigit() and 1 <= int(piece) <= count:
            idx = int(piece) - 1
            if idx not in chosen:
                chosen.append(idx)
        else:
            print(f"  Ignoring '{piece}' (not a number from the list).")
    return chosen


def youtube_id(text):
    """Accept a bare ID or any common YouTube URL."""
    m = re.search(r"(?:youtu\.be/|v=|/shorts/|/live/|/embed/)([\w-]{11})", text)
    if m:
        return m.group(1)
    return text if re.fullmatch(r"[\w-]{11}", text) else None


def publish_iso(text):
    """'2027-01-20 09:00' (your computer's time zone) -> ISO timestamp."""
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M").astimezone().isoformat(timespec="minutes")
    except ValueError:
        return None


def main():
    if not EVENTS.exists():
        sys.exit("events.json not found here. Run fetch_events.py first.")
    if not TEMPLATE.exists():
        sys.exit(f"Missing {TEMPLATE.name} next to this script.")

    data = json.loads(EVENTS.read_text())
    all_events = data.get("events", [])
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = [e for e in all_events if (e.get("end") or e["start"])[:10] >= today]
    upcoming.sort(key=lambda e: e["start"])
    if not upcoming:
        sys.exit("No upcoming events in events.json. Run fetch_events.py again.")

    print("\nUpcoming events:\n")
    for i, e in enumerate(upcoming, 1):
        vid = f"  [video: {e['youtubeId']}]" if e.get("youtubeId") else ""
        print(f"  {i}. {pretty_range(e)}  {e['title']}{vid}")

    picks = parse_selection(
        ask("\nWhich events should appear? (e.g. 1,3  or press Enter for all): "),
        len(upcoming),
    )
    if not picks:
        sys.exit("Nothing selected. Nothing written.")
    selected = [upcoming[i] for i in sorted(picks, key=lambda i: upcoming[i]["start"])]

    for e in selected:
        print(f"\n--- {e['title']} ({pretty_range(e)})")
        current = e.get("youtubeId")
        if current:
            print(f"  Current video: {current}  publish: {e.get('publishAt', 'immediately')}")
        raw = ask("  YouTube link or ID (Enter to keep as is, '-' to remove): ")
        if raw == "-":
            e.pop("youtubeId", None)
            e.pop("publishAt", None)
            continue
        if not raw:
            continue
        vid = youtube_id(raw)
        if not vid:
            print("  Couldn't read a YouTube ID from that; leaving the video unchanged.")
            continue
        e["youtubeId"] = vid
        when = ask("  Show it from when? (YYYY-MM-DD HH:MM in your local time, Enter = now): ")
        if when:
            iso = publish_iso(when)
            if iso:
                e["publishAt"] = iso
            else:
                print("  Couldn't read that time; the video will show immediately.")
                e.pop("publishAt", None)
        else:
            e.pop("publishAt", None)

    # Save video info back so fetch_events.py keeps it on the next run.
    EVENTS.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # The selection, for the hosted page. publish.py uploads this file.
    PUBLISHED.write_text(json.dumps(
        {"updated": datetime.now().astimezone().isoformat(timespec="seconds"),
         "events": selected},
        indent=2, ensure_ascii=False,
    ))

    payload = json.dumps(selected, ensure_ascii=False).replace("</", "<\\/")
    template = TEMPLATE.read_text()
    new_html, n = re.subn(
        r"/\*DATA_START\*/.*?/\*DATA_END\*/",
        lambda _: f"/*DATA_START*/{payload}/*DATA_END*/",
        template,
        flags=re.S,
    )
    if n != 1:
        sys.exit("Couldn't find the DATA_START/DATA_END markers in the template.")
    OUTPUT.write_text(new_html)
    print(f"\nWrote {PUBLISHED} and {OUTPUT} with {len(selected)} event(s).")
    print("Run publish.py to update the live page (or paste the .html file by hand).")


if __name__ == "__main__":
    main()
