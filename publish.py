#!/usr/bin/env python3
"""Put the events you picked online, so the Squarespace page updates by itself.

Takes events-published.json (written by build_block.py) and pushes it as
events.json to this repository's gh-pages branch, which GitHub Pages serves at
https://yardofhair.github.io/website_update_events/events.json

The gh-pages branch holds only that file, so main never gets generated files.
Needs git, and the same GitHub sign-in you already use to push this repo.

Usage:  python3 publish.py
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = Path("events-published.json")
BRANCH = "gh-pages"


def git(*args, cwd, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check, text=True,
                          capture_output=True)


def remove_tree(path):
    def make_writable(func, p, _exc):  # Windows marks some .git files read-only
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onerror=make_writable)


def main():
    if not SOURCE.exists():
        sys.exit(f"{SOURCE} not found here. Run build_block.py first.")
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    count = len(data.get("events", []))
    if not count:
        sys.exit(f"{SOURCE} has no events; nothing published.")

    try:
        origin = git("remote", "get-url", "origin", cwd=HERE).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.exit("Couldn't find git or this repo's 'origin' remote.")

    tmp = Path(tempfile.mkdtemp(prefix="ldrl-publish-"))
    try:
        has_branch = git("ls-remote", "--exit-code", "--heads", origin, BRANCH,
                         cwd=HERE, check=False).returncode == 0
        if has_branch:
            git("clone", "--quiet", "--depth", "1", "--branch", BRANCH, origin,
                str(tmp), cwd=HERE)
        else:
            git("init", "--quiet", cwd=tmp)
            git("checkout", "--quiet", "--orphan", BRANCH, cwd=tmp)
            git("remote", "add", "origin", origin, cwd=tmp)

        (tmp / "events.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        (tmp / ".nojekyll").write_text("")  # serve files as they are
        git("add", "events.json", ".nojekyll", cwd=tmp)

        if git("diff", "--cached", "--quiet", cwd=tmp, check=False).returncode == 0:
            print("Online events are already up to date. Nothing to publish.")
            return
        git("commit", "--quiet", "-m", f"Publish {count} event(s)", cwd=tmp)
        git("push", "--quiet", "origin", f"HEAD:{BRANCH}", cwd=tmp)
    except subprocess.CalledProcessError as exc:
        sys.exit(f"Publish failed: {(exc.stderr or exc.stdout or '').strip()}")
    finally:
        remove_tree(tmp)

    print(f"Published {count} event(s). The live page shows them within about 10 minutes.")


if __name__ == "__main__":
    main()
