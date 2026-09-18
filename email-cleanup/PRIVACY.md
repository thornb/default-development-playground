# Privacy limits for this project

Agreed before any inbox access, and binding for every session that works on
this project:

1. **No raw email data in git.** Sender addresses, subjects, snippets, or
   bodies never get committed. Only methodology (search queries, scripts,
   thresholds, category definitions) is version-controlled.
2. **Metadata only, always.** Analysis uses sender, subject line, date, and
   labels. Full message bodies are never read, even to disambiguate a case.
3. **Nothing off-limits.** Any label/folder may be searched for the agreed
   cleanup categories (old promos/updates, unsubscribe candidates,
   spam/trash, high-volume senders).
4. **Nothing destructive without review.** Archiving, trashing, deleting, or
   unsubscribing always stops for explicit sign-off on the specific batch
   first. No standing approval for future runs.
5. **Reports may be saved locally, never committed.** Candidate lists /
   sender-frequency reports can be written under `data/` for reference
   within a session, but that directory is gitignored and its contents are
   never pushed.
