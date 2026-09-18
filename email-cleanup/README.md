# Email Cleanup

A workflow (not a standalone program) for triaging a large Gmail inbox,
run through a Claude session using Claude's Gmail connector. See
`PRIVACY.md` for the ground rules this project always follows.

## Why not a standalone script?

Claude's Gmail access here is its own OAuth connector, usable only inside
a Claude session -- there's no API key to hand to a local script. A fully
standalone tool would mean setting up your own Google Cloud project, OAuth
consent screen, and credentials. We chose the connector instead: less
setup, same repeatability, since the queries and logic below are versioned
just like code.

## Workflow

1. Run one of the search queries below (via the Gmail connector's
   `search_threads`) for a category.
2. Save the *metadata only* (sender, subject, date, labelIds, threadId --
   never snippet/body) for the results to `data/<category>.json` (gitignored).
3. Run `scripts/analyze_senders.py data/<category>.json` to get sender
   frequency, label breakdown, and high-volume-sender candidates.
4. Present the candidates for review. Nothing gets archived, trashed, or
   unsubscribed until it's explicitly approved, batch by batch.

## Categories and their queries

| Category | Gmail query | Goal |
|---|---|---|
| Old promos | `category:promotions -is:starred older_than:6m` | Archive candidates |
| Old updates | `category:updates -is:starred older_than:6m` | Archive candidates |
| Spam review | `in:spam` | Confirm before emptying |
| High-volume senders | (derived from the above via `analyze_senders.py`) | Unsubscribe candidates |

`older_than:6m` is a starting point, not a rule -- adjust per category based
on what the sender counts turn up.

## Files

- `PRIVACY.md` -- the privacy limits this project operates under
- `scripts/analyze_senders.py` -- sender-frequency / category analysis over a local export
- `data/` -- gitignored; local-only exports and reports, never committed
