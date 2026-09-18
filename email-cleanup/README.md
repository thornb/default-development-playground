# Email Cleanup

A workflow (not a standalone program) for triaging a large Gmail inbox,
run through a Claude session using Claude's Gmail connector. See
`PRIVACY.md` for the ground rules this project always follows.

## Two ways to execute

- **Claude's Gmail connector** (used for identification, and for small
  batches) -- OAuth'd to your account, usable only inside a Claude session.
  No setup, but each write (archive/label/trash) needs its own individual
  approval -- fine for a handful of threads, not for hundreds.
- **`scripts/gmail_bulk.py`** (for real batches) -- a standalone script
  using your own Google Cloud OAuth credentials and the Gmail API's
  `batchModify` endpoint, which can relabel up to 1000 messages in a
  single call. Needs one-time setup (below) but then runs independently
  of any Claude session.

## Standalone bulk script setup

One-time, and mostly outside this repo:

1. Create a Google Cloud project ([console.cloud.google.com](https://console.cloud.google.com)) --
   free.
2. Enable the Gmail API for that project. Google may ask you to attach a
   billing account (payment method) before it will enable the API -- this
   is a fraud-prevention step, not a charge. Personal-use volumes here stay
   far under the free quota (millions of units/day).
3. Configure the OAuth consent screen: type "External", publishing status
   "Testing", and add your own Gmail address as a test user. No Google
   verification review is needed for personal, single-user use.
4. Create an OAuth Client ID of type "Desktop app". Download its JSON and
   save it as `email-cleanup/credentials.json` (gitignored -- never commit
   this).
5. `pip install -r requirements.txt`
6. Run the script once, e.g. `python scripts/gmail_bulk.py "from:x@y.com older_than:6m"`
   (dry run by default). The first run opens a browser to authorize; it
   caches a `token.json` (also gitignored) afterward so you won't need to
   re-authorize each time.

See the docstring in `scripts/gmail_bulk.py` for full usage.

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
  months):** there is no working "always allow this tool" persistence for
  MCP tool calls in this environment -- each connector call needs its own
  individual approval, so a 250-thread batch means 250 approvals. Two
  zero-friction alternatives instead:
  - **`scripts/gmail_bulk.py --execute`** with the same query (once the
    one-time OAuth setup above is done) -- a handful of API calls, no
    per-item approval.
  - **Gmail's own web UI**, no setup at all: search the same query, click
    **"Select all conversations that match this search"**, then Archive
    (or Delete). Two clicks for any number of threads.

  Claude's role for a batch like this is to run the query, report the
  count and sender/date range for approval, and hand off the exact query
  string -- not to execute it thread-by-thread via the connector.

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
- `scripts/gmail_bulk.py` -- standalone bulk archive/label script (own OAuth credentials, real `batchModify` calls)
- `requirements.txt` -- dependencies for `gmail_bulk.py`
- `data/` -- gitignored; local-only exports and reports, never committed
- `credentials.json`, `token.json` -- gitignored; your own OAuth credentials and cached token, never committed
