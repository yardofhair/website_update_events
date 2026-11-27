# Update Events Sync

A small tool that pulls upcoming race events from the Lucky Dog Racing League website, lets you choose which ones to feature, and produces a ready-to-paste block for a Squarespace page.

## How it works

1. **Fetch**: `fetch_events.py` downloads upcoming events from the league's public events feed and saves them to `events.json`.
2. **Choose**: `build_block.py` lists the upcoming events, asks which to include, and optionally asks for a YouTube link and a "show from" time for each.
3. **Publish**: it writes `events-block-ready.html`. Paste its contents into a Squarespace Code Block.

## Files

| File | Purpose |
| --- | --- |
| `fetch_events.py` | Pulls upcoming events into `events.json` and reports what is new, changed, or removed. |
| `build_block.py` | Interactive picker that exports the finished Squarespace block. |
| `squarespace-events-block.html` | Template for the block. Needed by `build_block.py`; not pasted directly unless you use the fetch version. |
| `events.json` | Event data. Also stores your YouTube IDs and publish times so they are not lost when the data refreshes. |
| `events-block-ready.html` | The finished block, with your chosen events built in. |

## Requirements

- Python 3.8 or newer (no extra packages needed)
- A Squarespace plan that supports Code Blocks

## Usage

Keep `fetch_events.py`, `build_block.py` and `squarespace-events-block.html` in the same folder, then run:

```
python3 fetch_events.py
python3 build_block.py
```

Then:

1. Open `events-block-ready.html` and copy everything in it.
2. In Squarespace, edit the page, add a **Code Block**, uncheck **Display Source**, and paste.
3. Save and check the live page. The editor preview may not run scripts.
4. Upload the updated `events.json` and `events-block-ready.html` to this repository to keep a history.

## YouTube links

When `build_block.py` asks for a video, you can paste any normal YouTube link or the 11-character video ID. If you give a "show from" time (`YYYY-MM-DD HH:MM`, in your computer's time zone), the link stays hidden on the page until that time has passed.

## Optional: load the data instead of baking it in

The block can also load `events.json` from a public web address (for example via GitHub Pages) so the page updates without re-pasting. To use this, set `EVENTS_URL` at the top of `squarespace-events-block.html`, paste that unmodified template into Squarespace, and keep the repository public.

## Notes

- If a fetch fails or returns no events, `fetch_events.py` leaves your existing `events.json` untouched.
- Event details come from the league's website. Each event on your page links back to its original page.
- Do not commit passwords, API keys, or other credentials to this repository.
