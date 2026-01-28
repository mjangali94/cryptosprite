# utils/fetch_binance.py
import requests
from typing import Dict, Any, List

BINANCE_API_BASE = "https://api.binance.com/api/v3"


def fetch_binance(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Fetch JSON data from Binance REST API.
    Raises HTTPError if request fails.

    Args:
        endpoint: API endpoint, e.g., "ticker/price"
        params: Query parameters dict

    Returns:
        JSON response as dict
    """
    url = f"{BINANCE_API_BASE}/{endpoint}"
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # propagate errors, do not catch
    return response.json()


# -------------------------
# Helper functions
# -------------------------
def get_price(symbol: str, quote: str = "USDT") -> Dict[str, Any]:
    """
    Get the latest price for a symbol from Binance.

    Args:
        symbol: Base symbol like 'BTC'
        quote: Quote currency, default 'USDT'

    Returns:
        Dictionary with 'symbol' and 'price'
    """
    symbol_pair = f"{symbol.upper()}{quote.upper()}"
    return fetch_binance("ticker/price", {"symbol": symbol_pair})


def get_24h_stats(symbol: str, quote: str = "USDT") -> Dict[str, Any]:
    """
    Get 24h price statistics for a symbol from Binance.

    Args:
        symbol: Base symbol like 'BTC'
        quote: Quote currency, default 'USDT'

    Returns:
        Dictionary with 24h stats like priceChange, highPrice, lowPrice, etc.
    """
    symbol_pair = f"{symbol.upper()}{quote.upper()}"
    return fetch_binance("ticker/24hr", {"symbol": symbol_pair})


def get_klines(symbol: str, interval: str, limit: int = 500) -> List[List[Any]]:
    """
    Fetch historical candlestick (kline) data from Binance.

    Args:
        symbol: Base symbol like 'BTC'
        interval: Kline interval, e.g., '1h', '1d', '1m'
        limit: Number of candles to fetch, max 1000

    Returns:
        List of candles, each candle is a list:
        [
            open_time, open, high, low, close, volume,
            close_time, quote_asset_volume, number_of_trades,
            taker_buy_base, taker_buy_quote, ignore
        ]
    """
    symbol_pair = f"{symbol.upper()}USDT"
    return fetch_binance("klines", {"symbol": symbol_pair, "interval": interval, "limit": limit})