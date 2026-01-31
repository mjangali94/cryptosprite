# ai/tools/volume.py

from typing import List
from langchain_core.tools import tool

from ai.domain_functions.volume import get_current_volume, get_volume_history, summarize_volume, compare_volumes, \
    _extract_volumes, _compute_trend_direction
from ai.schemas.volume import CryptoVolumeInput, CryptoVolumeHistoryInput, CompareVolumesInput, CompareAverageVolumesInput

# -------------------------
# Tools
# -------------------------
@tool(args_schema=CryptoVolumeInput, return_direct=True)
def get_crypto_volume(symbol: str, currency: str = "USD") -> str:
    """
    Fetch the current 24-hour trading volume and price for a given cryptocurrency.

    Args:
        symbol (str): Cryptocurrency symbol, e.g., "BTC".
        currency (str, optional): Currency in which to fetch volume and price. Defaults to "USD".

    Returns:
        str: Human-readable summary including 24h volume and current price.
    """
    result = get_current_volume(symbol.upper(), currency.upper())
    if "error" in result:
        return f"❌ Volume fetch failed: {result['error']}"

    return (
        f"💹 {result['symbol']} 24h Volume: {result['volume']:,.2f} {currency.upper()}\n"
        f"Current Price: ${result['price']:,.2f} USD"
    )


@tool(args_schema=CryptoVolumeHistoryInput, return_direct=True)
def get_crypto_volume_history(symbol: str, interval: str, amount: int) -> str:
    """
    Fetch historical trading volume for a cryptocurrency and summarize it.

    Args:
        symbol (str): Cryptocurrency symbol, e.g., "ETH".
        interval (str): Interval granularity: "hours", "days", or "months".
        amount (int): Number of intervals to fetch.

    Returns:
        str: Human-readable natural language summary of volume trends.
    """
    data = get_volume_history(symbol.upper(), "USD", interval, amount)
    if "error" in data:
        return f"❌ Volume history fetch failed: {data['error']}"
    return summarize_volume(symbol.upper(), data.get("history", []))


@tool(args_schema=CompareVolumesInput, return_direct=True)
def compare_crypto_volumes(symbols: List[str], interval: str = "days", amount: int = 7) -> str:
    """
    Compare trading volume trends across multiple cryptocurrencies.

    Args:
        symbols (List[str]): List of cryptocurrency symbols, e.g., ["BTC", "ETH"].
        interval (str, optional): Interval granularity ("hours", "days", "months"). Defaults to "days".
        amount (int, optional): Number of intervals to fetch. Defaults to 7.

    Returns:
        str: Multi-coin summary comparing volume trends.
    """
    return compare_volumes(symbols, interval, amount)


@tool(args_schema=CryptoVolumeHistoryInput, return_direct=True)
def get_crypto_average_volume(symbol: str, interval: str, amount: int) -> str:
    """
    Compute the average trading volume of a cryptocurrency over a specified period.

    Args:
        symbol (str): Cryptocurrency symbol.
        interval (str): Interval granularity.
        amount (int): Number of intervals to fetch.

    Returns:
        str: Human-readable summary including average, highest, lowest volume, and trend.
    """
    data = get_volume_history(symbol.upper(), "USD", interval, amount)
    volumes, history = _extract_volumes(data)
    if not volumes:
        return f"No volume data available for {symbol.upper()} over the last {amount} {interval}."

    avg_volume = sum(volumes) / len(volumes)
    trend = _compute_trend_direction(volumes)
    return (
        f"📊 Average Volume Summary for {symbol.upper()}:\n"
        f"- **Average Volume**: {avg_volume:,.2f} USD over the last {len(volumes)} {interval} periods.\n"
        f"- **Highest Volume**: {max(volumes):,.2f} USD\n"
        f"- **Lowest Volume**: {min(volumes):,.2f} USD\n"
        f"- **Trend**: {trend}"
    )


@tool(args_schema=CryptoVolumeHistoryInput, return_direct=True)
def detect_volume_spikes(symbol: str, interval: str, amount: int, threshold: float = 0.2) -> str:
    """
    Detect significant spikes or drops in trading volume for a cryptocurrency.

    Args:
        symbol (str): Cryptocurrency symbol.
        interval (str): Interval granularity.
        amount (int): Number of intervals to fetch.
        threshold (float, optional): Percent change to consider significant (default 0.2 = 20%).

    Returns:
        str: Human-readable message indicating if a spike/drop was detected.
    """
    data = get_volume_history(symbol.upper(), "USD", interval, amount)
    volumes, history = _extract_volumes(data)
    if not volumes:
        return f"No volume data available for {symbol.upper()}."

    first, last = volumes[0], volumes[-1]
    change_pct = (last - first) / first if first != 0 else 0

    if abs(change_pct) > threshold:
        trend = "spike" if change_pct > 0 else "drop"
        return f"⚡ Significant volume {trend} detected for {symbol.upper()}! Change: {change_pct*100:.2f}%"
    return f"No major volume spikes detected for {symbol.upper()}. Change: {change_pct*100:.2f}%"


@tool(args_schema=CompareAverageVolumesInput, return_direct=True)
def compare_average_volumes(symbols: List[str], interval: str = "days", amount: int = 7) -> str:
    """
    Compare average trading volumes for multiple cryptocurrencies.

    Args:
        symbols (List[str]): List of cryptocurrency symbols.
        interval (str, optional): Interval granularity. Defaults to "days".
        amount (int, optional): Number of intervals to fetch. Defaults to 7.

    Returns:
        str: Multi-coin summary with average volumes.
    """
    summaries = []
    for symbol in symbols:
        data = get_volume_history(symbol.upper(), "USD", interval, amount)
        volumes, history = _extract_volumes(data)
        if not volumes:
            summaries.append(f"{symbol.upper()}: no data")
            continue
        avg = sum(volumes) / len(volumes)
        summaries.append(f"{symbol.upper()}: Average Volume = {avg:,.2f} USD")
    return "Average Volumes:\n" + "\n".join(summaries)