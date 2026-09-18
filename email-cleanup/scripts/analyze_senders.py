"""Summarize sender-frequency and category stats from a local, metadata-only
export of Gmail search results.

This does NOT call the Gmail API itself -- it operates on JSON files saved
under ../data/ (gitignored) containing records of the shape:

    {"sender": str, "subject": str, "date": str, "labelIds": [str], "threadId": str}

Those records are produced by hand (or by a Claude session using the Gmail
connector) via search_threads, keeping strictly to metadata: sender,
subject line, date, and labels -- never message bodies or snippets.

Usage:
    python scripts/analyze_senders.py data/promotions_sample.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HIGH_VOLUME_THRESHOLD = 5  # threads from one sender in a sample -> flag as candidate


def load_records(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def summarize(records: list[dict]) -> dict:
    by_sender = defaultdict(list)
    for r in records:
        by_sender[r["sender"]].append(r)

    counts = Counter({sender: len(rs) for sender, rs in by_sender.items()})
    label_counts = Counter(
        label for r in records for label in r.get("labelIds", [])
    )

    candidates = [
        {
            "sender": sender,
            "count": count,
            "oldest": min(r["date"] for r in by_sender[sender]),
            "newest": max(r["date"] for r in by_sender[sender]),
            "sample_subjects": [r["subject"] for r in by_sender[sender][:3]],
        }
        for sender, count in counts.most_common()
        if count >= HIGH_VOLUME_THRESHOLD
    ]

    return {
        "total_threads": len(records),
        "unique_senders": len(counts),
        "label_breakdown": dict(label_counts),
        "high_volume_senders": candidates,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/analyze_senders.py <path-to-export.json>")
        sys.exit(1)

    result = summarize(load_records(Path(sys.argv[1])))
    print(json.dumps(result, indent=2))
