"""
db_connection.py
----------------
Handles all SQLite database setup and connection.
Creates tables if they don't already exist.
"""

import sqlite3
import os

# DB lives in the /data folder
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crypto.db")


def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # Allows dict-like row access
    return conn


def init_db():
    """
    Creates all required tables if they don't exist.
    Safe to call multiple times (idempotent).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Table 1: crypto_prices ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_prices (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_name        TEXT    NOT NULL,
            symbol           TEXT    NOT NULL,
            price            REAL,
            market_cap       REAL,
            volume           REAL,
            price_change_24h REAL,
            timestamp        TEXT    NOT NULL
        )
    """)

    # --- Table 2: insights (used in Version 3) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            insight_text TEXT    NOT NULL,
            created_at   TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("  ✅ Database initialized successfully.")


if __name__ == "__main__":
    init_db()
    print(f"  DB location: {os.path.abspath(DB_PATH)}")
