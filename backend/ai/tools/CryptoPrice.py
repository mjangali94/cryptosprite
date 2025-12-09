import datetime
from typing import Optional

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from utils.asset_symbols import asset_symbols
from utils.date_resolve import resolve_date




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



    