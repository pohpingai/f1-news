"""Stats robot: saves this season's F1 standings and race results to data/stats.json.

Data comes from the free Jolpica F1 API (the replacement for the old Ergast API).
No AI here - just plain downloading and tidying.

Jolpica's limits (docs/rate_limits.md): 4 requests a second, 500 an hour.
This script makes about 8 requests per run and waits PAUSE seconds between them,
and GitHub runs it every 6 hours, so we use roughly 32 requests a DAY.

Safety: if any request fails, the old stats.json is kept unchanged (we never save half the data).
The file is only rewritten when the numbers actually changed.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API = "https://api.jolpi.ca/ergast/f1"
PAUSE = 1.5          # seconds between requests (limit is 4 per second - we do under 1)
PAGE = 100           # rows per page for race results
TIMEOUT = 30
HEADERS = {"User-Agent": "f1-news-daily-stats-robot (runs every 6 hours)"}

DATA_DIR = Path(os.environ.get("F1_DATA_DIR") or Path(__file__).resolve().parent.parent / "data")
OUT = DATA_DIR / "stats.json"

_calls = 0


def get(path, params=None):
    """Download one page from Jolpica. Retries a few times if the API says 'slow down' (429)."""
    global _calls
    for attempt in range(4):
        if _calls:
            time.sleep(PAUSE)
        _calls += 1
        r = requests.get(f"{API}/{path}", params=params, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 429 or r.status_code >= 500:
            wait = 10 * (attempt + 1)
            print(f"  Jolpica answered {r.status_code}; waiting {wait}s and trying again")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()["MRData"]
    raise RuntimeError(f"Jolpica kept refusing {path}")


def driver_name(d):
    return f"{d.get('givenName', '')} {d.get('familyName', '')}".strip()


def fetch_driver_standings():
    data = get("current/driverstandings/", {"limit": PAGE})
    lists = data["StandingsTable"]["StandingsLists"]
    if not lists:
        return data["StandingsTable"].get("season"), None, []
    sl = lists[0]
    rows = []
    for s in sl["DriverStandings"]:
        d = s["Driver"]
        rows.append({
            "position": int(s["position"]) if s.get("position") else None,
            "driver": driver_name(d),
            "driver_id": d["driverId"],
            "code": d.get("code"),
            "number": d.get("permanentNumber"),
            "team": ", ".join(c["name"] for c in s.get("Constructors", [])),
            "points": float(s["points"]),
            "wins": int(s["wins"]),
        })
    return sl["season"], int(sl["round"]), rows


def fetch_constructor_standings():
    data = get("current/constructorstandings/", {"limit": PAGE})
    lists = data["StandingsTable"]["StandingsLists"]
    if not lists:
        return []
    return [{
        "position": int(s["position"]) if s.get("position") else None,
        "team": s["Constructor"]["name"],
        "team_id": s["Constructor"]["constructorId"],
        "points": float(s["points"]),
        "wins": int(s["wins"]),
    } for s in lists[0]["ConstructorStandings"]]


def fetch_results():
    """All race results this season. They come in pages of 100 rows, and one race
    can be split across two pages, so we join them back together by round."""
    races = {}
    offset, total = 0, None
    while total is None or offset < total:
        data = get("current/results/", {"limit": PAGE, "offset": offset})
        total = int(data["total"])
        for race in data["RaceTable"]["Races"]:
            rnd = int(race["round"])
            if rnd not in races:
                c = race["Circuit"]
                races[rnd] = {
                    "round": rnd,
                    "race": race["raceName"],
                    "date": race["date"],
                    "circuit": c["circuitName"],
                    "country": c["Location"].get("country"),
                    "results": [],
                }
            for res in race["Results"]:
                d, t = res["Driver"], res["Constructor"]
                races[rnd]["results"].append({
                    "position": int(res["position"]),
                    "position_text": res["positionText"],   # "R" = retired, "D" = disqualified, etc.
                    "driver": driver_name(d),
                    "driver_id": d["driverId"],
                    "code": d.get("code"),
                    "team": t["name"],
                    "grid": int(res["grid"]) if res.get("grid") else None,
                    "laps": int(res["laps"]) if res.get("laps") else None,
                    "status": res.get("status"),
                    "time": (res.get("Time") or {}).get("time"),
                    "points": float(res["points"]),
                    "fastest_lap_rank": (res.get("FastestLap") or {}).get("rank"),
                })
        offset += PAGE
        if offset > 2000:   # safety stop: a season never has this many rows
            break
    out = sorted(races.values(), key=lambda r: r["round"])
    for r in out:
        r["results"].sort(key=lambda x: x["position"])
    return out, total


def main():
    try:
        season, rnd, drivers = fetch_driver_standings()
        teams = fetch_constructor_standings()
        races, total_rows = fetch_results()
    except Exception as e:  # network or API problem: keep yesterday's file
        print(f"Could not get the stats ({e}). Keeping the old data/stats.json.")
        return 0   # do not fail the robot - the news must still update

    counted = sum(len(r["results"]) for r in races)
    if counted != total_rows:
        print(f"Got {counted} result rows but Jolpica said {total_rows}. Keeping the old file.")
        return 0
    if not drivers or not teams:
        print("Standings came back empty. Keeping the old file.")
        return 0

    stats = {
        "source": "Jolpica F1 API (api.jolpi.ca), Ergast-compatible",
        "note": ("Standings points include sprint races. 'races' lists Grand Prix results only "
                 "(no sprints, no qualifying), so adding up race points can be less than the standings."),
        "season": season,
        "after_round": rnd,
        "last_race": races[-1]["race"] if races else None,
        "driver_standings": drivers,
        "constructor_standings": teams,
        "races": races,
    }

    old = {}
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if {k: v for k, v in old.items() if k != "updated_at"} == stats:
            print(f"Stats unchanged (season {season}, after round {rnd}). {_calls} requests.")
            return 0

    stats = {"updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **stats}
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(stats, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Saved stats: season {season}, after round {rnd} ({stats['last_race']}), "
          f"{len(drivers)} drivers, {len(teams)} teams, {len(races)} races. {_calls} requests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
