# 🚀 Crypto Decision Intelligence System

> An automated crypto intelligence system that tracks, analyzes, and generates insights from live market data.

## 🧩 Problem Statement

Cryptocurrency markets are highly volatile and data-heavy, making it difficult for traders and analysts to track meaningful trends in real time.

While Version 3 introduced Smart Insights, human-readable signal explanations, and an Alerts System, it still relied entirely on rule-based logic — meaning every decision came from fixed thresholds with no ability to learn from historical patterns.

Version 4 completes the system by introducing a **Machine Learning Prediction Layer** — training a Random Forest Classifier per coin on historical data and predicting the next price direction (Up / Down) with a confidence score. Combined with the existing signal engine, this creates a full decision intelligence loop from raw data to ML-backed predictions.

## 🏗 Project Structure

```
crypto-intelligence-system/
├── data/                        # SQLite database lives here
├── scripts/
│   ├── fetch_data.py            # CoinGecko API → raw data
│   ├── process_data.py          # Clean + store + read helpers
│   ├── analyse_data.py          # RSI · SMA 7 · SMA 14 · Volatility engine
│   ├── signal_engine.py         # Buy / Sell / Hold rule-based classifier
│   ├── generate_insights.py     # Smart insights + confidence + market summary
│   └── ml_pipeline.py           # Orchestrates train → predict → store (NEW)
├── database/
│   └── db_connection.py         # DB setup & connection (V4: ml_predictions table)
├── models/
│   ├── train_model.py           # Random Forest trainer per coin (NEW)
│   ├── predict.py               # Loads saved models, generates predictions (NEW)
│   └── saved/                   # Trained .pkl model files (auto-generated, not tracked)
├── dashboard/
│   └── app.py                   # Streamlit dashboard (V4: 5-tab layout + ML tab)
├── scheduler/
│   └── run_pipeline.py          # Master pipeline orchestrator (V4: ML step added)
├── requirements.txt
└── README.md
```

## 🏗 System Architecture (Version 4 — Final)

Version 4 completes the pipeline with a full ML layer on top of V3:

CoinGecko API → Data Fetching → Data Cleaning → SQLite Storage → Indicator Analysis → Signal Generation → Insight Generation → ML Training → Predictions → Streamlit Dashboard

- **Fetch Layer**: Collects top 50 cryptocurrencies from CoinGecko (free, no API key)
- **Processing Layer**: Enhanced data quality — type enforcement, null handling, duplicate guard
- **Storage Layer**: Stores prices, signals, insights, and ML predictions in SQLite
- **Indicator Engine**: Computes RSI (14-period), SMA 7, SMA 14, and Volatility
- **Signal Engine**: Rule-based BUY / SELL / HOLD classification
- **Insight Engine**: Human-readable explanations + confidence levels + market summary
- **ML Training**: Random Forest Classifier trained per coin on 7 engineered features
- **Prediction Engine**: Loads saved models, predicts next price direction + confidence %
- **Presentation Layer**: 5-tab Streamlit dashboard — Live Market · Intelligence · Alerts · ML Predictions · Trend Analysis

This design keeps every layer modular, independently testable, and extensible.

## 📊 Dashboard Preview

New tab added in this version:- 

> ![img1](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/4d82b3b5665da6abeffb17c66c4287262166ff69/Version-4/images/img_9.png)

> ![img2](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/4d82b3b5665da6abeffb17c66c4287262166ff69/Version-4/images/img_10.png)

> ![img3](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/4d82b3b5665da6abeffb17c66c4287262166ff69/Version-4/images/img_11.png)

> ![img4](https://github.com/sanchit-2511/Crypto-Decision-Intelligence-System/blob/4d82b3b5665da6abeffb17c66c4287262166ff69/Version-4/images/img_12.png)


## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run full pipeline (fetch + signals + insights + ML train + predict)
python scheduler/run_pipeline.py

# 3. Launch the dashboard
streamlit run dashboard/app.py

# 4. (Optional) Run pipeline on auto-schedule every 5 min
python scheduler/run_pipeline.py --schedule
```

> **Note:** ML models require a minimum of **20 snapshots per coin** to train. Run the pipeline regularly to build up historical data — the more data, the better the model. Trained models are saved as `.pkl` files in `models/saved/` (excluded from version control).

## 🤖 ML Layer — How Predictions Work

### Model
**Random Forest Classifier** — chosen for its robustness on small/noisy datasets, no requirement for feature scaling, built-in feature importance, and full explainability.

### Features Used

| Feature | Description |
|---------|-------------|
| RSI | 14-period Relative Strength Index |
| SMA 7 | 7-snapshot Simple Moving Average |
| SMA 14 | 14-snapshot Simple Moving Average |
| SMA Crossover | SMA7 − SMA14 (direction of crossover) |
| Volatility | Rolling std dev / mean × 100 |
| Price Change % | Percentage change from previous snapshot |
| Volume (normalized) | Volume relative to coin's own average |

### Label
If the **next recorded price > current price** → label = 1 (Up), else → 0 (Down).

### Prediction Output
- 🔼 **Up** / 🔽 **Down** — predicted next direction
- **Confidence %** — model's probability score for the prediction
- **Model Accuracy** — accuracy on held-out test data during training
- **Signal vs Prediction Alignment** — where rule-based BUY signal + ML predicts Up (highest conviction)

> ⚠️ **Disclaimer:** Predictions are based on historical price patterns and are for **educational purposes only**. They do not constitute financial advice.

## ⚠️ Current Limitations (Version 4)

- ML models trained on limited data (accuracy improves significantly with more pipeline runs)
- No deep learning or time-series specific models (LSTM etc.) — kept simple intentionally
- No live deployment or cloud hosting yet
- No external alerting (email, Telegram, etc.)
- Predictions cover next snapshot direction only, not longer time horizons

## 🗺 Version Roadmap

| Version | Features | Status |
|---------|----------|--------|
| v1 | Data pipeline · Storage · Dashboard · Scheduling | ✅ Built |
| v2 | RSI · Moving Averages · Volatility · Buy/Sell/Hold Signals · 3-tab Dashboard | ✅ Built |
| v3 | Smart Insights · Confidence Levels · Market Summary · Alerts · Advanced Filters | ✅ Built |
| v4 | Random Forest ML · Price Direction Predictions · Feature Importance · 5-tab Dashboard | ✅ Built |

## 🛠 Tech Stack

- **Python** · **Pandas** · **NumPy** · **Requests**
- **Scikit-learn** (Random Forest · train/test split · accuracy scoring)
- **SQLite** (database)
- **Streamlit + Plotly** (dashboard)
- **schedule** (automation)
- **CoinGecko API** (free, no key needed)