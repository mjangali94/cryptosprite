import datetime
from typing import Optional, Dict, Any

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field, validator

from utils.asset_symbols import resolve_asset_symbol


API_BASE_URL = "http://127.0.0.1:8000/api"
REQUEST_TIMEOUT = 10


# ------------------------- Helpers -------------------------
def fetch_api(endpoint: str) -> Dict[str, Any]:
    """Generic API request handler with safe error handling."""
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return {"error": data["error"]}

        return data

    except requests.exceptions.ConnectionError:
        return {"error": "❌ Could not connect to backend API."}

    except requests.exceptions.Timeout:
        return {"error": "⏳ API request timed out."}

    except requests.exceptions.HTTPError as e:
        return {"error": f"❌ API returned error: {str(e)}"}

    except Exception:
        return {"error": "❌ Unexpected error while fetching crypto data."}


# ------------------------- Schemas -------------------------
class CryptoPrice(BaseModel):
    symbol: str = Field(..., description="Crypto symbol like BTC")
    currency: str = Field("USD", description="Quote currency (default USD)")


class CryptoPriceHistorical(BaseModel):
    symbol: str = Field(..., description="Crypto symbol like BTC")
    currency: str = Field("USD", description="Quote currency")
    date: Optional[str] = Field(
        None,
        description="Historical date in YYYY-MM-DD. Defaults to today."
    )

    @validator("date", always=True)
    def default_today(cls, value):
        return value or datetime.date.today().isoformat()


class ResolveSymbolInput(BaseModel):
    query: str = Field(..., description="User query: name, ticker, or partial text")


class CryptoHistory(BaseModel):
    interval: str = Field(..., description="minutes, hours, days, months")
    symbol: str = Field(..., description="Crypto symbol like BTC")
    amount: int = Field(..., description="Quantity of interval units")


# ------------------------- Tools -------------------------
@tool(args_schema=CryptoPrice)
def get_crypto_price(symbol: str, currency: str = "USD"):
    """Fetch latest crypto price."""
    data = fetch_api(f"crypto_price/{symbol.upper()}/{currency.lower()}")

    if "error" in data:
        return data["error"]

    return (
        f"💰 Current price of {data['symbol']}: "
        f"${data['price']:,.2f} {currency.upper()}"
    )


@tool(args_schema=CryptoPriceHistorical)
def get_crypto_price_by_date(symbol: str, currency: str, date: str):
    """Fetch crypto price for a specific date."""
    data = fetch_api(f"crypto_price/{symbol.upper()}/{currency}/{date}")

    if "error" in data:
        return data["error"]

    return (
        f"💰 {symbol.upper()} price on {date}: "
        f"${data['price']:,.2f} {currency.upper()}"
    )


@tool(args_schema=CryptoPrice)
def get_crypto_price_percentage_change(symbol: str, currency: str = "USD"):
    """Fetch today's % change."""
    data = fetch_api(
        f"crypto_price/percentage_change/{symbol.upper()}/{currency.lower()}"
    )

    if "error" in data:
        return data["error"]

    direction = "📈 increased" if data["percentage_change"] >= 0 else "📉 decreased"

    return (
        f"{data['symbol'].upper()} has {direction} "
        f"by {abs(data['percentage_change']):.2f}% today."
    )


@tool(args_schema=ResolveSymbolInput)
def resolve_asset(query: str):
    """
    Resolve any crypto asset query into symbol + ID.
    Handles names, tickers, partials, and natural language.
    """
    return resolve_asset_symbol(query)


@tool(args_schema=CryptoHistory)
def get_crypto_history(interval: str, symbol: str, amount: int):
    """Fetch historical crypto data."""
    data = fetch_api(f"crypto_history/{interval}/{symbol}/{amount}")

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
