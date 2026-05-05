"""
soul.orbits — TikTok one-time OAuth setup.

Walks you through getting an access_token + refresh_token for the
TikTok Content Posting API. Run this LOCALLY (not in CI) — it opens a
browser for the user-consent step.

Usage:
    1. Set in your .env (from developers.tiktok.com → your app → Basic info):
         TIKTOK_CLIENT_KEY=...
         TIKTOK_CLIENT_SECRET=...
       And add this redirect URI in your app's settings:
         http://localhost:7321/callback

    2. Run:
         python automation/tiktok_setup.py

    3. Browser opens → log in to @soul.orbits TikTok → Authorize
    4. Script prints access_token + refresh_token. Add both to .env and
       to GitHub repository secrets as TIKTOK_ACCESS_TOKEN and
       TIKTOK_REFRESH_TOKEN.
"""
from __future__ import annotations

import os
import sys
import json
import secrets
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from pathlib import Path

REDIRECT_URI = "http://localhost:7321/callback"
SCOPES = "user.info.basic,video.upload,video.publish"


def env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        # Try loading .env from repo root
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip()
        raise SystemExit(f"missing env: {name} (add to .env or export)")
    return val


def main():
    client_key = env("TIKTOK_CLIENT_KEY")
    client_secret = env("TIKTOK_CLIENT_SECRET")
    state = secrets.token_urlsafe(16)

    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/?"
        + urllib.parse.urlencode({
            "client_key": client_key,
            "scope": SCOPES,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "state": state,
        })
    )

    received: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            qs = urllib.parse.urlparse(self.path).query
            params = dict(urllib.parse.parse_qsl(qs))
            received.update(params)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            ok = params.get("code") and params.get("state") == state
            html = (
                "<h2>soul.orbits — TikTok auth</h2>"
                + ("<p>OK. You can close this tab.</p>" if ok else f"<p>FAIL: {params}</p>")
            )
            self.wfile.write(html.encode("utf-8"))

    httpd = HTTPServer(("localhost", 7321), Handler)
    Thread(target=httpd.handle_request, daemon=True).start()

    print("Opening browser for TikTok consent...", flush=True)
    print(f"  {auth_url}", flush=True)
    webbrowser.open(auth_url)

    # Wait until handler captures the code (handle_request blocks until 1 req)
    while not received and httpd.RequestHandlerClass:
        pass

    if "code" not in received:
        raise SystemExit(f"no code received: {received}")
    if received.get("state") != state:
        raise SystemExit("state mismatch — possible CSRF, abort")

    # Exchange code → tokens
    body = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "code": received["code"],
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        tokens = json.loads(r.read().decode("utf-8"))

    if "access_token" not in tokens:
        raise SystemExit(f"token exchange failed: {tokens}")

    print("\n=== TikTok tokens (add to .env + GitHub secrets) ===\n", flush=True)
    print(f"TIKTOK_ACCESS_TOKEN={tokens['access_token']}")
    print(f"TIKTOK_REFRESH_TOKEN={tokens['refresh_token']}")
    print(f"\nAccess token expires in: {tokens.get('expires_in')}s (~24h)")
    print(f"Refresh token expires in: {tokens.get('refresh_expires_in')}s (~1y)")
    print(f"Scopes granted: {tokens.get('scope')}")
    print(f"\nopen_id: {tokens.get('open_id')}")


if __name__ == "__main__":
    main()
