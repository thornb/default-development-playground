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
5. Execute the approved action -- see **Identify vs. execute** below for
   where that actually happens.

## Identify vs. execute

Claude only *identifies* candidates here; where the action actually runs
depends on size:

- **A handful of threads (roughly ≤20):** Claude can archive/trash/label
  them directly via the Gmail connector (`unlabel_thread` etc.), one
  approval per thread.
- **A real batch (hundreds of threads, e.g. a daily newsletter going back
  months):** do it in Gmail's own web UI instead. There is no working
  "always allow this tool" persistence for MCP tool calls in this
  environment -- each call needs its own individual approval, so a
  250-thread batch means 250 approvals. Gmail's UI does the same
  (reversible) action in two clicks:
  1. Search the same query Claude used to find the candidates (see the
     table below), e.g. `from:sender@example.com older_than:6m`.
  2. Select all on the page, then click **"Select all conversations that
     match this search"**.
  3. Click **Archive** (or Delete, if that was the agreed action).

  Claude's role for a batch like this is to run the query, report the
  count and sender/date range for approval, and hand off the exact query
  string for you to paste into Gmail -- not to execute it thread-by-thread.

## Known limitations

- **Spam folder is not queryable** through this Gmail connector: both
  `in:spam` and `label:spam` return zero results here even when the
  account has spam messages. Spam review currently has to happen directly
  in Gmail.

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
