"""Generate a static, self-contained HTML dashboard for an MLB hitter.

Usage:
    python scripts/build_dashboard.py "aaron judge"

Fetches bio + hitting stats from the MLB Stats API, then embeds them
directly into templates/dashboard_template.html to produce index.html.
No JavaScript fetch calls at runtime -- the page works offline, opened
as a local file, or hosted anywhere (GitHub Pages, etc).
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

from fetch_stats import get_player_dashboard_data

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "templates" / "dashboard_template.html"
OUTPUT_PATH = REPO_ROOT / "index.html"

# (label, stat-dict key, formatter)
HERO_STATS = [
    ("AVG", "avg", str),
    ("HR", "homeRuns", str),
    ("RBI", "rbi", str),
    ("OPS", "ops", str),
]
SECONDARY_STATS = [
    ("Games", "gamesPlayed"),
    ("Hits", "hits"),
    ("Runs", "runs"),
    ("Doubles", "doubles"),
    ("Home Runs", "homeRuns"),
    ("Walks", "baseOnBalls"),
    ("Strikeouts", "strikeOuts"),
    ("Stolen Bases", "stolenBases"),
    ("OBP", "obp"),
    ("SLG", "slg"),
]


def calc_age(birth_date: str) -> int:
    b = datetime.date.fromisoformat(birth_date)
    today = datetime.date.today()
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day))


def stat_tiles(stats: dict, spec: list[tuple[str, str]], size: str) -> str:
    cells = []
    for label, key in spec:
        value = stats.get(key, "--")
        cells.append(
            f'<div class="stat stat--{size}">'
            f'<span class="stat__value">{value}</span>'
            f'<span class="stat__label">{label}</span>'
            f"</div>"
        )
    return "\n".join(cells)


def build(name_or_id: str) -> None:
    data = get_player_dashboard_data(name_or_id)
    bio = data["bio"]
    season_split = data["season"] or {}
    career_split = data["career"] or {}
    season_stats = season_split.get("stat", {})
    career_stats = career_split.get("stat", {})
    season_year = season_split.get("season", str(datetime.date.today().year))

    hero_html = stat_tiles(season_stats, [(l, k) for l, k, _ in HERO_STATS], "hero")
    secondary_html = stat_tiles(season_stats, SECONDARY_STATS, "secondary")
    career_html = stat_tiles(career_stats, SECONDARY_STATS, "secondary")

    team_name = (
        (bio.get("currentTeam") or {}).get("name")
        or (season_split.get("team") or {}).get("name")
        or (career_split.get("team") or {}).get("name")
        or ""
    )
    position = (bio.get("primaryPosition") or {}).get("abbreviation", "")
    bats = (bio.get("batSide") or {}).get("description", "")
    throws = (bio.get("pitchHand") or {}).get("description", "")
    age = calc_age(bio["birthDate"]) if bio.get("birthDate") else None
    meta_bits = [b for b in [
        position,
        f"Bats {bats[0]}/Throws {throws[0]}" if bats and throws else "",
        f"{bio.get('height', '')}, {bio.get('weight', '')} lb" if bio.get("height") else "",
        f"Age {age}" if age else "",
    ] if b]

    template = TEMPLATE_PATH.read_text()
    replacements = {
        "__TITLE__": f"{bio['fullName']} Stats",
        "__PLAYER_NAME__": bio["fullName"],
        "__PLAYER_NUMBER__": str(bio.get("primaryNumber", "")),
        "__TEAM_NAME__": team_name,
        "__PLAYER_META__": " &middot; ".join(meta_bits),
        "__SEASON_YEAR__": str(season_year),
        "__HERO_STATS_HTML__": hero_html,
        "__SECONDARY_STATS_HTML__": secondary_html,
        "__CAREER_STATS_HTML__": career_html,
        "__LAST_UPDATED__": datetime.datetime.now(datetime.timezone.utc).strftime("%b %-d, %Y %H:%M UTC"),
        "__DATA_JSON__": json.dumps(data, indent=2),
    }
    for token, value in replacements.items():
        template = template.replace(token, value)

    OUTPUT_PATH.write_text(template)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    who = sys.argv[1] if len(sys.argv) > 1 else "aaron judge"
    build(who)
