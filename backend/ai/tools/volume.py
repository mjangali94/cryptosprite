# ai/tools/volume.py

from langchain_core.tools import tool

from ai.domain_functions.volume import (
    get_current_volume,
    get_volume_history,
    summarize_volume,
)
from ai.schemas.volume import CryptoVolumeInput, CryptoVolumeHistoryInput


# -------------------------
# Volume Tools
# -------------------------
@tool(args_schema=CryptoVolumeInput, return_direct=True)
def get_crypto_volume(symbol: str, currency: str = "USD") -> str:
    """
    Fetch the current 24-hour trading volume and price for a cryptocurrency.

    Args:
        symbol (str): Cryptocurrency symbol, e.g., "BTC".
        currency (str, optional): Quote currency. Defaults to "USD".

    Returns:
        str: Human-readable summary including 24h trading volume and current price.
    """
    symbol = symbol.upper()
    currency = currency.upper()

    result = get_current_volume(symbol, currency)
    if "error" in result:
        return f"❌ Volume fetch failed: {result['error']}"

    return (
        f"💹 {symbol} 24h Volume: {result['volume']:,.2f} {currency}\n"
        f"Current Price: ${result['price']:,.2f} {currency}"
    )


@tool(args_schema=CryptoVolumeHistoryInput, return_direct=True)
def get_crypto_volume_history(
    symbol: str,
    interval: str,
    amount: int,
    currency: str = "USD",
) -> str:
    """
    Fetch historical trading volume for a cryptocurrency and summarize it.

    Args:
        symbol (str): Cryptocurrency symbol, e.g., "ETH".
        interval (str): Time granularity ("hours", "days", "months").
        amount (int): Number of intervals to fetch.
        currency (str, optional): Quote currency. Defaults to "USD".

    Returns:
        str: Natural-language summary describing volume trends.
    """
    symbol = symbol.upper()
    currency = currency.upper()

    data = get_volume_history(symbol, currency, interval, amount)
    if "error" in data:
        return f"❌ Volume history fetch failed: {data['error']}"

    return summarize_volume(symbol, data.get("history", []), currency)