"""
soul.orbits — publish a post to Instagram via Meta Graph API.

Required environment variables:
    META_ACCESS_TOKEN     long-lived user access token
    IG_USER_ID            Instagram Business/Creator account ID

Usage:
    python publish.py <post.yaml>

Reads the YAML, finds the matching image(s) in ./images/,
uploads to Meta, publishes, and writes a publish log.

Supports:
    - Single image post (template: daily_transit | quote)
    - Carousel post     (template: carousel — up to 10 slides)

Reels are NOT supported here yet (different endpoint + video upload).
"""
from __future__ import annotations

import os
import sys
import time
import json
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

import urllib.request
import urllib.parse
import urllib.error
import http.client

GRAPH_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"

PUBLISH_LOG = Path(__file__).resolve().parent / "publish_log.jsonl"


def env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise SystemExit(f"missing env var: {key}")
    return val


def http_post(path: str, params: dict[str, Any]) -> dict:
    url = f"{GRAPH_BASE}/{path.lstrip('/')}"
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} POST {path}: {body}") from None


def http_get(path: str, params: dict[str, Any]) -> dict:
    qs = urllib.parse.urlencode(params)
    url = f"{GRAPH_BASE}/{path.lstrip('/')}?{qs}"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} GET {path}: {body}") from None


def wait_for_container(creation_id: str, token: str, max_wait_s: int = 120) -> None:
    """Poll the container until status_code == FINISHED."""
    deadline = time.time() + max_wait_s
    while time.time() < deadline:
        info = http_get(creation_id, {"fields": "status_code", "access_token": token})
        status = info.get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"container {creation_id} errored: {info}")
        time.sleep(3)
    raise TimeoutError(f"container {creation_id} did not finish in {max_wait_s}s")


def public_image_url(image_path: Path) -> str:
    """
    Meta Graph API needs a publicly-fetchable URL for the image.
    For now, expect the caller to have uploaded the image somewhere reachable
    and provide the URL via env IMAGE_BASE_URL + relative path,
    OR the YAML may declare image_urls directly.

    In CI (GitHub Actions), images live in the repo and we serve them via
    the raw.githubusercontent.com URL during the workflow.
    """
    base = os.environ.get("IMAGE_BASE_URL")
    if not base:
        raise SystemExit(
            "IMAGE_BASE_URL not set — Meta needs a public URL for each image. "
            "In GitHub Actions, set this to "
            "https://raw.githubusercontent.com/<user>/<repo>/<branch>/content/week-XX"
        )
    rel = image_path.name
    return f"{base.rstrip('/')}/images/{rel}"


def publish_single(post_yaml: Path, caption: str, ig_user_id: str, token: str) -> dict:
    image_path = post_yaml.parent / "images" / f"{post_yaml.stem}.png"
    if not image_path.exists():
        raise SystemExit(f"image not found: {image_path}")

    image_url = public_image_url(image_path)

    # 1. create container
    res = http_post(
        f"{ig_user_id}/media",
        {"image_url": image_url, "caption": caption, "access_token": token},
    )
    creation_id = res["id"]

    # 2. wait for container ready
    wait_for_container(creation_id, token)

    # 3. publish
    pub = http_post(
        f"{ig_user_id}/media_publish",
        {"creation_id": creation_id, "access_token": token},
    )
    return {"type": "single", "creation_id": creation_id, "media_id": pub["id"]}


def publish_reel(post_yaml: Path, caption: str, ig_user_id: str, token: str) -> dict:
    """
    Publish an Instagram Reel.

    The YAML must have:
        template: reel
        video: relative path to the MP4 (under the same folder as the YAML
               or under reels/out/ — first match wins)

    The video URL must be publicly fetchable (raw.githubusercontent.com works).
    """
    data = yaml.safe_load(post_yaml.read_text(encoding="utf-8"))
    video_rel = data.get("video")
    if not video_rel:
        raise SystemExit(f"reel YAML missing 'video' field: {post_yaml}")

    # Resolve to a public URL. We assume the MP4 lives under the repo and
    # IMAGE_BASE_URL points at content/week-XX-real. For reels we let the YAML
    # specify either an absolute URL (http...) or a path relative to the repo root.
    if video_rel.startswith("http"):
        video_url = video_rel
    else:
        base = os.environ.get("REPO_RAW_BASE_URL")
        if not base:
            raise SystemExit(
                "REPO_RAW_BASE_URL not set — needed to serve the MP4 to Meta. "
                "Example: https://raw.githubusercontent.com/<user>/<repo>/main"
            )
        video_url = f"{base.rstrip('/')}/{video_rel.lstrip('/')}"

    cover_url = data.get("cover_url")  # optional thumbnail

    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true",
        "access_token": token,
    }
    if cover_url:
        params["cover_url"] = cover_url

    res = http_post(f"{ig_user_id}/media", params)
    creation_id = res["id"]

    # Reels can take longer to process — wait up to 5 minutes.
    wait_for_container(creation_id, token, max_wait_s=300)

    pub = http_post(
        f"{ig_user_id}/media_publish",
        {"creation_id": creation_id, "access_token": token},
    )
    return {"type": "reel", "creation_id": creation_id, "media_id": pub["id"], "video_url": video_url}


def publish_carousel(post_yaml: Path, caption: str, ig_user_id: str, token: str) -> dict:
    images_dir = post_yaml.parent / "images"
    slides = sorted(images_dir.glob(f"{post_yaml.stem}-slide*.png"))
    if not slides:
        raise SystemExit(f"no carousel slides found for {post_yaml.stem}")
    if len(slides) > 10:
        raise SystemExit(f"carousel max 10 slides, got {len(slides)}")

    # 1. create children containers
    child_ids = []
    for slide in slides:
        url = public_image_url(slide)
        res = http_post(
            f"{ig_user_id}/media",
            {"image_url": url, "is_carousel_item": "true", "access_token": token},
        )
        child_ids.append(res["id"])

    for cid in child_ids:
        wait_for_container(cid, token)

    # 2. create parent carousel container
    parent = http_post(
        f"{ig_user_id}/media",
        {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
            "access_token": token,
        },
    )
    parent_id = parent["id"]
    wait_for_container(parent_id, token)

    # 3. publish parent
    pub = http_post(
        f"{ig_user_id}/media_publish",
        {"creation_id": parent_id, "access_token": token},
    )
    return {"type": "carousel", "parent_id": parent_id, "media_id": pub["id"], "children": child_ids}


def load_caption(post_yaml: Path) -> str:
    """
    Caption lives in the sibling .md file.
    Convention: caption is the section under '## Caption' until the next '##' or EOF.
    """
    md = post_yaml.with_suffix(".md")
    if not md.exists():
        raise SystemExit(f"caption markdown not found: {md}")
    text = md.read_text(encoding="utf-8")
    if "## Caption" not in text:
        raise SystemExit(f"no '## Caption' section in {md}")
    after = text.split("## Caption", 1)[1]
    block = after.split("\n## ", 1)[0]
    # strip the opening ``` fences
    lines = [ln for ln in block.splitlines() if ln.strip() != "```"]
    return "\n".join(lines).strip()


def log_publish(entry: dict) -> None:
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with PUBLISH_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: publish.py <post.yaml>", file=sys.stderr)
        sys.exit(1)

    post_yaml = Path(sys.argv[1]).resolve()
    if not post_yaml.exists():
        raise SystemExit(f"not found: {post_yaml}")

    data = yaml.safe_load(post_yaml.read_text(encoding="utf-8"))
    caption = load_caption(post_yaml)
    token = env("META_ACCESS_TOKEN")
    ig_user_id = env("IG_USER_ID")

    if data["template"] == "carousel":
        result = publish_carousel(post_yaml, caption, ig_user_id, token)
    elif data["template"] == "reel":
        result = publish_reel(post_yaml, caption, ig_user_id, token)
    else:
        result = publish_single(post_yaml, caption, ig_user_id, token)

    result["post"] = post_yaml.name
    log_publish(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
