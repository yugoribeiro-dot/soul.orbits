"""
soul.orbits — daily comment drafting helper.

Fetches the latest post from a curated list of large astrology accounts
via the Instagram Graph API Business Discovery endpoint, then asks Claude
to draft 3 distinct comments per post in the soul.orbits voice. Emails
the result to EMAIL_TO so the user can copy-paste in ~5 minutes/day.

Why this exists: comment-engagement on bigger accounts is the #1 organic
growth lever for new IG accounts in 2026. Automating the *drafting* keeps
the human voice (and avoids TOS violation from auto-posting comments).

Required env:
    META_ACCESS_TOKEN
    IG_USER_ID
    ANTHROPIC_API_KEY
    RESEND_API_KEY, EMAIL_TO   (for emailing drafts)
"""
from __future__ import annotations

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Curated targets — large public astrology accounts. Edit freely.
TARGETS = [
    "cosmicrxx",
    "notallgeminis",
    "astrology_marina",
    "chaninicholas",
    "themaywellsnyder",
]

GRAPH_BASE = "https://graph.facebook.com/v21.0"
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-4-5"  # latest at time of writing

VOICE_BRIEF = """\
You are writing comments for @soul.orbits — a new IG astrology account with
this voice:
  - Editorial-irreverent: serious astrology insight, casual delivery
  - Says concrete things, not platitudes ("Saturn edits, doesn't punish" >
    "the universe has a plan ✨")
  - References real transits/placements when relevant
  - No emojis except very sparingly (never as decoration)
  - Conversational, like one astrologer talking to another in a DM
  - Sometimes self-deprecating, sometimes sharp
  - Never starts with "Love this!" or "So true!" or generic affirmation
  - 1-2 sentences max — comments that feel like an aside, not a speech

Goal: comments that make the original poster's followers click the
@soul.orbits username because the comment was distinctive enough to
notice. Voice > virality.
"""


def env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"missing env: {name}")
    return val


def http_get_json(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} GET {url[:80]}...: {msg}") from None


def fetch_target_recent_post(target_username: str, ig_user_id: str, token: str) -> dict | None:
    """Use Business Discovery to fetch the most recent post from a public
    business/creator account."""
    fields = (
        f"business_discovery.username({target_username})"
        f"{{username,name,followers_count,"
        f"media.limit(1){{caption,permalink,media_type,timestamp}}}}"
    )
    url = f"{GRAPH_BASE}/{ig_user_id}?fields={urllib.parse.quote(fields)}&access_token={token}"
    try:
        data = http_get_json(url)
    except RuntimeError as e:
        print(f"[draft_comments] fetch failed for {target_username}: {e}", file=sys.stderr)
        return None
    bd = data.get("business_discovery")
    if not bd:
        return None
    media_list = (bd.get("media") or {}).get("data") or []
    if not media_list:
        return None
    m = media_list[0]
    return {
        "username": bd.get("username", target_username),
        "name": bd.get("name", ""),
        "followers": bd.get("followers_count", 0),
        "caption": (m.get("caption") or "").strip(),
        "permalink": m.get("permalink", ""),
        "media_type": m.get("media_type", ""),
        "timestamp": m.get("timestamp", ""),
    }


def ask_claude(prompt: str) -> str:
    api_key = env("ANTHROPIC_API_KEY")
    body = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 800,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        ANTHROPIC_API,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"anthropic HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}") from None
    parts = data.get("content", [])
    text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
    return text.strip()


def draft_comments_for(post: dict) -> list[str]:
    cap = post["caption"][:1200]  # cap to keep token cost low
    prompt = (
        f"{VOICE_BRIEF}\n\n"
        f"Account you're commenting on: @{post['username']} ({post['followers']:,} followers)\n"
        f"Their post caption:\n---\n{cap}\n---\n\n"
        "Write THREE distinct comment drafts in the soul.orbits voice. Each on its own line, "
        "prefixed with '— '. No numbering, no extra commentary. Just three lines starting with '— '.\n"
        "Constraint: each comment is 1-2 sentences, under 200 characters, no decorative emoji.\n"
    )
    raw = ask_claude(prompt)
    drafts = [ln.lstrip("— ").strip() for ln in raw.splitlines() if ln.strip().startswith("—")]
    if not drafts:
        # fallback: split by double-newline
        drafts = [b.strip() for b in raw.split("\n\n") if b.strip()]
    return drafts[:3]


def build_email(rows: list[dict]) -> tuple[str, str, str]:
    """rows = [{post: {...}, drafts: [...]}, ...]"""
    subject = f"☉ daily comment drafts — {len(rows)} accounts"
    rows_html = []
    rows_text = []
    for r in rows:
        p = r["post"]
        drafts = r["drafts"]
        cap = (p["caption"] or "").replace("\n", " ")[:240]
        drafts_html = "".join(
            f'<li style="margin-bottom:8px;color:#F5EFE0;line-height:1.45;">{d}</li>'
            for d in drafts
        )
        rows_html.append(f"""
<div style="background:linear-gradient(160deg,#1a0f3a,#14122B);padding:24px;border-radius:14px;margin-bottom:18px;border:1px solid rgba(255,200,87,0.18);">
  <div style="font-size:13px;letter-spacing:3px;color:#FFC857;text-transform:uppercase;margin-bottom:6px;">@{p['username']} · {p['followers']:,}</div>
  <div style="font-size:15px;color:#F5EFE0;opacity:0.7;margin-bottom:12px;font-style:italic;">"{cap}{'…' if len(p['caption']) > 240 else ''}"</div>
  <a href="{p['permalink']}" style="display:inline-block;font-size:13px;color:#FF4D8D;margin-bottom:14px;">→ open the post</a>
  <ol style="padding-left:18px;font-size:15px;color:#F5EFE0;">{drafts_html}</ol>
</div>
""")
        rows_text.append(
            f"\n=== @{p['username']} ({p['followers']:,} followers) ===\n"
            f"\"{cap}\"\n{p['permalink']}\n\n"
            + "\n".join(f"  {i+1}. {d}" for i, d in enumerate(drafts))
        )

    html = f"""\
<!DOCTYPE html>
<html><body style="font-family:-apple-system,Segoe UI,sans-serif;background:#0d0a1f;color:#F5EFE0;padding:32px;max-width:640px;margin:0 auto;">
  <div style="font-size:13px;letter-spacing:4px;color:#FFC857;text-transform:uppercase;margin-bottom:6px;">soul.orbits</div>
  <h1 style="font-size:26px;line-height:1.2;margin:0 0 8px;color:#F5EFE0;">☉ Daily comment drafts</h1>
  <p style="font-size:14px;color:#F5EFE0;opacity:0.7;margin:0 0 24px;">Pick one per account, copy, paste, post. ~5 min total. Distinctive voice &gt; volume.</p>
  {"".join(rows_html)}
  <p style="margin-top:32px;font-size:11px;color:#F5EFE0;opacity:0.4;">Generated automatically. Edit, swap or skip any draft. The point is human voice — these are starting points, not finished comments.</p>
</body></html>"""
    text = "soul.orbits — Daily comment drafts\n" + "".join(rows_text)
    return subject, html, text


def main():
    token = env("META_ACCESS_TOKEN")
    ig = env("IG_USER_ID")

    rows = []
    for t in TARGETS:
        print(f"[draft_comments] fetching @{t}...", flush=True)
        post = fetch_target_recent_post(t, ig, token)
        if not post:
            print(f"[draft_comments] no post for @{t} (private/inactive?) — skipping", flush=True)
            continue
        try:
            drafts = draft_comments_for(post)
        except Exception as e:
            print(f"[draft_comments] claude failed for @{t}: {e}", file=sys.stderr)
            continue
        rows.append({"post": post, "drafts": drafts})
        print(f"[draft_comments] @{t}: {len(drafts)} drafts ready", flush=True)

    if not rows:
        print("[draft_comments] nothing to send", flush=True)
        return

    subject, html, text = build_email(rows)

    try:
        from notify_email import send
        send(subject, html, text)
        print("[draft_comments] email sent", flush=True)
    except Exception as e:
        print(f"[draft_comments] email failed: {e}", file=sys.stderr)
        # Fallback: print to stdout for CI logs
        print("\n" + text)


if __name__ == "__main__":
    main()
