"""
Collect Formula 1 news from RSS feeds and save it to data/news.json.

What this script does, step by step:
1. Load the stories we already saved (if any).
2. Download each news feed and read its stories.
3. Add new stories. The link is the ID, so a story is never added twice.
4. Delete stories older than 30 days.
5. Save everything back to data/news.json, newest first.

If one feed is broken, we print a warning and carry on with the others.
"""

import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser

# ---- Settings you can change ---------------------------------------------

# F1_DATA_DIR lets a test use a separate copy of the data (the live site is never touched).
NEWS_FILE = Path(os.environ.get("F1_DATA_DIR") or Path(__file__).resolve().parent.parent / "data") / "news.json"
KEEP_DAYS = 30
SNIPPET_LENGTH = 200

# Each feed: a display name, the feed address, and an optional tag filter.
# Optional filters for a feed:
#   "only_tag":  keep a story only if it has this tag (The Race mixes in other series).
#   "skip_tags": drop stories with any of these tags (Sky Sports "Video" clips).
#   "f1_only":   keep a story only if its headline or snippet says F1 / Formula 1 / Formula One
#                (the FIA feeds cover all motorsport: rally, karting, F4...).
#   "trim_snippet_start": remove this text pattern from the start of the snippet.
FEEDS = [
    {"source": "Formula1.com", "url": "https://www.formula1.com/en/latest/all.xml"},
    {"source": "Autosport", "url": "https://www.autosport.com/rss/f1/news/"},
    {"source": "Motorsport.com", "url": "https://www.motorsport.com/rss/f1/news/"},
    {"source": "The Race", "url": "https://www.the-race.com/feed/", "only_tag": "Formula 1"},
    {"source": "RaceFans", "url": "https://www.racefans.net/feed/"},
    {"source": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/formula1/rss.xml"},
    {"source": "PlanetF1", "url": "https://www.planetf1.com/rss"},
    {"source": "Crash.net", "url": "https://www.crash.net/rss/f1"},
    # Added in Session 10 (checked with scripts/check_feeds.py):
    {"source": "GPFans", "url": "https://www.gpfans.com/en/rss.xml"},
    {"source": "Sky Sports", "url": "https://www.skysports.com/rss/12433", "skip_tags": ["Video"]},
    {"source": "ESPN", "url": "https://www.espn.com/espn/rss/f1/news"},
    {"source": "FIA", "url": "https://www.fia.com/rss/press-release", "f1_only": True,
     "trim_snippet_start": r"^(Sport|FIA|Members) news\s+"},
    {"source": "FIA", "url": "https://www.fia.com/rss/news", "f1_only": True,
     "trim_snippet_start": r"^(Sport|FIA|Members) news\s+"},
]

F1_WORDS = re.compile(r"\b(F1|Formula 1|Formula One)\b", re.I)

USER_AGENT = "Mozilla/5.0 (compatible; F1NewsBot/1.0)"

# ---------------------------------------------------------------------------


def now_utc():
    return datetime.now(timezone.utc)


def to_iso(dt):
    """Turn a date into text like 2026-11-14T09:13:34Z."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def from_iso(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def clean_text(raw):
    """Remove HTML tags and extra spaces, then cut to about 200 characters."""
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > SNIPPET_LENGTH:
        text = text[:SNIPPET_LENGTH].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
    return text


def story_date(entry):
    """Return the story's published date, or None if the feed has no date."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc)


def has_tag(entry, wanted):
    tags = [t.get("term", "") for t in entry.get("tags", [])]
    return any(t.strip().lower() == wanted.lower() for t in tags)


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def read_feed(feed, seen_time):
    """Download one feed and return a list of stories (as dictionaries)."""
    parsed = feedparser.parse(download(feed["url"]))
    stories = []
    for entry in parsed.entries:
        link = (entry.get("link") or "").strip().split("#")[0]
        title = clean_text(entry.get("title"))
        if not link or not title:
            continue
        if "only_tag" in feed and not has_tag(entry, feed["only_tag"]):
            continue
        if any(has_tag(entry, tag) for tag in feed.get("skip_tags", [])):
            continue
        snippet = clean_text(entry.get("summary") or entry.get("description"))
        if feed.get("trim_snippet_start"):
            snippet = re.sub(feed["trim_snippet_start"], "", snippet)
        if feed.get("f1_only") and not F1_WORDS.search(f"{title} {snippet}"):
            continue
        published = story_date(entry)
        stories.append({
            "title": title,
            "source": feed["source"],
            # If the feed has no date (Formula1.com), use the time we first saw it.
            "date": to_iso(published or seen_time),
            "date_is_seen_time": published is None,
            "link": link,
            "snippet": snippet,
        })
    return stories


def load_saved():
    if NEWS_FILE.exists():
        data = json.loads(NEWS_FILE.read_text(encoding="utf-8"))
        return data.get("stories", [])
    return []


def main():
    seen_time = now_utc()
    saved = load_saved()
    by_link = {story["link"]: story for story in saved}  # link = ID
    print(f"Already saved: {len(saved)} stories")

    cutoff = seen_time - timedelta(days=KEEP_DAYS)
    working_feeds = 0
    for feed in FEEDS:
        try:
            stories = read_feed(feed, seen_time)
        except Exception as error:  # one broken feed should not stop the rest
            print(f"  WARNING {feed['source']}: {error}")
            continue
        working_feeds += 1
        new = [s for s in stories
               if s["link"] not in by_link and from_iso(s["date"]) >= cutoff]
        for story in new:
            by_link[story["link"]] = story
        print(f"  {feed['source']}: {len(stories)} in feed, {len(new)} new")

    # Delete stories older than 30 days.
    kept = [s for s in by_link.values() if from_iso(s["date"]) >= cutoff]
    removed = len(by_link) - len(kept)

    # Newest first.
    kept.sort(key=lambda s: s["date"], reverse=True)

    if working_feeds == 0:
        print("ERROR: every feed failed")
        sys.exit(1)

    # Only rewrite the file if something changed (keeps the history tidy).
    if NEWS_FILE.exists() and kept == saved:
        print("No changes, file not rewritten")
        return

    NEWS_FILE.parent.mkdir(parents=True, exist_ok=True)
    NEWS_FILE.write_text(
        json.dumps({"updated": to_iso(seen_time), "stories": kept}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(kept)} stories ({removed} older than {KEEP_DAYS} days removed)")


if __name__ == "__main__":
    main()
