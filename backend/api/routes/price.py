# routes/price.py
from fastapi import APIRouter
from utils.crypto_assets import resolve_asset_symbol
from api.models.models import CryptoPrice
from api.utils.fetch_coinbase import fetch_coinbase

router = APIRouter()

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