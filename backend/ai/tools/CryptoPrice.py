import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from utils.crypto_assets import resolve_asset_symbol
from api.utils.fetch_coinbase import fetch_coinbase
# -------------------------
# Coinbase Config
# -------------------------
COINBASE_API_BASE = "https://api.exchange.coinbase.com"
REQUEST_TIMEOUT = 8


# -------------------------
# Domain Functions
# -------------------------
def get_spot_price(symbol: str, currency: str) -> dict:
    """Fetch latest spot price for a given symbol/currency pair."""
    data = fetch_coinbase(f"products/{symbol}-{currency}/ticker")
    if "error" in data:
        return data
    return {"symbol": symbol, "price": float(data["price"])}


def get_price_history(symbol: str, currency: str, interval: str, amount: int) -> dict:
    """Fetch historical prices using Coinbase candles."""
    granularity_map = {"hours": 3600, "days": 86400, "months": 86400}  # months approximated by daily candles
    points_map = {"hours": amount, "days": amount, "months": amount * 30}  # months = ~30 days each

    granularity = granularity_map.get(interval)
    points = points_map.get(interval)
    if not granularity:
        return {"error": "Invalid interval (use hours/days/months)"}

    data = fetch_coinbase(f"products/{symbol}-{currency}/candles", params={"granularity": granularity})
    if "error" in data:
        return data

    candles = data[:points]
    candles.reverse()  # oldest → newest
    history = [{"price": c[4]} for c in candles]

    return {"symbol": symbol, "currency": currency, "interval": interval, "points": len(history), "history": history}


def compute_trend(prices: list[float]) -> dict:
    """Compute trend, % change, high, low from a price list."""
    if not prices or prices[0] == 0:
        return {"trend": "unknown", "price_change_percent": 0, "high": 0, "low": 0, "points": 0}

    first, last = prices[0], prices[-1]
    change = (last - first) / first * 100

    return {
        "trend": "upward" if change > 0 else "downward" if change < 0 else "sideways",
        "price_change_percent": round(change, 2),
        "high": round(max(prices), 2),
        "low": round(min(prices), 2),
        "points": len(prices),
    }


# -------------------------
# Schemas
# -------------------------
class CryptoPrice(BaseModel):
    symbol: str = Field(..., description="Crypto symbol like BTC")
    currency: str = Field("USD", description="Quote currency")


class ResolveSymbolInput(BaseModel):
    query: str = Field(..., description="Asset name or ticker")


class CryptoHistoryInput(BaseModel):
    interval: str = Field(..., description="hours, days, months")
    symbol: str = Field(..., description="Crypto symbol")
    amount: int = Field(..., description="Number of points")


class CryptoTrendInput(BaseModel):
    symbol: str = Field(..., description="Crypto symbol")


# -------------------------
# Tools
# -------------------------
@tool(args_schema=CryptoPrice, return_direct=True)
def get_crypto_price(symbol: str, currency: str = "USD"):
    """Latest spot price (Coinbase direct)."""
    result = get_spot_price(symbol.upper(), currency.upper())
    if "error" in result:
        return f"❌ Price fetch failed: {result['error']}"
    return f"💰 {result['symbol']} price: ${result['price']:,.2f} {currency.upper()}"


@tool(args_schema=ResolveSymbolInput, return_direct=True)
def resolve_asset(query: str):
    """Resolve asset name to symbol."""
    return resolve_asset_symbol(query)


@tool(args_schema=CryptoHistoryInput, return_direct=True)
def get_crypto_history(interval: str, symbol: str, amount: int):
    """Historical prices (Coinbase candles)."""
    return get_price_history(symbol.upper(), "USD", interval, amount)


@tool(args_schema=CryptoHistoryInput, return_direct=True)
def get_crypto_signals(interval: str, symbol: str, amount: int):
    """Compute trend signal for a given interval."""
    data = get_price_history(symbol.upper(), "USD", interval, amount)
    if "error" in data:
        return data
    prices = [p["price"] for p in data["history"]]
    return compute_trend(prices)


@tool(args_schema=CryptoTrendInput, return_direct=True)
def get_crypto_trends_tool(symbol: str):
    """
    Return trends with explicit timeframes:
    - short_term: last 12 hours
    - mid_term: last 14 days
    - long_term: last ~12 months
    """
    symbol = symbol.upper()
    trends = {}

    configs = {
        "short_term": ("hours", 12),
        "mid_term": ("days", 14),
        "long_term": ("months", 12),
    }

    for name, (interval, amount) in configs.items():
        data = get_price_history(symbol, "USD", interval, amount)
        if "error" in data:
            trends[name] = {"trend": "unknown", "timeframe": None}
            continue
        prices = [p["price"] for p in data["history"]]
        trends[name] = compute_trend(prices)
        trends[name]["timeframe"] = f"{amount} {interval}" if interval != "months" else f"~{amount} months"

    return trends