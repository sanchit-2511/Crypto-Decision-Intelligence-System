"""
app.py — Streamlit Dashboard
-----------------------------
Version 1: Live prices, top gainers/losers, price trend chart.
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os

# Path setup so imports work from anywhere
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.db_connection import init_db
from scripts.fetch_data import fetch_crypto_data
from scripts.process_data import (
    clean_data, store_data,
    get_latest_prices, get_price_history,
    get_top_gainers, get_top_losers
)

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Intelligence System",
    page_icon="🚀",
    layout="wide"
)

# ── Init DB on first run ───────────────────────────────────────────────────────
init_db()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🚀 Crypto Decision Intelligence System")
st.caption("Live market data · Auto-updated · Version 1.0")
st.divider()

# ── Sidebar Controls ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Refresh Data Now", use_container_width=True):
        with st.spinner("Fetching from CoinGecko..."):
            coins = fetch_crypto_data()
            df    = clean_data(coins)
            store_data(df)
        st.success("Data updated!")

    st.divider()
    st.markdown("**Data Source:** CoinGecko API")
    st.markdown("**DB:** SQLite (local)")
    st.markdown("**Top N coins:** 50")

# ── Load Data ──────────────────────────────────────────────────────────────────
df = get_latest_prices()

if df.empty:
    st.warning("No data yet. Click **Refresh Data Now** in the sidebar to fetch live prices.")
    st.stop()

# ── KPI Cards (Row 1) ──────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_market_cap = df["market_cap"].sum()
total_volume     = df["volume"].sum()
gainers_count    = (df["price_change_24h"] > 0).sum()
losers_count     = (df["price_change_24h"] < 0).sum()

col1.metric("🌐 Total Market Cap",  f"${total_market_cap/1e12:.2f}T")
col2.metric("📊 24h Total Volume",  f"${total_volume/1e9:.1f}B")
col3.metric("📈 Gainers (24h)",     f"{gainers_count} coins")
col4.metric("📉 Losers (24h)",      f"{losers_count} coins")

st.divider()

# ── Live Prices Table ──────────────────────────────────────────────────────────
st.subheader("💰 Live Prices — Top 50 Coins")

display_df = df.copy()
display_df["price"]            = display_df["price"].apply(lambda x: f"${x:,.4f}")
display_df["market_cap"]       = display_df["market_cap"].apply(lambda x: f"${x/1e9:.2f}B")
display_df["volume"]           = display_df["volume"].apply(lambda x: f"${x/1e9:.2f}B")
display_df["price_change_24h"] = display_df["price_change_24h"].apply(
    lambda x: f"🟢 +{x:.2f}%" if x >= 0 else f"🔴 {x:.2f}%"
)

display_df = display_df.rename(columns={
    "coin_name":        "Coin",
    "symbol":           "Symbol",
    "price":            "Price (USD)",
    "market_cap":       "Market Cap",
    "volume":           "24h Volume",
    "price_change_24h": "24h Change",
    "timestamp":        "Last Updated"
})

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

# ── Top Gainers & Losers (Side by Side) ───────────────────────────────────────
col_g, col_l = st.columns(2)

with col_g:
    st.subheader("🏆 Top 5 Gainers")
    gainers = get_top_gainers(5)
    fig_g = px.bar(
        gainers,
        x="symbol",
        y="price_change_24h",
        color="price_change_24h",
        color_continuous_scale="Greens",
        labels={"price_change_24h": "24h Change (%)", "symbol": "Coin"},
        text=gainers["price_change_24h"].apply(lambda x: f"+{x:.2f}%")
    )
    fig_g.update_traces(textposition="outside")
    fig_g.update_layout(showlegend=False, coloraxis_showscale=False, height=350)
    st.plotly_chart(fig_g, use_container_width=True)

with col_l:
    st.subheader("💀 Top 5 Losers")
    losers = get_top_losers(5)
    fig_l = px.bar(
        losers,
        x="symbol",
        y="price_change_24h",
        color="price_change_24h",
        color_continuous_scale="Reds_r",
        labels={"price_change_24h": "24h Change (%)", "symbol": "Coin"},
        text=losers["price_change_24h"].apply(lambda x: f"{x:.2f}%")
    )
    fig_l.update_traces(textposition="outside")
    fig_l.update_layout(showlegend=False, coloraxis_showscale=False, height=350)
    st.plotly_chart(fig_l, use_container_width=True)

st.divider()

# ── Price Trend Chart ──────────────────────────────────────────────────────────
st.subheader("📈 Price Trend — Historical View")

available_symbols = sorted(df["symbol"].tolist())
selected_coin = st.selectbox("Select a coin:", available_symbols, index=0)

history = get_price_history(selected_coin)

if len(history) < 2:
    st.info(f"Not enough history for **{selected_coin}** yet. Refresh a few more times to build the trend line.")
else:
    history["timestamp"] = pd.to_datetime(history["timestamp"])
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=history["timestamp"],
        y=history["price"],
        mode="lines+markers",
        name=selected_coin,
        line=dict(color="#00d4ff", width=2),
        fill="tozeroy",
        fillcolor="rgba(0, 212, 255, 0.08)"
    ))
    fig_trend.update_layout(
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        height=400,
        hovermode="x unified"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()
st.caption("🤖 Crypto Decision Intelligence System · v1.0 · Data: CoinGecko API · Built with Python + Streamlit")
