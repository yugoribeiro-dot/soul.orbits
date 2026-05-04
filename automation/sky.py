"""
soul.orbits — daily sky report for content planning.
Uses kerykeion (Swiss Ephemeris) for exact positions.

Usage:
    python sky.py 2026-05-04 2026-05-11
"""
import sys
from datetime import date, datetime, timedelta, timezone
from kerykeion import AstrologicalSubject

PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter",
           "saturn", "uranus", "neptune", "pluto", "mean_node"]

GLYPHS = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀", "mars": "♂",
    "jupiter": "♃", "saturn": "♄", "uranus": "♅", "neptune": "♆",
    "pluto": "♇", "mean_node": "☊",
}

ASPECTS = [
    (0, "conjunction", "☌", 7),
    (60, "sextile", "⚹", 4),
    (90, "square", "□", 6),
    (120, "trine", "△", 6),
    (180, "opposition", "☍", 7),
]


def angle_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def sky_at(dt: datetime) -> dict:
    """Returns positions and key aspects for a moment."""
    s = AstrologicalSubject(
        name="sky", year=dt.year, month=dt.month, day=dt.day,
        hour=dt.hour, minute=dt.minute,
        lat=0.0, lng=0.0, tz_str="UTC", city="Greenwich",
        online=False, geonames_username=None,
    )
    out = {}
    for p in PLANETS:
        pl = getattr(s, p, None)
        if pl is None:
            continue
        out[p] = {
            "sign": pl.sign,
            "deg_in_sign": pl.position,
            "abs_lon": pl.abs_pos,
            "retrograde": pl.retrograde,
        }
    return out


def find_aspects(positions: dict) -> list:
    found = []
    keys = list(positions.keys())
    for i, p1 in enumerate(keys):
        for p2 in keys[i+1:]:
            if p1 == "moon" or p2 == "moon":
                continue  # moon aspects shift hourly
            sep = angle_diff(positions[p1]["abs_lon"], positions[p2]["abs_lon"])
            for exact, name, glyph, orb in ASPECTS:
                if abs(sep - exact) <= orb:
                    found.append({
                        "p1": p1, "p2": p2, "aspect": name,
                        "glyph": glyph, "orb": round(abs(sep - exact), 2),
                    })
                    break
    return sorted(found, key=lambda x: x["orb"])


def daily_report(start: date, end: date):
    print(f"\n=== Sky report {start} → {end} (UTC noon) ===\n")
    prev_signs = {}
    cur = start
    while cur <= end:
        dt = datetime(cur.year, cur.month, cur.day, 12, 0, tzinfo=timezone.utc)
        pos = sky_at(dt)
        print(f"--- {cur.isoformat()} {cur.strftime('%a')} ---")
        for p in PLANETS:
            if p not in pos:
                continue
            d = pos[p]
            arrow = ""
            if p in prev_signs and prev_signs[p] != d["sign"]:
                arrow = f"  ← INGRESS into {d['sign']}"
            rx = " ℞" if d["retrograde"] else ""
            print(f"  {GLYPHS[p]} {p:<10} {d['sign']:<6} {d['deg_in_sign']:5.2f}°{rx}{arrow}")
            prev_signs[p] = d["sign"]
        asp = find_aspects(pos)[:6]
        if asp:
            print("  major aspects (slow):")
            for a in asp:
                p1, p2 = a["p1"], a["p2"]
                print(f"    {GLYPHS[p1]} {p1} {a['glyph']} {GLYPHS[p2]} {p2}  ({a['aspect']}, orb {a['orb']}°)")
        print()
        cur += timedelta(days=1)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        start = date.fromisoformat(sys.argv[1])
        end = date.fromisoformat(sys.argv[2])
    else:
        today = datetime.now(timezone.utc).date()
        start = today
        end = today + timedelta(days=7)
    daily_report(start, end)
