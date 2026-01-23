import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from utils.asset_symbols import resolve_asset_symbol

API_BASE_URL = "http://127.0.0.1:8000/api"
REQUEST_TIMEOUT = 10


# ------------------------- Helpers -------------------------
def fetch_api(endpoint: str) -> Dict[str, Any]:
    """Generic API request handler with safe error handling."""
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return {"error": data["error"]}

        return data

    except requests.exceptions.RequestException:
        return {"error": "❌ Could not fetch crypto data."}


# ------------------------- Schemas -------------------------
class CryptoPrice(BaseModel):
    symbol: str = Field(..., description="Crypto symbol like BTC")
    currency: str = Field("USD", description="Quote currency (default USD)")


class ResolveSymbolInput(BaseModel):
    query: str = Field(..., description="User query: name, ticker, or partial text")


class CryptoHistoryInput(BaseModel):
    symbol: str = Field(..., description="Crypto symbol like BTC")
    interval: str = Field("days", description="Interval unit: hours, days, months")
    amount: int = Field(7, description="Number of interval units to fetch")


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


@tool(args_schema=CryptoHistoryInput)
def get_crypto_history(symbol: str, interval: str = "days", amount: int = 7):
    """
    Fetch historical crypto price data from backend API.
    Returns a list of {timestamp, price} for signals computation.
    """
    symbol = symbol.upper()
    interval = interval.lower().strip()
    data = fetch_api(f"crypto_history/{interval}/{symbol}/{amount}")

    if "error" in data:
        return data["error"]

    # Simplify output for backend use
    history = [{"timestamp": p["timestamp"], "price": p["price"]} for p in data.get("history", [])]

    return {
        "symbol": symbol,
        "interval": interval,
        "amount": amount,
        "history": history
    }