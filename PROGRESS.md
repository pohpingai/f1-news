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

## Session 3 — 15 Nov 2026: card polish

### Done
- Merged cards stand out: a bigger "3 sources" badge and a red stripe down the left side.
  (If one website has two stories in a card, the badge says "2 stories" instead.)
- Inside each day, merged cards come first (most sources at the top), then the rest, newest first.
- The AI's merge reason now sits behind a small "Why grouped?" button on each merged card.
  Tap to open, tap again to close.

### Tested
- With the real cards from the live site (60 cards, 6 merged), on a phone-sized screen:
  merged cards always come before single cards in the same day; 6 badges and 6 "Why grouped?"
  buttons; the reason is hidden until tapped and hides again on a second tap; no sideways
  scrolling; "All stories" view unchanged (247 stories); no errors.
- The live robot run after Step 2 worked: it created `data/cards.json` with the key from GitHub Secrets.

### Next ideas
- Watch a few days of cards and adjust the AI rules if merges look wrong.
- Maybe: show the "kept separate" decisions on a small "AI log" page.

## Session 4 — 15 Nov 2026: labels + rumour tracker

### Done
- Every card now has a label: **Confirmed**, **Rumour** or **Opinion**, shown as a coloured tag.
  The label is decided in the same AI request that groups stories. Cards without a label (older
  cards, or AI slips) get one in a small "catch-up" request.
- New `scripts/rumour_tracker.py` with its memory in `data/rumours.json`. Each rumour has: claim,
  people/teams, first seen, last seen, all sources with dates, status, trend, proof, and history.
- Each run, new Rumour cards are matched to a known rumour (update) or added as new.
  New Confirmed cards are checked as possible proof that confirms or denies an open rumour.
- Safety lock: Confirmed / Denied only if the proof card is labelled Confirmed AND the AI's
  evidence words are found word-for-word in that card. Otherwise the change is "blocked" and logged.
- Trend (rising / steady / fading) and Faded (14 days quiet) are worked out by plain code.
- New "Rumours" tab: Active first (rising first), trend arrows, source count, first/last seen,
  "Sources" and "History" buttons; confirmed rumours show the official proof and link.
- The robot runs the tracker after the AI brain. Scripts accept `F1_DATA_DIR` for safe tests.

### Tested
- Labels on today's 63 cards: 34 Confirmed, 2 Rumour, 27 Opinion. First try put some features
  under Confirmed/Rumour; made the rule clearer ("features, history pieces, explainers, lists are
  Opinion even when they contain facts") and re-labelled.
- Real rumours found: the FIA president's planned presidency-rule change, and the "ADUO for teams"
  cost-cap plan to be discussed at the F1 Commission. No Confirmed card was wrongly used as proof.
- TEST ONLY (scratch copy, not on the live site): a fake official FIA announcement turned the
  presidency-rule rumour into Confirmed, with the proof and reason saved. A fake "set to be
  approved, sources say" report only added a source to the cost-cap rumour (stayed Active).
- Safety lock: 3 fake cheating attempts were all blocked (invented words, proof card only a Rumour,
  no evidence); the honest case passed.
- Plain-code rules: +6 days → trend "fading"; +15 days → Active becomes Faded. Re-run with nothing
  new: no AI call. No key: skipped.
- AI reasons first mentioned internal codes like "R1"; told the AI to describe things in words.
- Page on a phone: labels, Rumours tab, Sources/History buttons, no sideways scroll, no errors;
  without `rumours.json` the tab says "No rumours tracked yet".

### Cost
- Rumour tracker: about $0.0005–0.001 per run when there are new rumour/confirmed cards.
- One-time catch-up labelling of old cards: about $0.002.
- All AI steps together: roughly $0.03–0.05 per day (~$1–1.50 a month).

### Things to know
- Labels are AI judgments and can be wrong now and then (e.g. a quote-based feature as Confirmed).
- It is a quiet news week, so only 2 rumours so far; expect more during driver-market season.
- The tracker only sees cards from the last 48 hours on its first run.

### Next ideas
- Watch the labels and rumours for a few days and adjust the rules.
- Maybe: a link from a Rumour card to its entry in the Rumours tab.
