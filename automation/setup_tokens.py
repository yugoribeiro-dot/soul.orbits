"""
soul.orbits — one-shot setup:
  1. Read short-lived token + app credentials from .env
  2. Exchange for long-lived token (~60 days)
  3. Find the FB Page connected to the IG account
  4. Extract IG_USER_ID
  5. Write META_ACCESS_TOKEN (long-lived) and IG_USER_ID back to .env

Run once after generating the short-lived token in Graph API Explorer.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
GRAPH = "https://graph.facebook.com/v21.0"


def load_env() -> dict[str, str]:
    if not ENV_PATH.exists():
        sys.exit(f"missing {ENV_PATH}")
    out = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def write_env(values: dict[str, str]) -> None:
    """Update .env in place, preserving comments and order."""
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    seen = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k = stripped.split("=", 1)[0].strip()
            if k in values:
                new_lines.append(f"{k}={values[k]}")
                seen.add(k)
                continue
        new_lines.append(line)
    # append any keys not in file
    for k, v in values.items():
        if k not in seen:
            new_lines.append(f"{k}={v}")
    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def http_get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def exchange_for_long_lived(app_id: str, app_secret: str, short_token: str) -> str:
    qs = urllib.parse.urlencode({
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token,
    })
    data = http_get(f"{GRAPH}/oauth/access_token?{qs}")
    return data["access_token"]


def find_ig_user_id(token: str, page_name_hint: str | None = "soul") -> tuple[str, str]:
    """
    Returns (page_name, ig_user_id).
    If a page_name_hint is given, prefers a page whose name contains it (case-insensitive).
    Otherwise picks the only page with an IG business account, or errors.
    """
    pages = http_get(f"{GRAPH}/me/accounts?fields=id,name,access_token&access_token={token}")["data"]
    if not pages:
        raise SystemExit("no FB pages found for this user")

    # try each page until we find one with an IG business account
    candidates = []
    if page_name_hint:
        ranked = sorted(pages, key=lambda p: (page_name_hint.lower() not in p["name"].lower(),))
    else:
        ranked = pages

    for page in ranked:
        info = http_get(
            f"{GRAPH}/{page['id']}?fields=instagram_business_account&access_token={token}"
        )
        ig = info.get("instagram_business_account")
        if ig:
            candidates.append((page["name"], ig["id"]))
            # if hint matches, return immediately
            if page_name_hint and page_name_hint.lower() in page["name"].lower():
                return page["name"], ig["id"]

    if not candidates:
        raise SystemExit("no FB page is connected to an Instagram business account")
    return candidates[0]


def main():
    env = load_env()

    for k in ["META_APP_ID", "META_APP_SECRET", "META_ACCESS_TOKEN"]:
        if not env.get(k):
            sys.exit(f"missing {k} in .env")

    print("[1/3] exchanging for long-lived token...")
    long_token = exchange_for_long_lived(
        env["META_APP_ID"], env["META_APP_SECRET"], env["META_ACCESS_TOKEN"]
    )
    print("      got long-lived token (60-day TTL)")

    print("[2/3] finding FB page + IG business account...")
    page_name, ig_id = find_ig_user_id(long_token, page_name_hint="soul")
    print(f"      page='{page_name}'  ig_user_id={ig_id}")

    print("[3/3] writing .env...")
    write_env({
        "META_ACCESS_TOKEN": long_token,
        "IG_USER_ID": ig_id,
    })
    print("done. .env updated with long-lived token + IG_USER_ID.")


if __name__ == "__main__":
    main()
