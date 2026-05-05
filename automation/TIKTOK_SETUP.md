# TikTok cross-post setup — soul.orbits

Auto-pushes every IG post (carousel + Reel) to your TikTok drafts. You open the app, pick trending sound, tap Post. ~60 seconds per post.

Why TikTok matters for soul.orbits: TikTok gives organic reach to brand-new accounts (IG doesn't). Astrologia in PT/BR has massive audience there. 0→5k in 3-4 weeks is realistic if posting consistently with trending sounds.

## One-time setup (10 minutes)

### 1. Create TikTok account (if you don't have one)

Go to tiktok.com → sign up as **@soul.orbits** (or matching handle).

### 2. Create the developer app

1. Go to https://developers.tiktok.com/
2. Log in with the @soul.orbits TikTok account
3. **Manage apps → Create app**
4. App name: `soul.orbits cross-post`
5. App description: anything sensible
6. Category: **Lifestyle** (closest match for astrology)
7. Save

### 3. Configure the app

Inside the app:

**Add product → Login Kit**

**Add product → Content Posting API**

**App settings → URL Properties → Redirect URI:**
```
http://localhost:7321/callback
```

**App settings → Scopes — request:**
- `user.info.basic`
- `video.upload`
- `video.publish`

(scope approval is automatic for these — no Meta-style review)

**App settings → Domain ownership:**
- Add `raw.githubusercontent.com` as a verified URL prefix
- TikTok requires meta-tag verification on the domain — for raw.githubusercontent.com this works because the file you upload IS served from that host. Follow the on-screen verification steps. If it fails, fall back to using TikTok's PULL_FROM_URL with a verifiable domain (or skip photo carousels and only do Reels — which use FILE_UPLOAD without domain verification).

**Copy from Basic info:**
- Client Key
- Client Secret

### 4. Generate access + refresh tokens

```bash
cd ~/soul-orbits

# add to .env
echo "TIKTOK_CLIENT_KEY=<your-client-key>" >> .env
echo "TIKTOK_CLIENT_SECRET=<your-client-secret>" >> .env

# run the OAuth flow — opens browser
python automation/tiktok_setup.py
```

Browser opens → log in to @soul.orbits TikTok → Authorize.

The script prints `TIKTOK_ACCESS_TOKEN` (24h) and `TIKTOK_REFRESH_TOKEN` (~1y).

### 5. Add secrets to GitHub

Go to: https://github.com/yugoribeiro-dot/soul.orbits/settings/secrets/actions

| Name | Value |
|---|---|
| `TIKTOK_CLIENT_KEY` | from step 3 |
| `TIKTOK_CLIENT_SECRET` | from step 3 |
| `TIKTOK_REFRESH_TOKEN` | from step 4 |

(`TIKTOK_ACCESS_TOKEN` not needed in CI — auto-refreshed every run)

### 6. Test locally

```bash
set -a && source .env && set +a
export REPO_RAW_BASE_URL=https://raw.githubusercontent.com/yugoribeiro-dot/soul.orbits/main
python automation/cross_post_tiktok.py content/week-01-real/01R-mon-may4-mars-jupiter-reel.yaml
```

Open TikTok app → Profile → drafts. The video should be there within ~30s.

## How it works going forward

Each successful IG publish triggers:
1. `cross_post_tiktok.py` is called automatically
2. For Reels → MP4 uploaded via FILE_UPLOAD → drafts
3. For carousels → 7 slides uploaded as Photo Mode → drafts
4. Failure here is **non-fatal** to the IG publish (try/except wrap)

## Manual workflow each post

1. Get notification (email or just check TikTok)
2. Open TikTok → drafts
3. Tap the draft
4. **Add sound** → trending tab → pick something cosmic/dark/punchy
5. Caption is pre-filled, hashtags too
6. Post

Time: ~60 seconds.

## Troubleshooting

**"refresh token expired"** → re-run `tiktok_setup.py` and update GH secret.

**Photo carousel fails with "domain not verified"** → TikTok requires you to verify ownership of the host serving photos. For raw.githubusercontent.com:
- Option 1: verify via meta-tag (TikTok shows you the tag — but you can't add to GitHub raw)
- Option 2: serve photos from your own verified domain (e.g. `images.soulorbits.com` proxied to GitHub)
- Option 3: only auto-cross-post Reels (videos use FILE_UPLOAD, no domain verification needed). Photo carousels stay IG-only.

If domain verification is a blocker, we can fall back to Reels-only cross-post by setting `TIKTOK_PHOTOS_DISABLED=true` env (not yet implemented; ask if you need this).

**Token rotated mid-run** → script prints a warning. Update `TIKTOK_REFRESH_TOKEN` in GH secrets when you see this.
