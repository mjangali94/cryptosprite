# routes/history.py
import requests
from fastapi import APIRouter
from utils.crypto_assets import resolve_asset_symbol

router = APIRouter()
COINBASE_API_BASE = "https://api.exchange.coinbase.com"


def fetch_coinbase(endpoint: str, params: dict = None) -> dict:
    url = f"{COINBASE_API_BASE}/{endpoint}"
    resp = requests.get(url, params=params)
    if not resp.ok:
        return {"error": f"Coinbase API error {resp.status_code}"}
    return resp.json()


@router.get("/api/crypto_history/{interval}/{symbol}/{amount}")
def get_crypto_history(interval: str, symbol: str, amount: int, currency: str = "USD") -> dict:
    """
    Fetch historical price candles from Coinbase.
    interval: "hours", "days", "months"
    """
    symbol = symbol.upper()
    currency = currency.upper()
    pair = f"{symbol}-{currency}"

    granularity_map = {"hours": 3600, "days": 86400, "months": 86400*30}
    granularity = granularity_map.get(interval)
    if granularity is None:
        return {"error": f"Invalid interval '{interval}'. Use hours/days/months."}

    data = fetch_coinbase(f"products/{pair}/candles", params={"granularity": granularity})
    if "error" in data:
        return data

    # Coinbase returns [time, low, high, open, close, volume]
    history = [
        {
            "timestamp": int(c[0]),
            "low": c[1],
            "high": c[2],
            "open": c[3],
            "close": c[4],
            "volume": c[5],
            "price": c[4]  # simplified price for trends
        }
        for c in data
    ]

    return {
        "symbol": symbol,
        "name": resolve_asset_symbol(symbol)["name"],
        "interval": interval,
        "amount": amount,
        "points": len(history),
        "history": history
    }