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
- ~~Turn on GitHub Pages~~ and ~~Step 2: add AI~~ (done in session 2).

## Session 2 — 15 Nov 2026: Step 2, the AI brain

### Done
- `scripts/ai_cluster.py` sends NEW stories to the AI (OpenRouter, model `anthropic/claude-haiku-5.5`).
  The AI groups stories about the same event into cards. A new story can join a card from the
  last 48 hours. On the very first run only the last 48 hours are grouped.
- Each card has an AI title, a 2-sentence summary, all source links, a "sources disagree" note
  (only when they do), and the AI's reason for each merge. Close calls it kept apart are saved too.
- One-sentence "headline of the day" (Malaysia date).
- Saved in `data/cards.json`. `data/news.json` is unchanged.
- `news.html` now has two views: "Top stories (AI)" and "All stories" (the old view, with filters).
  The "Why did the AI group these?" box shows the reasons.
- The workflow runs the AI step with the key from GitHub Secrets (`OPENROUTER_API_KEY`).
- Safety: no key → AI skipped; AI error → those stories are retried next run; the news still updates.

### Tested (on 67 stories from the last 48 hours)
- First try merged two things wrongly: two RaceFans "On This Day" pieces about different Brazil
  races, and two different people's opinions about Ferrari. Added rules for history pieces,
  opinions, and stories from the same website. Second try: 6 correct merges, and both wrong
  ones were kept apart with clear reasons.
- Re-run with no new stories: no AI call, file unchanged.
- A "late" story correctly joined an existing card (McLaren Las Vegas upgrade).
- No key: AI step skipped politely.
- Headline of the day first mentioned "websites"; fixed the rule so it only talks about F1 news.
- Page checked on a phone: both views, badges, reasons box, no sideways scroll, no errors.
  Without `cards.json` the page falls back to "All stories".

### Cost
- First run (67 stories): $0.009. A normal 2-hour run: about $0.001–0.003.
  Roughly $0.02–0.04 per day (~$1/month). The OpenRouter key has a $5 limit.

### Things to know
- The AI can still make mistakes. Check the "Why did the AI group these?" reasons now and then.
- Test data was not committed; the robot creates `data/cards.json` on its first run after merging.

### Next ideas
- Watch a few days of cards and adjust the rules if merges look wrong.
- Maybe: show the "kept separate" decisions on a small "AI log" page.
