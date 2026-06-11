"""
run_pipeline.py
---------------
Master pipeline orchestrator — Version 2.
Flow: Fetch → Clean → Store → Analyse → Generate Signals → Store Signals

Usage:
    python scheduler/run_pipeline.py             # Run once
    python scheduler/run_pipeline.py --schedule  # Run every 5 minutes
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
from scripts.signal_engine import generate_signals, store_signals

INTERVAL_MINUTES = 5


def run_pipeline():
    """Executes one full pipeline cycle."""
    print(f"\n{'='*55}")
    print(f"  🚀 Pipeline run @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    # Step 1: Fetch
    coins = fetch_crypto_data()
    if not coins:
        print("  ⚠️  No data fetched. Skipping this run.")
        return

    # Step 2: Clean
    df = clean_data(coins)
    print(f"  🧹 Cleaned → {len(df)} valid coins")

    # Step 3: Store prices
    store_data(df)

    # Step 4: Analyse + Generate signals
    print(f"\n  🔬 Running indicator analysis...")
    signals_df = generate_signals()

    # Step 5: Store signals
    store_signals(signals_df)

    # Step 6: Quick summary
    if not signals_df.empty and "signal" in signals_df.columns:
        summary = signals_df["signal"].value_counts()
        print(f"\n  📊 Signal Summary:")
        for signal, count in summary.items():
            print(f"     {signal}: {count} coins")

    print(f"\n  ✅ Full pipeline complete.\n")


def main():
    parser = argparse.ArgumentParser(description="Crypto Intelligence Pipeline v2")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help=f"Run pipeline every {INTERVAL_MINUTES} minutes continuously"
    )
    args = parser.parse_args()

    print("🗄  Initializing database...")
    init_db()

    if args.schedule:
        print(f"⏰ Scheduler active — every {INTERVAL_MINUTES} minutes. Ctrl+C to stop.\n")
        run_pipeline()
        schedule.every(INTERVAL_MINUTES).minutes.do(run_pipeline)
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_pipeline()


if __name__ == "__main__":
    main()