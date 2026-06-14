"""
generate_insights.py
--------------------
V3 — Smart Insights Engine
Generates human-readable explanations for every signal.
Includes confidence level based on how many conditions aligned.
Also generates a Market Summary paragraph.
No external API needed — pure rule-based intelligence.
"""

import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database.db_connection import get_connection
from scripts.signal_engine import get_latest_signals
from scripts.process_data import get_latest_prices


# ── Insight Builder ────────────────────────────────────────────────────────────

def build_insight(row: pd.Series) -> dict:
    """
    Takes one coin's signal row and returns a rich insight dict with:
    - reason: why this signal fired
    - confidence: Strong / Moderate / Weak
    - confidence_score: 0–100
    - risk_note: volatility context
    """
    signal   = row.get("signal", "")
    rsi      = row.get("rsi")
    sma_7    = row.get("sma_7")
    sma_14   = row.get("sma_14")
    vol_label = row.get("volatility_label", "")

    # ── Insufficient data ──────────────────────────────────────────────────────
    if "Insufficient" in str(signal) or pd.isna(rsi):
        return {
            "reason":           "Not enough historical data to generate a signal yet.",
            "confidence":       "N/A",
            "confidence_score": 0,
            "risk_note":        "Collect more data by running the pipeline regularly."
        }

    reasons      = []
    score_parts  = []

    # ── RSI analysis ──────────────────────────────────────────────────────────
    if rsi < 30:
        reasons.append(f"RSI at {rsi:.1f} — strongly oversold territory")
        score_parts.append(40)
    elif rsi < 35:
        reasons.append(f"RSI at {rsi:.1f} — oversold conditions detected")
        score_parts.append(30)
    elif rsi > 70:
        reasons.append(f"RSI at {rsi:.1f} — strongly overbought territory")
        score_parts.append(40)
    elif rsi > 65:
        reasons.append(f"RSI at {rsi:.1f} — overbought conditions detected")
        score_parts.append(30)
    else:
        reasons.append(f"RSI at {rsi:.1f} — neutral momentum zone")
        score_parts.append(10)

    # ── SMA crossover analysis ─────────────────────────────────────────────────
    if sma_7 is not None and sma_14 is not None:
        diff_pct = ((sma_7 - sma_14) / sma_14) * 100 if sma_14 != 0 else 0
        if sma_7 > sma_14:
            reasons.append(
                f"Bullish MA crossover — SMA7 is {abs(diff_pct):.2f}% above SMA14"
            )
            score_parts.append(35)
        elif sma_7 < sma_14:
            reasons.append(
                f"Bearish MA crossover — SMA7 is {abs(diff_pct):.2f}% below SMA14"
            )
            score_parts.append(35)
        else:
            reasons.append("SMA7 and SMA14 are converging — no clear crossover yet")
            score_parts.append(10)

    # ── Volatility context ────────────────────────────────────────────────────
    vol_clean = vol_label.replace("🟢 ", "").replace("🟡 ", "").replace("🔴 ", "")
    if "Low" in vol_clean:
        risk_note = "🟢 Low volatility — trend is stable and reliable"
        score_parts.append(25)
    elif "Medium" in vol_clean:
        risk_note = "🟡 Medium volatility — moderate risk, monitor closely"
        score_parts.append(15)
    elif "High" in vol_clean:
        risk_note = "🔴 High volatility — signal carries elevated risk"
        score_parts.append(5)
    else:
        risk_note = "Volatility data unavailable"
        score_parts.append(10)

    # ── Confidence calculation ─────────────────────────────────────────────────
    confidence_score = min(sum(score_parts), 100)

    if confidence_score >= 70:
        confidence = "💪 Strong"
    elif confidence_score >= 40:
        confidence = "👍 Moderate"
    else:
        confidence = "⚠️ Weak"

    reason_text = " · ".join(reasons)

    return {
        "reason":           reason_text,
        "confidence":       confidence,
        "confidence_score": confidence_score,
        "risk_note":        risk_note
    }


def generate_coin_insights(signals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs build_insight() on every coin in the signals DataFrame.
    Returns an enriched DataFrame with insight columns added.
    """
    if signals_df.empty:
        return signals_df

    insights = signals_df.apply(build_insight, axis=1, result_type="expand")
    enriched = pd.concat([signals_df, insights], axis=1)
    return enriched


# ── Market Summary ─────────────────────────────────────────────────────────────

def generate_market_summary(signals_df: pd.DataFrame, prices_df: pd.DataFrame) -> str:
    """
    Generates a single auto-written paragraph summarizing the current market state.
    Pure rule-based text — no external API.
    """
    if signals_df.empty or prices_df.empty:
        return "Market summary unavailable — run the pipeline to fetch data."

    now = datetime.now().strftime("%B %d, %Y at %H:%M")

    # Signal counts
    buy_count  = (signals_df["signal"] == "🟢 BUY").sum()
    sell_count = (signals_df["signal"] == "🔴 SELL").sum()
    hold_count = (signals_df["signal"] == "🟡 HOLD").sum()
    total_sig  = buy_count + sell_count + hold_count

    # Overall market tone
    if buy_count > sell_count and buy_count > hold_count:
        tone = "bullish"
        tone_emoji = "🟢"
    elif sell_count > buy_count and sell_count > hold_count:
        tone = "bearish"
        tone_emoji = "🔴"
    else:
        tone = "mixed / neutral"
        tone_emoji = "🟡"

    # Volatility distribution
    high_vol   = signals_df["volatility_label"].str.contains("High",   na=False).sum()
    medium_vol = signals_df["volatility_label"].str.contains("Medium", na=False).sum()
    low_vol    = signals_df["volatility_label"].str.contains("Low",    na=False).sum()

    if high_vol > medium_vol and high_vol > low_vol:
        vol_summary = "Overall market volatility is elevated — caution advised."
    elif low_vol > medium_vol and low_vol > high_vol:
        vol_summary = "Overall market volatility is low — conditions are relatively stable."
    else:
        vol_summary = "Overall market volatility is moderate."

    # BTC / ETH specific note
    btc_signal = signals_df[signals_df["symbol"] == "BTC"]["signal"].values
    eth_signal = signals_df[signals_df["symbol"] == "ETH"]["signal"].values
    major_note = ""
    if len(btc_signal) > 0 and len(eth_signal) > 0:
        major_note = (
            f"Major assets: BTC is showing a {btc_signal[0]} signal "
            f"and ETH is at {eth_signal[0]}."
        )
    elif len(btc_signal) > 0:
        major_note = f"BTC is currently showing a {btc_signal[0]} signal."

    # Top gainer
    if not prices_df.empty:
        top_gainer = prices_df.nlargest(1, "price_change_24h").iloc[0]
        gainer_note = (
            f"Top performer in the last 24h: {top_gainer['coin_name']} "
            f"({top_gainer['symbol']}) with +{top_gainer['price_change_24h']:.2f}%."
        )
    else:
        gainer_note = ""

    summary = (
        f"{tone_emoji} **Market Snapshot — {now}**\n\n"
        f"As of this update, the market is showing a **{tone}** tone. "
        f"Out of {total_sig} tracked coins with active signals, "
        f"**{buy_count} are in BUY territory**, {sell_count} are in SELL territory, "
        f"and {hold_count} are holding neutral. "
        f"{vol_summary} "
        f"{major_note} "
        f"{gainer_note}"
    )

    return summary.strip()


# ── Store Insights ─────────────────────────────────────────────────────────────

def store_insights(summary: str):
    """Saves the market summary into the insights table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO insights (insight_text, created_at)
        VALUES (?, ?)
    """, (summary, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    print("  ✅ Market summary stored.")


def get_latest_insight() -> str:
    """Returns the most recent market summary from the DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT insight_text FROM insights
        ORDER BY created_at DESC LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    return row["insight_text"] if row else ""


if __name__ == "__main__":
    from scripts.signal_engine import get_latest_signals
    from scripts.process_data import get_latest_prices

    signals = get_latest_signals()
    prices  = get_latest_prices()

    enriched = generate_coin_insights(signals)
    summary  = generate_market_summary(signals, prices)
    store_insights(summary)

    print("\n📊 Sample Insights:")
    cols = ["symbol", "signal", "confidence", "reason"]
    available = [c for c in cols if c in enriched.columns]
    print(enriched[available].head(10).to_string(index=False))

    print(f"\n📝 Market Summary:\n{summary}")
