"""
soul.orbits — publish today's scheduled post for a given slot.

Looks at content/schedule.yaml to find which post is scheduled for today (UTC)
in the requested slot, ensures the image (or video) is rendered, then calls
publish.py.

Slot resolution:
    - First positional arg, OR
    - SLOT env var, OR
    - default "primary"

This is the entry point for the daily cron.
"""
from __future__ import annotations

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Make sibling modules importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "content" / "schedule.yaml"


def main():
    if not SCHEDULE.exists():
        raise SystemExit(f"schedule not found: {SCHEDULE}")

    slot = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SLOT", "primary")).strip().lower()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sched = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))

    posts = sched.get("posts", [])
    entry = next(
        (e for e in posts if e["date"] == today and e.get("slot", "primary") == slot),
        None,
    )
    if not entry:
        print(f"no post scheduled for {today} slot={slot} — exiting cleanly")
        return

    post_yaml = ROOT / entry["yaml"]
    if not post_yaml.exists():
        raise SystemExit(f"post yaml missing: {post_yaml}")

    # For Reels we don't need to re-render — the MP4 is already in the repo.
    # For carousels/singles we re-render to keep images fresh.
    data = yaml.safe_load(post_yaml.read_text(encoding="utf-8"))
    if data.get("template") != "reel":
        print(f"rendering {post_yaml.name}...")
        subprocess.run(
            [sys.executable, str(ROOT / "automation" / "render_post.py"), str(post_yaml)],
            check=True,
        )

    print(f"publishing {post_yaml.name} (slot={slot})...")
    result = subprocess.run(
        [sys.executable, str(ROOT / "automation" / "publish.py"), str(post_yaml)],
        check=True,
        capture_output=True,
        text=True,
    )
    # Echo publish.py output so the GH Actions log shows the media_id.
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Notify on Telegram when a Reel is published, so the user can add
    # trending audio in IG within the first 60min for max algorithm reach.
    if data.get("template") == "reel":
        media_id = ""
        try:
            payload = json.loads(result.stdout.strip().splitlines()[-1]) if result.stdout else {}
            media_id = payload.get("media_id", "")
        except Exception:
            pass
        try:
            from notify_email import reel_published
            reel_published(media_id)
        except Exception as e:
            print(f"email notify skipped: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
