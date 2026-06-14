"""
app.py — Streamlit Dashboard
Version 4 (Final): ML Predictions tab + Feature Importance chart
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
from scripts.ml_pipeline import run_ml_pipeline
from models.predict import get_latest_predictions, get_feature_importances

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
    .alert-card  { border-radius:10px; padding:14px 18px; margin-bottom:10px; font-size:0.9rem; }
    .alert-buy   { background:#0d3320; border-left:4px solid #00e676; }
    .alert-sell  { background:#3d0e0e; border-left:4px solid #ff5252; }
    .alert-risk  { background:#2d1a00; border-left:4px solid #ff9800; }
    .pred-up     { background:#0d3320; border-left:4px solid #00e676; border-radius:8px; padding:12px 16px; margin-bottom:8px; }
    .pred-down   { background:#3d0e0e; border-left:4px solid #ff5252; border-radius:8px; padding:12px 16px; margin-bottom:8px; }
    .health-bar  { font-size:0.8rem; color:#888; }
    .disclaimer  { background:#1a1a1a; border:1px solid #333; border-radius:8px;
                   padding:10px 14px; font-size:0.8rem; color:#888; margin-top:12px; }
</style>
""", unsafe_allow_html=True)

# ── Init ───────────────────────────────────────────────────────────────────────
init_db()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🚀 Crypto Decision Intelligence System")
st.caption("Live data · RSI · SMA · Signals · Smart Insights · ML Predictions · Version 4.0 (Final)")

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
        with st.spinner("Training ML models + predicting..."):
            run_ml_pipeline()
        st.success("✅ Full pipeline complete!")
        st.rerun()

    st.divider()
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
df_prices      = get_latest_prices()
df_signals     = get_latest_signals()
df_predictions = get_latest_predictions()

if df_prices.empty:
    st.warning("No data yet — click **Refresh & Analyse** in the sidebar to get started.")
    st.stop()

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Live Market",
    "🧠 Intelligence",
    "🔔 Alerts",
    "🤖 ML Predictions",
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
        "coin_name":"Coin","symbol":"Symbol","price":"Price (USD)",
        "market_cap":"Market Cap","volume":"24h Volume",
        "price_change_24h":"24h Change","timestamp":"Last Updated"
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
# TAB 2 — INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if df_enriched.empty:
        st.info("No signals yet — click Refresh & Analyse.")
    else:
        buy_c  = (df_enriched["signal"] == "🟢 BUY").sum()
        sell_c = (df_enriched["signal"] == "🔴 SELL").sum()
        hold_c = (df_enriched["signal"] == "🟡 HOLD").sum()
        na_c   = (df_enriched["signal"] == "⚪ Insufficient Data").sum()

        s1,s2,s3,s4 = st.columns(4)
        s1.metric("🟢 BUY", buy_c); s2.metric("🔴 SELL", sell_c)
        s3.metric("🟡 HOLD", hold_c); s4.metric("⚪ N/A", na_c)

        st.divider()
        st.subheader("🎯 Intelligence Board")

        f1,f2,f3,f4 = st.columns([1.2,1.2,1.2,1.4])
        with f1: sig_filter = st.selectbox("Signal", ["All","🟢 BUY","🔴 SELL","🟡 HOLD","⚪ Insufficient Data"])
        with f2: vol_filter = st.selectbox("Volatility", ["All","🟢 Low","🟡 Medium","🔴 High"])
        with f3: rsi_min, rsi_max = st.slider("RSI Range", 0, 100, (0, 100))
        with f4: search = st.text_input("🔍 Search coin", placeholder="e.g. BTC, ETH...")

        merged = df_enriched.merge(
            df_prices[["symbol","coin_name","price","price_change_24h"]], on="symbol", how="left"
        )
        filtered = merged.copy()
        if sig_filter != "All": filtered = filtered[filtered["signal"] == sig_filter]
        if vol_filter != "All": filtered = filtered[filtered["volatility_label"] == vol_filter]
        if search:
            q = search.upper()
            filtered = filtered[
                filtered["symbol"].str.upper().str.contains(q) |
                filtered["coin_name"].str.upper().str.contains(q)
            ]
        rsi_mask = filtered["rsi"].isna() | ((filtered["rsi"] >= rsi_min) & (filtered["rsi"] <= rsi_max))
        filtered = filtered[rsi_mask]

        st.caption(f"Showing {len(filtered)} coins")
        board = filtered[["coin_name","symbol","price","price_change_24h","rsi",
                           "volatility_label","signal","confidence","reason","risk_note"]].copy()
        board["price"]            = board["price"].apply(lambda x: f"${x:,.4f}" if pd.notna(x) else "—")
        board["price_change_24h"] = board["price_change_24h"].apply(
            lambda x: f"+{x:.2f}%" if pd.notna(x) and x>=0 else f"{x:.2f}%" if pd.notna(x) else "—")
        board["rsi"] = board["rsi"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
        board = board.rename(columns={
            "coin_name":"Coin","symbol":"Symbol","price":"Price","price_change_24h":"24h Δ",
            "rsi":"RSI","volatility_label":"Volatility","signal":"Signal",
            "confidence":"Confidence","reason":"Why?","risk_note":"Risk Note"
        })
        st.dataframe(board, use_container_width=True, hide_index=True,
                     column_config={"Why?": st.column_config.TextColumn(width="large"),
                                    "Risk Note": st.column_config.TextColumn(width="medium")})

        st.divider()
        st.subheader("📡 RSI Overview")
        rsi_df = merged.dropna(subset=["rsi"]).copy()
        fig_rsi = px.bar(rsi_df.sort_values("rsi"), x="symbol", y="rsi",
                         color="rsi", color_continuous_scale=["#ff5252","#ffd600","#ffd600","#00e676"],
                         range_color=[0,100], title="RSI by Coin  (< 35 Oversold 🟢 | > 65 Overbought 🔴)")
        fig_rsi.add_hline(y=35, line_dash="dash", line_color="#00e676", annotation_text="Oversold (35)")
        fig_rsi.add_hline(y=65, line_dash="dash", line_color="#ff5252", annotation_text="Overbought (65)")
        fig_rsi.update_layout(height=400, xaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig_rsi, use_container_width=True)

        st.subheader("🌊 Volatility Ranking")
        vol_df = merged.dropna(subset=["volatility_score"]).copy()
        vol_df["volatility_score"] = pd.to_numeric(vol_df["volatility_score"], errors="coerce")
        vol_df = vol_df.nlargest(20, "volatility_score")
        fig_vol = px.bar(vol_df, x="symbol", y="volatility_score",
                         color="volatility_score",
                         color_continuous_scale=["#00e676","#ffd600","#ff5252"],
                         title="Top 20 Most Volatile Coins")
        fig_vol.update_layout(height=360, coloraxis_showscale=False,
                              xaxis_title="", yaxis_title="Volatility Score (%)")
        st.plotly_chart(fig_vol, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ALERTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔔 Smart Alerts")
    if df_enriched.empty:
        st.info("No alerts yet — run the pipeline first.")
    else:
        merged_alerts = df_enriched.merge(
            df_prices[["symbol","coin_name","price","price_change_24h"]], on="symbol", how="left"
        )

        st.markdown("### 🟢 Top BUY Opportunities")
        buys = merged_alerts[merged_alerts["signal"] == "🟢 BUY"].sort_values("confidence_score", ascending=False)
        if buys.empty:
            st.info("No BUY signals in current snapshot.")
        else:
            for _, row in buys.head(5).iterrows():
                st.markdown(f"""<div class='alert-card alert-buy'>
                    <strong>{row['coin_name']} ({row['symbol']})</strong>
                    &nbsp;·&nbsp; ${row['price']:,.4f}
                    &nbsp;·&nbsp; {row['price_change_24h']:+.2f}%
                    &nbsp;·&nbsp; Confidence: {row['confidence']}<br>
                    <span style='color:#aaa'>📋 {row['reason']}</span><br>
                    <span style='color:#aaa'>⚡ {row['risk_note']}</span>
                </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🔴 SELL Signals & High Risk Coins")
        sells     = merged_alerts[merged_alerts["signal"] == "🔴 SELL"]
        high_risk = merged_alerts[
            merged_alerts["volatility_label"].str.contains("High", na=False) &
            (merged_alerts["signal"] != "🟢 BUY")
        ]
        risk_combined = pd.concat([sells, high_risk]).drop_duplicates(subset="symbol")
        if risk_combined.empty:
            st.info("No SELL signals or high-risk coins detected.")
        else:
            for _, row in risk_combined.head(5).iterrows():
                label = "SELL Signal" if row["signal"] == "🔴 SELL" else "High Volatility"
                st.markdown(f"""<div class='alert-card alert-sell'>
                    <strong>{row['coin_name']} ({row['symbol']})</strong>
                    &nbsp;·&nbsp; [{label}]
                    &nbsp;·&nbsp; ${row['price']:,.4f}
                    &nbsp;·&nbsp; Confidence: {row['confidence']}<br>
                    <span style='color:#aaa'>📋 {row['reason']}</span><br>
                    <span style='color:#aaa'>⚡ {row['risk_note']}</span>
                </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### ⚡ Strong Momentum Coins")
        if "rsi" in merged_alerts.columns:
            momentum = merged_alerts.dropna(subset=["rsi"]).copy()
            momentum["rsi"] = pd.to_numeric(momentum["rsi"], errors="coerce")
            momentum["rsi_distance"] = abs(momentum["rsi"] - 50)
            for _, row in momentum.nlargest(5, "rsi_distance").iterrows():
                direction = "🔼 Upward" if row["rsi"] > 50 else "🔽 Downward"
                st.markdown(f"""<div class='alert-card alert-risk'>
                    <strong>{row['coin_name']} ({row['symbol']})</strong>
                    &nbsp;·&nbsp; RSI: {row['rsi']:.1f}
                    &nbsp;·&nbsp; Momentum: {direction}
                    &nbsp;·&nbsp; Signal: {row['signal']}<br>
                    <span style='color:#aaa'>⚡ {row['risk_note']}</span>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ML PREDICTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🤖 ML Price Direction Predictions")
    st.caption("Random Forest Classifier trained on RSI, SMA, Volatility, Price Change & Volume.")

    st.markdown("""<div class='disclaimer'>
        ⚠️ <strong>Disclaimer:</strong> Predictions are based on historical price patterns
        and are for <strong>educational purposes only</strong>. They do not constitute
        financial advice. Crypto markets are highly unpredictable.
    </div>""", unsafe_allow_html=True)
    st.write("")

    if df_predictions.empty:
        st.info("No predictions yet — click **Refresh & Analyse** to train models and generate predictions.\n\n"
                "Models require a minimum of **20 snapshots** per coin to train.")
    else:
        # Summary KPIs
        up_count   = (df_predictions["predicted_direction"] == "🔼 Up").sum()
        down_count = (df_predictions["predicted_direction"] == "🔽 Down").sum()
        avg_conf   = df_predictions["confidence_pct"].mean()
        avg_acc    = df_predictions["model_accuracy"].mean()

        k1,k2,k3,k4 = st.columns(4)
        k1.metric("🔼 Predicted Up",     up_count)
        k2.metric("🔽 Predicted Down",   down_count)
        k3.metric("📊 Avg Confidence",   f"{avg_conf:.1f}%" if pd.notna(avg_conf) else "—")
        k4.metric("🎯 Avg Model Accuracy", f"{avg_acc:.1f}%" if pd.notna(avg_acc) else "—")

        st.divider()

        # Merge with coin names + current signals
        pred_merged = df_predictions.merge(
            df_prices[["symbol","coin_name","price","price_change_24h"]], on="symbol", how="left"
        )
        if not df_signals.empty:
            pred_merged = pred_merged.merge(
                df_signals[["symbol","signal"]], on="symbol", how="left"
            )

        # Filter: direction
        dir_filter = st.selectbox("Filter by prediction:", ["All","🔼 Up","🔽 Down"])
        if dir_filter != "All":
            pred_merged = pred_merged[pred_merged["predicted_direction"] == dir_filter]

        st.subheader("📋 Prediction Board")
        board_cols = ["coin_name","symbol","price","predicted_direction",
                      "confidence_pct","model_accuracy","training_samples"]
        if "signal" in pred_merged.columns:
            board_cols.append("signal")

        board = pred_merged[board_cols].copy()
        board["price"]           = board["price"].apply(lambda x: f"${x:,.4f}" if pd.notna(x) else "—")
        board["confidence_pct"]  = board["confidence_pct"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        board["model_accuracy"]  = board["model_accuracy"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        board["training_samples"]= board["training_samples"].apply(lambda x: int(x) if pd.notna(x) else "—")

        rename = {
            "coin_name":"Coin","symbol":"Symbol","price":"Price",
            "predicted_direction":"Prediction","confidence_pct":"Confidence",
            "model_accuracy":"Model Accuracy","training_samples":"Trained On","signal":"Current Signal"
        }
        board = board.rename(columns={k:v for k,v in rename.items() if k in board.columns})
        st.dataframe(board, use_container_width=True, hide_index=True)

        st.divider()

        # Confidence distribution chart
        st.subheader("📊 Prediction Confidence Distribution")
        fig_conf = px.histogram(
            df_predictions.dropna(subset=["confidence_pct"]),
            x="confidence_pct", nbins=20,
            color_discrete_sequence=["#7c4dff"],
            labels={"confidence_pct": "Confidence (%)"},
            title="How confident is the model across all predictions?"
        )
        fig_conf.update_layout(height=320, xaxis_title="Confidence (%)", yaxis_title="Number of Coins")
        st.plotly_chart(fig_conf, use_container_width=True)

        st.divider()

        # Feature importance chart
        st.subheader("🔍 Feature Importance — What the Model Relies On")
        st.caption("Average importance across all trained models. Shows which indicators drive predictions most.")
        feat_df = get_feature_importances()
        if not feat_df.empty:
            fig_feat = px.bar(
                feat_df, x="Importance", y="Feature",
                orientation="h",
                color="Importance",
                color_continuous_scale=["#2a2a4a","#7c4dff","#00d4ff"],
                title="Feature Importance (averaged across all coin models)"
            )
            fig_feat.update_layout(
                height=380, coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                xaxis_title="Importance Score", yaxis_title=""
            )
            st.plotly_chart(fig_feat, use_container_width=True)
        else:
            st.info("Feature importance data will appear after models are trained.")

        # Signal vs Prediction alignment
        if "signal" in pred_merged.columns and not pred_merged.empty:
            st.divider()
            st.subheader("🔗 Signal vs Prediction Alignment")
            st.caption("Where rule-based signals and ML predictions agree — highest conviction opportunities.")
            aligned = pred_merged[
                ((pred_merged["signal"] == "🟢 BUY") & (pred_merged["predicted_direction"] == "🔼 Up")) |
                ((pred_merged["signal"] == "🔴 SELL") & (pred_merged["predicted_direction"] == "🔽 Down"))
            ].copy()
            if aligned.empty:
                st.info("No aligned signals and predictions in the current snapshot.")
            else:
                aligned_display = aligned[["Coin","Symbol","Price","Prediction",
                                           "Confidence","Current Signal"]].copy() if "Coin" in aligned.columns else aligned
                st.dataframe(aligned_display, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TREND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("📈 Price Trend + Moving Averages")
    available_symbols = sorted(df_prices["symbol"].tolist())
    selected = st.selectbox("Select coin:", available_symbols, key="trend_selector")
    history  = get_price_history(selected)

    if len(history) < 2:
        st.info(f"Not enough data for **{selected}** yet — {len(history)} snapshot(s). "
                f"Run the pipeline more to build the trend.")
    else:
        history["timestamp"] = pd.to_datetime(history["timestamp"])
        prices_s = history["price"].astype(float)
        sma7_s   = prices_s.rolling(window=7).mean()
        sma14_s  = prices_s.rolling(window=14).mean()

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=prices_s, mode="lines", name="Price",
            line=dict(color="#00d4ff", width=2),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.05)"
        ))
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=sma7_s, mode="lines", name="SMA 7",
            line=dict(color="#ffd600", width=1.5, dash="dot")
        ))
        fig_trend.add_trace(go.Scatter(
            x=history["timestamp"], y=sma14_s, mode="lines", name="SMA 14",
            line=dict(color="#ff6b35", width=1.5, dash="dash")
        ))
        fig_trend.update_layout(
            xaxis_title="Time", yaxis_title="Price (USD)", height=450,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        st.divider()
        ca,cb,cc,cd = st.columns(4)
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
st.caption("🤖 Crypto Decision Intelligence System · v4.0 Final · Random Forest · Smart Insights · Built with Python + Streamlit")
