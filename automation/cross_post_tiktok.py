"""
soul.orbits — cross-post a published IG post to TikTok drafts.

Called from publish_today.py after a successful IG publish. For Reels,
uploads the MP4 to TikTok Inbox. For carousels, uploads the slide images
as a TikTok Photo Mode post.

Both land in the user's TikTok drafts. They open the app, pick trending
sound, tap Post.

Required env (same as automation/tiktok.py):
    TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
    REPO_RAW_BASE_URL    # to build photo URLs for PULL_FROM_URL
"""
from __future__ import annotations

import os
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent


def _photo_urls_for(post_yaml: Path) -> list[str]:
    """Build raw.githubusercontent.com URLs for each carousel slide PNG."""
    base = os.environ.get("REPO_RAW_BASE_URL")
    if not base:
        raise SystemExit("REPO_RAW_BASE_URL not set — needed for TikTok photo URLs")
    images_dir = post_yaml.parent / "images"
    slides = sorted(images_dir.glob(f"{post_yaml.stem}-slide*.png"))
    urls = []
    for s in slides:
        rel = s.relative_to(ROOT).as_posix()
        urls.append(f"{base.rstrip('/')}/{rel}")
    return urls


def _caption_for(post_yaml: Path) -> tuple[str, str]:
    """Return (title, full_caption). Title = first non-empty line. Full
    caption (description) = all caption text."""
    md = post_yaml.with_suffix(".md")
    if not md.exists():
        return (post_yaml.stem, "")
    text = md.read_text(encoding="utf-8")
    if "## Caption" not in text:
        return (post_yaml.stem, "")
    block = text.split("## Caption", 1)[1].split("\n## ", 1)[0]
    lines = [ln for ln in block.splitlines() if ln.strip() and ln.strip() != "```"]
    if not lines:
        return (post_yaml.stem, "")
    title = lines[0].strip()
    full = "\n".join(lines).strip()
    return (title[:90], full)


def cross_post(post_yaml: Path) -> dict:
    data = yaml.safe_load(post_yaml.read_text(encoding="utf-8"))
    template = data.get("template")

    # Lazy import so missing TikTok envs don't block IG publish.
    from tiktok import upload_video_to_inbox, upload_photo_carousel

    title, full_caption = _caption_for(post_yaml)

    if template == "reel":
        video_rel = data.get("video")
        if not video_rel:
            raise SystemExit(f"reel YAML missing 'video' field: {post_yaml}")
        mp4 = ROOT / video_rel
        result = upload_video_to_inbox(mp4)
        result["type"] = "video"
        return result

    if template == "carousel":
        urls = _photo_urls_for(post_yaml)
        if not urls:
            raise SystemExit(f"no carousel slides found for {post_yaml.stem}")
        result = upload_photo_carousel(urls, title=title, description=full_caption)
        result["type"] = "photo_carousel"
        return result

    # Daily transit single image, quote, etc.
    # TikTok doesn't have a single-image format — wrap as 1-slide photo carousel.
    if template in ("daily_transit", "quote"):
        images_dir = post_yaml.parent / "images"
        png = images_dir / f"{post_yaml.stem}.png"
        if not png.exists():
            raise SystemExit(f"image not found: {png}")
        base = os.environ.get("REPO_RAW_BASE_URL")
        if not base:
            raise SystemExit("REPO_RAW_BASE_URL not set")
        rel = png.relative_to(ROOT).as_posix()
        url = f"{base.rstrip('/')}/{rel}"
        result = upload_photo_carousel([url], title=title, description=full_caption)
        result["type"] = "photo_single"
        return result

    raise SystemExit(f"unsupported template for cross-post: {template}")


def main():
    if len(sys.argv) < 2:
        print("Usage: cross_post_tiktok.py <post.yaml>", file=sys.stderr)
        sys.exit(1)
    out = cross_post(Path(sys.argv[1]).resolve())
    import json
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
