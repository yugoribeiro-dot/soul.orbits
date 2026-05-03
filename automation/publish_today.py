"""
soul.orbits — publish today's scheduled post.

Looks at content/schedule.yaml to find which post is scheduled for today (UTC),
ensures the image is rendered, then calls publish.py.

This is the entry point for the daily cron.
"""
from __future__ import annotations

import os
import sys
import yaml
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "content" / "schedule.yaml"


def main():
    if not SCHEDULE.exists():
        raise SystemExit(f"schedule not found: {SCHEDULE}")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sched = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))

    entry = next((e for e in sched.get("posts", []) if e["date"] == today), None)
    if not entry:
        print(f"no post scheduled for {today} — exiting cleanly")
        return

    post_yaml = ROOT / entry["yaml"]
    if not post_yaml.exists():
        raise SystemExit(f"post yaml missing: {post_yaml}")

    # Render fresh (idempotent)
    print(f"rendering {post_yaml}...")
    subprocess.run(
        [sys.executable, str(ROOT / "automation" / "render_post.py"), str(post_yaml)],
        check=True,
    )

    # Publish
    print(f"publishing {post_yaml}...")
    subprocess.run(
        [sys.executable, str(ROOT / "automation" / "publish.py"), str(post_yaml)],
        check=True,
    )


if __name__ == "__main__":
    main()
