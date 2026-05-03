# soul.orbits — Meta Graph API Setup

One-time setup to publish to Instagram automatically. Estimated time: **30–45 minutes** with Claude in Chrome driving.

## Prerequisites checklist

- [ ] **Instagram account @soul.orbits exists**
- [ ] **Account type is Business or Creator** (not Personal)
- [ ] **Connected Facebook Page** (any FB Page; can be private/empty)
- [ ] **Meta Developer account** at [developers.facebook.com](https://developers.facebook.com)
- [ ] **GitHub repository** for soul.orbits (we'll push the code)

If any of the first 4 are missing, do them first (instructions below).

---

## Step 1 — Convert IG to Business or Creator (skip if already done)

Open the Instagram app on phone:
1. Profile → ☰ menu → Settings and privacy
2. For professionals → Account type and tools → **Switch to professional**
3. Choose **Creator** (recommended for soul.orbits — solopreneur, content-led)
4. Pick category: **Digital creator** or **Astrologer**
5. Skip the contact step

Free, ~3 minutes. Reverts anytime.

## Step 2 — Create Facebook Page (skip if you have one to use)

1. [facebook.com/pages/create](https://www.facebook.com/pages/create)
2. Page name: `soul.orbits` (or anything — won't be used publicly)
3. Category: `Astrologer` or `Personal Blog`
4. Skip the rest, leave it empty/private

The Page is required by Meta as a "container" for IG Business assets. It's a quirk, not a feature.

## Step 3 — Connect IG to Facebook Page

In Instagram app:
1. Profile → Edit profile → **Page**
2. Connect the Facebook Page you created

OR via Facebook web:
1. Go to your Page → Settings → **Linked Accounts** → Instagram → connect

## Step 4 — Create Meta Developer App

1. [developers.facebook.com](https://developers.facebook.com) → Log in with your FB account
2. Click **My Apps** → **Create App**
3. Use case: **Other**
4. App type: **Business**
5. App name: `soul-orbits-publisher`
6. Contact email: your email
7. Business portfolio: skip or create new

## Step 5 — Add Instagram Graph API

1. In your new app's dashboard → **Add product**
2. Find **Instagram** → click **Set up**
3. Find **Facebook Login for Business** → click **Set up**

## Step 6 — Configure permissions and get token

This step is the trickiest. Use the **Graph API Explorer**:

1. [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Select your app from dropdown (top right)
3. Click **Generate Access Token**
4. Permissions to grant (check these boxes):
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `business_management`
5. Click **Generate Access Token** → log in if prompted → grant
6. Copy the **short-lived** token shown (valid ~1 hour)

## Step 7 — Exchange for long-lived token (60 days)

In a terminal, replace `<APP_ID>`, `<APP_SECRET>`, `<SHORT_TOKEN>`:

```bash
curl -G "https://graph.facebook.com/v21.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=<APP_ID>" \
  -d "client_secret=<APP_SECRET>" \
  -d "fb_exchange_token=<SHORT_TOKEN>"
```

Response:
```json
{"access_token":"EAAG...","token_type":"bearer","expires_in":5183944}
```

Save the new `access_token` — this is your **long-lived token**.

## Step 8 — Find your IG User ID

```bash
# 1. Get your FB Page ID from this:
curl "https://graph.facebook.com/v21.0/me/accounts?access_token=<LONG_TOKEN>"

# 2. With the page_id from above, get the IG account ID:
curl "https://graph.facebook.com/v21.0/<PAGE_ID>?fields=instagram_business_account&access_token=<LONG_TOKEN>"
```

The `instagram_business_account.id` is your **`IG_USER_ID`**.

## Step 9 — Save credentials in GitHub

In your soul-orbits GitHub repo:
1. Settings → Secrets and variables → Actions → **New repository secret**
2. Add three secrets:
   - `META_ACCESS_TOKEN` → the long-lived token
   - `IG_USER_ID` → from Step 8
   - `META_APP_ID` and `META_APP_SECRET` (for the monthly token refresh)

## Step 10 — Test publish

Locally (with PowerShell):

```powershell
$env:META_ACCESS_TOKEN = "EAAG..."
$env:IG_USER_ID = "1789..."
$env:IMAGE_BASE_URL = "https://raw.githubusercontent.com/<you>/soul-orbits/main/content/week-01"
python automation/publish.py content/week-01/01-mon-mercury-sagittarius.yaml
```

If success: a media_id prints and the post appears on @soul.orbits.

## Step 11 — Activate the daily cron

Push the repo to GitHub. The workflow `.github/workflows/publish-daily.yml` runs at 09:00 UTC daily and publishes whatever `content/schedule.yaml` says is scheduled for that date.

To trigger manually for testing: GitHub repo → Actions → publish-daily → **Run workflow**.

---

## Token expiry handling

Long-lived tokens expire in ~60 days. Set a reminder for day 50. Refresh:

```bash
META_APP_ID=... META_APP_SECRET=... META_ACCESS_TOKEN=<old> \
  python automation/refresh_token.py
```

Update the `META_ACCESS_TOKEN` GitHub secret with the new value.

(A separate workflow `refresh_token.yml` can do this monthly automatically — TODO.)

---

## Troubleshooting

- **"The image is invalid"** → image URL is not publicly fetchable. Check `IMAGE_BASE_URL` and that the file exists on the branch you're using.
- **"Application does not have permission"** → permissions in Step 6 not granted, or app is in Development mode (it's fine for personal use; submit for review only if you want others to use it).
- **"Media ID is invalid for publishing"** → the container wasn't FINISHED yet. The script polls but if it's still failing, increase `max_wait_s` in `publish.py`.
- **Carousel fails** → Meta requires all carousel images to be reachable AND all <8MB AND aspect ratio between 4:5 and 1.91:1. Our 1080×1350 (4:5) is at the edge — fine, but verify.
