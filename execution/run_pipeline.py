#!/usr/bin/env python3
"""
Master pipeline orchestrator for PNBS Instagram Competitor Analysis.

Chains three steps in sequence:
  1. scrape_instagram.py   — fetch competitor posts
  2. analyze_competitors.py — analyze with Claude
  3. generate_strategy.py  — generate weekly content plan

Usage:
    python execution/run_pipeline.py                  # full run
    python execution/run_pipeline.py --skip-scrape    # reuse today's existing scraped data
    python execution/run_pipeline.py --skip-scrape --skip-analysis  # only regenerate strategy
"""

import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging — writes to both console and a dated log file
# ---------------------------------------------------------------------------

Path(".tmp").mkdir(exist_ok=True)
log_file = f".tmp/pipeline_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

DIVIDER = "=" * 60


def banner(title: str) -> None:
    logger.info(DIVIDER)
    logger.info(title)
    logger.info(DIVIDER)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run(skip_scrape: bool = False, skip_analysis: bool = False) -> None:
    banner(f"PNBS Instagram Strategy Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    scraped_file = None
    analysis_file = None

    # ------------------------------------------------------------------
    # Step 1 — Scrape
    # ------------------------------------------------------------------
    if skip_scrape:
        logger.info("\n[1/3] Scraping SKIPPED — looking for existing scraped file...")
        scraped_dir = Path(".tmp/scraped")
        candidates = sorted(scraped_dir.glob("competitor_posts_*.json"), reverse=True) if scraped_dir.exists() else []
        if not candidates:
            logger.error("No existing scraped data found. Re-run without --skip-scrape.")
            sys.exit(1)
        scraped_file = str(candidates[0])
        logger.info(f"  Using: {scraped_file}")
    else:
        logger.info("\n[1/3] Scraping competitor Instagram accounts...")
        try:
            # Import here so errors are caught per-step
            sys.path.insert(0, str(Path(__file__).parent))
            from scrape_instagram import main as scrape
            scraped_file = scrape()
            logger.info(f"  ✓ Scraped data saved to: {scraped_file}")
        except Exception as exc:
            logger.error(f"  ✗ Scraping failed: {exc}")
            logger.error("  Tip: Check Instagram credentials in .env, or increase DELAY_BETWEEN_POSTS.")
            sys.exit(1)

    # ------------------------------------------------------------------
    # Step 2 — Analyze
    # ------------------------------------------------------------------
    if skip_analysis:
        logger.info("\n[2/3] Analysis SKIPPED — looking for existing analysis file...")
        analysis_dir = Path(".tmp/analysis")
        candidates = sorted(analysis_dir.glob("competitor_analysis_*.json"), reverse=True) if analysis_dir.exists() else []
        if not candidates:
            logger.error("No existing analysis found. Re-run without --skip-analysis.")
            sys.exit(1)
        analysis_file = str(candidates[0])
        logger.info(f"  Using: {analysis_file}")
    else:
        logger.info("\n[2/3] Analyzing competitor content with Claude...")
        try:
            from analyze_competitors import main as analyze
            analysis_file = analyze(scraped_file)
            logger.info(f"  ✓ Analysis saved to: {analysis_file}")
        except Exception as exc:
            logger.error(f"  ✗ Analysis failed: {exc}")
            logger.error("  Tip: Check ANTHROPIC_API_KEY in .env.")
            sys.exit(1)

    # ------------------------------------------------------------------
    # Step 3 — Generate Strategy
    # ------------------------------------------------------------------
    logger.info("\n[3/3] Generating weekly content strategy...")
    try:
        from generate_strategy import main as generate
        strategy_file = generate(analysis_file)
        logger.info(f"  ✓ Strategy saved to: {strategy_file}")
    except Exception as exc:
        logger.error(f"  ✗ Strategy generation failed: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    banner("Pipeline complete!")
    logger.info(f"  Weekly strategy → {strategy_file}")
    logger.info(f"  Pipeline log    → {log_file}")
    logger.info(DIVIDER)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the PNBS Instagram strategy pipeline.")
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip scraping and reuse the most recent scraped data.",
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip analysis and reuse the most recent analysis file (implies --skip-scrape).",
    )
    args = parser.parse_args()

    if args.skip_analysis:
        args.skip_scrape = True  # Can't analyze without scraping, but we're skipping both

    run(skip_scrape=args.skip_scrape, skip_analysis=args.skip_analysis)
