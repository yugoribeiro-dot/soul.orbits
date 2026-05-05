"""
soul.orbits — TikTok Content Posting API client.

Uploads videos (Reels) and photo carousels (post slides) to TikTok via the
official Content Posting API. Uses FILE_UPLOAD source so we don't need
domain verification (raw.githubusercontent.com is not verifiable with
TikTok).

By default uses MEDIA_UPLOAD post_mode → content lands in the user's
TikTok drafts (Inbox). User opens app, picks trending sound, taps Post.
This is the recommended path because:
    1. No app approval delay (Direct Post needs review)
    2. Trending sound = TikTok's #1 growth lever, has to be picked manually

Required env:
    TIKTOK_ACCESS_TOKEN   from OAuth flow (24h lifetime)
    TIKTOK_REFRESH_TOKEN  long-lived (~1 year)
    TIKTOK_CLIENT_KEY     from developers.tiktok.com app
    TIKTOK_CLIENT_SECRET  from developers.tiktok.com app

Endpoints used:
    POST /v2/oauth/token/                          refresh access token
    POST /v2/post/publish/inbox/video/init/        video → drafts
    POST /v2/post/publish/content/init/            photos → drafts
    POST /v2/post/publish/status/fetch/            poll publish status
"""
from __future__ import annotations

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Any

API_BASE = "https://open.tiktokapis.com"
AUTH_URL = f"{API_BASE}/v2/oauth/token/"
INIT_VIDEO_INBOX = f"{API_BASE}/v2/post/publish/inbox/video/init/"
INIT_CONTENT = f"{API_BASE}/v2/post/publish/content/init/"
STATUS_FETCH = f"{API_BASE}/v2/post/publish/status/fetch/"


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

def refresh_access_token() -> str:
    """Refresh the short-lived access token using the refresh token. Returns
    the new access token. Caller may also persist the new refresh token
    (TikTok rotates it)."""
    client_key = os.environ["TIKTOK_CLIENT_KEY"]
    client_secret = os.environ["TIKTOK_CLIENT_SECRET"]
    refresh = os.environ["TIKTOK_REFRESH_TOKEN"]

    data = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh,
    }).encode("utf-8")

    req = urllib.request.Request(
        AUTH_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.loads(r.read().decode("utf-8"))
    if "access_token" not in body:
        raise RuntimeError(f"tiktok: refresh failed: {body}")

    # If TikTok rotated the refresh token, surface it so caller can persist it.
    if body.get("refresh_token") and body["refresh_token"] != refresh:
        print(
            f"[tiktok] refresh token rotated — update TIKTOK_REFRESH_TOKEN secret to:"
            f" {body['refresh_token'][:20]}... (full value in env after run)",
            file=sys.stderr,
        )
        os.environ["TIKTOK_REFRESH_TOKEN_NEW"] = body["refresh_token"]

    return body["access_token"]


def get_token() -> str:
    """Return a usable access token. Uses TIKTOK_ACCESS_TOKEN if set, else
    refreshes."""
    tok = os.environ.get("TIKTOK_ACCESS_TOKEN")
    if tok:
        return tok
    return refresh_access_token()


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _post_json(url: str, body: dict, token: str, timeout: int = 30) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} POST {url}: {msg}") from None


def _put_chunk(upload_url: str, chunk: bytes, content_range: str, content_type: str) -> None:
    req = urllib.request.Request(
        upload_url,
        data=chunk,
        headers={
            "Content-Range": content_range,
            "Content-Type": content_type,
            "Content-Length": str(len(chunk)),
        },
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            r.read()
    except urllib.error.HTTPError as e:
        # 308 Resume Incomplete is OK on intermediate chunks
        if e.code in (200, 201, 204, 308):
            return
        msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} PUT chunk: {msg}") from None


# ─────────────────────────────────────────────────────────────────────────────
# Video upload (Reels / MP4) → TikTok drafts
# ─────────────────────────────────────────────────────────────────────────────

def upload_video_to_inbox(mp4_path: Path) -> dict:
    """Upload an MP4 to the user's TikTok Inbox (drafts).

    Returns the init response: { publish_id, upload_url, ... }.
    Polls status until UPLOAD complete.
    """
    if not mp4_path.exists():
        raise SystemExit(f"video not found: {mp4_path}")

    size = mp4_path.stat().st_size
    # TikTok requires single-chunk for files <= 64 MB; we're well under that.
    chunk_size = size
    total_chunks = 1

    token = get_token()

    init = _post_json(INIT_VIDEO_INBOX, {
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunks,
        }
    }, token)

    if "data" not in init:
        raise RuntimeError(f"tiktok inbox init failed: {init}")

    upload_url = init["data"]["upload_url"]
    publish_id = init["data"]["publish_id"]

    with mp4_path.open("rb") as f:
        chunk = f.read()
    _put_chunk(
        upload_url,
        chunk,
        content_range=f"bytes 0-{size - 1}/{size}",
        content_type="video/mp4",
    )

    # Poll status until processed (or fail)
    status = wait_for_publish(publish_id, token)
    return {"publish_id": publish_id, "status": status}


# ─────────────────────────────────────────────────────────────────────────────
# Photo carousel (carousel posts) → TikTok drafts
# ─────────────────────────────────────────────────────────────────────────────

def upload_photo_carousel(
    photo_urls: list[str],
    title: str,
    description: str = "",
    cover_index: int = 0,
) -> dict:
    """Upload a TikTok photo carousel (Photo Mode post). Photos must be
    publicly fetchable by TikTok via PULL_FROM_URL.

    Note: PULL_FROM_URL requires the source domain to be verified in your
    TikTok app settings. raw.githubusercontent.com requires verification
    via meta tag or DNS. For initial setup, ensure your TikTok app has
    the host added under "URL Prefix" / verified domains.

    Returns init response with publish_id.
    """
    if not photo_urls:
        raise SystemExit("no photo urls")
    if len(photo_urls) > 35:
        raise SystemExit("TikTok photo carousel max is 35")

    token = get_token()

    body = {
        "post_info": {
            "title": title[:90],  # TikTok title limit
            "description": description[:2200],
            "disable_comment": False,
            "auto_add_music": True,  # TikTok suggests trending music automatically
        },
        "source_info": {
            "source": "PULL_FROM_URL",
            "photo_cover_index": cover_index,
            "photo_images": photo_urls,
        },
        "post_mode": "MEDIA_UPLOAD",  # → drafts
        "media_type": "PHOTO",
    }

    init = _post_json(INIT_CONTENT, body, token)
    if "data" not in init:
        raise RuntimeError(f"tiktok content init failed: {init}")

    publish_id = init["data"]["publish_id"]
    status = wait_for_publish(publish_id, token, max_wait_s=180)
    return {"publish_id": publish_id, "status": status}


# ─────────────────────────────────────────────────────────────────────────────
# Status polling
# ─────────────────────────────────────────────────────────────────────────────

def wait_for_publish(publish_id: str, token: str, max_wait_s: int = 300) -> dict:
    deadline = time.time() + max_wait_s
    last = None
    while time.time() < deadline:
        last = _post_json(STATUS_FETCH, {"publish_id": publish_id}, token)
        data = last.get("data") or {}
        status = data.get("status")
        if status in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
            return last
        if status in ("FAILED",):
            raise RuntimeError(f"tiktok publish failed: {last}")
        time.sleep(4)
    raise TimeoutError(f"tiktok publish_id {publish_id} did not finish in {max_wait_s}s; last={last}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI for ad-hoc testing
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:\n  python tiktok.py video <path-to-mp4>\n  python tiktok.py photos <title> <url1> [<url2> ...]", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "video":
        result = upload_video_to_inbox(Path(sys.argv[2]))
    elif cmd == "photos":
        title = sys.argv[2]
        urls = sys.argv[3:]
        result = upload_photo_carousel(urls, title)
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, indent=2))
