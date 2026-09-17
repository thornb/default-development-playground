"""Thin client for the free, public MLB Stats API (statsapi.mlb.com).

No API key required. Docs are unofficial/community-maintained; this module
only uses the handful of endpoints needed for a single player's bio and
hitting stats.
"""
from __future__ import annotations

import datetime
from typing import Any

import requests

BASE_URL = "https://statsapi.mlb.com/api/v1"
YANKEES_TEAM_ID = 147

# Well-known player IDs, so callers can pass a name instead of hunting for an id.
KNOWN_PLAYER_IDS = {
    "aaron judge": 592450,
}


def resolve_player_id(name_or_id: str | int) -> int:
    if isinstance(name_or_id, int) or str(name_or_id).isdigit():
        return int(name_or_id)
    key = str(name_or_id).strip().lower()
    if key in KNOWN_PLAYER_IDS:
        return KNOWN_PLAYER_IDS[key]
    raise ValueError(f"Unknown player {name_or_id!r}; pass a numeric MLB player id instead")


def get_player_bio(player_id: int) -> dict[str, Any]:
    resp = requests.get(f"{BASE_URL}/people/{player_id}", timeout=10)
    resp.raise_for_status()
    people = resp.json().get("people", [])
    if not people:
        raise LookupError(f"No player found for id {player_id}")
    return people[0]


def _fetch_hitting_splits(player_id: int, stats_type: str, season: int | None = None) -> list[dict[str, Any]]:
    params = {"stats": stats_type, "group": "hitting"}
    if season is not None:
        params["season"] = season
    resp = requests.get(f"{BASE_URL}/people/{player_id}/stats", params=params, timeout=10)
    resp.raise_for_status()
    for block in resp.json().get("stats", []):
        splits = block.get("splits", [])
        if splits:
            return splits
    return []


def get_season_hitting_stats(player_id: int, season: int | None = None) -> dict[str, Any] | None:
    """Season hitting line. Tries `season`, then falls back one year if empty
    (e.g. queried during the off-season before a new year's games start)."""
    season = season or datetime.date.today().year
    splits = _fetch_hitting_splits(player_id, "season", season)
    if not splits:
        splits = _fetch_hitting_splits(player_id, "season", season - 1)
    return splits[0] if splits else None


def get_career_hitting_stats(player_id: int) -> dict[str, Any] | None:
    splits = _fetch_hitting_splits(player_id, "career")
    return splits[0] if splits else None


def get_player_dashboard_data(name_or_id: str | int) -> dict[str, Any]:
    player_id = resolve_player_id(name_or_id)
    bio = get_player_bio(player_id)
    season = get_season_hitting_stats(player_id)
    career = get_career_hitting_stats(player_id)
    return {
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "bio": bio,
        "season": season,
        "career": career,
    }


if __name__ == "__main__":
    import json
    import sys

    who = sys.argv[1] if len(sys.argv) > 1 else "aaron judge"
    print(json.dumps(get_player_dashboard_data(who), indent=2))
