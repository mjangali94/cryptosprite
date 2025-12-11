import asyncio
import datetime

from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from ai.agents.CryptoChat import run_agent
from fastapi.middleware.cors import CORSMiddleware
from utils.asset_symbols import asset_symbols
import requests

router = APIRouter()


class AgentRequest(BaseModel):
    query:str

class AgentResponse(BaseModel):
    result:str

@router.post("/api/crypto_agent")
async def call_agent(request: AgentRequest):
    result = await asyncio.to_thread(run_agent, request.query)
    return AgentResponse(result=str(result.get("result")))


@router.get("/api/crypto_price/{symbol}/{currency}")
async def get_crypto_price(symbol: str, currency: str ="USD"):
    """Get info about a crypto asset."""
    print("Request received for:", symbol, currency)
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
        "symbol": symbol,
        "name":name,
        "price": data.get("current_price"),
        "currency": currency.lower()
    }




@router.get("/api/crypto_price/{symbol}/{currency}/{date}")
async def get_crypto_price_by_date(symbol: str, currency: str ="USD", date: str = None):
    """
    Get historical price info for a crypto asset.
    Date should be in format 'YYYY-MM-DD'.
    """
    name = asset_symbols.get(symbol.upper())
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}
    url = f"https://api.coingecko.com/api/v3/coins/{name}/history"
    params = {
        "date": datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y"),
        "localization": "false"
    }
    headers = {"User-Agent": "CryptoSprite/1.0"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        return {"error": f"CoinGecko API error: {response.status_code}"}

    data = response.json().get("market_data")
    if not data:
        return {"error": f"No price data found for {symbol} on {date}"}

    return {
        "symbol": symbol,
        "name": name,
        "price": data["current_price"].get(currency.lower()),
        "currency": currency.lower(),
        "date": date
    }



@router.get("/api/crypto_price/percentage_change/{symbol}/{currency}/")
async def get_crypto_price_percentage_change(symbol: str, currency: str = "USD"):
    """
    Calculates today's % change compared to yesterday using CoinGecko historical data.
    """

    name = asset_symbols.get(symbol.upper())
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}

    url = f"https://api.coingecko.com/api/v3/coins/{name}/history"
    headers = {"User-Agent": "CryptoSprite/1.0"}

    # ---- Helper to fetch a historical price ----
    def fetch_price(date_obj):
        date_str = date_obj.strftime("%d-%m-%Y")
        resp = requests.get(url, params={"date": date_str, "localization": "false"}, headers=headers)

        if resp.status_code != 200:
            return None

        market_data = resp.json().get("market_data")
        if not market_data:
            return None

        return market_data["current_price"].get(currency.lower())

    # Today & yesterday dates
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    # Fetch prices
    today_price = fetch_price(today)
    yesterday_price = fetch_price(yesterday)

    if today_price is None:
        return {"error": f"No price data for {name} today ({today})"}

    if yesterday_price is None:
        return {"error": f"No price data for {name} yesterday ({yesterday})"}

    # Percentage change
    percentage_change = ((today_price - yesterday_price) / yesterday_price) * 100

    return {
        "symbol": symbol.upper(),
        "name": name,
        "today_price": today_price,
        "yesterday_price": yesterday_price,
        "percentage_change": round(percentage_change, 2)
    }



@router.get("/api/crypto_history/{interval}/{symbol}/{amount}")
async def get_crypto_history(interval: str, symbol: str, amount: int):
    """
    Universal crypto history endpoint.
    Supported intervals:
        - hours
        - days
        - months
    """
    interval = interval.lower().strip()

    # Supported intervals
    valid_intervals = ["hours", "days", "months"]
    if interval not in valid_intervals:
        return {"error": f"Invalid interval '{interval}'. Use hours/days/months."}

    # Convert symbol
    name = asset_symbols.get(symbol.upper())
    if not name:
        return {"error": f"Symbol '{symbol}' not found"}

    # Convert everything to days for CoinGecko
    if interval == "hours":
        days = max(amount / 24, 1/24)  # at least 1 hour (~0.0417 days)
        cg_interval = "hourly"
    elif interval == "months":
        days = amount * 30
        cg_interval = "daily"
    else:  # days
        days = amount
        cg_interval = "daily"

    url = f"https://api.coingecko.com/api/v3/coins/{name}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": cg_interval
    }
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
