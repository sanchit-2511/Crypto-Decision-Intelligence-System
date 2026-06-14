# 🚀 Crypto Decision Intelligence System

> An automated crypto intelligence system that collects live market data, computes technical indicators, generates human-readable insights, and predicts price direction using Machine Learning.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b?style=flat-square&logo=streamlit)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003b57?style=flat-square&logo=sqlite)](https://sqlite.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-f7931e?style=flat-square&logo=scikit-learn)](https://scikit-learn.org)
[![CoinGecko](https://img.shields.io/badge/CoinGecko-API-8cc63f?style=flat-square)](https://coingecko.com)

---

## 🧩 Problem Statement

Cryptocurrency markets are highly volatile and data-heavy, making it difficult for traders and analysts to track meaningful trends in real time.

Most platforms provide raw data but lack structured insights, historical tracking, and decision-support systems. This project solves that by building an end-to-end **Crypto Decision Intelligence System** that evolves across 4 versions — from a simple data pipeline to a full ML-powered decision engine — combining Data Engineering, Data Analysis, Data Science, and Product Thinking in a single project.

---

## 🏗 Repository Structure

```
Crypto-Decision-Intelligence-System/
│
├── Version-1/          ← Data Pipeline + Live Dashboard
│   └── README.md
│
├── Version-2/          ← Intelligence Layer (RSI · SMA · Signals)
│   └── README.md
│
├── Version-3/          ← Smart Insights + Alerts + Market Summary
│   └── README.md
│
├── Version-4/          ← ML Predictions (Random Forest)
│   └── README.md
│
└── README.md           ← You are here
```

Each version folder contains its own complete codebase + README with setup instructions, architecture details, and dashboard screenshots.

---

## 🗺 Version Roadmap

| Version | Core Theme | Key Features | Status |
|---------|-----------|--------------|--------|
| [v1](#-version-1--data-pipeline--live-dashboard) | Data Pipeline | Live data fetch · SQLite storage · Auto-scheduling · Streamlit dashboard | ✅ Complete |
| [v2](#-version-2--intelligence-layer) | Intelligence Layer | RSI · SMA 7 & 14 · Volatility · Buy/Sell/Hold signals · 3-tab dashboard | ✅ Complete |
| [v3](#-version-3--smart-insights--alerts) | Decision Intelligence | Smart insights · Confidence levels · Market summary · Alerts system · Advanced filters | ✅ Complete |
| [v4](#-version-4--ml-prediction-layer) | ML Predictions | Random Forest · Price direction prediction · Feature importance · Signal alignment | ✅ Complete |

---

## 📦 Version 1 — Data Pipeline + Live Dashboard

**The Foundation.** Establishes the full automated data pipeline from scratch.

### What it does
- Fetches live prices for top 50 cryptocurrencies from CoinGecko API (free, no key needed)
- Cleans and stores timestamped records in SQLite — building historical data automatically
- Displays a live Streamlit dashboard with price table, top gainers/losers, and trend chart
- Runs on a schedule (every 5 minutes) without any manual intervention

### Pipeline Flow
```
CoinGecko API → Fetch → Clean → Store (SQLite) → Streamlit Dashboard
```

### Tech Introduced
Python · Pandas · Requests · SQLite · Streamlit · Plotly · schedule

### Data Collected Per Coin
`coin_name` · `symbol` · `price` · `market_cap` · `volume` · `price_change_24h` · `timestamp`

### DB Table
`crypto_prices` — core historical price storage

---

## 📦 Version 2 — Intelligence Layer

**From raw data to signals.** Adds a full technical indicator engine on top of V1.

### What it does
- Computes RSI (14-period), SMA 7, SMA 14, and Volatility from accumulated price history
- Applies rule-based logic to classify every coin as BUY / SELL / HOLD
- Fixes the V1 trend line issue with precise timestamps and a duplicate guard
- Upgrades the dashboard to a 3-tab layout: Live Market · Intelligence Board · Trend Analysis

### Pipeline Flow
```
Fetch → Clean → Store → Compute Indicators → Generate Signals → Store Signals → Dashboard
```

### Signal Rules
| Signal | Condition |
|--------|-----------|
| 🟢 BUY | RSI < 35 AND SMA7 > SMA14 (oversold + bullish crossover) |
| 🔴 SELL | RSI > 65 AND SMA7 < SMA14 (overbought + bearish crossover) |
| 🟡 HOLD | Everything else |
| ⚪ N/A | Fewer than 14 snapshots available |

### New Files
`scripts/analyse_data.py` · `scripts/signal_engine.py`

### DB Table Added
`coin_signals` — stores computed signals with timestamps

### Tech Introduced
NumPy · RSI calculation · Moving averages · Volatility scoring

---

## 📦 Version 3 — Smart Insights + Alerts

**From signals to explanations.** Adds a human-readable intelligence layer on top of V2.

### What it does
- Generates a natural-language explanation for every signal — *why* it fired, not just what it is
- Assigns a confidence level (💪 Strong / 👍 Moderate / ⚠️ Weak) based on how many conditions aligned
- Auto-generates a Market Summary paragraph on every pipeline run summarizing the overall market state
- Adds a dedicated Alerts tab with three smart sections: Top BUY Opportunities, SELL/High-Risk Coins, Strong Momentum
- Adds advanced dashboard filters: Signal type · Volatility level · RSI range slider · Coin search

### Pipeline Flow
```
Fetch → Clean → Store → Indicators → Signals → Generate Insights → Market Summary → Store → Dashboard
```

### Sample Insight Output
```
BTC → 🟢 BUY
Why: RSI at 31.4 — oversold conditions detected · Bullish MA crossover — SMA7 is 0.82% above SMA14
Confidence: 💪 Strong
Risk Note: 🟢 Low volatility — trend is stable and reliable
```

### New Files
`scripts/generate_insights.py`

### DB Table Added
`insights` — stores market summary text with timestamps

### Dashboard Tabs
📊 Live Market · 🧠 Intelligence · 🔔 Alerts · 📈 Trend Analysis

---

## 📦 Version 4 — ML Prediction Layer

**The complete system.** Adds Machine Learning on top of the full V3 stack.

### What it does
- Trains a **Random Forest Classifier** per coin using 7 engineered features from historical data
- Predicts the next price direction: 🔼 Up or 🔽 Down — with a confidence percentage
- Shows model accuracy (trained on 80/20 split) transparently on the dashboard
- Displays a **Feature Importance chart** showing which indicators the model relied on most
- Introduces **Signal vs Prediction Alignment** — where rule-based BUY + ML predicts Up (highest conviction)
- All models saved as `.pkl` files and reloaded on each pipeline run

### Pipeline Flow
```
Fetch → Clean → Store → Indicators → Signals → Insights →
Train ML Models → Generate Predictions → Store Predictions → Dashboard
```

### ML Features Used
| Feature | Description |
|---------|-------------|
| RSI | 14-period Relative Strength Index |
| SMA 7 | Short-term moving average |
| SMA 14 | Long-term moving average |
| SMA Crossover | SMA7 − SMA14 |
| Volatility | Rolling std / mean × 100 |
| Price Change % | Pct change from previous snapshot |
| Volume (norm) | Volume relative to coin's own average |

### Label
If next price > current price → **1 (Up)**, else → **0 (Down)**

### New Files
`models/train_model.py` · `models/predict.py` · `scripts/ml_pipeline.py`

### DB Table Added
`ml_predictions` — stores direction, confidence %, model accuracy, and training sample count

### Dashboard Tabs
📊 Live Market · 🧠 Intelligence · 🔔 Alerts · 🤖 ML Predictions · 📈 Trend Analysis

> ⚠️ **Disclaimer:** ML predictions are based on historical price patterns and are for **educational purposes only**. They do not constitute financial advice.

---

## ⚡ Quick Start (Version 4 — Full System)

```bash
# 1. Navigate to the Version-4 folder
cd Version-4

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Run the full pipeline once
python scheduler/run_pipeline.py

# 4. Launch the dashboard
streamlit run dashboard/app.py

# 5. (Optional) Run on auto-schedule every 5 minutes
python scheduler/run_pipeline.py --schedule
```

> **Note:** ML models need a minimum of **20 snapshots per coin** to train. RSI and SMA signals need **14 snapshots**. Run the pipeline regularly — the system gets smarter over time.

---

## 🛠 Complete Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Data Fetching | Requests · CoinGecko API |
| Data Processing | Pandas · NumPy |
| Database | SQLite |
| ML | Scikit-learn (Random Forest) |
| Dashboard | Streamlit · Plotly |
| Automation | schedule library |

---

## 📊 Full Pipeline Architecture (V4)

```
┌─────────────────────────────────────────────────────────┐
│                   CoinGecko API (Free)                  │
└──────────────────────────┬──────────────────────────────┘
                           │ Top 50 coins
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Fetch + Clean + Duplicate Guard            │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  SQLite Database                        │
│  crypto_prices · coin_signals · insights · ml_predictions│
└──────┬──────────────────────────────────────────────────┘
       │
       ├──▶ Indicator Engine (RSI · SMA7 · SMA14 · Volatility)
       │              │
       │              ▼
       │       Signal Engine (BUY / SELL / HOLD)
       │              │
       │              ▼
       │       Insight Engine (Why? · Confidence · Risk Note)
       │              │
       │              ▼
       └──▶ ML Engine (Train → Predict → Store)
                      │
                      ▼
        ┌─────────────────────────┐
        │   Streamlit Dashboard   │
        │  5 Tabs · Live + Smart  │
        └─────────────────────────┘
```

---

## 🙌 Project Highlights

This project demonstrates end-to-end ownership across **4 disciplines** in one system:

- **Data Engineering** — automated pipeline, SQLite schema design, duplicate handling, historical data accumulation
- **Data Analysis** — RSI, Moving Averages, Volatility computation, trend classification
- **Data Science** — feature engineering, Random Forest training, confidence scoring, feature importance
- **Product Thinking** — versioned delivery, clean UI, human-readable outputs, explainable signals

---

*Built with Python · Streamlit · SQLite · scikit-learn · CoinGecko API*
