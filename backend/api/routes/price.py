# routes/price.py
import requests
from fastapi import APIRouter
from utils.crypto_assets import resolve_asset_symbol
from api.models.models import CryptoPrice

router = APIRouter()
COINBASE_API_BASE = "https://api.exchange.coinbase.com"


def fetch_coinbase(endpoint: str, params: dict = None) -> dict:
    url = f"{COINBASE_API_BASE}/{endpoint}"
    resp = requests.get(url, params=params)
    if not resp.ok:
        return {"error": f"Coinbase API error {resp.status_code}"}
    return resp.json()


@router.get("/api/crypto_price/{symbol}")
@router.get("/api/crypto_price/{symbol}/{currency}")
def get_crypto_price(symbol: str, currency: str = "USD") -> CryptoPrice | dict:
    """
    Fetch current price info from Coinbase.
    """
    symbol = symbol.upper()
    currency = currency.upper()
    pair = f"{symbol}-{currency}"

    data = fetch_coinbase(f"products/{pair}/ticker")
    if "error" in data:
        return data

    return CryptoPrice(
        symbol=symbol,
        name=resolve_asset_symbol(symbol)["name"],
        price=float(data.get("price", 0)),
        currency=currency
    )