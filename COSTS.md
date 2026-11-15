# Money tracker (side tracker)

Use this at the end of the project to decide which features to keep.
Live, automatic numbers are on the website: **💰 AI costs** (`costs.html`, data in `data/costs.json`).

## What is free
| Part | Cost |
|---|---|
| Collecting the news (`fetch_news.py`) | $0 |
| The robot (GitHub Actions, public repo) | $0 |
| The website (GitHub Pages) | $0 |

Only the AI features below cost money. They all use one OpenRouter key (limit: $5)
and the model `anthropic/claude-haiku-5.5` ($0.10 read / $0.50 written per million tokens).

## The paid features: keep or drop?
Estimates come from real test runs. The robot runs 12 times a day, but most runs have only a few new stories.

| Feature | What it does | Est. per day | What you lose if you drop it | Added in | Keep? |
|---|---|---|---|---|---|
| **AI grouping + labels** | Groups same-event stories into cards; writes title, 2-sentence summary, "sources disagree" note, merge reason; labels Confirmed / Reported / Rumour / Opinion | ~$0.02–0.04 (with the 4 new sources since Session 10: ~+$0.005–0.015) | The "Top stories (AI)" tab, the labels, and (because they need cards) the rumour tracker and headline of the day. "All stories" still works. | Step 2 (+ labels in Step 3) | ☐ |
| **Headline of the day** | One sentence at the top of the page | ~$0.002–0.003 | Just that sentence | Step 2 | ☐ |
| **Rumour tracker** | Remembers rumours across days, trend, history, official confirmations | ~$0.005–0.01 | The "Rumours" tab | Step 3 | ☐ |
| **Ask tab (chat)** | Answers your questions from the saved news, with sources and thinking steps (2 AI steps per question) | ~$0.0002–0.0015 per question; e.g. 20 questions ≈ $0.015–0.02 (named-topic questions search 30 days: ~+$0.0003 each) | The Ask tab | Step 5 | ☐ |
| **Label catch-up** | Labels cards that have no label | One-off ~$0.002, then ~$0 | Some cards might show no label | Step 3 | ☐ |
| **All robot AI features together** | | **~$0.025–0.06 per day (~$0.75–1.80 per month)** | | | |
| **Ask tab** | Only when you ask; capped by the Worker's daily limit (default $0.20) and the `f1-news-ask` key's own limit | | | | |

**Where to see Ask costs:** each answer shows its cost and today's chat spending; the total is on
openrouter.ai under the `f1-news-ask` key (the Worker cannot write to `data/costs.json`).
The Cloudflare Worker itself is free (100,000 requests/day on the free plan).

**How to drop a feature:** delete its step in `.github/workflows/fetch-news.yml`
(the headline and label catch-up are inside `ai_cluster.py`; ask Claude to switch them off).

## Money spent so far (building + testing + robot)
Taken from the OpenRouter key's usage page. This total includes everything paid by the key.

| Date | What | Spent |
|---|---|---|
| 14–15 Nov 2026 | Step 2 AI brain: building and testing | ~$0.019 |
| 15 Nov 2026 | Step 3 labels + rumour tracker: building and testing | ~$0.015 |
| 15 Nov 2026 | Cost tracker: testing | ~$0.005 |
| 14–15 Nov 2026 | Robot's real runs on GitHub (the rest) | ~$0.008 |
| 15 Nov 2026 | Step 5 "Reported" label + Ask tab: building and testing (+ robot runs) | ~$0.015 |
| 15 Nov 2026 | Ask: 30-day search for named topics, testing (old vs new) (+ robot runs) | ~$0.010 |
| 15 Nov 2026 | Step 6 report card: building, 3 full runs + debugging (+ robot runs) | ~$0.019 |
| 15 Nov 2026 | Session 10 new sources: testing on a data copy + report card (+ robot runs) | ~$0.017 |
| **15 Nov 2026** | **Total used on the main key so far** | **$0.109** |
| | Left on the $5 limit | $4.89 |

**Report card (`tests/report_card.py`):** about **$0.004 per run** (18 tests). It only costs money
when someone runs it; it is not part of the robot.

*Update this table at the end of each session (check `https://openrouter.ai/settings/keys` or ask Claude).*
