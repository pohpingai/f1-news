"""
Feed checker: tries possible RSS feeds for new F1 news sources and reports which ones work.

For each site it:
1. Reads the site's homepage and looks for RSS links the site advertises ("feed discovery").
2. Tries the likely feed addresses (plus the ones it discovered).
3. For each feed that answers, reports: number of stories, how many have dates,
   how many look like F1 stories (by keywords), the most common tags, and a few headlines.

It does not change anything. Run it with:   python scripts/check_feeds.py
(It runs on GitHub too: Actions -> "Check new feeds" -> Run workflow.)
"""

import collections
import re
import urllib.request

import feedparser

USER_AGENT = "Mozilla/5.0 (compatible; F1NewsBot/1.0)"

# name -> (homepages to search for RSS links, feed addresses to try)
CANDIDATES = {
    "GPFans": (["https://www.gpfans.com/en/"],
               ["https://www.gpfans.com/en/rss.xml", "https://www.gpfans.com/en/rss/",
                "https://www.gpfans.com/rss.xml", "https://www.gpfans.com/en/f1-news/rss.xml"]),
    "Sky Sports F1": (["https://www.skysports.com/f1"],
                      ["https://www.skysports.com/rss/12433", "https://www.skysports.com/rss/0,20514,12433,00.xml"]),
    "ESPN F1": (["https://www.espn.com/f1/"],
                ["https://www.espn.com/espn/rss/f1/news", "https://www.espn.com/f1/rss",
                 "https://www.espn.co.uk/espn/rss/f1/news"]),
    "Reuters F1": (["https://www.reuters.com/sports/formula1/"],
                   ["https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml",
                    "https://www.reuters.com/sports/formula1/rss", "https://feeds.reuters.com/reuters/sportsNews"]),
    "FIA": (["https://www.fia.com/", "https://www.fia.com/news"],
            ["https://www.fia.com/rss/news", "https://www.fia.com/rss/press-release", "https://www.fia.com/rss.xml",
             "https://www.fia.com/news/rss"]),
    "Mercedes": (["https://www.mercedesamgf1.com/"], ["https://www.mercedesamgf1.com/rss", "https://www.mercedesamgf1.com/news/rss"]),
    "Ferrari": (["https://www.ferrari.com/en-EN/formula1"], ["https://www.ferrari.com/en-EN/formula1/rss"]),
    "McLaren": (["https://www.mclaren.com/racing/"], ["https://www.mclaren.com/racing/rss/", "https://www.mclaren.com/rss"]),
    "Red Bull Racing": (["https://www.redbullracing.com/"], ["https://www.redbullracing.com/int-en/rss"]),
    "Aston Martin": (["https://www.astonmartinf1.com/"], ["https://www.astonmartinf1.com/en-GB/rss"]),
    "Williams": (["https://www.williamsf1.com/"], ["https://www.williamsf1.com/rss", "https://www.williamsf1.com/news/rss"]),
    "Haas": (["https://www.haasf1team.com/"], ["https://www.haasf1team.com/rss.xml", "https://www.haasf1team.com/news/rss"]),
    "Alpine": (["https://www.alpinecars.com/en/formula-1/"], ["https://www.alpinecars.com/en/rss"]),
    "Racing Bulls": (["https://www.visacashapprb.com/"], ["https://www.visacashapprb.com/int-en/rss"]),
    "Audi (Sauber)": (["https://www.sauber-group.com/", "https://www.audif1.com/"], ["https://www.sauber-group.com/rss"]),
    "Cadillac": (["https://www.cadillacf1team.com/"], ["https://www.cadillacf1team.com/rss"]),
}

F1_WORDS = re.compile(r"\b(f1|formula ?1|formula one|grand prix|gp|verstappen|hamilton|leclerc|norris|piastri|"
                      r"russell|antonelli|alonso|ferrari|mclaren|mercedes|red bull|williams|alpine|haas|"
                      r"aston martin|sauber|audi|cadillac|racing bulls|fia|qualifying|pit ?stop)\b", re.I)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=25) as res:
        return res.status, res.headers.get("Content-Type", ""), res.read()


def discover(homepage):
    """Find RSS/Atom links that a homepage advertises in its <head>."""
    try:
        _, _, body = get(homepage)
    except Exception as e:
        return [], f"homepage error: {e}"
    html = body.decode("utf-8", "replace")
    links = []
    for tag in re.findall(r"<link[^>]+>", html, re.I):
        if re.search(r"application/(rss|atom)\+xml", tag, re.I):
            m = re.search(r'href=["\']([^"\']+)', tag)
            if m:
                href = m.group(1)
                if href.startswith("/"):
                    href = re.match(r"https?://[^/]+", homepage).group(0) + href
                links.append(href)
    return links, f"homepage OK, {len(links)} RSS link(s) advertised"


def check(url):
    try:
        status, ctype, body = get(url)
    except Exception as e:
        return {"url": url, "ok": False, "why": str(e)[:120]}
    feed = feedparser.parse(body)
    entries = feed.entries
    if not entries:
        return {"url": url, "ok": False, "why": f"HTTP {status}, {ctype[:40]}, but no stories in it (not an RSS feed)"}
    dated = sum(1 for e in entries if e.get("published_parsed") or e.get("updated_parsed"))
    f1 = sum(1 for e in entries if F1_WORDS.search(f'{e.get("title", "")} {e.get("summary", "")}'))
    tags = collections.Counter(t.get("term", "") for e in entries for t in e.get("tags", []))
    newest = max((e.get("published") or e.get("updated") or "" for e in entries), default="")
    return {"url": url, "ok": True, "stories": len(entries), "dated": dated, "f1": f1,
            "tags": tags.most_common(6), "newest": newest,
            "samples": [e.get("title", "")[:90] for e in entries[:4]]}


def main():
    for name, (homepages, urls) in CANDIDATES.items():
        print(f"\n=== {name}")
        found = []
        for home in homepages:
            links, note = discover(home)
            print(f"  {home}: {note}" + (f" -> {links}" if links else ""))
            found += links
        tried = set()
        for url in urls + found:
            if url in tried:
                continue
            tried.add(url)
            r = check(url)
            if r["ok"]:
                print(f"  ✅ {url}\n       {r['stories']} stories, {r['dated']} with dates, {r['f1']} look like F1, newest: {r['newest']}"
                      f"\n       tags: {r['tags']}\n       e.g. {r['samples']}")
            else:
                print(f"  ❌ {url}  -> {r['why']}")


if __name__ == "__main__":
    main()
