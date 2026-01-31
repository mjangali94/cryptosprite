from typing import List, Dict

from ai.fetch.fetch_coinbase import fetch_coinbase

# -------------------------
# Constants
# -------------------------
INTERVAL_CONFIG = {
    "hours": {"granularity": 3600, "multiplier": 1},
    "days": {"granularity": 86400, "multiplier": 1},
    "months": {"granularity": 86400, "multiplier": 30},
}


# -------------------------
# Domain Functions
# -------------------------
def get_spot_price(symbol: str, currency: str) -> Dict:
    """
    Fetch the latest spot price of a cryptocurrency from Coinbase.

    Args:
        symbol: cryptocurrency symbol (e.g., 'BTC')
        currency: currency for price (e.g., 'USD')

    Returns:
        dict: {symbol, currency, price} or {error: str}
    """
    data = fetch_coinbase(f"products/{symbol}-{currency}/ticker")
    if "error" in data:
        return {"error": data["error"]}

    try:
        price = float(data["price"])
    except (KeyError, TypeError, ValueError):
        return {"error": "Invalid data format from API"}

    return {"symbol": symbol, "currency": currency, "price": price}


def get_price_history(symbol: str, currency: str, interval: str, amount: int) -> Dict:
    """
    Fetch historical OHLCV data for a cryptocurrency.

    Args:
        symbol: cryptocurrency symbol
        currency: currency for price
        interval: "hours", "days", or "months"
        amount: number of intervals to fetch (>=1)

    Returns:
        dict: {symbol, currency, interval, points, history} or {error: str}
    """
    if interval not in INTERVAL_CONFIG:
        return {"error": "Invalid interval (use hours/days/months)"}
    if amount < 1:
        return {"error": "Amount must be >= 1"}

    config = INTERVAL_CONFIG[interval]
    granularity = config["granularity"]
    points = amount * config["multiplier"]

    data = fetch_coinbase(f"products/{symbol}-{currency}/candles", params={"granularity": granularity})
    if "error" in data or not isinstance(data, list):
        return {"error": "Failed to fetch candle data"}

    # Only take the most recent `points` and reverse to chronological order
    candles = data[:points][::-1]

    history: List[Dict] = [
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

    return {"symbol": symbol, "currency": currency, "interval": interval, "points": len(history), "history": history}


def compute_trend(prices: List[float], symbol: str = "") -> Dict:
    """
    Compute the price trend for a list of prices.

    Args:
        prices: list of closing prices
        symbol: optional cryptocurrency symbol for context

    Returns:
        dict: trend summary including trend direction, % change, high, low, points
    """
    if not prices or len(prices) < 2 or prices[0] == 0:
        return {
            "symbol": symbol,
            "trend": "unknown",
            "price_change_percent": 0,
            "high": 0,
            "low": 0,
            "points": len(prices),
        }

    first, last = prices[0], prices[-1]
    change_pct = (last - first) / first * 100

    # Determine trend direction
    if change_pct > 0:
        trend_dir = "upward"
    elif change_pct < 0:
        trend_dir = "downward"
    else:
        trend_dir = "sideways"

    return {
        "symbol": symbol,
        "trend": trend_dir,
        "price_change_percent": round(change_pct, 2),
        "high": round(max(prices), 2),
        "low": round(min(prices), 2),
        "points": len(prices),
    }