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
    """Fetch JSON data from local FastAPI backend with retries."""
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
                time.sleep(delay)
                delay *= 2
            else:
                return {"error": f"HTTP error {response.status_code}"}
        except requests.exceptions.RequestException:
            time.sleep(delay)
            delay *= 2
    return {"error": "❌ Too many requests, try again later."}


# ------------------------- Schemas -------------------------
class CryptoPrice(BaseModel):
    symbol: str = Field(..., description="Crypto symbol like BTC")
    currency: str = Field("USD", description="Quote currency (default USD)")


class ResolveSymbolInput(BaseModel):
    query: str = Field(..., description="User query: name, ticker, or partial text")


class CryptoHistoryInput(BaseModel):
    interval: str = Field(..., description="hours, days, months")
    symbol: str = Field(..., description="Crypto symbol like BTC")
    amount: int = Field(..., description="Number of intervals to fetch")


# ------------------------- Tools -------------------------
@tool(args_schema=CryptoPrice)
def get_crypto_price(symbol: str, currency: str = "USD"):
    """Fetch latest crypto price from local FastAPI (Coinbase backend)."""
    data = fetch_api(f"crypto_price/{symbol.upper()}/{currency.upper()}")
    if "error" in data:
        return data["error"]

    return (
        f"💰 Current price of {data['symbol']}: "
        f"${data['price']:,.2f} {currency.upper()}"
    )


@tool(args_schema=ResolveSymbolInput)
def resolve_asset(query: str):
    """Resolve any crypto asset query into symbol + ID using asset_symbols helper."""
    return resolve_asset_symbol(query)


@tool(args_schema=CryptoHistoryInput)
def get_crypto_history(interval: str, symbol: str, amount: int):
    """Fetch historical price data from local FastAPI backend."""
    data = fetch_api(f"crypto_history/{interval}/{symbol.upper()}/{amount}")
    return data


@tool(args_schema=CryptoHistoryInput)
def get_crypto_signals(interval: str, symbol: str, amount: int):
    """
    Compute deterministic signals from historical prices.
    Returns trend, % change, high/low, and points.
    """
    history_data = fetch_api(f"crypto_history/{interval}/{symbol.upper()}/{amount}")
    if "error" in history_data:
        return history_data["error"]

    prices = [p["price"] for p in history_data.get("history", [])]
    if not prices:
        return {"error": "No price history available."}

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



from langchain_core.tools import tool
from pydantic import BaseModel, Field

class CryptoTrendInput(BaseModel):
    symbol: str = Field(..., description="Crypto symbol like BTC")

@tool(args_schema=CryptoTrendInput)
def get_crypto_trends_tool(symbol: str):
    """
    Returns short, mid, long-term trends in plain language.
    """
    import requests

    url = f"http://127.0.0.1:8000/api/crypto_trends/{symbol.upper()}"
    resp = requests.get(url)
    if not resp.ok:
        return f"❌ Error fetching trends: {resp.status_code}"

    data = resp.json()
    lines = [f"Trends for {symbol.upper()}:"]
    for term in ["short_term", "mid_term", "long_term"]:
        info = data.get(term, {})
        trend = info.get("trend", "unknown")
        high = info.get("high")
        low = info.get("low")
        points = info.get("points")
        if trend != "unknown":
            lines.append(
                f"- {term.replace('_',' ').title()}: {trend}, high: {high}, low: {low}, data points: {points}"
            )
        else:
            lines.append(f"- {term.replace('_',' ').title()}: {trend}")
    return "\n".join(lines)