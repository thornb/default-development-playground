"""Standalone bulk Gmail label changes via the Gmail API's batchModify endpoint.

Unlike scripts/fetch_stats.py-style tools, this does NOT go through Claude's
Gmail connector -- it authenticates directly with Google using your own
OAuth credentials, so it can modify up to 1000 messages per API call instead
of one thread per approval.

One-time setup (see ../README.md "Standalone bulk script setup" for the full
walkthrough):
  1. Create a Google Cloud project and enable the Gmail API.
  2. Configure the OAuth consent screen (External + Testing, add yourself as
     a test user -- no Google verification needed for personal use).
  3. Create an OAuth Client ID (type: Desktop app) and download it as
     credentials.json into this directory (email-cleanup/). It is gitignored.
  4. First run opens a browser for you to authorize; a token.json (also
     gitignored) is cached afterward so you won't need to re-authorize.

Usage:
    # Dry run (default): count matching messages, change nothing.
    python scripts/gmail_bulk.py "from:example@newsletter.com older_than:6m"

    # Actually archive them (remove INBOX label).
    python scripts/gmail_bulk.py "from:example@newsletter.com older_than:6m" --execute

    # Different label change, e.g. move to Trash instead of archiving.
    python scripts/gmail_bulk.py "in:spam" --execute --remove-label INBOX --add-label TRASH
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
REPO_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = REPO_DIR / "credentials.json"
TOKEN_PATH = REPO_DIR / "token.json"
BATCH_SIZE = 1000  # Gmail API max ids per batchModify call


def get_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                raise SystemExit(
                    f"Missing {CREDENTIALS_PATH}. Download your OAuth Client ID's "
                    "JSON from Google Cloud Console and save it there first."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def list_message_ids(service, query: str) -> list[str]:
    ids: list[str] = []
    page_token = None
    while True:
        resp = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token, maxResults=500)
            .execute()
        )
        ids.extend(m["id"] for m in resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return ids


def batch_modify(service, message_ids: list[str], add_labels: list[str], remove_labels: list[str]) -> None:
    for i in range(0, len(message_ids), BATCH_SIZE):
        chunk = message_ids[i : i + BATCH_SIZE]
        service.users().messages().batchModify(
            userId="me",
            body={"ids": chunk, "addLabelIds": add_labels, "removeLabelIds": remove_labels},
        ).execute()
        print(f"  modified {i + len(chunk)}/{len(message_ids)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", help="Gmail search query, same syntax as the Gmail search box")
    parser.add_argument("--execute", action="store_true", help="Actually apply the change (default: dry run)")
    parser.add_argument("--remove-label", action="append", default=["INBOX"], dest="remove_labels")
    parser.add_argument("--add-label", action="append", default=[], dest="add_labels")
    args = parser.parse_args()

    service = get_service()
    message_ids = list_message_ids(service, args.query)
    print(f"Query matched {len(message_ids)} messages.")

    if not message_ids:
        return

    if not args.execute:
        print("Dry run -- no changes made. Re-run with --execute to apply.")
        return

    batch_modify(service, message_ids, args.add_labels, args.remove_labels)
    print("Done.")


if __name__ == "__main__":
    main()
