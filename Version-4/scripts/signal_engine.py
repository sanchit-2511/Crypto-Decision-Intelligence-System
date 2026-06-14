"""
signal_engine.py
----------------
Version 2 — Signal Engine
Rule-based Buy / Sell / Hold classifier.
Combines RSI + Moving Average crossover + Volatility
to produce a clear, explainable signal per coin.

Rules:
  BUY  → RSI < 35  AND SMA7 > SMA14  (oversold + bullish crossover)
  SELL → RSI > 65  AND SMA7 < SMA14  (overbought + bearish crossover)
  HOLD → everything else
  INSUFFICIENT DATA → not enough history yet
"""

import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database.db_connection import get_connection
from scripts.analyse_data import analyse_all_coins

# ── Thresholds (easy to tune later) ───────────────────────────────────────────
RSI_OVERSOLD   = 35
RSI_OVERBOUGHT = 65


# ── Signal Logic ──────────────────────────────────────────────────────────────

def classify_signal(rsi, sma_7, sma_14) -> str:
    """
    Applies rule-based logic to produce a signal string.
    """
    # Can't signal without indicators
    if rsi is None or sma_7 is None or sma_14 is None:
        return "⚪ Insufficient Data"

    if rsi < RSI_OVERSOLD and sma_7 > sma_14:
        return "🟢 BUY"
    elif rsi > RSI_OVERBOUGHT and sma_7 < sma_14:
        return "🔴 SELL"
    else:
        return "🟡 HOLD"


def generate_signals() -> pd.DataFrame:
    """
    Runs the full indicator analysis, applies signal rules,
    and returns an enriched DataFrame with signals.
    """
    df = analyse_all_coins()
    if df.empty:
        return pd.DataFrame()

    df["signal"] = df.apply(
        lambda row: classify_signal(row["rsi"], row["sma_7"], row["sma_14"]),
        axis=1
    )

    return df


def store_signals(df: pd.DataFrame):
    """
    Persists the latest signals into the coin_signals table.
    """
    if df.empty:
        print("  ⚠️  No signals to store.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stored = 0

    for _, row in df.iterrows():
        # Only store if we actually computed something
        if row.get("status") == "insufficient_data":
            continue

        cursor.execute("""
            INSERT INTO coin_signals
                (symbol, rsi, sma_7, sma_14, volatility_score, volatility_label, signal, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["symbol"],
            row["rsi"],
            row["sma_7"],
            row["sma_14"],
            row["volatility_score"],
            row["volatility_label"],
            row["signal"],
            now
        ))
        stored += 1

    conn.commit()
    conn.close()
    print(f"  ✅ Stored signals for {stored} coins.")


def get_latest_signals() -> pd.DataFrame:
    """
    Reads the most recent signal for each coin from the DB.
    Used by the dashboard.
    """
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT symbol, rsi, sma_7, sma_14,
               volatility_score, volatility_label, signal, timestamp
        FROM coin_signals
        WHERE timestamp = (SELECT MAX(timestamp) FROM coin_signals)
        ORDER BY symbol ASC
    """, conn)
    conn.close()
    return df


if __name__ == "__main__":
    print("🚦 Generating signals...")
    df = generate_signals()
    store_signals(df)

    print("\n📊 Signal Summary:")
    summary = df.groupby("signal")["symbol"].count().reset_index()
    summary.columns = ["Signal", "Count"]
    print(summary.to_string(index=False))

    print("\n🔍 Sample (first 10 coins):")
    cols = ["symbol", "rsi", "sma_7", "sma_14", "volatility_label", "signal"]
    available = [c for c in cols if c in df.columns]
    print(df[available].head(10).to_string(index=False))
