import asyncio
from typing import Optional
import requests
from fastapi import APIRouter
from .models.models import CryptoPrice, AgentChatRequest, AgentChatResponse
from ai.agents.CryptoChat import run_agent
from utils.asset_symbols import asset_symbols, resolve_asset_symbol

router = APIRouter()

COINBASE_API_BASE = "https://api.exchange.coinbase.com"


# ----------------- Crypto Agent Endpoint -----------------
@router.post("/api/crypto_agent")
async def call_agent(request: AgentChatRequest):
    """
    Call the crypto chat agent asynchronously.
    """
    result = await asyncio.to_thread(run_agent, request.query)
    return AgentChatResponse(result=str(result.get("result")))


# ----------------- Current Crypto Price -----------------
@router.get("/api/crypto_price/{symbol}")
@router.get("/api/crypto_price/{symbol}/{currency}")
async def get_crypto_price(symbol: str, currency: str = "USD"):
    """
    Get current price info about a crypto asset using Coinbase API.
    """
    symbol_upper = symbol.upper()
    pair = f"{symbol_upper}-{currency.upper()}"

    url = f"{COINBASE_API_BASE}/products/{pair}/ticker"

    resp = requests.get(url)
    if not resp.ok:
        return {"error": f"Coinbase API error: {resp.status_code}"}

    data = resp.json()
    price = float(data.get("price", 0))

    return CryptoPrice(
        symbol=symbol_upper,
        name=resolve_asset_symbol(symbol_upper)["name"],
        price=price,
        currency=currency.upper()
    )


# ----------------- Crypto History -----------------
@router.get("/api/crypto_history/{interval}/{symbol}/{amount}")
async def get_crypto_history(interval: str, symbol: str, amount: int, currency: str = "USD"):
    """
    Fetch historical price candles from Coinbase.
    interval: "hours", "days", "months"
    """
    symbol_upper = symbol.upper()
    pair = f"{symbol_upper}-{currency.upper()}"

    # Coinbase uses granularity in seconds
    if interval == "hours":
        granularity = 3600  # 1 hour
    elif interval == "days":
        granularity = 86400  # 1 day
    elif interval == "months":
        granularity = 86400 * 30  # 1 month approx
    else:
        return {"error": f"Invalid interval '{interval}'. Use hours/days/months."}

    url = f"{COINBASE_API_BASE}/products/{pair}/candles"
    params = {"granularity": granularity}

    resp = requests.get(url, params=params)
    if not resp.ok:
        return {"error": f"Coinbase API error: {resp.status_code}"}

    data = resp.json()
    # Coinbase returns: [time, low, high, open, close, volume]
    history = [
        {"timestamp": int(c[0]), "low": c[1], "high": c[2], "open": c[3], "close": c[4], "volume": c[5]}
        for c in data
    ]

    # Also include a simple "price" field for compatibility with trends
    for h in history:
        h["price"] = h["close"]

    return {
        "symbol": symbol_upper,
        "name": resolve_asset_symbol(symbol_upper)["name"],
        "interval": interval,
        "amount": amount,
        "points": len(history),
        "history": history
    }


# ----------------- Crypto Signals -----------------
@router.get("/api/crypto_signals/{symbol}/{currency}")
async def get_crypto_signals(symbol: str, currency: str = "USD"):
    """
    Compute simple deterministic signals based on historical candles.
    """
    hist_resp = await get_crypto_history("days", symbol, 7, currency)
    if "error" in hist_resp:
        return hist_resp

    prices = [c["close"] for c in hist_resp["history"]]
    trend = "upward" if prices[-1] > prices[0] else "downward" if prices[-1] < prices[0] else "sideways"

    return {
        "symbol": symbol.upper(),
        "name": resolve_asset_symbol(symbol)["name"],
        "short_term": {"trend": trend},
        "mid_term": {"interval": "7 days", "trend": trend, "high": max(prices), "low": min(prices)},
        "long_term": {"interval": "30 days", "trend": trend, "high": max(prices), "low": min(prices)}
    }


# ----------------- Multi-Term Crypto Trends -----------------
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


@router.get("/api/crypto_trends/{symbol}")
async def get_crypto_trends(symbol: str):
    """
    Returns short, mid, long term trends with high/low for each timeframe.
    """
    symbol = symbol.upper()
    response = {"symbol": symbol}

    for label, (interval, amount) in TIMEFRAMES.items():
        data = await get_crypto_history(interval, symbol, amount)

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