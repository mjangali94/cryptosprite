from typing import List

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from utils.crypto_assets import resolve_asset_symbol


COINBASE_API_BASE = "https://api.exchange.coinbase.com"
REQUEST_TIMEOUT = 8

# -------------------------
# Coinbase Helper
# -------------------------
def fetch_coinbase(endpoint: str, params: dict | None = None) -> dict:
    url = f"{COINBASE_API_BASE}/{endpoint.lstrip('/')}"
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 429:
            return {"error": "Coinbase rate limit exceeded"}
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"error": "Coinbase request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# -------------------------
# Domain Functions
# -------------------------
def get_spot_price(symbol: str, currency: str) -> dict:
    data = fetch_coinbase(f"products/{symbol}-{currency}/ticker")
    if "error" in data:
        return data
    return {
        "symbol": symbol,
        "price": float(data["price"]),
    }

def get_price_history(symbol: str, currency: str, interval: str, amount: int) -> dict:
    if interval == "hours":
        granularity = 3600
        points = amount
    elif interval == "days":
        granularity = 86400
        points = amount
    elif interval == "months":
        granularity = 86400
        points = amount * 30
    else:
        return {"error": "Invalid interval (use hours/days/months)"}

    data = fetch_coinbase(
        f"products/{symbol}-{currency}/candles",
        params={"granularity": granularity},
    )
    if "error" in data:
        return data

    candles = data[:points]
    candles.reverse()
    history = [
        {
            "time": c[0],
            "low": c[1],
            "high": c[2],
            "open": c[3],
            "close": c[4],
            "volume": c[5],
        }
        for c in candles
    ]
    return {
        "symbol": symbol,
        "currency": currency,
        "interval": interval,
        "points": len(history),
        "history": history,
    }

def compute_trend(prices: list[float], symbol: str = "") -> dict:
    if not prices or prices[0] == 0:
        return {"trend": "unknown"}
    first, last = prices[0], prices[-1]
    change = (last - first) / first * 100
    return {
        "symbol": symbol,
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
    symbol: str
    currency: str = "USD"

class ResolveSymbolInput(BaseModel):
    query: str

class CryptoHistoryInput(BaseModel):
    interval: str = Field(default="days")
    symbol: str
    amount: int = Field(default=3)

class CryptoTrendInput(BaseModel):
    symbol: str

# -------------------------
# Tools
# -------------------------
@tool(args_schema=CryptoPrice, return_direct=True)
def get_crypto_price(symbol: str, currency: str = "USD"):
    """Latest spot price of a cryptocurrency."""
    if not symbol:
        return "❌ Symbol not provided"
    result = get_spot_price(symbol.upper(), currency.upper())
    if "error" in result:
        return f"❌ Price fetch failed: {result['error']}"
    return f"💰 {result['symbol']} price: ${result['price']:,.2f} {currency.upper()}"

@tool(args_schema=ResolveSymbolInput, return_direct=True)
def resolve_asset(query: str):
    """Resolve asset name to symbol (dict for tests)."""
    if not query:
        return {"symbol": None, "id": None, "name": None, "match": "none", "error": "Query not provided"}
    result = resolve_asset_symbol(query)
    if result.get("symbol"):
        return result
    return {"symbol": None, "id": None, "name": None, "match": "none", "error": f"Could not resolve crypto symbol from '{query}'"}

@tool(args_schema=CryptoHistoryInput, return_direct=True)
def get_crypto_history(interval: str = "days", symbol: str = "", amount: int = 3):
    """Return historical prices (dict for tests)."""
    if not symbol:
        return {"error": "Symbol not provided"}
    data = get_price_history(symbol.upper(), "USD", interval, amount)
    if "error" in data:
        return {"error": data["error"]}
    return data

@tool(args_schema=CryptoHistoryInput, return_direct=True)
def get_crypto_signals(interval: str = "days", symbol: str = "", amount: int = 3):
    """Compute trend signal (dict for tests)."""
    if not symbol:
        return {"error": "Symbol not provided"}
    data = get_price_history(symbol.upper(), "USD", interval, amount)
    if "error" in data:
        return {"error": data["error"]}
    prices = [p["close"] for p in data.get("history", [])]
    trend = compute_trend(prices, symbol.upper())
    return trend

@tool(args_schema=CryptoTrendInput, return_direct=True)
def get_crypto_trends_tool(symbol: str):
    """Return trends with headers for tests (Short Term, Mid Term, Long Term)."""
    if not symbol:
        return "❌ Symbol not provided"
    symbol = symbol.upper()
    trends = {}
    configs = {
        "short_term": ("hours", 12, "Short Term (Last 12 hours)"),
        "mid_term": ("days", 14, "Mid Term (Last 14 days)"),
        "long_term": ("months", 12, "Long Term (Last ~12 months)"),
    }

    for name, (interval, amount, label) in configs.items():
        data = get_price_history(symbol, "USD", interval, amount)
        if "error" in data:
            trends[name] = {"trend": "unknown", "price_change_percent": 0, "high": 0, "low": 0, "points": 0, "label": label}
        else:
            prices = [p["close"] for p in data.get("history", [])]
            trends[name] = compute_trend(prices, symbol)
            trends[name]["label"] = label

    formatted = [
        f"{trends[k]['label']}: {trends[k]['trend']} "
        f"(change {trends[k]['price_change_percent']}%, high {trends[k]['high']}, low {trends[k]['low']})"
        for k in ["short_term", "mid_term", "long_term"]
    ]

    return f"Trends for {symbol}:\n" + "\n".join(formatted)



# -------------------------
# Schema
# -------------------------
class MultiCryptoInput(BaseModel):
    symbols: List[str] = Field(..., description="List of cryptocurrency symbols")
    interval: str = Field("days", description="Interval: hours/days/months")
    amount: int = Field(7, description="Number of intervals to fetch")

# -------------------------
# Tool
# -------------------------
@tool(args_schema=MultiCryptoInput, return_direct=True)
def compare_crypto_trends(symbols: List[str], interval: str = "days", amount: int = 7):
    """
    Generate a natural language summary for N cryptocurrencies.

    Args:
        symbols: list of symbols like ['BTC', 'ETH', 'SOL']
        interval: granularity for trend analysis ('hours', 'days', 'months')
        amount: number of intervals to fetch
    Returns:
        str: human-readable summary
    """
    from ai.agents.CryptoChat import run_agent
    summaries = []
    trend_data = {}

    # Step 1: fetch current prices and trends
    for symbol in symbols:
        # Get current price
        price_result = run_agent(f"Get current price for {symbol}")
        price_str = price_result.get("result", f"{symbol} price unavailable")

        # Get trends (short, mid, long) via the trend tool
        trends_result = run_agent(f"Get trends for {symbol}")
        trends_str = trends_result.get("result", "")

        trend_data[symbol] = {
            "price": price_str,
            "trends": trends_str
        }

    # Step 2: Build human-readable summary for each coin
    for symbol, data in trend_data.items():
        summary = [f"### {symbol}\n"]
        summary.append(f"1. **Current Price**: {data['price']}\n")
        summary.append(f"2. **Historical Trends**:\n{data['trends']}\n")

        # Optional: parse trends_str to determine trend direction (simplified)
        if "upward" in data['trends'].lower():
            trend_dir = "rising"
        elif "downward" in data['trends'].lower():
            trend_dir = "falling"
        else:
            trend_dir = "sideways"
        summary.append(f"3. **Trend Direction**: {symbol} is currently **{trend_dir}**.\n")

        summaries.append("\n".join(summary))

    # Step 3: Overall summary
    overall = ["### Summary Comparison\n"]
    for symbol, data in trend_data.items():
        # Extract the short-term trend direction for simplicity
        if "upward" in data['trends'].lower():
            overall.append(f"- {symbol} is currently rising.")
        elif "downward" in data['trends'].lower():
            overall.append(f"- {symbol} is currently falling.")
        else:
            overall.append(f"- {symbol} is moving sideways.")

    summaries.append("\n".join(overall))

    return "\n---\n".join(summaries)

