"""
soul.orbits — interactive .env filler with format validation.

Shows each value as you type (Windows getpass is unreliable),
validates length/format, asks for confirmation before saving.
"""
import re
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def write_env(values: dict[str, str]) -> None:
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    seen = set()
    new = []
    for ln in lines:
        s = ln.strip()
        if s and not s.startswith("#") and "=" in s:
            k = s.split("=", 1)[0].strip()
            if k in values:
                new.append(f"{k}={values[k]}")
                seen.add(k)
                continue
        new.append(ln)
    for k, v in values.items():
        if k not in seen:
            new.append(f"{k}={v}")
    ENV_PATH.write_text("\n".join(new) + "\n", encoding="utf-8")


def prompt(label: str, validator, hint: str) -> str:
    while True:
        print(f"\n--- {label} ---")
        print(f"  expected: {hint}")
        val = input(f"  paste here: ").strip()
        # strip surrounding quotes if any
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        ok, msg = validator(val)
        if not ok:
            print(f"  ✗ rejected: {msg}")
            print(f"  try again. (Ctrl+C to abort)")
            continue
        print(f"  ✓ ok ({len(val)} chars)")
        return val


def is_app_id(v: str) -> tuple[bool, str]:
    if not v.isdigit():
        return False, "must be all digits"
    if len(v) < 14 or len(v) > 18:
        return False, f"length {len(v)} unusual (expected 15-17)"
    return True, ""


def is_app_secret(v: str) -> tuple[bool, str]:
    if not re.fullmatch(r"[0-9a-fA-F]{32}", v):
        return False, "must be exactly 32 hex characters (0-9, a-f)"
    return True, ""


def is_access_token(v: str) -> tuple[bool, str]:
    if not v.startswith("EAA"):
        return False, "Meta access tokens start with 'EAA'"
    if len(v) < 100:
        return False, f"too short ({len(v)} chars)"
    if len(v) > 500:
        return False, f"too long ({len(v)} chars) — likely paste corruption"
    return True, ""


def main():
    print("=== soul.orbits — fill .env ===")
    print("Tip: each value is shown after you paste so you can verify it.")
    print("If a value looks wrong, retype/repaste it.\n")

    app_id = prompt(
        "META_APP_ID",
        is_app_id,
        "16-digit numeric (e.g. 2133864204114102)",
    )
    app_secret = prompt(
        "META_APP_SECRET",
        is_app_secret,
        "32 hex chars from App settings → Basic → App secret → Show",
    )
    access_token = prompt(
        "META_ACCESS_TOKEN",
        is_access_token,
        "starts with 'EAA', 200-400 chars, from Graph API Explorer",
    )

    print("\n--- summary ---")
    print(f"  META_APP_ID = {app_id}")
    print(f"  META_APP_SECRET = {app_secret[:4]}…{app_secret[-4:]} ({len(app_secret)} chars)")
    print(f"  META_ACCESS_TOKEN = {access_token[:6]}…{access_token[-4:]} ({len(access_token)} chars)")
    confirm = input("\nSave to .env? (y/n): ").strip().lower()
    if confirm != "y":
        print("aborted.")
        return

    write_env({
        "META_APP_ID": app_id,
        "META_APP_SECRET": app_secret,
        "META_ACCESS_TOKEN": access_token,
    })
    print("✓ .env updated")


if __name__ == "__main__":
    main()
