import datetime
from typing import Optional

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from utils.asset_symbols import (asset_symbols,
                                 resolve_asset_symbol)


class CryptoPrice(BaseModel):
    symbol: str = Field(..., description="The symbol of the crypto asset.")
    currency: str = Field("USD", description="Currency to quote in, default USD")
    

@tool(args_schema=CryptoPrice)
def get_crypto_price(symbol: str, currency: str = "USD"):
    """
    Fetch crypto price from your backend API.
    It also considers different currency pairs.
    Returns a clean human-readable text summary.
    """

    url = f"http://127.0.0.1:8000/api/crypto_price/{symbol.upper()}/{currency.lower()}"
    resp = requests.get(url)
    data = resp.json()
    if "error" in data:
        return data["error"]
    return f"💰 Current price of {data['symbol']}: ${data['price']:,.2f} {currency.upper()}"



class CryptoPriceHistorical(BaseModel):
    symbol: str = Field(..., description="The symbol of the crypto asset.")
    currency: str = Field("USD", description="Currency to quote in, default USD")
    date: str = Field("2025-12-01", description="Date of historical price.")


@tool(args_schema=CryptoPriceHistorical)
def get_crypto_price_by_date(symbol: str, currency: str = "USD", date: str = None):
    """
    Fetch the price of a cryptocurrency for a specific date from your backend API.

    Args:
        symbol (str): The symbol of the cryptocurrency (e.g., BTC, ETH).
        currency (str, optional): The currency to quote in. Defaults to "USD".
        date (str, optional): The date to fetch the price for in YYYY-MM-DD format.

    Returns:
        str: A human-readable summary of the cryptocurrency price for the given date,
             or an error message if the data could not be retrieved.
    """

    url = f"http://127.0.0.1:8000/api/crypto_price/{symbol.upper()}/{currency}/{date}"
    resp = requests.get(url)
    data = resp.json()
    if "error" in data:
        return data["error"]
    return f"💰 Price of {symbol.upper()} on {date}: ${data['price']:,.2f} {currency.upper()}"


@tool(args_schema=CryptoPrice)
def get_crypto_price_percentage_change(symbol:str, currency: str = "USD"):
    """
    Fetch today's percentage change for a cryptocurrency from your backend API.
    """
    url = f"http://127.0.0.1:8000/api/crypto_price/percentage_change/{symbol.upper()}/{currency}/"
    resp = requests.get(url)
    data = resp.json()

    if "error" in data:
        return data["error"]

    change = data["percentage_change"]
    name = data["symbol"]

    direction = "📈 increased" if change >= 0 else "📉 decreased"

    return (
        f"{name.upper()} has {direction} by {abs(change):.2f}% today.")




class ResolveSymbolInput(BaseModel):
    query: str = Field(..., description="User query containing asset name or symbol")

@tool(args_schema=ResolveSymbolInput)
def resolve_asset(query: str):
    """
    Resolves any crypto query into a clean symbol + CoinGecko ID.
    Supports: tickers, full names, misspellings, partial matches, natural language.
    """
    return resolve_asset_symbol(query)



class CryptoHistory(BaseModel):
    interval: str = Field(..., description="minutes, hours, days, months")
    symbol: str = Field(..., description="Crypto symbol like BTC")
    amount: int = Field(..., description="Number of units (e.g. 30 days, 6 months)")


@tool(args_schema=CryptoHistory)
def get_crypto_history(interval: str, symbol: str, amount: int):
    """
    Fetch historical crypto data with flexible intervals.
    """
    url = f"http://127.0.0.1:8000/api/crypto_history/{interval}/{symbol}/{amount}"
    resp = requests.get(url)
    data = resp.json()

    if "error" in data:
        return data["error"]

    history = data["history"]

    start = history[0]["price"]
    end = history[-1]["price"]
    perc = ((end - start) / start) * 100

    direction = "📈 up" if perc >= 0 else "📉 down"

    summary = (
        f"{symbol.upper()} over last {amount} {interval} is {direction} "
        f"{abs(perc):.2f}%. Start: ${start:.2f}, End: ${end:.2f}."
    )

    return {
        "summary": summary,
        "history": history
    }