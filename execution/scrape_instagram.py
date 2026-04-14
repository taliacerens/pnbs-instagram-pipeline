#!/usr/bin/env python3
"""
Scrapes recent posts from competitor Instagram accounts using instaloader.

Input:  Hardcoded list of competitor usernames (see COMPETITOR_ACCOUNTS)
Output: .tmp/scraped/competitor_posts_{YYYY-MM-DD}.json

Usage:
    python execution/scrape_instagram.py

Auth (optional but recommended):
    Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env.
    Use a dedicated dummy account — never your main account.
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import instaloader

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

COMPETITOR_ACCOUNTS = [
    "ecole_studi",
    "iscod.fr",
    "digitalcollege",
    "isefac.national",
    "nuevo_cfa",
    "campus_des_ecoles",
]

POSTS_PER_ACCOUNT = 20      # How many recent posts to fetch per account
DELAY_BETWEEN_POSTS = 1.5   # Seconds between post fetches (rate limiting)
DELAY_BETWEEN_ACCOUNTS = 6  # Seconds between accounts

OUTPUT_DIR = Path(".tmp/scraped")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Instaloader setup
# ---------------------------------------------------------------------------

def setup_loader() -> instaloader.Instaloader:
    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
    )

    username = os.getenv("INSTAGRAM_USERNAME", "").strip()
    password = os.getenv("INSTAGRAM_PASSWORD", "").strip()

    if username:
        try:
            loader.load_session_from_file(username)
            logger.info(f"Logged in as @{username} (session)")
        except Exception:
            try:
                loader.login(username, password)
                loader.save_session_to_file()
                logger.info(f"Logged in as @{username}")
            except Exception as exc:
                logger.warning(f"Login failed ({exc})")
    return loader


# ---------------------------------------------------------------------------
# Per-account scraper
# ---------------------------------------------------------------------------

def scrape_account(loader: instaloader.Instaloader, username: str) -> dict | None:
    """
    Fetch the most recent POSTS_PER_ACCOUNT posts from `username`.
    Returns a dict with account metadata + post list, or None on failure.
    """
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        logger.error(f"  @{username}: profile not found — skipping.")
        return None
    except instaloader.exceptions.LoginRequiredException:
        logger.error(f"  @{username}: login required (private account) — skipping.")
        return None
    except Exception as exc:
        logger.error(f"  @{username}: unexpected error fetching profile — {exc}")
        return None

    logger.info(f"  @{username}  ({profile.followers:,} followers, {profile.mediacount} posts)")

    account_info = {
        "username": username,
        "full_name": profile.full_name,
        "followers": profile.followers,
        "following": profile.followees,
        "post_count": profile.mediacount,
        "biography": profile.biography,
    }

    posts = []
    count = 0

    try:
        for post in profile.get_posts():
            if count >= POSTS_PER_ACCOUNT:
                break

            # Map instaloader typename → human-readable format
            format_map = {
                "GraphSidecar": "carousel",
                "GraphVideo": "reel_or_video",
                "GraphImage": "image",
            }
            post_type = format_map.get(post.typename, post.typename)

            engagement = post.likes + post.comments
            engagement_rate = round(engagement / profile.followers * 100, 3) if profile.followers else 0

            posts.append({
                "shortcode": post.shortcode,
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "date": post.date.isoformat(),
                "post_type": post_type,
                "is_video": post.is_video,
                "likes": post.likes,
                "comments": post.comments,
                "video_view_count": post.video_view_count if post.is_video else None,
                "engagement": engagement,
                "engagement_rate": engagement_rate,
                "caption": post.caption or "",
                "hashtags": [str(h) for h in post.caption_hashtags],
                "mentions": [str(m) for m in post.caption_mentions],
            })

            count += 1
            time.sleep(DELAY_BETWEEN_POSTS)

    except Exception as exc:
        logger.warning(f"  @{username}: stopped early after {count} posts — {exc}")

    logger.info(f"  @{username}: fetched {len(posts)} posts")
    return {"account": account_info, "posts": posts}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"competitor_posts_{today}.json"

    loader = setup_loader()
    all_data: dict = {}

    for i, username in enumerate(COMPETITOR_ACCOUNTS):
        logger.info(f"\n[{i+1}/{len(COMPETITOR_ACCOUNTS)}] Scraping @{username} ...")
        result = scrape_account(loader, username)
        if result:
            all_data[username] = result

        # Pause between accounts even on failure (avoid hammering Instagram)
        if i < len(COMPETITOR_ACCOUNTS) - 1:
            time.sleep(DELAY_BETWEEN_ACCOUNTS)

    # Save
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"\nDone. Scraped {len(all_data)}/{len(COMPETITOR_ACCOUNTS)} accounts.")
    logger.info(f"Output: {output_file}")
    return str(output_file)


if __name__ == "__main__":
    main()
