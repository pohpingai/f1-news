"""
Made-up TEST news for the report card. None of this is real news, and none of it goes on the site.
All links point to https://example.com/test/... so test stories can never be mixed up with real ones.
Dates are "hours ago", so the tests work on any day.
"""

from datetime import datetime, timedelta, timezone


def at(hours_ago):
    t = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def story(key, source, title, snippet, hours_ago):
    return {"title": title, "source": source, "date": at(hours_ago), "date_is_seen_time": False,
            "link": f"https://example.com/test/{key}", "snippet": snippet}


# ---- 1. Stories for the AI brain (grouping + labels) ----------------------------------------

def grouping_and_label_stories():
    return [
        # Same story from two sites (should become ONE card)
        story("g1-autosport", "Autosport", "Alpine confirms Paul Aron as 2027 reserve driver",
              "Alpine has announced that Paul Aron will be its official reserve driver for the 2027 Formula 1 season.", 6),
        story("g1-motorsport", "Motorsport.com", "Paul Aron named Alpine reserve for 2027 F1 season",
              "Alpine has confirmed Estonian driver Paul Aron as its reserve driver for next season, the team announced on Tuesday.", 5),
        # Two DIFFERENT stories about the same driver (should stay TWO cards)
        story("g2-practice", "RaceFans", "Hamilton fastest in first Las Vegas practice",
              "Lewis Hamilton topped the opening practice session in Las Vegas, two tenths clear of Max Verstappen.", 4),
        story("g2-fashion", "PlanetF1", "Hamilton launches new fashion label in London",
              "Lewis Hamilton has unveiled a new fashion label at an event in London, with the first collection out in spring.", 8),
        # Two history pieces from the same site about DIFFERENT races (should stay TWO cards)
        story("g3-senna", "RaceFans", "On This Day: Senna clinches first title at Suzuka",
              "Ayrton Senna wins at Suzuka to clinch his first world championship.", 10),
        story("g3-hakkinen", "RaceFans", "On This Day: Hakkinen seals second title at Suzuka",
              "Mika Hakkinen wins the Japanese Grand Prix to seal his second consecutive world championship.", 11),
        # Labels
        story("l1-official", "Formula1.com", "FIA confirms 24-race calendar for 2027",
              "The FIA World Motor Sport Council has today approved the 2027 Formula 1 calendar, which features 24 races, the governing body announced.", 7),
        story("l2-quote", "Crash.net", "Norris: 'I have to be better on Saturdays'",
              "Lando Norris says he must improve his qualifying form, speaking to the media in Las Vegas on Thursday.", 3),
        story("l3-rumour", "PlanetF1", "Audi in talks with Bearman for 2028, sources say",
              "Audi is understood to be in early talks with Oliver Bearman about a 2028 race seat, according to sources close to the team.", 9),
        story("l4-opinion", "The Race", "Opinion: Why Ferrari must build its future around Leclerc",
              "Ferrari's best chance of a title is to commit fully to Charles Leclerc, argues our columnist.", 12),
    ]


# Which stories belong together, and which label each card should get.
SAME_CARD = [("g1-autosport", "g1-motorsport")]
DIFFERENT_CARDS = [("g2-practice", "g2-fashion"), ("g3-senna", "g3-hakkinen")]
EXPECTED_LABELS = {"l1-official": "Confirmed", "l2-quote": "Reported", "l3-rumour": "Rumour", "l4-opinion": "Opinion"}


# ---- 2. Cards + known rumours for the rumour tracker ----------------------------------------

def card(key, label, title, source, snippet, hours_ago):
    s = story(key, source, title, snippet, hours_ago)
    return {"id": "ctest-" + key, "label": label, "title": title, "summary": snippet, "disagreement": "",
            "created": at(hours_ago), "updated": at(hours_ago), "merge_reasons": [], "stories": [s]}


def rumour(rid, claim, people, source, title, hours_ago):
    d = at(hours_ago)
    return {"id": rid, "claim": claim, "people": people, "status": "Active", "trend": "steady",
            "first_seen": d, "last_seen": d,
            "sources": [{"title": title, "source": source, "date": d, "link": f"https://example.com/test/{rid}-first"}],
            "cards": [], "proof": None,
            "history": [{"time": d, "event": "created", "detail": "test rumour", "reason": "test"}]}


def tracker_data():
    rumours = [
        rumour("rtest-bearman", "Oliver Bearman could reportedly join Audi for 2028.", ["Oliver Bearman", "Audi"],
               "PlanetF1", "Audi in talks with Bearman for 2028, sources say", 30),
        rumour("rtest-schumacher", "Cadillac could reportedly name Mick Schumacher as its 2027 test driver.",
               ["Cadillac", "Mick Schumacher"], "Autosport", "Cadillac eyeing Mick Schumacher for test role", 30),
    ]
    cards = [
        # A Reported quote that SOUNDS like a confirmation — must NOT confirm the rumour.
        card("r1-quote", "Reported", "Bearman: 'I have signed with Audi for 2028'", "Crash.net",
             "Oliver Bearman told reporters in Las Vegas: 'I have signed with Audi for 2028.'", 3),
        # An OFFICIAL announcement — this one SHOULD confirm the Schumacher rumour.
        card("r2-official", "Confirmed", "Cadillac announces Mick Schumacher as 2027 test driver", "Formula1.com",
             "Cadillac has officially announced Mick Schumacher as its test driver for the 2027 season.", 2),
        # Another rumour report about Bearman — should only add a source.
        card("r3-rumour", "Rumour", "Audi set to finalise Bearman deal, sources say", "Motorsport.com",
             "Sources say Audi is set to finalise a deal with Oliver Bearman for the 2028 season.", 4),
    ]
    return cards, rumours


# ---- 3. Saved news for the Ask tests --------------------------------------------------------

def ask_data():
    cards = [
        card("a1-aron", "Confirmed", "Alpine confirms Paul Aron as 2027 reserve driver", "Autosport",
             "Alpine has announced that Paul Aron will be its official reserve driver for the 2027 Formula 1 season.", 6),
        card("a2-max-quote", "Reported", "Verstappen: 'Las Vegas should suit our car'", "Crash.net",
             "Max Verstappen says the long straights in Las Vegas should suit Red Bull's low-drag package.", 5),
        card("a3-max-penalty", "Confirmed", "Verstappen given five-place grid penalty in Las Vegas", "Formula1.com",
             "The stewards have handed Max Verstappen a five-place grid penalty for a new gearbox in Las Vegas.", 3),
        card("a4-max-opinion", "Opinion", "Why Verstappen is still F1's benchmark", "PlanetF1",
             "Max Verstappen remains the driver every team measures itself against, argues our columnist.", 20),
        card("a5-bearman", "Rumour", "Audi in talks with Bearman for 2028, sources say", "PlanetF1",
             "Audi is understood to be in early talks with Oliver Bearman about a 2028 race seat, according to sources.", 9),
        card("a6-leclerc", "Reported", "Leclerc: 'Ferrari must stay calm'", "Motorsport.com",
             "Charles Leclerc says Ferrari must stay calm after a difficult weekend and focus on the final races.", 8),
        card("a7-hamilton", "Confirmed", "Hamilton fastest in first Las Vegas practice", "RaceFans",
             "Lewis Hamilton topped the opening practice session in Las Vegas, two tenths clear of Max Verstappen.", 4),
    ]
    stories = [s for c in cards for s in c["stories"]]
    rumours = [rumour("rtest-ask-bearman", "Oliver Bearman could reportedly join Audi for 2028.",
                      ["Oliver Bearman", "Audi"], "PlanetF1", "Audi in talks with Bearman for 2028, sources say", 9)]
    rumours[0]["sources"][0]["link"] = "https://example.com/test/a5-bearman"
    return stories, cards, rumours
