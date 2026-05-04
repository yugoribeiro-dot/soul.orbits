# Telegram notifications setup — soul.orbits

When a Reel auto-publishes, you get a Telegram message reminding you to open IG and attach trending audio (5-10x more reach than custom/no audio).

## One-time setup (3 minutes)

### 1. Create the bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Pick a name: `soul orbits bot`
4. Pick a username ending in `bot`: e.g. `soul_orbits_alerts_bot`
5. BotFather replies with a token like `7891234567:AAEa...zX9q` — **copy it**

### 2. Get your chat ID

1. In Telegram, search for **@userinfobot**
2. Tap **Start** — it replies with your numeric ID, e.g. `123456789` — **copy it**
3. Open a DM with the bot you just created and send any message (e.g. "hi") — this is required so the bot can send you messages

### 3. Add secrets to GitHub

Go to: `https://github.com/yugoribeiro-dot/soul.orbits/settings/secrets/actions`

Add two new repository secrets:

| Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | the token from step 1 |
| `TELEGRAM_CHAT_ID` | your numeric ID from step 2 |

Save. Done.

## Test it

Local test (after putting them in `.env`):
```bash
cd ~/soul-orbits
set -a && source .env && set +a
python automation/notify_telegram.py "test from soul.orbits"
```

You should get the message in Telegram within 1-2 seconds.

If it fails: check the bot username and that you sent it a "hi" message in step 2.

## What you'll receive

Every time a Reel auto-publishes, you get:

> 🎬 **Reel published — soul.orbits**
>
> 👉 **Open Instagram now** (next 60 min for max reach)
> 1. Tap the Reel you just posted
> 2. Edit → Add audio → search trending
> 3. Pick something matching the vibe (cosmic/dark/punchy)
> 4. Save
>
> Trending audio = 5-10x more reach.
>
> https://www.instagram.com/reel/<id>/

Tap the link, attach trending audio, save. ~30 seconds.

## Carousels notify too?

Currently only Reels trigger the notification (since carousels don't benefit from trending audio). If you want a daily "post is live" ping for everything, edit `automation/publish_today.py` and remove the `if data.get("template") == "reel"` guard.
