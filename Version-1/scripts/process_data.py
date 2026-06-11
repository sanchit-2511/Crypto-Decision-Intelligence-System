"""
process_data.py
---------------
Cleans incoming coin data and stores it into the SQLite database.
Also provides helper functions to read data back for the dashboard.
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database.db_connection import get_connection


def clean_data(coins: list) -> pd.DataFrame:
    """
    Takes raw list of coin dicts, returns a cleaned Pandas DataFrame.
    Handles missing values, type casting, and rounding.
    """
    if not coins:
        return pd.DataFrame()

    df = pd.DataFrame(coins)

    # Drop rows where price is missing or zero
    df = df[df["price"] > 0].copy()

    # Round floats for clean storage
    df["price"]            = df["price"].round(6)
    df["price_change_24h"] = df["price_change_24h"].round(2)
    df["market_cap"]       = df["market_cap"].round(0)
    df["volume"]           = df["volume"].round(0)

    # Ensure no nulls in critical fields
    df["coin_name"] = df["coin_name"].fillna("Unknown")
    df["symbol"]    = df["symbol"].fillna("???")

    return df


def store_data(df: pd.DataFrame):
    """
    Inserts cleaned DataFrame rows into the crypto_prices table.
    """
    if df.empty:
        print("  ⚠️  No data to store.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    records = df[[
        "coin_name", "symbol", "price",
        "market_cap", "volume", "price_change_24h", "timestamp"
    ]].values.tolist()

    cursor.executemany("""
        INSERT INTO crypto_prices
            (coin_name, symbol, price, market_cap, volume, price_change_24h, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    conn.close()
    print(f"  ✅ Stored {len(records)} records to database.")


# ── Read helpers for dashboard ─────────────────────────────────────────────────

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
    """Returns top N gainers from the latest snapshot."""
    df = get_latest_prices()
    return df.nlargest(n, "price_change_24h")


def get_top_losers(n: int = 5) -> pd.DataFrame:
    """Returns top N losers from the latest snapshot."""
    df = get_latest_prices()
    return df.nsmallest(n, "price_change_24h")


if __name__ == "__main__":
    from scripts.fetch_data import fetch_crypto_data
    coins = fetch_crypto_data()
    df    = clean_data(coins)
    store_data(df)
    print("\nLatest Prices (Top 5):")
    print(get_latest_prices().head())
