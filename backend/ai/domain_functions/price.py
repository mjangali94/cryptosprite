from typing import Dict, List

from ai.fetch.fetch_coinbase import fetch_coinbase

INTERVAL_CONFIG = {
    "hours": {"granularity": 3600, "multiplier": 1},
    "days": {"granularity": 86400, "multiplier": 1},
    "months": {"granularity": 86400, "multiplier": 30},
}


def get_spot_price(symbol: str, currency: str) -> Dict:
    data = fetch_coinbase(f"products/{symbol}-{currency}/ticker")
    if "error" in data:
        return {"error": data["error"]}

    return {
        "symbol": symbol,
        "currency": currency,
        "price": float(data["price"]),
    }


def get_price_history(symbol: str, currency: str, interval: str, amount: int) -> Dict:
    if interval not in INTERVAL_CONFIG:
        return {"error": "Invalid interval (use hours/days/months)"}

    config = INTERVAL_CONFIG[interval]
    granularity = config["granularity"]
    points = amount * config["multiplier"]

    data = fetch_coinbase(
        f"products/{symbol}-{currency}/candles",
        params={"granularity": granularity},
    )

    if "error" in data or not isinstance(data, list):
        return {"error": "Failed to fetch candle data"}

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


def compute_trend(prices: List[float], symbol: str = "") -> Dict:
    if len(prices) < 2 or prices[0] == 0:
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

    return {
        "symbol": symbol,
        "trend": "upward" if change_pct > 0 else "downward" if change_pct < 0 else "sideways",
        "price_change_percent": round(change_pct, 2),
        "high": round(max(prices), 2),
        "low": round(min(prices), 2),
        "points": len(prices),
    }
