# F1 News Daily

A simple website that collects Formula 1 news from 8 sources every 2 hours.

- **The page:** `news.html` (the home page `index.html` forwards to it)
- **The data:** `data/news.json`
- **The collector:** `scripts/fetch_news.py`
- **The AI brain:** `scripts/ai_cluster.py` → `data/cards.json`
- **The robot that runs both every 2 hours:** `.github/workflows/fetch-news.yml`

## The AI brain

After collecting, the AI (Claude Haiku 5.5 via OpenRouter) groups stories about the same event
into one card with a title, a 2-sentence summary, all source links, a note if sources disagree,
and the reason it merged them. It also writes a "headline of the day".
It costs roughly $0.02–0.04 per day.

The key is stored in GitHub: **Settings → Secrets and variables → Actions → `OPENROUTER_API_KEY`**.
To run the AI on your own computer, set the key first (never save it in a file in this repo):

```bash
export OPENROUTER_API_KEY=your-key-here
python scripts/ai_cluster.py
```

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
