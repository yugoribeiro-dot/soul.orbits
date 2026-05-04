"""
soul.orbits — Telegram notification helper.

Sends a message to a configured chat when a Reel is published, prompting
the user to open Instagram and attach trending audio (max algorithm reach).

Usage as CLI:
    python notify_telegram.py "<message>"

Usage as module:
    from notify_telegram import notify
    notify("Reel just dropped — add trending audio in IG: <url>")

Required env:
    TELEGRAM_BOT_TOKEN   from @BotFather
    TELEGRAM_CHAT_ID     your numeric chat id (from @userinfobot)
"""
from __future__ import annotations

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error


def notify(text: str, parse_mode: str = "HTML") -> dict | None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("notify_telegram: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — skipping", file=sys.stderr)
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": chat,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": "false",
        }
    ).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"notify_telegram: HTTP {e.code}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"notify_telegram: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def reel_published(media_id: str, ig_user: str = "soul.orbits") -> None:
    """Standard Reel-published reminder — open IG and add trending audio."""
    permalink = f"https://www.instagram.com/reel/{media_id}/" if media_id else ""
    msg = (
        "🎬 <b>Reel published — soul.orbits</b>\n\n"
        "👉 <b>Open Instagram now</b> (next 60 min for max reach)\n"
        "1. Tap the Reel you just posted\n"
        "2. Edit → Add audio → search trending\n"
        "3. Pick something matching the vibe (cosmic/dark/punchy)\n"
        "4. Save\n\n"
        "Trending audio = 5-10x more reach.\n"
    )
    if permalink:
        msg += f'\n<a href="{permalink}">{permalink}</a>'
    notify(msg)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: notify_telegram.py <message>", file=sys.stderr)
        sys.exit(1)
    notify(sys.argv[1])
