#!/usr/bin/env python3
"""
Analyzes scraped competitor Instagram data using Claude API.

Categorizes content types, identifies top-performing formats,
extracts engagement patterns, and produces actionable insights
tailored to PNBS Campus.

Input:  .tmp/scraped/competitor_posts_{date}.json  (latest, auto-detected)
Output: .tmp/analysis/competitor_analysis_{date}.json

Usage:
    python execution/analyze_competitors.py
    python execution/analyze_competitors.py --input .tmp/scraped/competitor_posts_2026-04-14.json
"""

import os
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path(".tmp/analysis")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_latest_scraped_file() -> Path:
    scraped_dir = Path(".tmp/scraped")
    files = sorted(scraped_dir.glob("competitor_posts_*.json"), reverse=True)
    if not files:
        raise FileNotFoundError(
            "No scraped data found in .tmp/scraped/. Run scrape_instagram.py first."
        )
    return files[0]


def build_analysis_payload(scraped_data: dict) -> list[dict]:
    """
    Condense raw scraped data into a leaner structure for the Claude prompt.
    Keeps the top 8 posts per account (by engagement rate) + an aggregated summary.
    """
    payload = []

    for username, data in scraped_data.items():
        account = data["account"]
        posts = data["posts"]

        sorted_posts = sorted(posts, key=lambda p: p.get("engagement_rate", 0), reverse=True)

        # Per-format breakdown
        format_counts: dict[str, int] = {}
        format_er: dict[str, list[float]] = {}
        for p in posts:
            ft = p["post_type"]
            format_counts[ft] = format_counts.get(ft, 0) + 1
            format_er.setdefault(ft, []).append(p.get("engagement_rate", 0))

        format_summary = {
            ft: {
                "count": format_counts[ft],
                "avg_engagement_rate": round(sum(ers) / len(ers), 3),
            }
            for ft, ers in format_er.items()
        }

        payload.append({
            "username": username,
            "followers": account["followers"],
            "biography": account.get("biography", ""),
            "format_breakdown": format_summary,
            "top_8_posts": [
                {
                    "url": p["url"],
                    "date": p["date"],
                    "post_type": p["post_type"],
                    "engagement_rate": p.get("engagement_rate", 0),
                    "likes": p["likes"],
                    "comments": p["comments"],
                    "caption_preview": p["caption"][:300] if p["caption"] else "",
                    "hashtags": p["hashtags"][:15],
                }
                for p in sorted_posts[:8]
            ],
            "all_posts_formats": [p["post_type"] for p in posts],
            "avg_engagement_rate": round(
                sum(p.get("engagement_rate", 0) for p in posts) / len(posts), 3
            ) if posts else 0,
        })

    return payload


# ---------------------------------------------------------------------------
# Claude analysis
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT = """You are a senior social media strategist specializing in French alternance school marketing.

## Context: Who is PNBS?
PNBS (Paris Nord Business School) is a 100% alternance CFA (work-study school) offering programs from Bac+2 to Bac+5 in business and commerce.
- Tagline: "La Business School pour tous"
- Key differentiators: 0€ frais d'inscription, students are PAID (775€–1802€/month), 85% success rate, 300 partner companies
- Programs: BTS MCO, BTS NDRC, Titre Pro Négociateur Technico-Commercial, Bachelor (Bac+3), Master (Bac+5)
- 10 campuses across France (Saint-Denis/Paris being the main one)
- Target audience: 18-25 year-olds, post-Bac, looking for a paid work-study path in business/commerce

## Competitors being analyzed
- **ecole_studi**: Large online school (100% digital), very polished content
- **iscod.fr**: 100% online + 100% alternance — PNBS's closest competitor in model
- **digitalcollege**: "On ne recrute pas l'élite, on la forme" — 14 campuses, 87% alternance
- **isefac.national**: Specializes in events, communication, digital — top 10 Eduniversal
- **nuevo_cfa**: Multi-sector CFA
- **campus_des_ecoles**: Multi-campus network

## Scraped Instagram Data
{data}

## Your Task
Analyze this competitor Instagram data with the specific lens of what PNBS should adopt or avoid.
Focus on: what actually drives engagement (saves, comments) vs just likes. Carousels and reels with educational/testimonial content tend to win in this space.

Respond ONLY with a valid JSON object (no markdown, no code fences) matching this exact schema:

{{
  "content_type_breakdown": {{
    "<username>": {{
      "reels_pct": 0,
      "carousels_pct": 0,
      "single_images_pct": 0,
      "dominant_format": "",
      "avg_engagement_rate": 0
    }}
  }},
  "top_performing_formats": [
    {{
      "format": "",
      "why_it_works": "",
      "avg_engagement_rate": 0,
      "best_example_url": "",
      "caption_style_notes": "",
      "hook_examples": []
    }}
  ],
  "posting_patterns": {{
    "best_days": [],
    "best_times_estimated": [],
    "avg_posts_per_week": 0,
    "notes": ""
  }},
  "content_themes": [
    {{
      "theme": "",
      "description": "",
      "engagement_level": "high|medium|low",
      "example_caption_snippet": "",
      "best_account_doing_it": ""
    }}
  ],
  "hashtag_strategy": {{
    "top_hashtags": [],
    "avg_hashtags_per_post": 0,
    "hashtag_mix_strategy": "",
    "recommended_clusters": {{
      "ecole_et_formation": [],
      "alternance_et_emploi": [],
      "vie_etudiante": [],
      "reach_large": []
    }}
  }},
  "tone_and_style": {{
    "dominant_tone": "",
    "caption_structure": "",
    "hook_patterns": [],
    "cta_patterns": [],
    "emoji_usage": "",
    "avg_caption_length": ""
  }},
  "key_insights": [],
  "adapt_for_pnbs": [
    {{
      "content_type": "",
      "why_adopt": "",
      "how_to_adapt_for_pnbs": "",
      "pnbs_angle": "",
      "priority": "high|medium|low"
    }}
  ],
  "avoid": [
    {{
      "format_or_theme": "",
      "reason": ""
    }}
  ],
  "gap_opportunities": [
    {{
      "opportunity": "",
      "description": "",
      "why_competitors_miss_it": ""
    }}
  ]
}}

Be specific. Reference actual captions and engagement rates from the data. Identify what competitors are NOT doing that PNBS could own."""


def _repair_truncated_json(raw: str) -> str:
    """
    Attempt to close a JSON object that was cut off mid-stream due to token limits.
    Counts unclosed brackets/braces and appends the minimum closing sequence.
    Returns the repaired string (may still fail to parse if corruption is deep).
    """
    # Count nesting depth for objects and arrays
    stack = []
    in_string = False
    escape_next = False

    for ch in raw:
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            stack.append("}")
        elif ch == "[":
            stack.append("]")
        elif ch in ("}",  "]"):
            if stack and stack[-1] == ch:
                stack.pop()

    # Close any dangling string, then close open brackets in reverse order
    suffix = ""
    if in_string:
        suffix += '"'
    suffix += "".join(reversed(stack))
    return raw + suffix


def analyze_with_claude(client: anthropic.Anthropic, scraped_data: dict) -> dict:
    payload = build_analysis_payload(scraped_data)
    prompt = ANALYSIS_PROMPT.format(data=json.dumps(payload, ensure_ascii=False, indent=2))

    logger.info("Sending data to Claude for analysis...")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,  # Raised from 4096 — large competitor dataset needs room
        messages=[{"role": "user", "content": prompt}],
    )

    # Log stop reason so truncation is visible in logs
    stop_reason = response.stop_reason
    if stop_reason == "max_tokens":
        logger.warning("Claude hit max_tokens — response was truncated. Will attempt JSON repair.")

    raw = response.content[0].text.strip()

    # Strip markdown code fences if Claude adds them despite instructions
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else parts[0]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    # First attempt: parse as-is
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed ({e}). Attempting truncation repair...")

    # Second attempt: repair truncated JSON
    try:
        repaired = _repair_truncated_json(raw)
        result = json.loads(repaired)
        logger.info("JSON repair succeeded.")
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"Repair attempt failed ({e}). Trying to extract partial JSON...")

    # Third attempt: find the largest valid JSON object in the response
    # Walk backwards from the end to find the last valid closing brace
    for i in range(len(raw), 0, -1):
        candidate = raw[:i]
        # Only try positions that end on a closing brace/bracket
        if candidate[-1] not in ("}", "]"):
            continue
        try:
            result = json.loads(candidate)
            logger.warning(f"Extracted partial JSON (trimmed {len(raw) - i} chars from end).")
            return result
        except json.JSONDecodeError:
            continue

    # All attempts failed — save the raw response for debugging and raise
    debug_file = Path(".tmp/analysis/debug_raw_response.txt")
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    debug_file.write_text(raw, encoding="utf-8")
    raise ValueError(
        f"Could not parse Claude's response as JSON after 3 repair attempts.\n"
        f"Raw response saved to: {debug_file}\n"
        f"Try reducing POSTS_PER_ACCOUNT in scrape_instagram.py (currently fetching too much data), "
        f"or check {debug_file} to diagnose the issue."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(input_file: str | None = None) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if input_file is None:
        input_file = get_latest_scraped_file()
    else:
        input_file = Path(input_file)

    logger.info(f"Loading scraped data from: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        scraped_data = json.load(f)

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set in .env")

    client = anthropic.Anthropic(api_key=api_key)
    analysis = analyze_with_claude(client, scraped_data)

    today = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"competitor_analysis_{today}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    logger.info(f"Analysis saved to: {output_file}")
    return str(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze competitor Instagram data with Claude.")
    parser.add_argument("--input", help="Path to scraped JSON file (default: latest in .tmp/scraped/)")
    args = parser.parse_args()
    main(args.input)
