"""
run_pipeline.py
---------------
The master orchestrator for Version 1.
Runs the full pipeline: Fetch → Clean → Store
Can run once OR on a schedule (every X minutes).

Usage:
    python scheduler/run_pipeline.py            # Run once
    python scheduler/run_pipeline.py --schedule # Run every 5 min
"""

import sys
import os
import time
import argparse
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import schedule
from database.db_connection import init_db
from scripts.fetch_data import fetch_crypto_data
from scripts.process_data import clean_data, store_data


INTERVAL_MINUTES = 5   # ← Change this to run more/less frequently


def run_pipeline():
    """Executes one full fetch → clean → store cycle."""
    print(f"\n{'='*50}")
    print(f"  🚀 Pipeline run started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    # Step 1: Fetch
    coins = fetch_crypto_data()
    if not coins:
        print("  ⚠️  No data fetched. Skipping this run.")
        return

    # Step 2: Clean
    df = clean_data(coins)
    print(f"  🧹 Cleaned data → {len(df)} valid coins")

    # Step 3: Store
    store_data(df)

    print(f"  ✅ Pipeline complete.\n")


def main():
    parser = argparse.ArgumentParser(description="Crypto Intelligence Pipeline")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help=f"Run pipeline every {INTERVAL_MINUTES} minutes continuously"
    )
    args = parser.parse_args()

    # Always init DB first
    print("🗄  Initializing database...")
    init_db()

    if args.schedule:
        print(f"⏰ Scheduler started — running every {INTERVAL_MINUTES} minutes.")
        print("   Press Ctrl+C to stop.\n")

        run_pipeline()  # Run immediately on start

        schedule.every(INTERVAL_MINUTES).minutes.do(run_pipeline)

        while True:
            schedule.run_pending()
            time.sleep(30)   # Check every 30 seconds
    else:
        run_pipeline()       # Single run


if __name__ == "__main__":
    main()
