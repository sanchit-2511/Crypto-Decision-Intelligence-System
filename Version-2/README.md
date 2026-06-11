# 🚀 Crypto Decision Intelligence System

> An automated crypto intelligence system that tracks, analyzes, and generates insights from live market data.

## 🧩 Problem Statement

Cryptocurrency markets are highly volatile and data-heavy, making it difficult for traders and analysts to track meaningful trends in real time.

While Version 1 solved the problem of **data collection and storage**, it lacked the ability to interpret that data — leaving users with raw numbers but no direction.

Version 2 addresses this by introducing a full **Intelligence Layer** — computing RSI, Moving Averages, and Volatility on top of historical data, and converting those indicators into clear **Buy / Sell / Hold signals** for every tracked coin.

## 🏗 Project Structure

```
crypto-intelligence-system/
├── data/                        # SQLite database lives here
├── scripts/
│   ├── fetch_data.py            # CoinGecko API → raw data
│   ├── process_data.py          # Clean + store + read helpers (V2: duplicate guard)
│   ├── analyse_data.py          # RSI · SMA 7 · SMA 14 · Volatility engine (NEW)
│   └── signal_engine.py         # Buy / Sell / Hold rule-based classifier (NEW)
├── database/
│   └── db_connection.py         # DB setup & connection (V2: coin_signals table)
├── dashboard/
│   └── app.py                   # Streamlit dashboard (V2: 3-tab layout)
├── models/                      # (Version 4 — ML)
├── scheduler/
│   └── run_pipeline.py          # Master pipeline orchestrator (V2: analyse + signal steps)
├── requirements.txt
└── README.md
```

## 🏗 System Architecture (Version 2)

Version 2 extends the V1 pipeline with an Indicator Engine and Signal Engine:

CoinGecko API → Data Fetching → Data Cleaning → SQLite Storage → Indicator Analysis → Signal Generation → Streamlit Dashboard

- **Fetch Layer**: Collects top 50 cryptocurrencies from CoinGecko (free, no API key)
- **Processing Layer**: Cleans, validates data, and prevents duplicate entries with a 60-second guard
- **Storage Layer**: Stores timestamped price records + computed signals in SQLite
- **Indicator Engine**: Computes RSI (14-period), SMA 7, SMA 14, and Volatility from price history
- **Signal Engine**: Applies rule-based logic to classify each coin as BUY / SELL / HOLD
- **Presentation Layer**: 3-tab Streamlit dashboard — Live Market, Intelligence Board, Trend Analysis

This design keeps each layer independent and fully extensible for V3 and V4.

## 📊 Dashboard Preview

> ![dashboard_img1](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/be2d266d1618332ec97dd9a8551d7e47f3abb89d/Version-2/images/dashboard_img1.png)

> ![dashboard_img2](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/be2d266d1618332ec97dd9a8551d7e47f3abb89d/Version-2/images/dashboard_img2.png)

> ![dashboard_img3](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/be2d266d1618332ec97dd9a8551d7e47f3abb89d/Version-2/images/dashboard_img3.png)

> ![dashboard_img4](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/be2d266d1618332ec97dd9a8551d7e47f3abb89d/Version-2/images/dashboard_img4.png)

> ![dashboard_img5](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/be2d266d1618332ec97dd9a8551d7e47f3abb89d/Version-2/images/dashboard_img5.png)

> ![dashboard_img6](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/be2d266d1618332ec97dd9a8551d7e47f3abb89d/Version-2/images/dashboard_img6.png)


## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run pipeline once (fetch + analyse + store signals)
python scheduler/run_pipeline.py

# 3. Launch the dashboard
streamlit run dashboard/app.py

# 4. (Optional) Run pipeline on auto-schedule every 5 min
python scheduler/run_pipeline.py --schedule
```

> **Note:** RSI and Moving Average signals require a minimum of **14 pipeline runs** per coin to become active. Until then, the Intelligence tab will show "Insufficient Data" — this is expected behaviour.

## 🧠 Intelligence Layer — How Signals Work

| Indicator | What it measures | Threshold |
|-----------|-----------------|-----------|
| RSI | Momentum — overbought or oversold | < 35 = Oversold · > 65 = Overbought |
| SMA 7 | Short-term price trend (7 snapshots) | Crossover with SMA 14 = direction signal |
| SMA 14 | Long-term price trend (14 snapshots) | Baseline for crossover comparison |
| Volatility | Price stability (std dev / mean) | Low < 1% · Medium 1–3% · High > 3% |

**Signal Rules:**
- 🟢 **BUY** — RSI < 35 AND SMA 7 > SMA 14 (oversold + bullish crossover)
- 🔴 **SELL** — RSI > 65 AND SMA 7 < SMA 14 (overbought + bearish crossover)
- 🟡 **HOLD** — Everything else
- ⚪ **Insufficient Data** — Less than 14 snapshots available

## ⚠️ Current Limitations (Version 2)

- Signals require multiple pipeline runs to activate (min 14 snapshots per coin)
- Signal logic is rule-based — no machine learning yet
- No auto-generated insight narratives yet
- No alerting or notification system
- No predictive modeling

These limitations will be addressed in upcoming versions.

## 🗺 Version Roadmap

| Version | Features | Status |
|---------|----------|--------|
| v1 | Data pipeline · Storage · Dashboard · Scheduling | ✅ Built |
| v2 | RSI · Moving Averages · Volatility · Buy/Sell/Hold Signals · 3-tab Dashboard | ✅ Built |
| v3 | Auto-generated insights · Market narratives | 🔜 Next |
| v4 | ML price prediction | 🔜 |

## 🛠 Tech Stack

- **Python** · **Pandas** · **NumPy** · **Requests**
- **SQLite** (database)
- **Streamlit + Plotly** (dashboard)
- **schedule** (automation)
- **CoinGecko API** (free, no key needed)
