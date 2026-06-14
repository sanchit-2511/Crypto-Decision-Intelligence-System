"""
db_connection.py
----------------
V4: Added ml_predictions table.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crypto.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            insight_text TEXT    NOT NULL,
            created_at   TEXT    NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coin_signals (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol            TEXT    NOT NULL,
            rsi               REAL,
            sma_7             REAL,
            sma_14            REAL,
            volatility_score  REAL,
            volatility_label  TEXT,
            signal            TEXT,
            timestamp         TEXT    NOT NULL
        )
    """)

    # V4: ML predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_predictions (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol               TEXT    NOT NULL,
            predicted_direction  TEXT,
            confidence_pct       REAL,
            model_accuracy       REAL,
            training_samples     INTEGER,
            timestamp            TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("  ✅ Database initialized successfully.")


if __name__ == "__main__":
    init_db()
    print(f"  DB location: {os.path.abspath(DB_PATH)}")
