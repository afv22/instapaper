#!/usr/bin/env python3
"""
Instapaper Newsletter Archiver

Archives all bookmarks tagged with "newsletter" that are older than 7 days.
Designed to run as a cron job.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from requests_oauthlib import OAuth1Session

INSTAPAPER_API_BASE = "https://www.instapaper.com/api/1"
CONFIG_FILE = Path(__file__).parent / "instapaper_config.json"


def load_config():
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        print(f"Error: Configuration file not found at {CONFIG_FILE}", file=sys.stderr)
        print("Please create instapaper_config.json with your credentials.", file=sys.stderr)
        print("See instapaper_config.example.json for format.", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        return json.load(f)


def get_access_token(username, password, consumer_key, consumer_secret):
    """Get OAuth access token using xAuth."""
    oauth = OAuth1Session(
        client_key=consumer_key,
        client_secret=consumer_secret
    )

    url = f"{INSTAPAPER_API_BASE}/oauth/access_token"
    response = oauth.post(
        url,
        data={
            "x_auth_username": username,
            "x_auth_password": password,
            "x_auth_mode": "client_auth"
        }
    )

    if response.status_code != 200:
        print(f"Error getting access token: {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)

    # Parse OAuth response (form-encoded)
    tokens = dict(param.split('=') for param in response.text.split('&'))
    return tokens['oauth_token'], tokens['oauth_token_secret']


def get_newsletter_bookmarks(oauth_session):
    """Fetch all bookmarks tagged with 'newsletter'."""
    url = f"{INSTAPAPER_API_BASE}/bookmarks/list"

    bookmarks = []
    limit = 500  # Maximum allowed per request

    # API uses folder_id or tag, not both. We use tag filter.
    response = oauth_session.post(url, data={"limit": limit, "tag": "newsletter"})

    if response.status_code != 200:
        print(f"Error fetching bookmarks: {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        return []

    data = response.json()

    # Response format: [user_obj, bookmark1, bookmark2, ...]
    if len(data) > 1:
        bookmarks = data[1:]  # Skip first element (user object)

    return bookmarks


def archive_bookmark(oauth_session, bookmark_id):
    """Archive a single bookmark."""
    url = f"{INSTAPAPER_API_BASE}/bookmarks/archive"
    response = oauth_session.post(url, data={"bookmark_id": bookmark_id})

    return response.status_code == 200


def main():
    """Main execution function."""
    config = load_config()

    # Get OAuth tokens
    consumer_key = config["consumer_key"]
    consumer_secret = config["consumer_secret"]
    username = config["username"]
    password = config.get("password", "")  # Password optional for some accounts

    print("Authenticating with Instapaper...")
    access_token, access_token_secret = get_access_token(
        username, password, consumer_key, consumer_secret
    )

    # Create authenticated session
    oauth_session = OAuth1Session(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )

    print("Fetching newsletter bookmarks...")
    bookmarks = get_newsletter_bookmarks(oauth_session)
    print(f"Found {len(bookmarks)} bookmarks with 'newsletter' tag")

    if not bookmarks:
        print("No bookmarks to process")
        return

    # Filter bookmarks older than 7 days
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
    old_bookmarks = []

    for bookmark in bookmarks:
        # time field is Unix timestamp
        bookmark_time = datetime.fromtimestamp(bookmark["time"], tz=timezone.utc)
        if bookmark_time < cutoff_time:
            old_bookmarks.append(bookmark)

    print(f"Found {len(old_bookmarks)} newsletters older than 7 days")

    if not old_bookmarks:
        print("No bookmarks to archive")
        return

    # Archive old bookmarks
    archived_count = 0
    failed_count = 0

    for bookmark in old_bookmarks:
        bookmark_id = bookmark["bookmark_id"]
        title = bookmark.get("title", "Untitled")

        if archive_bookmark(oauth_session, bookmark_id):
            archived_count += 1
            print(f"✓ Archived: {title}")
        else:
            failed_count += 1
            print(f"✗ Failed to archive: {title}", file=sys.stderr)

    print(f"\nSummary: {archived_count} archived, {failed_count} failed")

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
