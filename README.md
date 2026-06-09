# 🚀 Crypto Decision Intelligence System

> An automated crypto intelligence system that tracks, analyzes, and generates insights from live market data.

## 🧩 Problem Statement

Cryptocurrency markets are highly volatile and data-heavy, making it difficult for traders and analysts to track meaningful trends in real time.

Most platforms provide raw data but lack structured insights, historical tracking, and decision-support systems.

This project aims to solve that by building an automated **Crypto Decision Intelligence System** that transforms raw market data into structured, trackable, and eventually actionable insights.


## 🏗 Project Structure

```
crypto-intelligence-system/
├── data/                        # SQLite database lives here
├── scripts/
│   ├── fetch_data.py            # CoinGecko API → raw data
│   ├── process_data.py          # Clean + store + read helpers
│   └── generate_insights.py     # (Version 3)
├── database/
│   └── db_connection.py         # DB setup & connection
├── dashboard/
│   └── app.py                   # Streamlit dashboard
├── models/                      # (Version 4 — ML)
├── scheduler/
│   └── run_pipeline.py          # Master pipeline orchestrator
├── requirements.txt
└── README.md
```

## 🏗 System Architecture (Version 1)

The system follows a simple data pipeline architecture:

CoinGecko API → Data Fetching → Data Cleaning → SQLite Storage → Streamlit Dashboard

* **Fetch Layer**: Collects top 50 cryptocurrencies
* **Processing Layer**: Cleans and validates data
* **Storage Layer**: Stores timestamped records in SQLite
* **Presentation Layer**: Visualizes data using Streamlit

This design ensures modularity and scalability for future versions.


## 📊 Dashboard Preview

![Dashboard Screenshot](dashboard_img1.png).

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run pipeline once (fetch + store data)
python scheduler/run_pipeline.py

# 3. Launch the dashboard
streamlit run dashboard/app.py

# 4. (Optional) Run pipeline on auto-schedule every 5 min
python scheduler/run_pipeline.py --schedule
```

## ⚠️ Current Limitations (Version 1)

* Limited historical data (requires multiple pipeline runs)
* No advanced analytics or trading signals yet
* No alerting or notification system
* No predictive modeling

These limitations will be addressed in upcoming versions.


## 🗺 Version Roadmap

| Version | Features | Status |
|---------|----------|--------|
| v1 | Data pipeline · Storage · Dashboard · Scheduling | ✅ Built |
| v2 | Momentum · Volatility · Trend signals | 🔜 Next |
| v3 | Auto-generated insights | 🔜 |
| v4 | ML price prediction | 🔜 |

## 🛠 Tech Stack
- **Python** · **Pandas** · **Requests**
- **SQLite** (database)
- **Streamlit + Plotly** (dashboard)
- **schedule** (automation)
- **CoinGecko API** (free, no key needed)
