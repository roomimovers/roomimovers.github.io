# Turning on live AI answers (about 15 minutes)

The chat on roomimovers.com already works without this. It answers questions from the business facts
and takes estimate requests, which are emailed to roomimovers@gmail.com.

This setup adds **live AI answers** for the questions the fact sheet does not cover. The chat sends the
visitor's recent messages to a small relay that you own. The relay holds your Anthropic key, so the key is never
in the website.

## What you need

1. An Anthropic account: https://console.anthropic.com (add a card, then create an API key under **API keys**).
2. A free Cloudflare account: https://dash.cloudflare.com/sign-up
3. Node.js (the LTS version): https://nodejs.org

## Steps

Open a terminal in this folder (`_tools/ai-relay`) and run these one at a time.

```bash
npm install
npx wrangler login
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler deploy
```

- `secret put` asks you to paste the key. It is stored by Cloudflare and never written to a file.
- `deploy` prints a web address ending in `workers.dev`. Copy it.

Then, in `_tools/business.json`, set:

```json
"chat": { "enabled": true, "ai_endpoint": "https://roomi-assistant.YOURNAME.workers.dev" }
```

Rebuild and publish the site:

```bash
py _tools/build_pages.py
```

Commit and push as usual. Open the live site, open the chat, ask something unusual such as
"do you do junk removal?" and confirm you get a short, sensible answer.

## Protect your spend (do this first)

1. In the Anthropic console, **Settings, Limits**: set a monthly spend limit (for example $20). The key stops
   working at the limit, so the worst case is capped.
2. In Cloudflare, **Security, WAF, Rate limiting rules**: add a rule for the relay's address, for example
   "more than 30 requests per 10 minutes from one IP, block for 10 minutes".
3. Optional daily cap: `npx wrangler kv namespace create RATE_KV`, paste the id into `wrangler.toml`
   (the commented block), set `DAILY_CAP`, then `npx wrangler deploy`.

The relay already refuses other websites, caps message size and length, keeps replies short, and rate limits
each visitor. It stores no conversations.

## Cost and model

`wrangler.toml` has `MODEL`. Two good choices:

| Model | Good for | Rough cost |
|---|---|---|
| `claude-opus-5-5` (default) | the most careful answers | about $0.01 per reply |
| `claude-haiku-5-5` | fast, plain FAQ answers | about $0.0003 per reply |

For a moving company's questions, Haiku is usually plenty. Change the line, then run `npx wrangler deploy`.
Check current pricing at https://www.anthropic.com/pricing.

## When your business facts change

The assistant's instructions are generated from `business.json` (rates, hours, license status, areas, FAQ).
After you change anything there:

```bash
py _tools/build_pages.py
cd _tools/ai-relay
npx wrangler deploy
```

That keeps the AI from quoting old rates and keeps it from saying you are licensed before the
registration number is entered.

## Turning it off

Set `"ai_endpoint": null` in `business.json`, rebuild and push. The chat keeps working from the fact sheet.
