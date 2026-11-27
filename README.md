# Update Events Sync

A small tool that pulls upcoming race events from the Lucky Dog Racing League website, lets you choose which ones to feature, and produces a ready-to-paste block for a Squarespace page.

## How it works

1. **Fetch**: `fetch_events.py` downloads upcoming events from the league's public events feed and saves them to `events.json`.
2. **Choose**: `build_block.py` lists the upcoming events, asks which to include, and optionally asks for a YouTube link and a "show from" time for each.
3. **Publish**: `publish.py` puts your picks online (GitHub Pages), and the Squarespace page loads them by itself. No re-pasting.

## Files

| File | Purpose |
| --- | --- |
| `fetch_events.py` | Pulls upcoming events into `events.json` and reports what is new, changed, or removed. |
| `build_block.py` | Interactive picker. Writes `events-published.json` (and a baked-in block as a fallback). |
| `publish.py` | Pushes your picks to the `gh-pages` branch as `events.json`, which GitHub Pages serves. |
| `squarespace-events-block.html` | The Code Block you paste into Squarespace once. Loads the published events. |
| `events.json` | Event data. Also stores your YouTube IDs and publish times so they are not lost when the data refreshes. |
| `events-published.json` | The events you picked, ready for `publish.py`. |
| `events-block-ready.html` | Fallback: the block with your chosen events built in, for pasting by hand. |

## Requirements

- Python 3.8 or newer (no extra packages needed)
- A Squarespace plan that supports Code Blocks

## One-time setup

1. Run the three commands below once, so the `gh-pages` branch exists.
2. On GitHub, open **Settings > Pages**, set **Source** to *Deploy from a branch*, pick `gh-pages` and `/ (root)`, and save. After a minute, https://yardofhair.github.io/website_update_events/events.json should show your events.
3. In Squarespace, edit the page, add a **Code Block**, uncheck **Display Source**, and paste the whole of `squarespace-events-block.html`. Save and check the live page (the editor preview may not run scripts).

## Each update

Keep the scripts and `squarespace-events-block.html` in the same folder, then run:

```
python3 fetch_events.py
python3 build_block.py
python3 publish.py
```

The live page shows the new events within about 10 minutes (GitHub Pages caching).

`events.json`, `events-published.json` and `events-block-ready.html` are generated, so they are gitignored on `main`. Only your picks go online, on the separate `gh-pages` branch. Back up `events.json` yourself if you want to keep your YouTube links and show-from times.

To skip hosting, you can still paste `events-block-ready.html` into the Code Block instead; it has the events built in.

## YouTube links

When `build_block.py` asks for a video, you can paste any normal YouTube link or the 11-character video ID. If you give a "show from" time (`YYYY-MM-DD HH:MM`, in your computer's time zone), the link stays hidden on the page until that time has passed.

## Notes

- If a fetch fails or returns no events, `fetch_events.py` leaves your existing `events.json` untouched.
- Event details come from the league's website. Each event on your page links back to its original page.
- The repository must stay public for GitHub Pages to serve the events on a free plan.
- Do not commit passwords, API keys, or other credentials to this repository.
