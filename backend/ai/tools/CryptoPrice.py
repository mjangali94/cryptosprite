import time

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from utils.asset_symbols import resolve_asset_symbol

API_BASE_URL = "http://127.0.0.1:8000/api"
REQUEST_TIMEOUT = 10


# ------------------------- Helpers -------------------------

def fetch_api(endpoint: str, retries=3, delay=2):
    url = f"{API_BASE_URL}/{endpoint}"
    for i in range(retries):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                return {"error": data["error"]}
            return data
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                time.sleep(delay)  # wait before retrying
                delay *= 2         # exponential backoff
            else:
                return {"error": f"HTTP error {response.status_code}"}
        except requests.exceptions.RequestException:
            time.sleep(delay)
            delay *= 2
    return {"error": "❌ Too many requests, try again later."}


def fetch_crypto_history(interval: str, symbol: str, amount: int):
    interval = interval.lower().strip()
    valid_intervals = ["hours", "days", "months"]
    if interval not in valid_intervals:
        return {"error": f"Invalid interval '{interval}'. Use hours/days/months."}

    name = resolve_asset_symbol(symbol.upper())["id"]
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}

    # Convert everything to days for CoinGecko API
    if interval == "hours":
        days = max(amount / 24, 1 / 24)
        cg_interval = "hourly"
    elif interval == "months":
        days = amount * 30
        cg_interval = "daily"
    else:  # days
        days = amount
        cg_interval = "daily"

    url = f"https://api.coingecko.com/api/v3/coins/{name}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": cg_interval}
    headers = {"User-Agent": "CryptoSprite/1.0"}

    resp = requests.get(url, params=params, headers=headers)
    if not resp.ok:
        return {"error": f"CoinGecko API error: {resp.status_code}"}

    data = resp.json()
    history = [{"timestamp": p[0], "price": p[1]} for p in data.get("prices", [])]

    return {
        "symbol": symbol.upper(),
        "name": name,
        "interval": interval,
        "amount": amount,
        "converted_days": days,
        "points": len(history),
        "history": history
    }


# ------------------------- Schemas -------------------------
class CryptoPrice(BaseModel):
    symbol: str = Field(..., description="Crypto symbol like BTC")
    currency: str = Field("USD", description="Quote currency (default USD)")


class ResolveSymbolInput(BaseModel):
    query: str = Field(..., description="User query: name, ticker, or partial text")



# ------------------------- Tools -------------------------
@tool(args_schema=CryptoPrice)
def get_crypto_price(symbol: str, currency: str = "USD"):
    """Fetch latest crypto price."""
    data = fetch_api(f"crypto_price/{symbol.upper()}/{currency.lower()}")

    if "error" in data:
        return data["error"]

    return (
        f"💰 Current price of {data['symbol']}: "
        f"${data['price']:,.2f} {currency.upper()}"
    )


@tool(args_schema=ResolveSymbolInput)
def resolve_asset(query: str):
    """
    Resolve any crypto asset query into symbol + ID.
    Handles names, tickers, partials, and natural language.
    """
    return resolve_asset_symbol(query)


class CryptoHistoryInput(BaseModel):
    interval: str = Field(..., description="hours, days, months")
    symbol: str = Field(..., description="Crypto symbol like BTC")
    amount: int = Field(..., description="Number of intervals to fetch")

@tool(args_schema=CryptoHistoryInput)
def get_crypto_history(interval: str, symbol: str, amount: int):
    """Tool wrapper for Crypto History"""
    return fetch_crypto_history(interval, symbol, amount)



@tool(args_schema=CryptoHistoryInput)
def get_crypto_signals(interval: str, symbol: str, amount: int):
    """Compute deterministic signals from historical prices."""
    history_data = fetch_crypto_history(interval, symbol, amount)
    if "error" in history_data:
        return history_data["error"]

    prices = [p["price"] for p in history_data["history"]]

    first, last = prices[0], prices[-1]
    change_percent = (last - first) / first * 100

    trend = "upward" if change_percent > 0 else "downward" if change_percent < 0 else "sideways"
    high = max(prices)
    low = min(prices)

    return {
        "symbol": symbol.upper(),
        "trend": trend,
        "price_change_percent": round(change_percent, 2),
        "high": high,
        "low": low,
        "points": len(prices)
    }