"""
process_data.py
---------------
V3: Enhanced data quality layer.
- Better null handling
- Type enforcement
- Data health tracking
- Duplicate guard (V2)
"""

import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database.db_connection import get_connection


def clean_data(coins: list) -> tuple:
    """
    Cleans incoming coin data.
    Returns (cleaned_df, health_report dict).
    """
    if not coins:
        return pd.DataFrame(), {"total": 0, "stored": 0, "skipped": 0, "reason": "No data fetched"}

    df = pd.DataFrame(coins)
    total = len(df)

    # Type enforcement
    numeric_cols = ["price", "market_cap", "volume", "price_change_24h"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing critical fields
    before = len(df)
    df = df.dropna(subset=["price", "symbol", "coin_name"])
    df = df[df["price"] > 0].copy()
    skipped = before - len(df)

    # Round for clean storage
    df["price"]            = df["price"].round(6)
    df["price_change_24h"] = df["price_change_24h"].round(2).fillna(0.0)
    df["market_cap"]       = df["market_cap"].round(0).fillna(0)
    df["volume"]           = df["volume"].round(0).fillna(0)

    df["coin_name"] = df["coin_name"].fillna("Unknown")
    df["symbol"]    = df["symbol"].str.upper().fillna("???")

    # Precise timestamp
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    health = {
        "total":   total,
        "stored":  len(df),
        "skipped": skipped,
        "timestamp": df["timestamp"].iloc[0] if len(df) > 0 else "—"
    }

    return df, health


def store_data(df: pd.DataFrame) -> dict:
    """
    Stores cleaned data with duplicate guard.
    Returns storage health report.
    """
    if df.empty:
        return {"stored": 0, "skipped": 0}

    conn = get_connection()
    cursor = conn.cursor()
    stored = 0
    skipped = 0

    for _, row in df.iterrows():
        cursor.execute("""
            SELECT COUNT(*) FROM crypto_prices
            WHERE symbol = ?
            AND timestamp >= datetime('now', '-60 seconds', 'localtime')
        """, (row["symbol"],))

        if cursor.fetchone()[0] > 0:
            skipped += 1
            continue

        cursor.execute("""
            INSERT INTO crypto_prices
                (coin_name, symbol, price, market_cap, volume, price_change_24h, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row["coin_name"], row["symbol"], row["price"],
            row["market_cap"], row["volume"], row["price_change_24h"],
            row["timestamp"]
        ))
        stored += 1

    conn.commit()
    conn.close()

    if stored > 0:
        print(f"  ✅ Stored {stored} records.")
    if skipped > 0:
        print(f"  ⏭️  Skipped {skipped} duplicates.")

    return {"stored": stored, "skipped": skipped}


# ── Read helpers ───────────────────────────────────────────────────────────────

def get_latest_prices() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT coin_name, symbol, price, market_cap, volume, price_change_24h, timestamp
        FROM crypto_prices
        WHERE timestamp = (SELECT MAX(timestamp) FROM crypto_prices)
        ORDER BY market_cap DESC
    """, conn)
    conn.close()
    return df


def get_price_history(symbol: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT timestamp, price, volume
        FROM crypto_prices
        WHERE symbol = ?
        ORDER BY timestamp ASC
    """, conn, params=(symbol.upper(),))
    conn.close()
    return df


def get_top_gainers(n: int = 5) -> pd.DataFrame:
    return get_latest_prices().nlargest(n, "price_change_24h")


def get_top_losers(n: int = 5) -> pd.DataFrame:
    return get_latest_prices().nsmallest(n, "price_change_24h")


def get_data_health() -> dict:
    """Returns DB health stats for the dashboard indicator."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(DISTINCT symbol) FROM crypto_prices")
    total_coins = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(timestamp) FROM crypto_prices")
    last_fetch = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM crypto_prices")
    total_records = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM coin_signals")
    total_signals = cursor.fetchone()[0]

    conn.close()
    return {
        "total_coins":   total_coins,
        "last_fetch":    last_fetch or "Never",
        "total_records": total_records,
        "total_signals": total_signals
    }
