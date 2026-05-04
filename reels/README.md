# soul.orbits — Reels (Remotion)

Programmatic video composition for Instagram Reels. Vertical 9:16 (1080×1920), 30fps, brand fonts via Google Fonts.

## Setup
```bash
npm install
```

## Develop (Studio)
```bash
npm run preview
```
Opens Remotion Studio at http://localhost:3000 — hot reload on file changes, scrub timeline, inspect compositions.

## Render
```bash
# Render the Mars□Jupiter Reel
npm run render

# Or directly
npx remotion render src/index.ts MarsJupiter out/<name>.mp4
```

## Compositions

| ID | File | Duration | Theme |
|---|---|---|---|
| `MarsJupiter` | `src/MarsJupiterReel.tsx` | 10s (300f @ 30fps) | Mon May 4 — fight your boss hook |

## Architecture

- `src/index.ts` — entry point, registers Root
- `src/Root.tsx` — declares all `<Composition>` entries
- `src/Starfield.tsx` — animated SVG starfield (220 stars, 5 tiers, twinkle + drift)
- `src/MarsJupiterReel.tsx` — full Reel: Hook → 4 sign scenes → CTA

## Brand colors
- `--cosmos`: `#14122B` (deep base)
- `--gold`: `#FFC857`
- `--pink`: `#FF4D8D`
- `--violet`: `#8A4DFF`
- `--moon`: `#F5EFE0`

## Fonts (auto-loaded via @remotion/google-fonts)
- Archivo Black (display headlines)
- Cormorant Garamond 500 + 500 italic (serif body, sign messages)
- Inter 600/900 (UI labels)

## Notes
- `out/*.mp4` and `out/preview-*.png` are gitignored — render artifacts
- Glyphs use the `︎` text variation selector to avoid emoji rendering
- Publishing to Instagram Reels requires a different Meta Graph API endpoint than feed posts (`media_type=REELS`, video_url) — not yet integrated in `automation/publish.py`
