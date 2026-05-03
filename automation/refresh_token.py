"""
soul.orbits — refresh the long-lived Meta access token.

Long-lived tokens last ~60 days. Refresh them every ~50 days.

Usage:
    META_ACCESS_TOKEN=<current> python refresh_token.py

Prints the new token. In CI, this should update the GitHub secret
(see refresh_token.yml workflow which runs monthly).
"""
import os
import sys
import json
import urllib.request
import urllib.parse


def main():
    token = os.environ.get("META_ACCESS_TOKEN")
    if not token:
        raise SystemExit("META_ACCESS_TOKEN env var required")

    params = urllib.parse.urlencode({
        "grant_type": "fb_exchange_token",
        "client_id": os.environ["META_APP_ID"],
        "client_secret": os.environ["META_APP_SECRET"],
        "fb_exchange_token": token,
    })
    url = f"https://graph.facebook.com/v21.0/oauth/access_token?{params}"

    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    print(data["access_token"])


if __name__ == "__main__":
    main()
