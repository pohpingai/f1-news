# Progress log

## ⭐ Start here — project summary (as of 17 Nov 2026)

*Read this first in a new thread. The session-by-session log follows below it.*

### What it is
A free website that collects F1 news every 2 hours, groups the same story from different sites,
labels each story, tracks rumours, keeps the championship standings, and has a private chat
that answers only from the saved news.
- **Live site:** https://pohpingai.github.io/f1-news/ · **Code:** https://github.com/pohpingai/f1-news
  (GitHub Pages serves the site from `main`).
- **Working style (CLAUDE.md):** beginner, simple words, plan first, small steps, test before
  saying it works, update PROGRESS.md and COSTS.md every session.

### How it works (robots on GitHub, results saved in `data/`)
| Robot | File | What it does | Saves |
|---|---|---|---|
| News, every 2 h (`fetch-news.yml`) | `scripts/fetch_news.py` | Reads 13 RSS feeds; headline, source, date, link, ~200-char snippet; link = ID; deletes stories older than 30 days | `data/news.json` |
| | `scripts/ai_cluster.py` | AI brain: groups the same story into cards (title, 2-sentence summary, "sources disagree" note, merge reason), labels every card, writes the headline of the day | `data/cards.json` |
| | `scripts/rumour_tracker.py` | AI memory of rumours: claim, people, sources, status, trend, history | `data/rumours.json` |
| Stats, every 6 h at :30 (`fetch-stats.yml`) | `scripts/fetch_stats.py` | No AI. Free **Jolpica F1 API** (`api.jolpi.ca`): driver + constructor standings and all race results; ~7 requests per run | `data/stats.json` |
| Every AI request | `ask_ai(..., feature=...)` | Logs the real cost per feature per day | `data/costs.json` → `costs.html` |

### News sources (12 sources, 13 feeds)
- Formula1.com (no dates → "seen at"), Autosport, Motorsport.com, The Race (F1 tag only), RaceFans,
  BBC Sport, PlanetF1 (`/rss`), Crash.net, **GPFans**, **Sky Sports** (videos skipped), **ESPN**,
  **FIA** press releases + news (F1 items only).
- Not possible: Reuters (no public RSS), team sites (no feeds; Haas feed = sponsors), Ferrari/Alpine
  (block bots), Audi/Sauber (unreachable). Check new feeds: `python scripts/check_feeds.py` or
  GitHub Actions → "Check new feeds".

### The website
- `news.html` — "Comic strip, more fun" design (cream / navy / red / yellow, Fredoka + Nunito, sticker
  labels, speech-bubble headline of the day, faint background cars, works on phones). Four tabs:
  - **Top stories (AI):** cards, most sources first each day; label sticker, red "N sources" pill, "Why grouped?".
  - **All stories:** every story, with source filter buttons.
  - **Rumours:** Active first; trend arrows, source count, first seen, Sources + History buttons.
  - **Ask:** private chat; one question box (shortcut buttons only fill it; Enter or Ask sends);
    thinking steps (what was searched, the dates, what was found) shown above each answer.
- `costs.html` — AI money tracker (still the OLD plain look).
- `stats-test.html` — plain test page for the Stats Agent (not linked from the site).

### Labels
**Confirmed** = official team/driver/FIA news, results, penalties · **Reported** = on-the-record quotes
and interviews · **Rumour** = "sources say", "in talks", "could" · **Opinion** = columns, analysis,
features, history. If unsure: Reported over Confirmed, Rumour over both. Changing the rules → bump
`LABELS_VERSION` in `ai_cluster.py`.

### Rumour safety lock (never weaken)
Confirmed only from a **Confirmed** card; Denied only from a Confirmed or **Reported** card; the AI's
evidence words must be found word-for-word in that card (checked by code), otherwise "blocked".
Trend is plain code: rising = 2+ sources in 2 days; fading = nothing new 5 days; Faded = 14 days.

### The Cloudflare Worker (`worker/ask-worker.js`, setup in `worker/SETUP.md`)
- Worker **`f1-news-ask`**, address **https://f1-news-ask.pohping-ai.workers.dev**,
  Cloudflare account ID `9e2f6ecc21dc9252de2ef530821dfd25`.
- Secrets on the Worker (**never overwrite**): `OPENROUTER_API_KEY` (separate chat key `f1-news-ask`)
  and `ASK_PASSCODE`. Daily limit `DAILY_LIMIT_USD` (default $0.20).
- **`/` = Ask:** passcode + daily limit → AI plans the search → code searches the saved news →
  AI answers ONLY from what was found, with numbered sources, or "Not in my news."
  Search range by code: a named time → that time; a named person/team/topic → all saved news (30 days);
  a catch-up → 7 days. Unclear questions → "Which driver do you mean?"; "pretend…" → refused.
- **`/stats` = Stats Agent (Stage 3, Agent 1):** OpenRouter tool calling with one tool,
  `get_standings` (drivers or constructors), reading `data/stats.json` from the website.
  Code checks: no tool call → "Not in my stats."; every number in the answer must be in the tool
  data (numbers typed in the question don't count); race winners / titles / other seasons →
  "Not in my stats."
- **Deploying:** it does NOT update by itself. After merging a Worker change:
  `cd worker && npx wrangler deploy` (settings in `worker/wrangler.toml`: logs on, preview links off,
  compatibility date 2026-11-15, keep_vars). The Cloudflare token is saved in the cloud environment
  **f1-dashboard** (not in **f1-news**).
- Live version: `f9598475` (Session 9). **`/stats` is NOT deployed yet** (checked 17 Nov).

### Report card (tests)
- `OPENROUTER_API_KEY=… python tests/report_card.py` (`--save` → `tests/LAST_REPORT.md`).
- **22 tests** with made-up data in `tests/fixtures.py` (never the real `data/`): grouping (3),
  labels (4), rumour safety (3), Ask (5), the user's 3 (Leclerc's daughter, Verstappen
  source + label, "Ask about the driver"), Stats S1–S4. Latest score **22/22** (~$0.005 per run).
- Run it after any AI change; never lower a test's expectations to make it pass.

### Money (OpenRouter, model `anthropic/claude-haiku-5.5`)
- Robot AI ≈ $0.025–0.06 a day (~$0.75–1.80 a month). Ask ≈ $0.0002–0.0015 per question;
  Stats ≈ $0.0003–0.0005 per question. GitHub Actions, GitHub Pages, Cloudflare and Jolpica are free.
- Main key: **$0.163 used, $4.84 left** of $5 (checked 17 Nov). `COSTS.md` has the keep-or-drop table.

### Keys and cloud environments
- GitHub Secret `OPENROUTER_API_KEY` (main key, $5 limit) — used by the robot.
- Cloud environment **f1-dashboard**: OpenRouter + Cloudflare tokens, the news sites (+16 extra
  sites added for feed testing, removable). Cloud environment **f1-news**: only `api.jolpi.ca` and
  `openrouter.ai`, no Cloudflare token. No key is ever in the code.

### Pull requests (all merged)
#1 news site · #2 AI brain · #3 merged cards first + badges · #4 labels + rumour tracker ·
#5 money tracker · #6 Reported label + Ask/Worker · #7 one Ask box · #8 30-day search ·
#9 report card + Ask fixes · #10 GPFans/Sky/ESPN/FIA + feed checker · #11 comic restyle ·
#12 Stats Agent step 1 (stats robot) · #13 Stats Agent step 2 (`/stats` + `get_standings`)

### Loose ends (17 Nov)
1. **Deploy the Worker** so `/stats` goes live, then test `stats-test.html` on the phone.
2. Restyle `costs.html` (and maybe `stats-test.html`) to the comic design.
3. Delete the 13 merged branches on GitHub (everything is in `main`).
4. Optional: remove the 16 feed-testing sites from the f1-dashboard environment.
5. Next: Stats Agent step 3+ (more tools, show it on the site), or whatever comes next.

---


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

## Session 5 — 15 Nov 2026: money side tracker

### Done
- Every AI request now logs its real cost (from OpenRouter) in `data/costs.json`, per Malaysia
  day and per feature: "AI grouping + labels", "Label catch-up", "Headline of the day",
  "Rumour tracker". Failed requests are logged too (they still cost money).
- New page `costs.html` (💰 AI costs link on the news page): total so far, average per day, rough
  monthly estimate, a table per feature (today / 7 days / all time / per day / per month) and a
  day-by-day table.
- New `COSTS.md`: keep-or-drop sheet for each paid feature, what you lose without it, and money
  spent so far.

### Tested
- On a scratch copy: all four features were logged with the same costs the scripts printed.
- Cost page on a phone with the test log (plus two made-up days, test only): numbers add up,
  no sideways page scroll, no errors; without `costs.json` it says "No AI costs recorded yet".

### Money so far
- $0.047 used on the OpenRouter key (building + testing + robot), $4.95 left of the $5 limit.

### Things to know
- `data/costs.json` starts empty: it only counts the robot's runs from now on.
- Needs Step 3 (PR #4) merged first, because it also counts the rumour tracker.

## Session 6 — 15 Nov 2026: "Reported" label + Ask tab

### Done
- New label **Reported** (on-the-record quotes and interviews). **Confirmed** now means official
  team / driver / FIA news, results and penalties only. All cards are re-labelled once
  (`LABELS_VERSION = 2`).
- Rumour tracker: only Confirmed (official) news can confirm a rumour; an official statement OR an
  on-the-record denial (Reported) can deny one. Evidence words are still checked word-for-word.
- New **Ask** tab: a chat that answers only from the saved cards, rumours and stories, with
  numbered source links and "Not in my news." when nothing matches. Thinking steps are shown
  above each answer. Quick buttons: Catch me up (last 7 days), Biggest rumour right now?,
  What's new on [driver]?
- New `worker/ask-worker.js` (Cloudflare Worker): holds the chat's OpenRouter key as a secret,
  checks the passcode, checks today's spending on the key (default limit $0.20/day), then:
  AI plans the search → code searches the saved news → AI answers only from what was found.
- `worker/SETUP.md`: step-by-step Cloudflare setup.

### Tested (Worker code run locally with a stand-in for Cloudflare, data = copy of the live site)
- Labels: 11 Confirmed, 29 Reported, 2 Rumour, 21 Opinion (one miss: a PlanetF1 opinion piece as Reported).
- Safety lock: 6 cases, including "Reported quote tries to confirm" → blocked, "Reported denial" → allowed.
- 5 questions: catch-up ($0.0014), biggest rumour ($0.0004), Antonelli ($0.0010), journalist ban
  ($0.0005), "Who won the Monaco GP this year?" → "Not in my news." ($0.00015). Spot-checked facts
  against the saved stories (Tsunoda appeal date, Verstappen 21st→2nd) — correct.
- Fixed during testing: catch-up answer was cut off (more room), "what's new" searched only 1 day
  (now 7), "ban" matched "Urban" (whole words now), wrong-passcode message was hidden.
- Wrong passcode → refused (1 s delay); daily limit reached → refused; question too long → refused;
  other websites not allowed; no secrets → clear message.
- Browser (phone size): setup box, buttons, answers with clickable [n] links, sources, cost line,
  chat kept when switching tabs, no sideways scroll, no errors.

### Money
- $0.063 used on the main key so far ($4.94 left). Ask: about $0.0002–0.0014 per question.

### Next
- User: follow `worker/SETUP.md` (separate `f1-news-ask` key, Cloudflare Worker, two secrets).
- The Worker reads the live site, so it only knows what the robot has saved.

## Session 7 — 15 Nov 2026: Worker deployed + simpler Ask box

### Done
- Deployed `worker/ask-worker.js` to the existing Cloudflare Worker `f1-news-ask` with Wrangler
  (live at https://f1-news-ask.pohping-ai.workers.dev). The secrets `ASK_PASSCODE` and
  `OPENROUTER_API_KEY` were checked before and after (names only) and were not changed.
  - Problem: the first deploy reset three dashboard settings (logs off, preview links on,
    compatibility date). Fixed with a second deploy using the original settings (logs on,
    preview links off, date 2026-11-15). The deploy settings file is only in Claude's scratch folder.
  - Cloudflare refused the first two attempts with "Too Many Requests"; the third worked.
- Ask tab: now ONE question box. The shortcut buttons (Catch me up, Biggest rumour,
  What's new on…?) only fill the box; Enter or "Ask" sends it. "What's new on" with no name is
  not sent, and pressing Enter while an answer is loading keeps your text in the box.

### Tested (pretend middleman with a fixed answer, so no AI cost)
- Each shortcut fills the box without sending; Enter and the Ask button both send the box text;
  "What's new on" + typed name sends "What's new on Verstappen"; empty name is not sent;
  Enter while loading sends nothing extra and keeps the text; phone size, no errors.

### Next
- User: test the live Ask tab on the phone with the real Worker.
- Maybe: keep the Wrangler settings file in the project (`worker/wrangler.toml`) for future deploys.

## Session 8 — 15 Nov 2026: Ask searches all saved news for named topics

### Done
- `worker/ask-worker.js`: the search range is now decided by plain code:
  - the question names a time ("today", "this week") → that time;
  - the question names a person, team or topic → ALL saved news (up to 30 days);
  - a general catch-up (no names) → the last 7 days.
  The AI only reports whether the question named a time; it no longer picks the range.
- New thinking step "📅 Dates searched: 19 Oct – 15 Nov 2026 (30 days: …)", including a note
  when the saved news does not go back that far.
- Answers still come only from the saved news ("Not in my news." otherwise).

### Tested (old vs new Worker, same questions, copy of today's live data)
- "Tell me about Charles Leclerc's daughter" → nothing about it is saved → "Not in my news." ($0.0005)
- "What happened between Hamilton and Leclerc at the Mexico GP?" (stories 2–13 Nov, older than
  7 days) → answer from 7 saved stories ($0.0011); claims checked against the saved previews.
- "What's new on Verstappen?" → now 30 days instead of 7: $0.00073 → $0.00099.
- "Catch me up on the last 7 days." → still 7 days (8–15 Nov), same cost (~$0.0012–0.0015).

### Cost difference
- Only named-topic questions that used to search 7 days change: about +$0.0003 per question
  (~+35%). The number of items sent to the AI is capped, so it cannot grow much more.
- Main key: $0.073 used so far, $4.93 left.

### Next
- After merging: deploy the new Worker to Cloudflare (same Wrangler steps as Session 7).

## Session 9 — 15 Nov 2026: Step 6, the report card

### Done
- `tests/report_card.py`: ONE command runs 18 tests with made-up test news (`tests/fixtures.py`)
  in a temporary folder, using the real AI code, and prints PASS/FAIL with reasons, a score and
  the cost of the run. `tests/ask_runner.mjs` runs the real Worker code for the Ask tests.
- Tests: grouping (3), labels (4), rumour safety (3), Ask (5) and the user's 3
  (Leclerc's daughter, Verstappen points with source + label, "Ask about the driver").
- Fixes found BY the report card (both also affected the live site):
  1. "Who will be Alpine's reserve driver in 2027?" got "Not in my news" because a question about
     the future made the search look ONLY at rumours. Now "rumours"/"news" focus only changes the
     order of results and never hides other kinds.
  2. "Ask about the driver" made the AI guess (it wrote about Verstappen). Now the planning step
     marks such questions "unclear" and the Worker asks "Which driver (or team) do you mean?".
     Requests to pretend / make up news are now refused by code too ("I can't pretend…").
- Ask tab shows ❓ for "which driver?" and 🛑 for refusals.

### Results
- First run (code before this session): **16/18** — failed A1 (Alpine reserve) and U3 (no name).
- After the fixes: **18/18**, and 18/18 again on a second run. Cost: about **$0.004 per run**.
- Saved in `tests/LAST_REPORT.md`.

### Money
- Main key: $0.092 used so far, $4.91 left.

### Next
- After merging: deploy the new `worker/ask-worker.js` to Cloudflare.
- Run the report card after every change to the AI parts.

## Session 10 — 15 Nov 2026: Worker deploy + more news sources

### Done
- Deployed the Session 9 Worker (report-card fixes) to Cloudflare; checked the live code has the
  fixes, secrets untouched, settings kept (logs on, preview links off, date 2026-11-15).
- New `scripts/check_feeds.py` (+ manual GitHub button "Check new feeds"): tries possible RSS
  feeds, reads homepages for advertised RSS links, and reports stories / dates / F1 share / tags.
- Added 4 new sources (5 feeds) to `scripts/fetch_news.py`:
  - **GPFans** `gpfans.com/en/rss.xml` — all F1, dated (only the latest 10 items per read).
  - **Sky Sports** `skysports.com/rss/12433` — all F1; "Video" clips are skipped (new `skip_tags`).
  - **ESPN** `espn.com/espn/rss/f1/news` — all F1, dated.
  - **FIA** press releases + news — covers ALL motorsport, so only items whose headline or
    snippet says F1 / Formula 1 / Formula One are kept (new `f1_only`); "Sport news" prefix trimmed.
- The collector now also accepts `F1_DATA_DIR` (safe tests on a copy of the data).

### Not added (and why)
- **Reuters**: no public RSS any more (feeds closed in 2020); the F1 page answers 401 Forbidden.
- **Team sites** (Mercedes, McLaren, Red Bull, Aston Martin, Williams, Racing Bulls, Cadillac):
  no RSS feed (404 or a normal web page). **Haas** has a feed, but it lists sponsors, not news.
- **Ferrari, Alpine**: their sites refuse automated visitors (403). **Audi/Sauber**: site not reachable.
- FIA `rss.xml`: old (last item March 2026), a list of pages, not news.

### Tested (on a copy of the live data)
- 55 new stories: GPFans 10, Sky Sports 16, ESPN 23, FIA 6. No Sky videos, no F4/karting/rally FIA items.
- AI brain: 11 cards now combine a new source with existing ones (e.g. Racing Bulls line-up:
  ESPN + Formula1.com + Sky Sports). Rumour tracker found a new rumour (Cadillac F1 sale, GPFans).
- Report card: **18/18** ($0.0039).

### Cost
- New sources add ~6–20 stories a day to ~33 → about +$0.005–0.015 per day. One-off catch-up of
  the first 56 stories: ~$0.01.
- Main key: $0.109 used so far, $4.89 left.

### Problems
- Claude could not add the new sites to the cloud machine's allowed list (the settings service
  refused), and running the checks on GitHub was blocked; the user added the sites by hand.

## Session 11 — 15 Nov 2026: "Comic strip, more fun" restyle

### Done (look only — every tab, feature and data file is unchanged)
- `news.html` restyled to the locked design: cream background, navy ink, F1 red, yellow;
  Fredoka (headings, tabs, labels, buttons) + Nunito (body) from Google Fonts; sentence case.
- Comic shapes: 3px navy borders, 24–28px rounded corners, 5px solid navy offset shadow.
  Story cards tilt −0.7° / +0.7° (no tilt on phones). Labels are sticker pills on the card's top
  edge (Confirmed / Reported / Rumour / Opinion colours as specified); "N sources" = red pill.
- Header: red rounded panel with faint white dots, "F1 News Daily" on a white sticker ("F1" in red),
  white F1 car with speed lines, tabs as one white pill bar (active tab yellow).
- Headline of the day: white speech bubble with a tail and a yellow "Meanwhile, today…" sticker.
- 3 very faint background cars (navy, red, yellow) fixed behind the content.
- Ask tab: greeting panel with the avatar ("Hi Poh Ping!" / "Ask me about any story."); my
  questions = navy bubbles, answers = cream bubbles with a navy border; Ask button = red pill.
- Removed the automatic dark mode (the design is a fixed light comic style).

### Tested
- Phone (iPhone size) and desktop: all 4 tabs, source filters, Why grouped / Sources / History
  buttons, and a real Ask answer (real Worker code + real AI on a copy of the live data).
  Fonts load, cards tilt only on desktop, labels sit on the card edge, cars stay behind the content,
  no all-caps, no sideways scrolling, no errors.
- Report card: **18/18** ($0.0043).

### Money
- Main key: $0.119 used so far, $4.88 left.

### Next ideas
- Maybe restyle `costs.html` to match (it still has the old plain look).

## Session 12 — 16 Nov 2026: Stage 3, Agent 1 (Stats Agent), Step 1: the stats robot

### Done
- New `scripts/fetch_stats.py` (no AI). It downloads from the free **Jolpica F1 API**
  (`api.jolpi.ca`, the Ergast replacement):
  - the current driver standings,
  - the current constructor (team) standings,
  - every race result of the current season, read in pages of 100 rows and joined back up by round.
- It saves everything to `data/stats.json`: season, "after round N", the last race, both standings
  and all races (position, driver, team, grid, laps, status, time, points, fastest-lap rank).
  A `note` in the file says standings include sprint points but `races` is Grand Prix only.
- New workflow `.github/workflows/fetch-stats.yml` runs it **every 6 hours** (at :30, so it
  doesn't clash with the news robot), plus a "Run workflow" button. It only saves when the
  numbers changed.
- `requests` added to `requirements.txt` (it was installed before, but never listed).
- Safety: if any download fails, or the number of result rows doesn't match what Jolpica says,
  the old `stats.json` is kept and the robot does not fail.

### Rate limits (from Jolpica's `docs/rate_limits.md`)
- Limit: 4 requests per second and 500 per hour. We make **7 requests per run**, waiting 1.5 s
  between them (under 1 per second), and run 4 times a day: about **28 requests a day**.
  If Jolpica says "slow down" (429), the script waits 10–40 s and tries again (max 4 tries).

### Tested
- Real run: season 2026, after round 20 (Brazilian GP): 25 drivers, 11 teams, 20 races × 22
  results = 440 rows, matching Jolpica's total. 7 requests, 13 seconds.
- Second run: "Stats unchanged", file not rewritten.
- Broken API address: "Could not get the stats… Keeping the old file", file byte-for-byte unchanged.
- Spot check: Antonelli 1st, 390 pts, 9 wins; Mercedes 1st, 652 pts; Brazil won by Norris from pole.
  Race-only points (Antonelli 359) are less than the standings (390) because of sprints, which is expected.

### Things to know
- The Claude cloud session needed a new personal environment **f1-news** (allows only
  `api.jolpi.ca` and `openrouter.ai`), because this session couldn't be moved onto `f1-dashboard`.
  The OpenRouter key is NOT in `f1-news` yet; it will be asked for in Step 2.
- GitHub only runs scheduled jobs from `main`, so the 6-hour robot starts after merging.

### Next
- Step 2: the Ask Worker gets OpenRouter tool calling with one tool, `get_standings`,
  reading `stats.json`.

## Session 12 (continued) — 16 Nov 2026: Stats Agent, Step 2: one tool (`get_standings`)

### Done
- **Where:** a new address **`/stats`** on the existing Worker `f1-news-ask` (`worker/ask-worker.js`).
  Why the same Worker: it reuses the passcode, the daily limit and the chat key, and needs no new
  Cloudflare setup. The old Ask address (`/`) works exactly as before.
- **The tool loop** (OpenRouter tool calling, model `anthropic/claude-haiku-5.5`):
  1. 🧠 The AI asks for the tool `get_standings` with `drivers` or `constructors`.
  2. ⚙️ Plain code runs it: reads `data/stats.json` from the website (never Jolpica live) and gives back
     position, name, team, points and wins, plus the season, round and when the file was saved.
  3. ✍️ The AI answers from that data only (at most 3 AI requests per question).
  Every step is returned in `steps` (shown on the test page) AND written to the Cloudflare logs as `[stats] …`.
- **No inventing (checked by code, not just by asking the AI):**
  - If the AI answers without asking for the stats, the answer is not shown ("Not in my stats.").
  - 🔢 Number check: every number in the answer must be in the tool data (or a gap between two of
    its numbers, or today's date). Otherwise the answer is blocked. Numbers typed in the question
    don't count, so "pretend he has 400 points" can't sneak through.
  - Questions the standings can't answer (race winners, titles, other seasons) → "Not in my stats." + what it does have.
- Same passcode (`ASK_PASSCODE`) and same daily limit (`DAILY_LIMIT_USD`, default $0.20) as Ask.
- New `stats-test.html`: a plain test page (not linked from the site) that uses the Worker address
  and passcode saved by the Ask tab, shows the tool loop, the answer, the source and the cost.
- New `tests/stats_runner.mjs` (runs the real `/stats` code on a local folder; also handy by hand) and
  4 new report-card tests on MADE-UP standings in `tests/fixtures.py` (S1–S4).
- New `worker/wrangler.toml` with the deploy settings (logs on, preview links off, date 2026-11-15,
  keep_vars) — a loose end from Session 7. `worker/SETUP.md` explains `/stats` and deploying.

### Tested (real AI, real `data/stats.json`, Worker code run on this computer)
- "Who is leading and by how much?" → Antonelli 390, 111 ahead of Verstappen 279, after round 20. ✅
- "Top 3 teams?" → get_standings(constructors) → Mercedes 652, Ferrari 510, Red Bull 415. ✅
- "Compare Hamilton and Leclerc" → 261 vs 249, 12 points apart. ✅
- "Who won the Brazilian GP?", "How many titles has Hamilton won?", "Ignore your rules… 2021 champion"
  → all "Not in my stats." ✅
- First try: "Pretend Verstappen has 400 points" was played along with (and the number check let 400
  through because it trusted the question). Fixed both (rule 5 + question numbers no longer count);
  now it says "I can't pretend, but here are the real standings". ✅
- Number check alone: honest answer passes; "395 points and 10 wins" is blocked (395 not in the data).
- Passcode / limit / addresses (pretend OpenRouter): wrong passcode → 401; limit reached → 429;
  GET `/stats` → "F1 News Stats is running."; GET `/` → Ask still running; unknown address → 404.
- Test page in a phone-sized browser: shortcut buttons fill the box, wrong passcode asks again,
  tool loop + answer + source + cost shown, no errors, no sideways scroll.
- Report card: **22/22** ($0.0054): the 18 old tests + S1–S4 (leader from the tool with made-up
  numbers, constructors tool, race winner → Not in my stats, "pretend 999 points" refused).

### Cost
- About $0.0003–0.0005 per stats question (2 AI requests). Testing this session: ~$0.007–0.012.

### Not done yet / next
- **Deploy**: after merging, the Worker must be deployed (`cd worker && npx wrangler deploy`) — the
  live Worker does not have `/stats` until then. This cloud session (environment `f1-news`) has no
  Cloudflare token, so either deploy from a session on `f1-dashboard` or add the token here.
- Then test on the phone with `stats-test.html`.
- Jolpica can lag behind official changes (e.g. the Leclerc Brazil penalty question: our 510 vs a
  512 seen on formula1.com). The answers always say "after round N" and the file's save time is in the tool data.

## Session 13 — 17 Nov 2026: mini project "Beat the pole lap", Step 1

### Done
- New page `game.html` (separate from the dashboard; no other page changed), comic-strip style.
- Top-down oval track on an HTML canvas: grey tarmac, red/white kerbs, navy outlines, chequered line.
- Your car (red): speeds up by itself; steer with ← → on a laptop or hold the ◀ ▶ buttons on a phone.
  Off the track the top speed drops from 160 to 40, so cutting corners does not pay.
- See-through ghost car (yellow) drives a fixed pole lap of **10.30 s** (`GHOST_LAP` at the top of
  the script — easy to change).
- Timer on screen. At the finish line: your time, ghost time, the gap (green = faster), your best.
  Best time is saved in the browser (`localStorage`, key `f1game_best`). "Try again" button.
  (Laptop: Enter or Space also starts a lap.)
- No AI, no sound, no new tools.

### Tested (phone-sized screen, iPhone 13)
- A test autopilot steered with the real ◀ ▶ buttons: full lap → "Pole position!", 9.72 s vs 10.30 s,
  gap −0.58 s, best saved; "Try again" resets the timer and hides the results; best still shown after reload.
- Steering off the track → speed drops to 40. No sideways scrolling, no errors.
- First try: the ghost (12 s) was beaten by 2.3 s, so it was made faster (10.30 s); a tie no longer
  counts as a "new" best.

### Next ideas (Step 2+)
- Countdown lights, a real F1-shaped track, lap splits, more ghosts (e.g. from real pole times).

## Session 14 — 17 Nov 2026: "Beat the pole lap" tweaks (Beginner / Pro)

### Done (`game.html` only)
- **Bug fixed:** the whole car now always stays inside the canvas (kept 24 px from the edge; before,
  only its centre was kept 12 px in, so part of it could vanish). Off the track for **2 seconds** →
  the car is put back on the track at the same point of the lap, with a "Back on track!" message.
- **Beginner mode (default):** soft invisible walls (the car slides along the track edge instead of
  leaving it) + gentle steering help that follows the curve (weaker while you steer yourself).
- **Pro mode:** the old behaviour, no help. A Beginner / Pro toggle under the track; switching starts over.
  The chosen mode is remembered.
- **Separate best times:** `f1game_best_beginner` and `f1game_best_pro`. The old single best time
  (from Session 13, no help) became the Pro best.

### Tested (phone-sized screen)
- Beginner with no steering at all: full lap on the help alone, 10.32 s, never off the track.
- Beginner holding ◀ the whole lap: slides along the wall, finishes (14.38 s), never off the track.
- Pro: steering off the track → back on the track after 2 s, "Back on track!" shown.
- Pro holding ▶ for 8 s: the car stops at the canvas edge (lowest y 496 of 520), never leaves it.
- Pro lap with the real buttons: 9.72 s saved as the Pro best; Beginner best (10.32) kept separately;
  mode and best times survive a reload. No errors, no sideways scrolling.
