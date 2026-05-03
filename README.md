# soul.orbits

Evolutionary astrology Instagram, automated.

## Project structure
- `brand/` — positioning, brand kit, content pillars, templates, calendars (Phase 0 ✅)
- `content/` — generated posts, organized by week (Phase 1)
- `templates/` — reusable image templates (HTML/SVG to render via gpt-image-2 or Canva API) (Phase 1)
- `automation/` — cron job + Postiz/Rube integration scripts (Phase 3)

## Phase status
- [x] **Phase 0** — Foundations (brand, voice, pillars, templates, week 1 calendar)
- [x] **Phase 1** — Copy + images for 6 static posts (Wed reel pending)
- [x] **Phase 2** — Render pipeline (HTML templates + Playwright batch render)
- [~] **Phase 3** — Meta Graph API + GitHub Actions cron (code ready; awaiting Meta app setup, see [automation/SETUP.md](automation/SETUP.md))
- [ ] **Phase 4** — Add Reel pipeline (Remotion)

## Quick links
- [Positioning](brand/01-positioning.md)
- [Brand Kit](brand/02-brand-kit.md)
- [Content Pillars](brand/03-content-pillars.md)
- [Post Templates](brand/04-post-templates.md)
- [Week 1 Calendar](brand/05-week-1-calendar.md)
