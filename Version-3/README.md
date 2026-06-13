# 🚀 Crypto Decision Intelligence System

> An automated crypto intelligence system that tracks, analyzes, and generates insights from live market data.

## 🧩 Problem Statement

Cryptocurrency markets are highly volatile and data-heavy, making it difficult for traders and analysts to track meaningful trends in real time.

While Version 2 introduced a powerful **Intelligence Layer** with RSI, Moving Averages, and Buy/Sell/Hold signals, it still lacked the ability to *explain* those signals in human-readable form — leaving users with numbers and labels but no context.

Version 3 bridges that gap by introducing a **Smart Insights Engine** that auto-generates explanations for every signal, a **Market Summary Card** that narrates the overall market state, and a dedicated **Alerts System** — transforming the dashboard from a signal board into a true decision intelligence tool.

## 🏗 Project Structure

```
crypto-intelligence-system/
├── data/                        # SQLite database lives here
├── scripts/
│   ├── fetch_data.py            # CoinGecko API → raw data
│   ├── process_data.py          # Clean + store + read helpers (V3: data quality layer)
│   ├── analyse_data.py          # RSI · SMA 7 · SMA 14 · Volatility engine
│   ├── signal_engine.py         # Buy / Sell / Hold rule-based classifier
│   └── generate_insights.py     # Smart insights + confidence + market summary (NEW)
├── database/
│   └── db_connection.py         # DB setup & connection
├── dashboard/
│   └── app.py                   # Streamlit dashboard (V3: 4-tab layout + alerts)
├── models/                      # (Version 4 — ML)
├── scheduler/
│   └── run_pipeline.py          # Master pipeline orchestrator (V3: insights step added)
├── requirements.txt
└── README.md
```

## 🏗 System Architecture (Version 3)

Version 3 extends the V2 pipeline with a Smart Insights Engine and Alerts System:

CoinGecko API → Data Fetching → Data Cleaning → SQLite Storage → Indicator Analysis → Signal Generation → Insight Generation → Market Summary → Streamlit Dashboard

- **Fetch Layer**: Collects top 50 cryptocurrencies from CoinGecko (free, no API key)
- **Processing Layer**: Enhanced data quality — type enforcement, null handling, duplicate guard, and DB health tracking
- **Storage Layer**: Stores timestamped price records, computed signals, and generated insights in SQLite
- **Indicator Engine**: Computes RSI (14-period), SMA 7, SMA 14, and Volatility from price history
- **Signal Engine**: Applies rule-based logic to classify each coin as BUY / SELL / HOLD
- **Insight Engine**: Generates human-readable explanations + confidence levels for every signal (NEW)
- **Market Summary**: Auto-writes a market narrative paragraph on every pipeline run (NEW)
- **Presentation Layer**: 4-tab Streamlit dashboard — Live Market, Intelligence, Alerts, Trend Analysis

This design keeps each layer independent and fully extensible for V4.

## 📊 Dashboard Preview

New sections which have been added:-

>![dashboard_img](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/feddc2e55a407af8ca2f08ad584872fdc5c92e78/Version-3/images/dashboard_img5.png)

>![dashboard_img](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/feddc2e55a407af8ca2f08ad584872fdc5c92e78/Version-3/images/dashboard_img8.png)

>![dashboard_img](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/feddc2e55a407af8ca2f08ad584872fdc5c92e78/Version-3/images/dashboard_img9.png)


## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run pipeline once (fetch + analyse + signals + insights)
python scheduler/run_pipeline.py

# 3. Launch the dashboard
streamlit run dashboard/app.py

# 4. (Optional) Run pipeline on auto-schedule every 5 min
python scheduler/run_pipeline.py --schedule
```

> **Note:** RSI and Moving Average signals require a minimum of **14 pipeline runs** per coin to become active. Insights and confidence levels improve as more historical data is collected.

## 🧠 Intelligence Layer — What's New in V3

### Smart Insights (Per Coin)
Every signal now comes with a full explanation of *why* it fired:

| Field | Description |
|-------|-------------|
| **Why?** | Human-readable reason — RSI level, MA crossover direction, strength |
| **Confidence** | 💪 Strong / 👍 Moderate / ⚠️ Weak — based on how many conditions aligned |
| **Risk Note** | Volatility context — whether the signal is stable or elevated risk |

### Market Summary Card
An auto-generated paragraph at the top of every dashboard session summarizing:
- Overall market tone (Bullish / Bearish / Mixed)
- Signal distribution across all tracked coins
- BTC and ETH specific signal status
- Top 24h performer

### Alerts System (3 Sections)
- 🟢 **Top BUY Opportunities** — BUY signals ranked by confidence score
- 🔴 **SELL Signals & High Risk Coins** — SELL signals + high volatility warnings
- ⚡ **Strong Momentum Coins** — Coins with RSI moving furthest from neutral (50)

### Advanced Filters (Intelligence Tab)
- Filter by Signal (BUY / SELL / HOLD / N/A)
- Filter by Volatility (Low / Medium / High)
- Filter by RSI Range (slider 0–100)
- Search by coin name or symbol

## ⚠️ Current Limitations (Version 3)

- Signals and insights are rule-based — no machine learning yet
- Confidence scoring uses heuristic weights, not trained model probabilities
- No price prediction or directional forecasting yet
- No external alerting (email, Telegram, etc.)

These limitations will be addressed in Version 4.

## 🗺 Version Roadmap

| Version | Features | Status |
|---------|----------|--------|
| v1 | Data pipeline · Storage · Dashboard · Scheduling | ✅ Built |
| v2 | RSI · Moving Averages · Volatility · Buy/Sell/Hold Signals · 3-tab Dashboard | ✅ Built |
| v3 | Smart Insights · Confidence Levels · Market Summary · Alerts · Advanced Filters | ✅ Built |
| v4 | ML price prediction | 🔜 Next |

## 🛠 Tech Stack

- **Python** · **Pandas** · **NumPy** · **Requests**
- **SQLite** (database)
- **Streamlit + Plotly** (dashboard)
- **schedule** (automation)
- **CoinGecko API** (free, no key needed)
