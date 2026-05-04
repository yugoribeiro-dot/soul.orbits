# Cosmic image library — soul.orbits

12 NASA/ESA Hubble images, public domain. Use as background overlays for **hero posts** (1×/week max — variety without diluting brand consistency).

| File | Subject | Best use |
|---|---|---|
| `heic1501a.jpg` | Pillars of Creation (Hubble visible 2014) — 34 MB | Big-statement post about transformation, generational transits |
| `heic0910e.jpg` | Mystic Mountain (Carina pillar) | Mars/courage themes, individuation, Saturn-in-Aries hero |
| `heic1107a.jpg` | Tarantula Nebula | Pluto themes, intensity, full moon hero |
| `heic0506a.jpg` | Crab Nebula (supernova remnant) — 41 MB | Death/rebirth, eclipse seasons, Pluto retrograde |
| `opo0501a.jpg` | Helix Nebula ("Eye of God") | Soul Map Snapshot landing hero, Neptune themes |
| `heic1118a.jpg` | Cat's Eye Nebula | Mercury, mind, perception |
| `heic0716a.jpg` | Antennae Galaxies (collision) | Relationship transits, Venus aspects |
| `heic0506b.jpg` | Crab variant | secondary |
| `heic1502b.jpg` | Veil Nebula (?) | Saturn/structure, slow transformation |
| `heic0817a.jpg` | tbd | secondary |
| `potw2014a.jpg` | picture of the week 2014 | secondary |
| `heic1118b.jpg` | Cat's Eye variant | secondary |

## License
All images are **public domain** under NASA/ESA Hubble image release policy. No attribution required for commercial use, but credit "ESA/Hubble & NASA" when convenient.

Source: https://esahubble.org/copyright/

## Usage
Drop into template_d_carousel_hook.html via:
```html
<body style="background-image: url('../brand/cosmic/heic0910e.jpg');">
```
Add overlay for legibility:
```css
body::after { content:''; position:absolute; inset:0; background:rgba(20,18,43,0.72); }
```
