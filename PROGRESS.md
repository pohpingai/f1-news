# Progress log

## Session 1 — 14 Nov 2026: Step 1, the basic news site (no AI yet)

### Done
- Created `CLAUDE.md` (my working rules) and this `PROGRESS.md`.
- `scripts/fetch_news.py` collects news from 8 RSS feeds:
  Formula1.com, Autosport, Motorsport.com, The Race (only stories tagged "Formula 1"),
  RaceFans, BBC Sport, PlanetF1, Crash.net.
- Saves headline, source, date, link and a ~200-character snippet to `data/news.json`.
  - The link is the ID, so no duplicates.
  - Stories older than 30 days are deleted (and never added in the first place).
  - Formula1.com has no dates, so we save the time we first saw the story ("seen at").
  - The file is only rewritten when something changed.
- `news.html` shows the news, newest first, grouped by day in Malaysia time,
  with buttons to filter by source. Works on phones and in dark mode.
  `index.html` forwards visitors to `news.html`.
- `.github/workflows/fetch-news.yml` runs the collector every 2 hours on GitHub
  (and has a "Run workflow" button for running it by hand).

### Tested
- Ran the collector: 246 stories from all 8 feeds. Second run: 0 new, file unchanged.
- Added a fake 45-day-old story: it was deleted.
- Opened the page in a phone-sized and desktop browser: grouped by day, Malaysia time
  correct, source filter works, no sideways scrolling, no errors.

### Things to know
- PlanetF1's feed address is `https://www.planetf1.com/rss` (`/feed` gives an error).
- Autosport and Motorsport.com have the same owner, so the same story can appear twice
  with different links. That is expected for now.
- On the very first run, all Formula1.com stories get the same "seen at" time.
- GitHub can start the 2-hour job a few minutes late. That is normal.

### Next ideas
- Turn on GitHub Pages (see README).
- Step 2: maybe add AI (for example, a daily summary or merging duplicate stories).
