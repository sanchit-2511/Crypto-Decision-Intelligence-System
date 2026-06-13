"""
app.py — Streamlit Dashboard
Version 3: Market Summary · Smart Insights · Alerts · Advanced Filters · Sparklines
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
    clean_data, store_data, get_latest_prices,
    get_price_history, get_top_gainers, get_top_losers, get_data_health
)
from scripts.signal_engine import generate_signals, store_signals, get_latest_signals
from scripts.generate_insights import (
    generate_coin_insights, generate_market_summary,
    store_insights, get_latest_insight
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Intelligence System",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
    .summary-box {
        background: linear-gradient(135deg, #0d1b2a, #1a2a4a);
        border: 1px solid #2a4a7a;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 8px;
        line-height: 1.7;
    }
    .alert-card {
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    .alert-buy  { background: #0d3320; border-left: 4px solid #00e676; }
    .alert-sell { background: #3d0e0e; border-left: 4px solid #ff5252; }
    .alert-risk { background: #2d1a00; border-left: 4px solid #ff9800; }
    .health-bar { font-size: 0.8rem; color: #888; }
</style>
""", unsafe_allow_html=True)

# ── Init ───────────────────────────────────────────────────────────────────────
init_db()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🚀 Crypto Decision Intelligence System")
st.caption("Live data · RSI · SMA · Signals · Smart Insights · Version 3.0")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Refresh & Analyse", use_container_width=True, type="primary"):
        with st.spinner("Fetching from CoinGecko..."):
            coins = fetch_crypto_data()
            df_raw, health = clean_data(coins)
            store_data(df_raw)
        with st.spinner("Running indicators + signals..."):
            sig_df = generate_signals()
            store_signals(sig_df)
        with st.spinner("Generating insights..."):
            prices_df = get_latest_prices()
            generate_coin_insights(sig_df)
            summary = generate_market_summary(sig_df, prices_df)
            store_insights(summary)
        st.success("✅ All done!")
        st.rerun()

    st.divider()

    # Data health indicator
    health_data = get_data_health()
    st.markdown("**🗄 Data Health**")
    st.markdown(f"<div class='health-bar'>Coins tracked: {health_data['total_coins']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='health-bar'>Total records: {health_data['total_records']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='health-bar'>Signals stored: {health_data['total_signals']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='health-bar'>Last fetch: {health_data['last_fetch']}</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("**Signal Guide**")
    st.markdown("🟢 **BUY** — RSI < 35 + SMA7 > SMA14")
    st.markdown("🔴 **SELL** — RSI > 65 + SMA7 < SMA14")
    st.markdown("🟡 **HOLD** — Everything else")
    st.markdown("⚪ **N/A** — Insufficient history")

# ── Load data ──────────────────────────────────────────────────────────────────
df_prices  = get_latest_prices()
df_signals = get_latest_signals()

if df_prices.empty:
    st.warning("No data yet — click **Refresh & Analyse** in the sidebar to get started.")
    st.stop()

# Enrich signals with insights
if not df_signals.empty:
    df_enriched = generate_coin_insights(df_signals)
else:
    df_enriched = pd.DataFrame()

# ── Market Summary Card ────────────────────────────────────────────────────────
summary_text = get_latest_insight()
if summary_text:
    st.markdown(f"<div class='summary-box'>{summary_text}</div>", unsafe_allow_html=True)
    st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Live Market",
    "🧠 Intelligence",
    "🔔 Alerts",
    "📈 Trend Analysis"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE MARKET
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌐 Market Cap",  f"${df_prices['market_cap'].sum()/1e12:.2f}T")
    c2.metric("📊 24h Volume",  f"${df_prices['volume'].sum()/1e9:.1f}B")
    c3.metric("📈 Gainers",     f"{(df_prices['price_change_24h'] > 0).sum()} coins")
    c4.metric("📉 Losers",      f"{(df_prices['price_change_24h'] < 0).sum()} coins")

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
    col_g, col_l = st.columns(2)

    with col_g:
        st.subheader("🏆 Top 5 Gainers")
        gainers = get_top_gainers(5)
        fig_g = px.bar(gainers, x="symbol", y="price_change_24h",
                       color="price_change_24h", color_continuous_scale="Greens",
                       text=gainers["price_change_24h"].apply(lambda x: f"+{x:.2f}%"))
        fig_g.update_traces(textposition="outside")
        fig_g.update_layout(showlegend=False, coloraxis_showscale=False,
                            height=350, xaxis_title="", yaxis_title="24h Change (%)")
        st.plotly_chart(fig_g, use_container_width=True)

    with col_l:
        st.subheader("💀 Top 5 Losers")
        losers = get_top_losers(5)
        fig_l = px.bar(losers, x="symbol", y="price_change_24h",
                       color="price_change_24h", color_continuous_scale="Reds_r",
                       text=losers["price_change_24h"].apply(lambda x: f"{x:.2f}%"))
        fig_l.update_traces(textposition="outside")
        fig_l.update_layout(showlegend=False, coloraxis_showscale=False,
                            height=350, xaxis_title="", yaxis_title="24h Change (%)")
        st.plotly_chart(fig_l, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — INTELLIGENCE (Signal Board + Smart Insights)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if df_enriched.empty:
        st.info("No signals yet — click Refresh & Analyse to generate intelligence.")
    else:
        # Summary metrics
        buy_c  = (df_enriched["signal"] == "🟢 BUY").sum()
        sell_c = (df_enriched["signal"] == "🔴 SELL").sum()
        hold_c = (df_enriched["signal"] == "🟡 HOLD").sum()
        na_c   = (df_enriched["signal"] == "⚪ Insufficient Data").sum()

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("🟢 BUY",  buy_c)
        s2.metric("🔴 SELL", sell_c)
        s3.metric("🟡 HOLD", hold_c)
        s4.metric("⚪ N/A",  na_c)

        st.divider()
        st.subheader("🎯 Intelligence Board")
        st.caption("Signals with AI-generated explanations and confidence levels.")

        # ── Filters ───────────────────────────────────────────────────────────
        f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.2, 1.4])

        with f1:
            sig_filter = st.selectbox("Signal", ["All", "🟢 BUY", "🔴 SELL", "🟡 HOLD", "⚪ Insufficient Data"])
        with f2:
            vol_filter = st.selectbox("Volatility", ["All", "🟢 Low", "🟡 Medium", "🔴 High"])
        with f3:
            rsi_min, rsi_max = st.slider("RSI Range", 0, 100, (0, 100))
        with f4:
            search = st.text_input("🔍 Search coin", placeholder="e.g. BTC, ETH...")

        # Merge with prices for coin names
        merged = df_enriched.merge(
            df_prices[["symbol", "coin_name", "price", "price_change_24h"]],
            on="symbol", how="left"
        )

        # Apply filters
        filtered = merged.copy()
        if sig_filter != "All":
            filtered = filtered[filtered["signal"] == sig_filter]
        if vol_filter != "All":
            filtered = filtered[filtered["volatility_label"] == vol_filter]
        if search:
            q = search.upper()
            filtered = filtered[
                filtered["symbol"].str.upper().str.contains(q) |
                filtered["coin_name"].str.upper().str.contains(q)
            ]
        # RSI filter (only on rows where RSI is not None)
        rsi_mask = filtered["rsi"].isna() | (
            (filtered["rsi"] >= rsi_min) & (filtered["rsi"] <= rsi_max)
        )
        filtered = filtered[rsi_mask]

        st.caption(f"Showing {len(filtered)} coins")

        # Build display table
        board = filtered[[
            "coin_name", "symbol", "price", "price_change_24h",
            "rsi", "volatility_label", "signal", "confidence", "reason", "risk_note"
        ]].copy()

        board["price"]            = board["price"].apply(lambda x: f"${x:,.4f}" if pd.notna(x) else "—")
        board["price_change_24h"] = board["price_change_24h"].apply(
            lambda x: f"+{x:.2f}%" if pd.notna(x) and x >= 0 else f"{x:.2f}%" if pd.notna(x) else "—"
        )
        board["rsi"] = board["rsi"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")

        board = board.rename(columns={
            "coin_name": "Coin", "symbol": "Symbol", "price": "Price",
            "price_change_24h": "24h Δ", "rsi": "RSI",
            "volatility_label": "Volatility", "signal": "Signal",
            "confidence": "Confidence", "reason": "Why?", "risk_note": "Risk Note"
        })

        st.dataframe(board, use_container_width=True, hide_index=True,
                     column_config={
                         "Why?": st.column_config.TextColumn(width="large"),
                         "Risk Note": st.column_config.TextColumn(width="medium"),
                     })

        st.divider()

        # RSI Overview chart
        st.subheader("📡 RSI Overview")
        rsi_df = merged.dropna(subset=["rsi"]).copy()
        fig_rsi = px.bar(
            rsi_df.sort_values("rsi"), x="symbol", y="rsi",
            color="rsi", color_continuous_scale=["#ff5252", "#ffd600", "#ffd600", "#00e676"],
            range_color=[0, 100],
            title="RSI by Coin  (< 35 = Oversold 🟢  |  > 65 = Overbought 🔴)"
        )
        fig_rsi.add_hline(y=35, line_dash="dash", line_color="#00e676", annotation_text="Oversold (35)")
        fig_rsi.add_hline(y=65, line_dash="dash", line_color="#ff5252", annotation_text="Overbought (65)")
        fig_rsi.update_layout(height=400, xaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig_rsi, use_container_width=True)

        # Volatility ranking
        st.subheader("🌊 Volatility Ranking")
        vol_df = merged.dropna(subset=["volatility_score"]).copy()
        vol_df["volatility_score"] = pd.to_numeric(vol_df["volatility_score"], errors="coerce")
        vol_df = vol_df.nlargest(20, "volatility_score")
        fig_vol = px.bar(
            vol_df, x="symbol", y="volatility_score",
            color="volatility_score",
            color_continuous_scale=["#00e676", "#ffd600", "#ff5252"],
            title="Top 20 Most Volatile Coins"
        )
        fig_vol.update_layout(height=380, coloraxis_showscale=False,
                              xaxis_title="", yaxis_title="Volatility Score (%)")
        st.plotly_chart(fig_vol, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ALERTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔔 Smart Alerts")
    st.caption("Rule-based alerts derived from signal intelligence.")

    if df_enriched.empty:
        st.info("No alerts yet — run the pipeline to generate signals first.")
    else:
        merged_alerts = df_enriched.merge(
            df_prices[["symbol", "coin_name", "price", "price_change_24h"]],
            on="symbol", how="left"
        )

        # ── Section 1: Top BUY Opportunities ──────────────────────────────────
        st.markdown("### 🟢 Top BUY Opportunities")
        buys = merged_alerts[merged_alerts["signal"] == "🟢 BUY"].copy()
        if buys.empty:
            st.info("No BUY signals in the current snapshot.")
        else:
            # Sort by confidence score
            buys = buys.sort_values("confidence_score", ascending=False)
            for _, row in buys.head(5).iterrows():
                st.markdown(f"""
                <div class='alert-card alert-buy'>
                    <strong>{row['coin_name']} ({row['symbol']})</strong>
                    &nbsp;·&nbsp; Price: ${row['price']:,.4f}
                    &nbsp;·&nbsp; 24h: {row['price_change_24h']:+.2f}%
                    &nbsp;·&nbsp; Confidence: {row['confidence']}<br>
                    <span style='color:#aaa'>📋 {row['reason']}</span><br>
                    <span style='color:#aaa'>⚡ {row['risk_note']}</span>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ── Section 2: SELL / High Risk ───────────────────────────────────────
        st.markdown("### 🔴 SELL Signals & High Risk Coins")
        sells = merged_alerts[merged_alerts["signal"] == "🔴 SELL"].copy()
        high_risk = merged_alerts[
            merged_alerts["volatility_label"].str.contains("High", na=False) &
            (merged_alerts["signal"] != "🟢 BUY")
        ].copy()
        risk_combined = pd.concat([sells, high_risk]).drop_duplicates(subset="symbol")

        if risk_combined.empty:
            st.info("No SELL signals or high-risk coins detected.")
        else:
            risk_combined = risk_combined.sort_values("confidence_score", ascending=False)
            for _, row in risk_combined.head(5).iterrows():
                label = "SELL Signal" if row["signal"] == "🔴 SELL" else "High Volatility"
                st.markdown(f"""
                <div class='alert-card alert-sell'>
                    <strong>{row['coin_name']} ({row['symbol']})</strong>
                    &nbsp;·&nbsp; [{label}]
                    &nbsp;·&nbsp; Price: ${row['price']:,.4f}
                    &nbsp;·&nbsp; Confidence: {row['confidence']}<br>
                    <span style='color:#aaa'>📋 {row['reason']}</span><br>
                    <span style='color:#aaa'>⚡ {row['risk_note']}</span>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ── Section 3: Strong Momentum ────────────────────────────────────────
        st.markdown("### ⚡ Strong Momentum Coins")
        st.caption("Coins with RSI moving strongly in either direction.")

        if "rsi" in merged_alerts.columns:
            momentum = merged_alerts.dropna(subset=["rsi"]).copy()
            momentum["rsi"] = pd.to_numeric(momentum["rsi"], errors="coerce")
            momentum["rsi_distance"] = abs(momentum["rsi"] - 50)
            strong = momentum.nlargest(5, "rsi_distance")

            if strong.empty:
                st.info("No strong momentum signals detected.")
            else:
                for _, row in strong.iterrows():
                    direction = "🔼 Upward" if row["rsi"] > 50 else "🔽 Downward"
                    st.markdown(f"""
                    <div class='alert-card alert-risk'>
                        <strong>{row['coin_name']} ({row['symbol']})</strong>
                        &nbsp;·&nbsp; RSI: {row['rsi']:.1f}
                        &nbsp;·&nbsp; Momentum: {direction}
                        &nbsp;·&nbsp; Signal: {row['signal']}<br>
                        <span style='color:#aaa'>⚡ {row['risk_note']}</span>
                    </div>
                    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TREND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📈 Price Trend + Moving Averages")
    st.caption("Price history with SMA7 and SMA14 overlaid. Builds richer over time.")

    available_symbols = sorted(df_prices["symbol"].tolist())
    selected = st.selectbox("Select coin:", available_symbols, key="trend_selector")

    history = get_price_history(selected)

    if len(history) < 2:
        st.info(f"Not enough data for **{selected}** yet — currently {len(history)} snapshot(s). "
                f"Run the pipeline a few more times to build the trend.")
    else:
        history["timestamp"] = pd.to_datetime(history["timestamp"])
        prices_s = history["price"].astype(float)

        sma7_s  = prices_s.rolling(window=7).mean()
        sma14_s = prices_s.rolling(window=14).mean()

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=prices_s, mode="lines",
            name="Price", line=dict(color="#00d4ff", width=2),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.05)"
        ))
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=sma7_s, mode="lines",
            name="SMA 7", line=dict(color="#ffd600", width=1.5, dash="dot")
        ))
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=sma14_s, mode="lines",
            name="SMA 14", line=dict(color="#ff6b35", width=1.5, dash="dash")
        ))
        fig_trend.update_layout(
            xaxis_title="Time", yaxis_title="Price (USD)",
            height=450, hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        st.divider()
        ca, cb, cc, cd = st.columns(4)
        ca.metric("📸 Snapshots",    len(history))
        cb.metric("💰 Latest Price", f"${prices_s.iloc[-1]:,.4f}")
        cc.metric("📉 Min Price",    f"${prices_s.min():,.4f}")
        cd.metric("📈 Max Price",    f"${prices_s.max():,.4f}")

        if "volume" in history.columns:
            st.subheader(f"📊 Volume History — {selected}")
            fig_vol2 = px.bar(history, x="timestamp", y="volume",
                              color_discrete_sequence=["#7c4dff"])
            fig_vol2.update_layout(height=250, xaxis_title="", yaxis_title="Volume (USD)")
            st.plotly_chart(fig_vol2, use_container_width=True)

st.divider()
st.caption("🤖 Crypto Decision Intelligence System · v3.0 · Smart Insights · Alerts · Built with Python + Streamlit")
