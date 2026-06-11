"""
app.py — Streamlit Dashboard
-----------------------------
Version 2: Tabbed layout — Live Market | Intelligence | Trend Analysis
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.db_connection import init_db
from scripts.fetch_data import fetch_crypto_data
from scripts.process_data import (
    clean_data, store_data,
    get_latest_prices, get_price_history,
    get_top_gainers, get_top_losers
)
from scripts.signal_engine import generate_signals, store_signals, get_latest_signals
from scripts.analyse_data import compute_sma

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Intelligence System",
    page_icon="🚀",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .signal-buy  { background:#0d3320; color:#00e676; padding:4px 12px;
                   border-radius:20px; font-weight:700; font-size:0.85rem; }
    .signal-sell { background:#3d0e0e; color:#ff5252; padding:4px 12px;
                   border-radius:20px; font-weight:700; font-size:0.85rem; }
    .signal-hold { background:#2d2d00; color:#ffd600; padding:4px 12px;
                   border-radius:20px; font-weight:700; font-size:0.85rem; }
    .signal-na   { background:#1e1e1e; color:#888;    padding:4px 12px;
                   border-radius:20px; font-weight:700; font-size:0.85rem; }
    .metric-card { background:#1a1a2e; border-radius:12px; padding:16px;
                   text-align:center; border:1px solid #2a2a4a; }
</style>
""", unsafe_allow_html=True)

# ── Init ───────────────────────────────────────────────────────────────────────
init_db()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🚀 Crypto Decision Intelligence System")
st.caption("Live market data · RSI · Moving Averages · Buy/Sell/Hold Signals · Version 2.0")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Refresh & Analyse", use_container_width=True, type="primary"):
        with st.spinner("Fetching from CoinGecko..."):
            coins = fetch_crypto_data()
            df_raw = clean_data(coins)
            store_data(df_raw)
        with st.spinner("Running indicator analysis..."):
            sig_df = generate_signals()
            store_signals(sig_df)
        st.success("✅ Data + signals updated!")
        st.rerun()

    st.divider()
    st.markdown("**Data Source:** CoinGecko API")
    st.markdown("**Indicators:** RSI · SMA7 · SMA14")
    st.markdown("**Signal Logic:** Rule-based")
    st.divider()
    st.markdown("**Signal Guide**")
    st.markdown("🟢 **BUY** — RSI < 35 + SMA7 > SMA14")
    st.markdown("🔴 **SELL** — RSI > 65 + SMA7 < SMA14")
    st.markdown("🟡 **HOLD** — Everything else")
    st.markdown("⚪ **N/A** — Need more data")

# ── Load data ──────────────────────────────────────────────────────────────────
df_prices  = get_latest_prices()
df_signals = get_latest_signals()

if df_prices.empty:
    st.warning("No data yet — click **Refresh & Analyse** in the sidebar.")
    st.stop()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Live Market", "🧠 Intelligence", "📈 Trend Analysis"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE MARKET
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # KPI cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌐 Market Cap",    f"${df_prices['market_cap'].sum()/1e12:.2f}T")
    c2.metric("📊 24h Volume",    f"${df_prices['volume'].sum()/1e9:.1f}B")
    c3.metric("📈 Gainers",       f"{(df_prices['price_change_24h'] > 0).sum()} coins")
    c4.metric("📉 Losers",        f"{(df_prices['price_change_24h'] < 0).sum()} coins")

    st.divider()
    st.subheader("💰 Live Prices — Top 50 Coins")

    display = df_prices.copy()
    display["price"]            = display["price"].apply(lambda x: f"${x:,.4f}")
    display["market_cap"]       = display["market_cap"].apply(lambda x: f"${x/1e9:.2f}B")
    display["volume"]           = display["volume"].apply(lambda x: f"${x/1e9:.2f}B")
    display["price_change_24h"] = display["price_change_24h"].apply(
        lambda x: f"🟢 +{x:.2f}%" if x >= 0 else f"🔴 {x:.2f}%"
    )
    display = display.rename(columns={
        "coin_name": "Coin", "symbol": "Symbol", "price": "Price (USD)",
        "market_cap": "Market Cap", "volume": "24h Volume",
        "price_change_24h": "24h Change", "timestamp": "Last Updated"
    })
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.divider()

    # Gainers / Losers
    col_g, col_l = st.columns(2)

    with col_g:
        st.subheader("🏆 Top 5 Gainers")
        gainers = get_top_gainers(5)
        fig_g = px.bar(
            gainers, x="symbol", y="price_change_24h",
            color="price_change_24h", color_continuous_scale="Greens",
            text=gainers["price_change_24h"].apply(lambda x: f"+{x:.2f}%")
        )
        fig_g.update_traces(textposition="outside")
        fig_g.update_layout(showlegend=False, coloraxis_showscale=False,
                            height=350, xaxis_title="", yaxis_title="24h Change (%)")
        st.plotly_chart(fig_g, use_container_width=True)

    with col_l:
        st.subheader("💀 Top 5 Losers")
        losers = get_top_losers(5)
        fig_l = px.bar(
            losers, x="symbol", y="price_change_24h",
            color="price_change_24h", color_continuous_scale="Reds_r",
            text=losers["price_change_24h"].apply(lambda x: f"{x:.2f}%")
        )
        fig_l.update_traces(textposition="outside")
        fig_l.update_layout(showlegend=False, coloraxis_showscale=False,
                            height=350, xaxis_title="", yaxis_title="24h Change (%)")
        st.plotly_chart(fig_l, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — INTELLIGENCE (Signal Board)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    if df_signals.empty:
        st.info("No signals yet — click **Refresh & Analyse** to generate signals.\n\n"
                "Signals improve as more historical data is collected (min 14 snapshots per coin).")
    else:
        # Signal summary cards
        buy_count  = (df_signals["signal"] == "🟢 BUY").sum()
        sell_count = (df_signals["signal"] == "🔴 SELL").sum()
        hold_count = (df_signals["signal"] == "🟡 HOLD").sum()
        na_count   = (df_signals["signal"] == "⚪ Insufficient Data").sum()

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("🟢 BUY Signals",  buy_count)
        s2.metric("🔴 SELL Signals", sell_count)
        s3.metric("🟡 HOLD Signals", hold_count)
        s4.metric("⚪ Need More Data", na_count)

        st.divider()
        st.subheader("🎯 Signal Board")

        # Merge signals with coin names
        merged = df_signals.merge(
            df_prices[["symbol", "coin_name", "price", "price_change_24h"]],
            on="symbol", how="left"
        )

        # Build display table
        board = merged[[
            "coin_name", "symbol", "price", "price_change_24h",
            "rsi", "sma_7", "sma_14", "volatility_label", "signal"
        ]].copy()

        board["price"]            = board["price"].apply(lambda x: f"${x:,.4f}" if pd.notna(x) else "—")
        board["price_change_24h"] = board["price_change_24h"].apply(
            lambda x: f"+{x:.2f}%" if pd.notna(x) and x >= 0 else f"{x:.2f}%" if pd.notna(x) else "—"
        )
        board["rsi"]   = board["rsi"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
        board["sma_7"] = board["sma_7"].apply(lambda x: f"${x:,.4f}" if pd.notna(x) else "—")
        board["sma_14"]= board["sma_14"].apply(lambda x: f"${x:,.4f}" if pd.notna(x) else "—")

        board = board.rename(columns={
            "coin_name": "Coin", "symbol": "Symbol", "price": "Price",
            "price_change_24h": "24h Δ", "rsi": "RSI",
            "sma_7": "SMA 7", "sma_14": "SMA 14",
            "volatility_label": "Volatility", "signal": "Signal"
        })

        # Filter controls
        filter_col1, filter_col2 = st.columns([1, 3])
        with filter_col1:
            signal_filter = st.selectbox(
                "Filter by signal:",
                ["All", "🟢 BUY", "🔴 SELL", "🟡 HOLD", "⚪ Insufficient Data"]
            )

        if signal_filter != "All":
            board = board[board["Signal"] == signal_filter]

        st.dataframe(board, use_container_width=True, hide_index=True)

        st.divider()

        # Volatility ranking chart
        st.subheader("🌊 Volatility Ranking")
        vol_df = merged.dropna(subset=["volatility_score"]).copy()
        vol_df["volatility_score"] = pd.to_numeric(vol_df["volatility_score"], errors="coerce")
        vol_df = vol_df.nlargest(20, "volatility_score")

        fig_vol = px.bar(
            vol_df, x="symbol", y="volatility_score",
            color="volatility_score",
            color_continuous_scale=["#00e676", "#ffd600", "#ff5252"],
            labels={"volatility_score": "Volatility Score", "symbol": "Coin"},
            title="Top 20 Most Volatile Coins"
        )
        fig_vol.update_layout(
            height=400, coloraxis_showscale=False,
            xaxis_title="", yaxis_title="Volatility Score (%)"
        )
        st.plotly_chart(fig_vol, use_container_width=True)

        # RSI heatmap-style bar
        st.subheader("📡 RSI Overview")
        rsi_df = merged.dropna(subset=["rsi"]).copy()

        fig_rsi = px.bar(
            rsi_df.sort_values("rsi"), x="symbol", y="rsi",
            color="rsi",
            color_continuous_scale=["#ff5252", "#ffd600", "#ffd600", "#00e676"],
            range_color=[0, 100],
            labels={"rsi": "RSI", "symbol": "Coin"},
            title="RSI by Coin  (< 35 = Oversold 🟢  |  > 65 = Overbought 🔴)"
        )
        fig_rsi.add_hline(y=35, line_dash="dash", line_color="#00e676",
                          annotation_text="Oversold (35)")
        fig_rsi.add_hline(y=65, line_dash="dash", line_color="#ff5252",
                          annotation_text="Overbought (65)")
        fig_rsi.update_layout(height=420, xaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig_rsi, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TREND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📈 Price Trend + Moving Averages")
    st.caption("Select a coin to see its price history overlaid with SMA 7 and SMA 14.")

    available_symbols = sorted(df_prices["symbol"].tolist())
    selected = st.selectbox("Select coin:", available_symbols, key="trend_selector")

    history = get_price_history(selected)

    if len(history) < 2:
        st.info(f"Not enough data for **{selected}** yet. Run the pipeline a few more times "
                f"to build the trend line. Currently have **{len(history)}** snapshot(s).")
    else:
        history["timestamp"] = pd.to_datetime(history["timestamp"])
        prices = history["price"].astype(float)

        # Compute MAs
        sma7_series  = prices.rolling(window=7).mean()
        sma14_series = prices.rolling(window=14).mean()

        fig_trend = go.Figure()

        # Price line
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=prices,
            mode="lines", name="Price",
            line=dict(color="#00d4ff", width=2),
            fill="tozeroy", fillcolor="rgba(0, 212, 255, 0.05)"
        ))

        # SMA 7
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=sma7_series,
            mode="lines", name="SMA 7",
            line=dict(color="#ffd600", width=1.5, dash="dot")
        ))

        # SMA 14
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=sma14_series,
            mode="lines", name="SMA 14",
            line=dict(color="#ff6b35", width=1.5, dash="dash")
        ))

        fig_trend.update_layout(
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            height=450,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Stats below chart
        st.divider()
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("📸 Snapshots",   len(history))
        col_b.metric("💰 Latest Price", f"${prices.iloc[-1]:,.4f}")
        col_c.metric("📉 Min Price",    f"${prices.min():,.4f}")
        col_d.metric("📈 Max Price",    f"${prices.max():,.4f}")

        # Volume chart
        if "volume" in history.columns:
            st.subheader(f"📊 Volume History — {selected}")
            fig_vol = px.bar(
                history, x="timestamp", y="volume",
                color_discrete_sequence=["#7c4dff"]
            )
            fig_vol.update_layout(height=250, xaxis_title="", yaxis_title="Volume (USD)")
            st.plotly_chart(fig_vol, use_container_width=True)

st.divider()
st.caption("🤖 Crypto Decision Intelligence System · v2.0 · RSI + SMA + Signal Engine · Built with Python + Streamlit")