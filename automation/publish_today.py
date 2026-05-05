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
PUBLISH_LOG = ROOT / "automation" / "publish_log.jsonl"


def latest_log_entry_for(post_name: str) -> dict | None:
    """Return the most recent publish_log entry for post_name, or None."""
    if not PUBLISH_LOG.exists():
        return None
    entries = []
    with PUBLISH_LOG.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get("post") == post_name:
                entries.append(e)
    return entries[-1] if entries else None


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

    data = yaml.safe_load(post_yaml.read_text(encoding="utf-8"))

    # Render carousels and singles. Reels skip render — MP4 is pre-built.
    if data.get("template") != "reel":
        print(f"rendering {post_yaml.name}...", flush=True)
        subprocess.run(
            [sys.executable, str(ROOT / "automation" / "render_post.py"), str(post_yaml)],
            check=True,
        )

    # Publish — let stdout/stderr flow through so workflow logs show real errors.
    print(f"publishing {post_yaml.name} (slot={slot})...", flush=True)
    subprocess.run(
        [sys.executable, str(ROOT / "automation" / "publish.py"), str(post_yaml)],
        check=True,
    )

    # Notify by email when a Reel is published, so the user can add
    # trending audio in IG within the first 60min for max algorithm reach.
    if data.get("template") == "reel":
        last = latest_log_entry_for(post_yaml.name) or {}
        media_id = last.get("media_id", "")
        try:
            from notify_email import reel_published
            reel_published(media_id)
            print(f"email sent for media_id={media_id}", flush=True)
        except Exception as e:
            print(f"email notify skipped: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
