"""
process_data.py
---------------
Cleans incoming coin data and stores it into the SQLite database.
V2 Fix: Precise timestamps + duplicate guard so historical trend works correctly.
"""

import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database.db_connection import get_connection


def clean_data(coins: list) -> pd.DataFrame:
    """
    Takes raw list of coin dicts, returns a cleaned Pandas DataFrame.
    """
    if not coins:
        return pd.DataFrame()

    df = pd.DataFrame(coins)

    df = df[df["price"] > 0].copy()

    df["price"]            = df["price"].round(6)
    df["price_change_24h"] = df["price_change_24h"].round(2)
    df["market_cap"]       = df["market_cap"].round(0)
    df["volume"]           = df["volume"].round(0)

    df["coin_name"] = df["coin_name"].fillna("Unknown")
    df["symbol"]    = df["symbol"].fillna("???")

    # V2 FIX: precise timestamp with seconds so every run is unique
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return df


def store_data(df: pd.DataFrame):
    """
    Inserts cleaned DataFrame rows into crypto_prices.
    V2 FIX: Duplicate guard — skips insert if same symbol was stored
    within the last 60 seconds (prevents double-runs polluting history).
    """
    if df.empty:
        print("  ⚠️  No data to store.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    stored = 0
    skipped = 0

    for _, row in df.iterrows():
        # Duplicate guard: check if this symbol was stored in last 60 seconds
        cursor.execute("""
            SELECT COUNT(*) FROM crypto_prices
            WHERE symbol = ?
            AND timestamp >= datetime('now', '-60 seconds', 'localtime')
        """, (row["symbol"],))

        count = cursor.fetchone()[0]
        if count > 0:
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
        print(f"  ✅ Stored {stored} records to database.")
    if skipped > 0:
        print(f"  ⏭️  Skipped {skipped} duplicate records (already stored recently).")


# ── Read helpers ───────────────────────────────────────────────────────────────

def get_latest_prices() -> pd.DataFrame:
    """Returns the most recent price snapshot for each coin."""
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
    """Returns full price history for a given coin symbol."""
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
    df = get_latest_prices()
    return df.nlargest(n, "price_change_24h")


def get_top_losers(n: int = 5) -> pd.DataFrame:
    df = get_latest_prices()
    return df.nsmallest(n, "price_change_24h")