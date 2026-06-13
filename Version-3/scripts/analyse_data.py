"""
analyse_data.py
---------------
Version 2 — Indicator Engine
Computes RSI, SMA (7 & 14), and Volatility for each coin
using historical data stored in the database.

Requires minimum 14 snapshots per coin for meaningful signals.
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from scripts.process_data import get_price_history, get_latest_prices

# ── Constants ──────────────────────────────────────────────────────────────────
MIN_DATA_POINTS   = 14    # Minimum snapshots needed for RSI & SMA14
RSI_PERIOD        = 14
SMA_SHORT         = 7
SMA_LONG          = 14
VOLATILITY_LOW    = 1.0   # % std dev below this  → Low
VOLATILITY_HIGH   = 3.0   # % std dev above this  → High


# ── RSI ────────────────────────────────────────────────────────────────────────

def compute_rsi(prices: pd.Series, period: int = RSI_PERIOD) -> float:
    """
    Computes RSI (Relative Strength Index) for a price series.
    Returns a float 0–100, or None if insufficient data.
    """
    if len(prices) < period + 1:
        return None

    delta  = prices.diff().dropna()
    gains  = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.rolling(window=period).mean().iloc[-1]
    avg_loss = losses.rolling(window=period).mean().iloc[-1]

    if avg_loss == 0:
        return 100.0  # No losses → fully overbought

    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


# ── Moving Averages ────────────────────────────────────────────────────────────

def compute_sma(prices: pd.Series, window: int) -> float:
    """
    Computes Simple Moving Average for the last `window` prices.
    Returns the latest SMA value, or None if insufficient data.
    """
    if len(prices) < window:
        return None
    return round(prices.rolling(window=window).mean().iloc[-1], 6)


# ── Volatility ─────────────────────────────────────────────────────────────────

def compute_volatility(prices: pd.Series) -> tuple:
    """
    Computes volatility as the coefficient of variation (std/mean * 100).
    Returns (score: float, label: str) or (None, 'Insufficient Data').
    """
    if len(prices) < 5:
        return None, "Insufficient Data"

    score = (prices.std() / prices.mean()) * 100
    score = round(score, 4)

    if score < VOLATILITY_LOW:
        label = "🟢 Low"
    elif score < VOLATILITY_HIGH:
        label = "🟡 Medium"
    else:
        label = "🔴 High"

    return score, label


# ── Main Analyser ──────────────────────────────────────────────────────────────

def analyse_coin(symbol: str) -> dict:
    """
    Runs all indicators for a single coin.
    Returns a dict with all computed metrics.
    """
    history = get_price_history(symbol)

    result = {
        "symbol":           symbol,
        "rsi":              None,
        "sma_7":            None,
        "sma_14":           None,
        "volatility_score": None,
        "volatility_label": "Insufficient Data",
        "data_points":      len(history),
        "status":           "ok"
    }

    if history.empty or len(history) < 2:
        result["status"] = "insufficient_data"
        return result

    prices = history["price"].astype(float)

    # RSI
    result["rsi"] = compute_rsi(prices)

    # Moving Averages
    result["sma_7"]  = compute_sma(prices, SMA_SHORT)
    result["sma_14"] = compute_sma(prices, SMA_LONG)

    # Volatility
    result["volatility_score"], result["volatility_label"] = compute_volatility(prices)

    return result


def analyse_all_coins() -> pd.DataFrame:
    """
    Runs analysis on all coins that have historical data.
    Returns a DataFrame with indicators for every coin.
    """
    latest = get_latest_prices()
    if latest.empty:
        print("  ⚠️  No coins found in database.")
        return pd.DataFrame()

    print(f"  🔬 Analysing {len(latest)} coins...")
    results = []

    for symbol in latest["symbol"]:
        result = analyse_coin(symbol)
        results.append(result)

    df = pd.DataFrame(results)
    print(f"  ✅ Analysis complete.")
    return df


if __name__ == "__main__":
    df = analyse_all_coins()
    print("\nSample output (first 5 coins):")
    print(df[["symbol", "rsi", "sma_7", "sma_14", "volatility_label", "data_points"]].head())
