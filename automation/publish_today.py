"""
soul.orbits — publish today's scheduled post for a given slot.

Looks at content/schedule.yaml to find which post is scheduled for today (UTC)
in the requested slot, ensures the image (or video) is rendered, then calls
publish.py.

Slot resolution:
    - First positional arg, OR
    - SLOT env var, OR
    - default "primary"

Idempotency:
    Skips publishing if the same post yaml has been published in the last
    12 hours (per publish_log.jsonl). Prevents duplicate posts when a
    delayed cron run hits a slot whose post was already published manually.

This is the entry point for the daily cron.
"""
from __future__ import annotations

import os
import sys
import yaml
import json
import traceback
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Make sibling modules importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "content" / "schedule.yaml"
PUBLISH_LOG = ROOT / "automation" / "publish_log.jsonl"

DEDUP_WINDOW = timedelta(hours=12)


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


def already_published_recently(post_name: str) -> dict | None:
    """If post was published within DEDUP_WINDOW, return that entry."""
    last = latest_log_entry_for(post_name)
    if not last:
        return None
    ts = last.get("ts")
    if not ts:
        return None
    try:
        when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None
    if datetime.now(timezone.utc) - when < DEDUP_WINDOW:
        return last
    return None


def run() -> None:
    if not SCHEDULE.exists():
        raise SystemExit(f"schedule not found: {SCHEDULE}")

    slot = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SLOT", "primary")).strip().lower()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[publish_today] today={today} slot={slot}", flush=True)

    sched = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))

    posts = sched.get("posts", [])
    entry = next(
        (e for e in posts if e["date"] == today and e.get("slot", "primary") == slot),
        None,
    )
    if not entry:
        print(f"[publish_today] no post scheduled for {today} slot={slot} — exiting cleanly", flush=True)
        return

    post_yaml = ROOT / entry["yaml"]
    if not post_yaml.exists():
        raise SystemExit(f"post yaml missing: {post_yaml}")

    # Dedup: if the same post was already published in the last 12h, skip.
    # Avoids duplicate posts when a cron run is delayed and lands on a slot
    # whose post was already published manually or by a previous run.
    dup = already_published_recently(post_yaml.name)
    if dup:
        print(
            f"[publish_today] {post_yaml.name} already published at {dup.get('ts')} "
            f"(media_id={dup.get('media_id')}) — skipping (dedup window {DEDUP_WINDOW})",
            flush=True,
        )
        return

    data = yaml.safe_load(post_yaml.read_text(encoding="utf-8"))

    # Render carousels and singles. Reels skip render — MP4 is pre-built.
    if data.get("template") != "reel":
        print(f"[publish_today] rendering {post_yaml.name}...", flush=True)
        subprocess.run(
            [sys.executable, str(ROOT / "automation" / "render_post.py"), str(post_yaml)],
            check=True,
        )

    print(f"[publish_today] publishing {post_yaml.name}...", flush=True)
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
            print(f"[publish_today] email sent for media_id={media_id}", flush=True)
        except Exception as e:
            print(f"[publish_today] email notify skipped: {e}", file=sys.stderr, flush=True)


def main():
    try:
        run()
    except SystemExit:
        raise
    except subprocess.CalledProcessError as e:
        print(f"[publish_today] subprocess failed: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"[publish_today] unexpected error: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
