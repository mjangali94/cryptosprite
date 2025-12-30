import asyncio
import datetime
from typing import Optional

import requests
from fastapi import APIRouter
from pydantic import BaseModel
from ai.agents.CryptoChat import run_agent
from utils.asset_symbols import asset_symbols

router = APIRouter()


# ----------------- Request / Response Models -----------------
class AgentRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    result: str


# ----------------- Crypto Agent Endpoint -----------------
@router.post("/api/crypto_agent", response_model=AgentResponse)
async def call_agent(request: AgentRequest):
    """
    Call the crypto chat agent asynchronously.
    """
    result = await asyncio.to_thread(run_agent, request.query)
    return AgentResponse(result=str(result.get("result")))


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
    return {
        "symbol": symbol.upper(),
        "name": name,
        "price": data.get("current_price"),
        "currency": currency.lower()
    }


# ----------------- Historical Crypto Price -----------------
@router.get("/api/crypto_price/{symbol}/{currency}/{date}")
async def get_crypto_price_by_date(symbol: str, currency: str = "USD", date: str = None):
    """
    Get historical price info for a crypto asset.
    Date format: 'YYYY-MM-DD'
    """
    name = asset_symbols.get(symbol.upper())
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}

    try:
        formatted_date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
    except ValueError:
        return {"error": f"Invalid date format: '{date}'. Use YYYY-MM-DD."}

    url = f"https://api.coingecko.com/api/v3/coins/{name}/history"
    headers = {"User-Agent": "CryptoSprite/1.0"}
    response = requests.get(url, params={"date": formatted_date, "localization": "false"}, headers=headers)

    if response.status_code != 200:
        return {"error": f"CoinGecko API error: {response.status_code}"}

    market_data = response.json().get("market_data")
    if not market_data:
        return {"error": f"No price data found for {symbol} on {date}"}

    return {
        "symbol": symbol.upper(),
        "name": name,
        "price": market_data["current_price"].get(currency.lower()),
        "currency": currency.lower(),
        "date": date
    }


# ----------------- Crypto Price Percentage Change -----------------
@router.get("/api/crypto_price/percentage_change/{symbol}/{currency}/")
async def get_crypto_price_percentage_change(symbol: str, currency: str = "USD"):
    """
    Calculate today's % change compared to yesterday using CoinGecko historical data.
    """
    name = asset_symbols.get(symbol.upper())
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}

    url = f"https://api.coingecko.com/api/v3/coins/{name}/history"
    headers = {"User-Agent": "CryptoSprite/1.0"}

    def fetch_price(date_obj: datetime.date) -> Optional[float]:
        date_str = date_obj.strftime("%d-%m-%Y")
        resp = requests.get(url, params={"date": date_str, "localization": "false"}, headers=headers)
        if resp.status_code != 200:
            return None
        market_data = resp.json().get("market_data")
        return market_data["current_price"].get(currency.lower()) if market_data else None

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    today_price = fetch_price(today)
    yesterday_price = fetch_price(yesterday)

    if today_price is None:
        return {"error": f"No price data for {name} today ({today})"}
    if yesterday_price is None:
        return {"error": f"No price data for {name} yesterday ({yesterday})"}

    percentage_change = ((today_price - yesterday_price) / yesterday_price) * 100
    return {
        "symbol": symbol.upper(),
        "name": name,
        "today_price": today_price,
        "yesterday_price": yesterday_price,
        "percentage_change": round(percentage_change, 2)
    }


# ----------------- Crypto History -----------------
@router.get("/api/crypto_history/{interval}/{symbol}/{amount}")
async def get_crypto_history(interval: str, symbol: str, amount: int):
    """
    Universal crypto history endpoint.
    Supported intervals: hours, days, months
    """
    interval = interval.lower().strip()
    valid_intervals = ["hours", "days", "months"]
    if interval not in valid_intervals:
        return {"error": f"Invalid interval '{interval}'. Use hours/days/months."}

    name = asset_symbols.get(symbol.upper())
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}

    # Convert everything to days for CoinGecko API
    if interval == "hours":
        days = max(amount / 24, 1 / 24)
        cg_interval = "hourly"
    elif interval == "months":
        days = amount * 30
        cg_interval = "daily"
    else:
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
