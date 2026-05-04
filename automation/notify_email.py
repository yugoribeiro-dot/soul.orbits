"""
soul.orbits — email notification helper (via Resend).

Sends an email when a Reel is published, prompting the user to open
Instagram and attach trending audio (max algorithm reach).

Usage as CLI:
    python notify_email.py "<subject>" "<html_body>"

Required env:
    RESEND_API_KEY    from resend.com → API Keys
    EMAIL_TO          recipient (e.g. hugo.ribeiro@hvr.pt)
    EMAIL_FROM        sender (default: onboarding@resend.dev — works without
                      domain verification, fine for transactional alerts)
"""
from __future__ import annotations

import os
import sys
import json
import urllib.request
import urllib.error


def send(subject: str, html: str, text: str | None = None) -> dict | None:
    api_key = os.environ.get("RESEND_API_KEY")
    to = os.environ.get("EMAIL_TO")
    sender = os.environ.get("EMAIL_FROM", "soul.orbits <onboarding@resend.dev>")
    if not api_key or not to:
        print("notify_email: RESEND_API_KEY / EMAIL_TO not set — skipping", file=sys.stderr)
        return None

    payload = {
        "from": sender,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if text:
        payload["text"] = text

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"notify_email: HTTP {e.code}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"notify_email: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def reel_published(media_id: str) -> None:
    """Standard Reel-published reminder — open IG and add trending audio."""
    permalink = f"https://www.instagram.com/reel/{media_id}/" if media_id else "https://www.instagram.com/soul.orbits/"
    subject = "🎬 Reel published — add trending audio in IG (60 min window)"
    html = f"""\
<!DOCTYPE html>
<html><body style="font-family:-apple-system,Segoe UI,sans-serif;background:#14122B;color:#F5EFE0;padding:32px;max-width:560px;margin:0 auto;">
  <div style="background:linear-gradient(160deg,#1a0f3a,#14122B);padding:28px;border-radius:16px;border:1px solid rgba(255,200,87,0.2);">
    <div style="font-size:14px;letter-spacing:4px;color:#FFC857;text-transform:uppercase;margin-bottom:12px;">soul.orbits</div>
    <h1 style="font-size:28px;line-height:1.2;margin:0 0 18px;color:#F5EFE0;">🎬 A Reel just published.</h1>
    <p style="font-size:16px;line-height:1.5;color:#F5EFE0;opacity:0.9;">
      Open Instagram in the next <b style="color:#FF4D8D;">60 minutes</b> and attach trending audio.
      That alone is <b>5–10× more reach</b> than the Reel as it sits now.
    </p>
    <ol style="font-size:15px;line-height:1.7;color:#F5EFE0;opacity:0.85;padding-left:20px;">
      <li>Tap the Reel you just posted</li>
      <li>Edit → Add audio → search trending</li>
      <li>Pick something matching the vibe (cosmic / dark / punchy)</li>
      <li>Save</li>
    </ol>
    <a href="{permalink}" style="display:inline-block;margin-top:24px;background:#FFC857;color:#14122B;padding:14px 24px;border-radius:999px;text-decoration:none;font-weight:900;letter-spacing:1px;">OPEN REEL →</a>
    <p style="margin-top:32px;font-size:12px;color:#F5EFE0;opacity:0.5;">
      Sent automatically by soul.orbits auto-publish pipeline. Add trending audio = more reach. No audio = nearly invisible.
    </p>
  </div>
</body></html>"""
    text = (
        "Reel just published — add trending audio in IG within 60 min for max reach.\n"
        "1. Tap the Reel\n2. Edit → Add audio → trending\n3. Pick cosmic/dark vibe\n4. Save\n\n"
        f"{permalink}\n"
    )
    send(subject, html, text)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: notify_email.py <subject> <html_body>", file=sys.stderr)
        sys.exit(1)
    send(sys.argv[1], sys.argv[2])
