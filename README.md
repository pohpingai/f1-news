# F1 News Daily

A simple website that collects Formula 1 news from 12 sources every 2 hours:
Formula1.com, Autosport, Motorsport.com, The Race, RaceFans, BBC Sport, PlanetF1, Crash.net,
GPFans, Sky Sports, ESPN and the FIA (F1 items only).

To test possible new feeds: `python scripts/check_feeds.py` (or on GitHub: Actions → "Check new feeds" → Run workflow).

- **The page:** `news.html` (the home page `index.html` forwards to it)
- **The data:** `data/news.json`
- **The collector:** `scripts/fetch_news.py`
- **The AI brain:** `scripts/ai_cluster.py` → `data/cards.json`
- **The Ask chat's middleman (Cloudflare Worker):** `worker/ask-worker.js` — setup in `worker/SETUP.md`
- **The rumour tracker:** `scripts/rumour_tracker.py` → `data/rumours.json`
- **The robot that runs all of them every 2 hours:** `.github/workflows/fetch-news.yml`

## The AI brain

After collecting, the AI (Claude Haiku 5.5 via OpenRouter) groups stories about the same event
into one card with a title, a 2-sentence summary, all source links, a note if sources disagree,
and the reason it merged them. It also writes a "headline of the day".
Every card is labelled **Confirmed** (official news), **Reported** (on-the-record quotes),
**Rumour** or **Opinion**.

The **Ask** tab is a chat that answers only from the saved news and rumours, with links to the
sources and the thinking steps shown above each answer. It goes through a free Cloudflare Worker
that keeps the OpenRouter key secret, checks a passcode and stops at a daily spending limit.
See `worker/SETUP.md`.

The **rumour tracker** remembers rumours across days: the claim, who is involved, first/last seen,
all sources, status (Active / Confirmed / Denied / Faded) and trend (rising / steady / fading),
with a history of every change and the AI's reason. A rumour only becomes Confirmed when an
official source says so (checked word-for-word by the code).

All the AI steps together cost roughly $0.02–0.05 per day. The real cost of every AI request is
logged per feature in `data/costs.json` and shown on the **💰 AI costs** page (`costs.html`).
`COSTS.md` is the keep-or-drop sheet with the money spent so far.

The key is stored in GitHub: **Settings → Secrets and variables → Actions → `OPENROUTER_API_KEY`**.
To run the AI on your own computer, set the key first (never save it in a file in this repo):

```bash
export OPENROUTER_API_KEY=your-key-here
python scripts/ai_cluster.py
```

## Report card (tests)

One command checks that the AI parts behave: grouping, labels, the rumour safety lock and the
Ask tab (18 tests with made-up test news — your real `data/` is never touched):

```bash
OPENROUTER_API_KEY=your-key python tests/report_card.py
```

It prints PASS/FAIL for each test with the reason, a score (e.g. 18/18) and the cost of the run
(about $0.004). Add `--save` to write the result to `tests/LAST_REPORT.md`.
It also needs Node.js (for the Ask tests).

## Run it on your own computer

```bash
pip install -r requirements.txt
python scripts/fetch_news.py
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Turn on the website (GitHub Pages)

1. On GitHub, open the repository → **Settings** → **Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Choose branch **main** and folder **/ (root)**, then **Save**.
4. After a minute or two the site is live at `https://<your-username>.github.io/<repo-name>/`.
