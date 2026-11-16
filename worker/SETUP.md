# Setting up the Ask tab (about 15 minutes, free)

The Ask tab needs a small "middleman" program that holds your OpenRouter key, so the key is
never in the website or the browser. It runs on **Cloudflare Workers** (free plan: 100,000
requests a day, far more than you need).

```
Your phone/browser  ──question + passcode──▶  Cloudflare Worker (holds the key)  ──▶  OpenRouter AI
        ▲                                              │
        └──────────── answer, steps, sources ◀─────────┘   (reads your saved news from GitHub Pages)
```

---

## Step 1 — Make a separate OpenRouter key just for chatting (2 min)

A separate key means the chat can never use up the robot's money, and you can see the chat's
spending on its own.

1. Go to **https://openrouter.ai/settings/keys** and click **Create Key**.
2. Name: `f1-news-ask`.
3. **Credit limit:** type `1` (one dollar). If you see a **reset** option, choose **Daily** and use `0.20` instead.
4. Click **Create** and **copy the key** (starts with `sk-or-`). You only see it once.
   Keep it in a safe place for Step 4 — do **not** paste it into the website, GitHub or a chat.

## Step 2 — Create a free Cloudflare account (3 min)

1. Go to **https://dash.cloudflare.com/sign-up** and sign up (free plan; no credit card needed).
2. Confirm your email.

## Step 3 — Create the Worker and paste the code (4 min)

1. In the Cloudflare dashboard, in the left menu click **Compute (Workers)** → **Workers & Pages**
   (the name may be slightly different), then **Create** → **Create Worker** (or "Start with Hello World").
2. Name it `f1-news-ask` and click **Deploy**. (It deploys a "Hello World" example first — that's fine.)
3. Click **Edit code**.
4. Delete everything in the editor. Open this file on GitHub:
   **https://github.com/pohpingai/f1-news/blob/main/worker/ask-worker.js**, click the **Copy raw file** button
   (two squares icon), and paste it into the Cloudflare editor.
5. Click **Deploy** (top right).
6. Copy your Worker's address. It looks like **`https://f1-news-ask.YOUR-NAME.workers.dev`**.
   Open it in a new tab: you should see `{"ok":true,"message":"F1 News Ask is running."}`.

## Step 4 — Add the two secrets (3 min)

1. Go back to your Worker's page → **Settings** → **Variables and Secrets** → **Add**.
2. Add the first one:
   - Type: **Secret**
   - Name: `OPENROUTER_API_KEY`
   - Value: paste the `f1-news-ask` key from Step 1
3. Click **Add** again for the second one:
   - Type: **Secret**
   - Name: `ASK_PASSCODE`
   - Value: your chat passcode. Make it long and easy to remember, e.g. four random words like
     `purple-tyre-monsoon-teapot`. Anyone with this passcode can chat (and spend up to the daily limit).
4. Click **Deploy** / **Save**.

*Optional* (only if you want to change the defaults) — add these as type **Text**:

| Name | Default | What it does |
|---|---|---|
| `DAILY_LIMIT_USD` | `0.20` | The Worker refuses questions once the chat key has spent this much today |
| `SITE_URL` | `https://pohpingai.github.io/f1-news/` | Where the Worker reads your saved news |
| `ALLOWED_ORIGINS` | `https://pohpingai.github.io` | Which website may talk to the Worker |
| `MODEL` | `anthropic/claude-haiku-5.5` | The AI model |

## Step 5 — Connect your phone/browser (1 min)

1. Open **https://pohpingai.github.io/f1-news/** → tap **Ask**.
2. Paste the Worker address from Step 3 and type your passcode → **Save**.
3. Tap **Catch me up (last 7 days)**. After a few seconds you should see the thinking steps, the answer and its sources.

The address and passcode are saved only in that browser. On another phone, do Step 5 again.
To remove them, tap **Disconnect this device**.

---

## The Stats agent (`/stats`, added in Stage 3)

The same Worker has a second address: **`https://f1-news-ask.YOUR-NAME.workers.dev/stats`**.
It uses the same passcode, the same daily limit and the same chat key. The AI there has one tool,
`get_standings`, which reads `data/stats.json` from the website (saved by the stats robot every 6 hours).

- Quick check: open the `/stats` address in a browser → `{"ok":true,"message":"F1 News Stats is running."}`
- Try it: open **https://pohpingai.github.io/f1-news/stats-test.html** (it uses the Worker address and
  passcode saved by the Ask tab in that browser).
- Logs: Cloudflare → your Worker → **Logs** shows lines starting with `[stats]` for every tool-loop step.

## Updating the Worker after a code change (Wrangler)

`worker/wrangler.toml` keeps the deploy settings (logs on, preview links off, date 2026-11-15), so a
deploy doesn't reset them. From the `worker` folder, with a Cloudflare API token set:

```bash
npx wrangler deploy
```

The secrets are never in this file and are not changed by a deploy.

## If something goes wrong

| You see | What to do |
|---|---|
| "The Worker is not set up yet" | One of the two secrets in Step 4 is missing or misspelled |
| "Wrong passcode" | Retype it; it must match `ASK_PASSCODE` exactly |
| "Could not reach the Worker" | Check the address (must start with `https://` and end with `.workers.dev`) |
| "Daily limit reached" | The chat spent its daily limit; it works again tomorrow (UTC) |
| "OpenRouter said 401" | The key in `OPENROUTER_API_KEY` is wrong or deleted |
| "OpenRouter said 402" | The chat key hit its credit limit; raise it on openrouter.ai |

## Changing the passcode or key later
Cloudflare → your Worker → Settings → Variables and Secrets → edit the secret → Deploy.
Then do Step 5 again on your devices.

## Updating the Worker code later
When `worker/ask-worker.js` changes on GitHub, repeat Step 3, points 3–5 (paste the new code, Deploy).
