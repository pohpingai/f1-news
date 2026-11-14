# F1 News Daily

A simple website that collects Formula 1 news from 8 sources every 2 hours.

- **The page:** `news.html` (the home page `index.html` forwards to it)
- **The data:** `data/news.json`
- **The collector:** `scripts/fetch_news.py`
- **The robot that runs it every 2 hours:** `.github/workflows/fetch-news.yml`

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
