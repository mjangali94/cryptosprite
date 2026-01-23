import asyncio
from typing import Optional
import requests
from fastapi import APIRouter
from api.models.models import CryptoPrice, AgentChatRequest, AgentChatResponse
from ai.agents.CryptoChat import run_agent
from utils.asset_symbols import asset_symbols

router = APIRouter()


# ----------------- Crypto Agent Endpoint -----------------
@router.post("/api/crypto_agent")
async def call_agent(request: AgentChatRequest):
    """
    Call the crypto chat agent asynchronously.
    This is the placeholder for LLM interpretation of market data.
    """
    # Offload to thread to avoid blocking
    result = await asyncio.to_thread(run_agent, request.query)
    return AgentChatResponse(result=str(result.get("result")))


# ----------------- Current Crypto Price -----------------
@router.get("/api/crypto_price/{symbol}/{currency}")
async def get_crypto_price(symbol: str, currency: str = "USD"):
    """
    Get current price info about a crypto asset.
    """
    name = asset_symbols.get(symbol.upper())
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": currency.lower(), "ids": name}

    response = requests.get(url, params=params)
    if not response.ok:
        return {"error": f"CoinGecko API error: {response.status_code}"}

    data = response.json()[0]

    return CryptoPrice(
        symbol=symbol.upper(),
        name=name,
        price=data.get("current_price"),
        currency=currency.lower()
    )


# ----------------- Placeholder for multi-dimensional signals -----------------
@router.get("/api/crypto_signals/{symbol}/{currency}")
async def get_crypto_signals(symbol: str, currency: str = "USD"):
    """
    Compute deterministic signals for the asset:
    - Price change
    - Volume behavior
    Currently minimal; future v1.1 will include more analysis.
    """
    name = asset_symbols.get(symbol.upper())
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}

    # Fetch current market data
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": currency.lower(), "ids": name}
    resp = requests.get(url, params=params)
    if not resp.ok:
        return {"error": f"CoinGecko API error: {resp.status_code}"}
    data = resp.json()[0]

    price = data.get("current_price")
    price_change_24h = data.get("price_change_percentage_24h")
    volume = data.get("total_volume")

    return {
        "symbol": symbol.upper(),
        "name": name,
        "price": price,
        "price_change_24h_percent": price_change_24h,
        "volume": volume,
    }