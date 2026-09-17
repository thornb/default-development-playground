# Yankees Player Dashboard

A static, mobile-friendly HTML dashboard showing MLB hitting stats for a
Yankees player, starting with Aaron Judge. Data comes from the free,
public [MLB Stats API](https://statsapi.mlb.com) — no API key needed.

## Regenerating `index.html`

```
pip install -r requirements.txt
python scripts/build_dashboard.py "aaron judge"
```

This fetches the player's bio, current-season hitting line, and career
hitting line, and writes a fully self-contained `index.html` (data is
embedded at build time, so the page needs no network access to view —
open it directly, or host it anywhere, e.g. GitHub Pages).

To add another player, add their MLB player id to `KNOWN_PLAYER_IDS` in
`scripts/fetch_stats.py`, or pass the numeric id directly:

```
python scripts/build_dashboard.py 592450
```

## Files

- `scripts/fetch_stats.py` — thin MLB Stats API client
- `scripts/build_dashboard.py` — renders `templates/dashboard_template.html` into `index.html`
- `templates/dashboard_template.html` — the dashboard's HTML/CSS/JS
- `index.html` — generated output (committed so the page is viewable without a build step)
