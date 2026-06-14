"""
train_model.py
--------------
V4 — ML Training Engine
Trains a Random Forest Classifier per coin using historical price data.
Label: will the next price be higher (1 = Up) or lower (0 = Down)?

Features used:
  - RSI
  - SMA 7 & SMA 14
  - SMA crossover (SMA7 - SMA14)
  - Volatility score
  - Price change 24h
  - Volume (normalized)

Minimum 20 data points required per coin to train.
Saves trained models to /models/saved/ as .pkl files.
"""

import pandas as pd
import numpy as np
import os
import sys
import pickle

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

from database.db_connection import get_connection

# ── Constants ──────────────────────────────────────────────────────────────────
MIN_SAMPLES   = 20      # Minimum rows needed to train
SAVED_DIR     = os.path.join(os.path.dirname(__file__), "saved")
RSI_PERIOD    = 14
SMA_SHORT     = 7
SMA_LONG      = 14


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes raw price history DataFrame and engineers all ML features.
    Returns DataFrame with feature columns + label column.
    """
    df = df.copy().reset_index(drop=True)
    df["price"]  = pd.to_numeric(df["price"],  errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)

    # ── RSI ───────────────────────────────────────────────────────────────────
    delta      = df["price"].diff()
    gain       = delta.clip(lower=0)
    loss       = -delta.clip(upper=0)
    avg_gain   = gain.rolling(RSI_PERIOD).mean()
    avg_loss   = loss.rolling(RSI_PERIOD).mean()
    rs         = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"]  = 100 - (100 / (1 + rs))

    # ── Moving Averages + Crossover ───────────────────────────────────────────
    df["sma_7"]        = df["price"].rolling(SMA_SHORT).mean()
    df["sma_14"]       = df["price"].rolling(SMA_LONG).mean()
    df["sma_crossover"]= df["sma_7"] - df["sma_14"]

    # ── Volatility ────────────────────────────────────────────────────────────
    df["volatility"]   = df["price"].rolling(7).std() / df["price"].rolling(7).mean() * 100

    # ── Price change % ────────────────────────────────────────────────────────
    df["price_change"] = df["price"].pct_change() * 100

    # ── Volume normalized ─────────────────────────────────────────────────────
    vol_mean           = df["volume"].mean()
    df["volume_norm"]  = df["volume"] / vol_mean if vol_mean > 0 else 0

    # ── Label: next price direction ───────────────────────────────────────────
    # 1 = next price higher than current (Up), 0 = Down
    df["label"] = (df["price"].shift(-1) > df["price"]).astype(int)

    return df


def train_coin_model(symbol: str) -> dict:
    """
    Trains a Random Forest model for a single coin.
    Returns result dict with model, accuracy, feature importances, etc.
    """
    # Fetch history
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT timestamp, price, volume
        FROM crypto_prices
        WHERE symbol = ?
        ORDER BY timestamp ASC
    """, conn, params=(symbol,))
    conn.close()

    if len(df) < MIN_SAMPLES:
        return {
            "symbol":  symbol,
            "status":  "insufficient_data",
            "samples": len(df),
            "message": f"Need {MIN_SAMPLES} snapshots, have {len(df)}"
        }

    # Feature engineering
    df = build_features(df)

    feature_cols = ["rsi", "sma_7", "sma_14", "sma_crossover",
                    "volatility", "price_change", "volume_norm"]

    df_clean = df.dropna(subset=feature_cols + ["label"])

    if len(df_clean) < MIN_SAMPLES:
        return {
            "symbol":  symbol,
            "status":  "insufficient_data",
            "samples": len(df_clean),
            "message": "Not enough clean rows after feature engineering"
        }

    X = df_clean[feature_cols].values
    y = df_clean["label"].values

    # Train / test split — use 80% train, 20% test
    # If not enough for split, train on all and report
    if len(X) >= 25:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
    else:
        X_train, X_test = X, X
        y_train, y_test = y, y

    # Train Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    # Accuracy
    y_pred   = model.predict(X_test)
    accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)

    # Feature importances
    importances = dict(zip(feature_cols, model.feature_importances_.round(4)))

    # Save model
    os.makedirs(SAVED_DIR, exist_ok=True)
    model_path = os.path.join(SAVED_DIR, f"{symbol}.pkl")
    with open(model_path, "wb") as f:
        pickle.dump({
            "model":        model,
            "feature_cols": feature_cols,
            "accuracy":     accuracy,
            "importances":  importances
        }, f)

    return {
        "symbol":       symbol,
        "status":       "trained",
        "samples":      len(df_clean),
        "accuracy":     accuracy,
        "importances":  importances,
        "model_path":   model_path
    }


def train_all_models() -> list:
    """
    Trains models for all coins that have enough historical data.
    Returns list of result dicts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT symbol FROM crypto_prices")
    symbols = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"  🏋️  Training models for {len(symbols)} coins...")
    results = []
    trained = 0
    skipped = 0

    for symbol in symbols:
        result = train_coin_model(symbol)
        results.append(result)
        if result["status"] == "trained":
            trained += 1
        else:
            skipped += 1

    print(f"  ✅ Trained: {trained} | ⏭️  Skipped (insufficient data): {skipped}")
    return results


if __name__ == "__main__":
    results = train_all_models()
    trained = [r for r in results if r["status"] == "trained"]
    if trained:
        print("\nSample trained models:")
        for r in trained[:5]:
            print(f"  {r['symbol']:6s} | Accuracy: {r['accuracy']}% | Samples: {r['samples']}")
