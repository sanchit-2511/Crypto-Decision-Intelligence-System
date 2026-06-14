"""
run_pipeline.py
---------------
Master pipeline orchestrator — Version 4 (Final)
Flow: Fetch → Clean → Store → Indicators → Signals → Insights → ML Train → Predict → Dashboard

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
from scripts.process_data import clean_data, store_data, get_latest_prices
from scripts.signal_engine import generate_signals, store_signals
from scripts.generate_insights import generate_coin_insights, generate_market_summary, store_insights
from scripts.ml_pipeline import run_ml_pipeline

INTERVAL_MINUTES = 5


def run_pipeline():
    print(f"\n{'='*55}")
    print(f"  🚀 Pipeline v4 @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    # Step 1: Fetch
    coins = fetch_crypto_data()
    if not coins:
        print("  ⚠️  No data fetched. Skipping.")
        return

    # Step 2: Clean
    df, health = clean_data(coins)
    print(f"  🧹 Clean: {health['stored']} valid | {health['skipped']} skipped")

    # Step 3: Store prices
    store_data(df)

    # Step 4: Indicators + Signals
    print(f"\n  🔬 Running indicators + signals...")
    signals_df = generate_signals()
    store_signals(signals_df)

    # Step 5: Insights + Market Summary
    print(f"\n  🧠 Generating insights...")
    prices_df = get_latest_prices()
    generate_coin_insights(signals_df)
    summary = generate_market_summary(signals_df, prices_df)
    store_insights(summary)

    # Step 6: ML — Train + Predict
    print(f"\n  🤖 Running ML pipeline...")
    ml_summary = run_ml_pipeline()

    # Step 7: Final summary
    if not signals_df.empty and "signal" in signals_df.columns:
        counts = signals_df["signal"].value_counts()
        print(f"\n  📊 Signal Summary:")
        for sig, count in counts.items():
            print(f"     {sig}: {count} coins")

    print(f"\n  🤖 ML Summary:")
    print(f"     Models trained:    {ml_summary.get('models_trained', 0)}")
    print(f"     Predictions made:  {ml_summary.get('predictions_made', 0)}")
    if "avg_model_accuracy" in ml_summary:
        print(f"     Avg accuracy:      {ml_summary['avg_model_accuracy']}%")

    print(f"\n  ✅ Full pipeline v4 complete.\n")


def main():
    parser = argparse.ArgumentParser(description="Crypto Intelligence Pipeline v4")
    parser.add_argument("--schedule", action="store_true",
                        help=f"Run every {INTERVAL_MINUTES} minutes continuously")
    args = parser.parse_args()

    print("🗄  Initializing database...")
    init_db()

    if args.schedule:
        print(f"⏰ Scheduler active — every {INTERVAL_MINUTES} min. Ctrl+C to stop.\n")
        run_pipeline()
        schedule.every(INTERVAL_MINUTES).minutes.do(run_pipeline)
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_pipeline()


if __name__ == "__main__":
    main()
