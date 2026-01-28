# routes/signals.py
from fastapi import APIRouter
from api.routes.history import get_crypto_history
from utils.crypto_assets import resolve_asset_symbol

router = APIRouter()

TIMEFRAMES = {
    "short_term": ("hours", 24),
    "mid_term": ("days", 7),
    "long_term": ("days", 30),
}


def calculate_trend(history: list[dict]) -> str:
    if not history or len(history) < 2:
        return "unknown"
    first = history[0]["price"]
    last = history[-1]["price"]
    if last > first:
        return "upward"
    if last < first:
        return "downward"
    return "sideways"


@router.get("/api/crypto_signals/{symbol}/{currency}")
def get_crypto_signals(symbol: str, currency: str = "USD") -> dict:
    """
    Compute simple signals from historical prices.
    """
    hist_resp = get_crypto_history("days", symbol, 7, currency)
    if "error" in hist_resp:
        return hist_resp

    prices = [c["close"] for c in hist_resp["history"]]
    first, last = prices[0], prices[-1]
    change_percent = (last - first) / first * 100
    trend = "upward" if change_percent > 0 else "downward" if change_percent < 0 else "sideways"

    return {
        "symbol": symbol.upper(),
        "name": resolve_asset_symbol(symbol)["name"],
        "trend": trend,
        "price_change_percent": round(change_percent, 2),
        "high": max(prices),
        "low": min(prices),
        "points": len(prices)
    }


@router.get("/api/crypto_trends/{symbol}")
def get_crypto_trends(symbol: str, currency: str = "USD") -> dict:
    """
    Compute short, mid, and long term trends using historical prices.
    """
    symbol = symbol.upper()
    response = {"symbol": symbol}

    for label, (interval, amount) in TIMEFRAMES.items():
        data = get_crypto_history(interval, symbol, amount, currency)
        if "error" in data:
            response[label] = {"trend": "unknown"}
            continue

        prices = [p["price"] for p in data["history"]]
        response[label] = {
            "interval": f"{amount} {interval}",
            "trend": calculate_trend(data["history"]),
            "high": max(prices),
            "low": min(prices),
            "points": len(prices),
        }

    return response