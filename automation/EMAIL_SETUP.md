# Email notifications setup — soul.orbits

When a Reel auto-publishes, you get an email at **hugo.ribeiro@hvr.pt** reminding you to open IG and attach trending audio. 30s in IG = 5–10× more reach.

## One-time setup (3 minutes)

### 1. Create a Resend account (free, 100 emails/day)

1. Go to https://resend.com and sign up (Google login is fine)
2. Skip domain verification — we use the sandbox sender `onboarding@resend.dev` (works immediately for transactional alerts; only required if you wanted to send marketing email from your own domain)
3. Go to **API Keys** → **Create API Key** → name it `soul-orbits` → permission **Sending access** → **Create**
4. **Copy the key** (starts with `re_...`) — you only see it once

### 2. Add secrets to GitHub

Go to: https://github.com/yugoribeiro-dot/soul.orbits/settings/secrets/actions

Add three repository secrets:

| Name | Value |
|---|---|
| `RESEND_API_KEY` | the `re_...` key from step 1 |
| `EMAIL_TO` | `hugo.ribeiro@hvr.pt` |
| `EMAIL_FROM` | `soul.orbits <onboarding@resend.dev>` (or leave unset — code defaults to this) |

Save. Done.

## Test it

Local test (after putting the values in `.env`):
```bash
cd ~/soul-orbits
set -a && source .env && set +a
python -c "from automation.notify_email import reel_published; reel_published('test123')"
```

Should arrive at hugo.ribeiro@hvr.pt within seconds. Check the spam folder the first time — Gmail/Outlook may quarantine the first email from a new sender.

## What you'll receive

Every Reel publish triggers an email styled in the brand colors (deep cosmos + gold), with a one-tap **OPEN REEL →** button to jump straight to Instagram.

## Use your own domain (optional, later)

When you want emails to come from `notify@soulorbits.com` or similar:
1. In Resend → **Domains** → add `soulorbits.com`
2. Copy the DNS records (SPF, DKIM, MX) into your domain registrar
3. Once verified, set `EMAIL_FROM=soul.orbits <notify@soulorbits.com>`

Not needed for the alert workflow — sandbox sender works fine.
