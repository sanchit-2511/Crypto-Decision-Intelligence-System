"""
predict.py
----------
V4 — Prediction Engine
Loads saved Random Forest models and generates next-direction
predictions for the latest snapshot of each coin.

Returns: predicted direction (Up/Down), confidence %, model accuracy.
"""

import pandas as pd
import numpy as np
import os
import sys
import pickle
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.db_connection import get_connection
from models.train_model import build_features

SAVED_DIR = os.path.join(os.path.dirname(__file__), "saved")

# Minimum probability gap from 50% to call a confident prediction
CONFIDENCE_THRESHOLD = 0.0   # Always show prediction, surface confidence in UI


def load_model(symbol: str) -> dict | None:
    """Loads saved model for a coin. Returns None if not found."""
    model_path = os.path.join(SAVED_DIR, f"{symbol}.pkl")
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as f:
        return pickle.load(f)


def predict_coin(symbol: str) -> dict:
    """
    Generates a prediction for a single coin using its saved model.
    Returns a prediction result dict.
    """
    model_data = load_model(symbol)
    if model_data is None:
        return {
            "symbol":              symbol,
            "status":              "no_model",
            "predicted_direction": "⚪ Insufficient Data",
            "confidence_pct":      None,
            "model_accuracy":      None,
            "training_samples":    None
        }

    model        = model_data["model"]
    feature_cols = model_data["feature_cols"]
    accuracy     = model_data["accuracy"]

    # Fetch recent price history (need enough for feature engineering)
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT timestamp, price, volume
        FROM crypto_prices
        WHERE symbol = ?
        ORDER BY timestamp ASC
    """, conn, params=(symbol,))
    conn.close()

    if len(df) < 15:
        return {
            "symbol":              symbol,
            "status":              "insufficient_data",
            "predicted_direction": "⚪ Insufficient Data",
            "confidence_pct":      None,
            "model_accuracy":      accuracy,
            "training_samples":    None
        }

    # Build features and take the latest row
    df_feat = build_features(df)
    df_feat = df_feat.dropna(subset=feature_cols)

    if df_feat.empty:
        return {
            "symbol":              symbol,
            "status":              "insufficient_data",
            "predicted_direction": "⚪ Insufficient Data",
            "confidence_pct":      None,
            "model_accuracy":      accuracy,
            "training_samples":    None
        }

    latest_features = df_feat[feature_cols].iloc[[-1]].values

    # Predict
    proba      = model.predict_proba(latest_features)[0]
    pred_class = int(np.argmax(proba))
    confidence = round(float(max(proba)) * 100, 1)

    direction = "🔼 Up" if pred_class == 1 else "🔽 Down"

    return {
        "symbol":              symbol,
        "status":              "predicted",
        "predicted_direction": direction,
        "confidence_pct":      confidence,
        "model_accuracy":      accuracy,
        "training_samples":    len(df_feat)
    }


def predict_all_coins() -> pd.DataFrame:
    """
    Runs predictions for all coins that have saved models.
    Returns a DataFrame of predictions.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT symbol FROM crypto_prices")
    symbols = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"  🔮 Generating predictions for {len(symbols)} coins...")
    results = []

    for symbol in symbols:
        result = predict_coin(symbol)
        results.append(result)

    df = pd.DataFrame(results)
    predicted = (df["status"] == "predicted").sum()
    print(f"  ✅ Predicted: {predicted} | ⚪ Skipped: {len(df) - predicted}")
    return df


def store_predictions(df: pd.DataFrame):
    """Saves prediction results into the ml_predictions table."""
    if df.empty:
        return

    conn   = get_connection()
    cursor = conn.cursor()
    now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stored = 0

    for _, row in df.iterrows():
        if row["status"] != "predicted":
            continue
        cursor.execute("""
            INSERT INTO ml_predictions
                (symbol, predicted_direction, confidence_pct, model_accuracy, training_samples, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row["symbol"],
            row["predicted_direction"],
            row["confidence_pct"],
            row["model_accuracy"],
            row["training_samples"],
            now
        ))
        stored += 1

    conn.commit()
    conn.close()
    print(f"  ✅ Stored {stored} predictions.")


def get_latest_predictions() -> pd.DataFrame:
    """Returns the most recent prediction for each coin. Used by dashboard."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT symbol, predicted_direction, confidence_pct,
               model_accuracy, training_samples, timestamp
        FROM ml_predictions
        WHERE timestamp = (SELECT MAX(timestamp) FROM ml_predictions)
        ORDER BY confidence_pct DESC
    """, conn)
    conn.close()
    return df


def get_feature_importances() -> pd.DataFrame:
    """
    Aggregates feature importances across all saved models.
    Returns average importance per feature — used for the dashboard chart.
    """
    if not os.path.exists(SAVED_DIR):
        return pd.DataFrame()

    model_files = [f for f in os.listdir(SAVED_DIR) if f.endswith(".pkl")]
    if not model_files:
        return pd.DataFrame()

    all_importances = []
    for fname in model_files:
        path = os.path.join(SAVED_DIR, fname)
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            all_importances.append(data["importances"])
        except Exception:
            continue

    if not all_importances:
        return pd.DataFrame()

    imp_df  = pd.DataFrame(all_importances)
    avg_imp = imp_df.mean().reset_index()
    avg_imp.columns = ["Feature", "Importance"]
    avg_imp = avg_imp.sort_values("Importance", ascending=False)

    # Clean feature names for display
    name_map = {
        "rsi":           "RSI",
        "sma_7":         "SMA 7",
        "sma_14":        "SMA 14",
        "sma_crossover": "SMA Crossover",
        "volatility":    "Volatility",
        "price_change":  "Price Change %",
        "volume_norm":   "Volume (norm)"
    }
    avg_imp["Feature"] = avg_imp["Feature"].map(name_map).fillna(avg_imp["Feature"])
    return avg_imp


if __name__ == "__main__":
    df = predict_all_coins()
    store_predictions(df)

    print("\n🔮 Sample Predictions:")
    predicted = df[df["status"] == "predicted"]
    if not predicted.empty:
        print(predicted[["symbol", "predicted_direction", "confidence_pct", "model_accuracy"]
              ].head(10).to_string(index=False))
