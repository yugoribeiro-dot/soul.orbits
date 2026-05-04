"""
soul.orbits — procedural SVG starfield generator.

Produces a 1080x1350 SVG with ~220 stars of varied size, brightness, color,
and a few "halo" stars for visual depth. Deterministic with a seed so the
same post always renders the same field (avoids post-to-post jitter).
"""
from __future__ import annotations
import random
import math


def generate_starfield(seed: int = 7, width: int = 1080, height: int = 1350) -> str:
    rng = random.Random(seed)

    # Star tiers (count, radius_range, opacity_range, color)
    tiers = [
        # tiny dust — many, faint
        (140, (0.4, 0.9), (0.18, 0.45), "255,255,255"),
        # small white
        (50, (0.9, 1.6), (0.45, 0.75), "255,255,255"),
        # medium gold
        (18, (1.4, 2.2), (0.55, 0.85), "255,200,140"),
        # bright pink-white (rare)
        (8, (1.8, 2.8), (0.65, 0.95), "255,200,220"),
        # halo stars (with glow)
        (4, (2.4, 3.4), (0.85, 1.0), "255,220,170"),
    ]

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid slice">']

    # subtle large nebula glows in the corners (not realistic nebulae, just depth)
    parts.append(
        '<defs>'
        '<radialGradient id="g1" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="rgba(138,77,255,0.18)"/>'
        '<stop offset="100%" stop-color="rgba(138,77,255,0)"/>'
        '</radialGradient>'
        '<radialGradient id="g2" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="rgba(255,77,141,0.15)"/>'
        '<stop offset="100%" stop-color="rgba(255,77,141,0)"/>'
        '</radialGradient>'
        '<radialGradient id="g3" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="rgba(255,200,87,0.10)"/>'
        '<stop offset="100%" stop-color="rgba(255,200,87,0)"/>'
        '</radialGradient>'
        '<filter id="glow" x="-100%" y="-100%" width="300%" height="300%">'
        '<feGaussianBlur stdDeviation="3" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
        '</defs>'
    )

    parts.append(f'<ellipse cx="{int(width*0.20)}" cy="{int(height*0.15)}" rx="{int(width*0.45)}" ry="{int(height*0.30)}" fill="url(#g1)"/>')
    parts.append(f'<ellipse cx="{int(width*0.85)}" cy="{int(height*0.30)}" rx="{int(width*0.40)}" ry="{int(height*0.28)}" fill="url(#g2)"/>')
    parts.append(f'<ellipse cx="{int(width*0.55)}" cy="{int(height*0.92)}" rx="{int(width*0.45)}" ry="{int(height*0.25)}" fill="url(#g3)"/>')

    for count, (rmin, rmax), (omin, omax), color in tiers:
        for _ in range(count):
            x = rng.uniform(0, width)
            y = rng.uniform(0, height)
            r = rng.uniform(rmin, rmax)
            o = rng.uniform(omin, omax)
            is_halo = (rmin >= 2.4)
            filt = ' filter="url(#glow)"' if is_halo else ''
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="rgba({color},{o:.2f})"{filt}/>')

    # cross-hair flares on the brightest stars (Hubble look)
    for _ in range(6):
        x = rng.uniform(60, width - 60)
        y = rng.uniform(60, height - 60)
        s = rng.uniform(8, 18)
        op = rng.uniform(0.30, 0.55)
        parts.append(f'<line x1="{x-s:.1f}" y1="{y:.1f}" x2="{x+s:.1f}" y2="{y:.1f}" stroke="rgba(255,235,200,{op:.2f})" stroke-width="0.6"/>')
        parts.append(f'<line x1="{x:.1f}" y1="{y-s:.1f}" x2="{x:.1f}" y2="{y+s:.1f}" stroke="rgba(255,235,200,{op:.2f})" stroke-width="0.6"/>')

    parts.append('</svg>')
    return "".join(parts)


def starfield_data_uri(seed: int = 7) -> str:
    """Return a data: URI safe to embed in CSS background-image."""
    import base64
    svg = generate_starfield(seed)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


if __name__ == "__main__":
    # CLI: python starfield.py [seed] > out.svg
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    print(generate_starfield(seed))
