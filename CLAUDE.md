# Rules for Claude in this project

## About me
- I am a beginner at coding. Please explain things in simple, everyday words.
- Avoid jargon. If you must use a technical word, explain it in one short sentence.

## How to work with me
1. **Plan first.** Before changing anything, tell me the plan in a short numbered list.
2. **Small steps.** Do one small piece at a time and tell me what you did and why.
3. **Test before saying it works.** Run the code and check the result.
4. **Update PROGRESS.md every session.** Add what was done, what is next, and any problems.
5. Do not delete or rewrite my files without asking first.

## About the project
A daily Formula 1 news website.
- `scripts/fetch_news.py` reads RSS news feeds and saves stories to `data/news.json`.
- `scripts/ai_cluster.py` (the "AI brain") groups stories about the same event into cards
  in `data/cards.json`, using OpenRouter (model: `anthropic/claude-haiku-5.5`).
- `news.html` is the web page: "Top stories (AI)" cards and "All stories" (`index.html` just forwards to it).
- `.github/workflows/fetch-news.yml` runs both scripts on GitHub every 2 hours.
- The site is published with GitHub Pages.

## Data rules
- Save only: headline, source, date, link, and a ~200-character snippet.
- The link is the ID, so the same story is never saved twice.
- Delete stories older than 30 days.
- Formula1.com gives no dates, so we save the time we first "saw" the story.
- Times on the page are shown in Malaysia time (UTC+8).

## AI rules
- The AI uses only headlines and snippets. It must never invent facts.
- If unsure whether two stories match, keep them separate.
- Only new stories are sent to the AI; a new story can join a card from the last 48 hours.
- Every merge saves the AI's reason; close calls it kept apart are saved in `decisions`.
- The OpenRouter key lives only in GitHub Secrets as `OPENROUTER_API_KEY`. Never put a key in the code.
- If there is no key or the AI fails, the site must still update with "All stories".
