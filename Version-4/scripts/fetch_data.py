"""
fetch_data.py
-------------
Fetches live cryptocurrency data from CoinGecko API (free, no API key needed).
Returns a clean list of coin records ready for processing.
"""

import requests
from datetime import datetime


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,          # Top 50 coins
    "page": 1,
    "sparkline": False,
    "price_change_percentage": "24h"
}


def fetch_crypto_data():
    """
    Fetches top 50 coins from CoinGecko.
    Returns a list of dicts with cleaned fields, or empty list on failure.
    """
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching data from CoinGecko...")
        response = requests.get(COINGECKO_URL, params=PARAMS, timeout=10)
        response.raise_for_status()

        raw_data = response.json()
        coins = []

        for coin in raw_data:
            coins.append({
                "coin_name":        coin.get("name", ""),
                "symbol":           coin.get("symbol", "").upper(),
                "price":            coin.get("current_price", 0),
                "market_cap":       coin.get("market_cap", 0),
                "volume":           coin.get("total_volume", 0),
                "price_change_24h": coin.get("price_change_percentage_24h", 0),
                "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        print(f"  ✅ Fetched {len(coins)} coins successfully.")
        return coins

    except requests.exceptions.RequestException as e:
        print(f"  ❌ API Error: {e}")
        return []


if __name__ == "__main__":
    data = fetch_crypto_data()
    if data:
        for coin in data[:5]:   # Preview first 5
            print(coin)
