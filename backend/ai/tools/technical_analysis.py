from typing import List
from langchain_core.tools import tool

from ai.schemas.technical_analysis import *
from ai.schemas.price import CryptoHistoryInput
from ai.domain_functions.technical_analysis import (
    calculate_moving_average,
    calculate_rsi,
    calculate_ema,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_price_trend,
)
from ai.domain_functions.price import get_price_history, compute_trend
from ai.domain_functions.volume import get_volume_history


# -------------------------
# Market / Trend Tools
# -------------------------

@tool(args_schema=MarketSummaryInput, return_direct=True)
def get_market_summary(symbols: List[str], interval: str = "days", amount: int = 7):
    """
    Generate a market summary for multiple cryptocurrencies including trend, average volume, and latest price.

    Args:
        symbols (List[str]): List of coin symbols, e.g., ["BTC", "ETH"].
        interval (str): Interval for historical data ('hours', 'days', 'months'). Defaults to 'days'.
        amount (int): Number of periods to consider. Defaults to 7.

    Returns:
        str: Formatted summary per coin.
    """
    summaries = []
    for sym in symbols:
        price_data = get_price_history(sym.upper(), "USD", interval, amount)
        prices = [p["close"] for p in price_data.get("history", [])]
        trend = "unknown"
        if prices:
            trend = calculate_price_trend(sym, interval, amount)
        vol_data = get_volume_history(sym.upper(), "USD", interval, amount)
        vols = [v["volume"] for v in vol_data.get("history", [])]
        avg_volume = round(sum(vols)/len(vols),2) if vols else 0
        latest_price = prices[-1] if prices else None
        summaries.append(f"{sym.upper()} - Trend: {trend}, Avg Volume: {avg_volume}, Latest Price: {latest_price}")
    return "Market Summary:\n" + "\n".join(summaries)


@tool(args_schema=TopMoversInput, return_direct=True)
def detect_top_movers(symbols: List[str], interval: str = "days", amount: int = 7):
    """
    Identify cryptocurrencies with the highest percentage gains or losses over a period.

    Returns:
        str: Formatted string listing symbol and % change.
    """
    changes = []
    for sym in symbols:
        price_data = get_price_history(sym.upper(), "USD", interval, amount)
        prices = [p["close"] for p in price_data.get("history", [])]
        if not prices:
            continue
        change = (prices[-1] - prices[0]) / prices[0] * 100 if prices[0] != 0 else 0
        changes.append((sym.upper(), round(change,2)))
    changes.sort(key=lambda x: x[1], reverse=True)
    output = [f"{s}: {'+' if c>0 else ''}{c}%" for s, c in changes]
    return "Top Movers:\n" + "\n".join(output)


@tool(args_schema=PriceVolumeCorrelationInput, return_direct=True)
def correlate_price_volume(symbol: str, interval: str = "days", amount: int = 7):
    """
    Analyze correlation between price and volume changes for a coin.

    Returns:
        str: 'positive' or 'negative' correlation description.
    """
    price_data = get_price_history(symbol.upper(), "USD", interval, amount)
    vol_data = get_volume_history(symbol.upper(), "USD", interval, amount)
    prices = [p["close"] for p in price_data.get("history",[])]
    vols = [v["volume"] for v in vol_data.get("history",[])]
    if not prices or not vols:
        return f"No data available for {symbol.upper()}"
    corr = "positive" if (prices[-1]-prices[0])*(vols[-1]-vols[0]) > 0 else "negative"
    return f"{symbol.upper()} shows a {corr} correlation between price and volume over the last {amount} {interval}."


@tool(args_schema=RSIInput, return_direct=True)
def get_rsi(symbol: str, interval: str = "days", amount: int = 14):
    """
    Calculate Relative Strength Index (RSI) for a coin.

    Returns:
        str: Formatted string with RSI value.
    """
    rsi = calculate_rsi(symbol, interval, amount)
    if rsi is None:
        return f"Insufficient data to calculate RSI for {symbol.upper()}"
    return f"{symbol.upper()} RSI ({amount} periods, {interval}): {rsi}"


@tool(args_schema=EMAInput, return_direct=True)
def get_ema(symbol: str, period: int = 14, interval: str = "days"):
    """
    Calculate Exponential Moving Average (EMA) for a coin.

    Returns:
        str: Formatted string with EMA value.
    """
    ema = calculate_ema(symbol, period, interval)
    if ema is None:
        return f"Insufficient data to calculate EMA for {symbol.upper()}"
    return f"{symbol.upper()} EMA ({period} periods, {interval}): {ema}"


@tool(args_schema=MACDInput, return_direct=True)
def get_macd(symbol: str, short_term: int = 12, long_term: int = 26, signal: int = 9, interval: str = "days"):
    """
    Calculate Moving Average Convergence Divergence (MACD) and signal line.

    Returns:
        str: Formatted string with MACD, signal, and histogram.
    """
    macd_res = calculate_macd(symbol, short_term, long_term, signal, interval)
    if not macd_res:
        return f"Insufficient data to calculate MACD for {symbol.upper()}"
    return (
        f"{symbol.upper()} MACD ({interval}):\n"
        f"- MACD Line: {macd_res['macd']}\n"
        f"- Signal Line: {macd_res['signal']}\n"
        f"- Histogram: {macd_res['histogram']}"
    )


@tool(args_schema=BollingerBandsInput, return_direct=True)
def get_bollinger_bands(symbol: str, period: int = 20, interval: str = "days", std_dev_multiplier: float = 2.0):
    """
    Calculate Bollinger Bands for a cryptocurrency.

    Returns:
        str: Formatted string with middle, upper, and lower bands.
    """
    bb = calculate_bollinger_bands(symbol, period, interval, std_dev_multiplier)
    if not bb:
        return f"Insufficient data to calculate Bollinger Bands for {symbol.upper()}"
    return (
        f"{symbol.upper()} Bollinger Bands ({period} periods, {interval}):\n"
        f"- Middle Band: {bb['middle']}\n"
        f"- Upper Band: {bb['upper']}\n"
        f"- Lower Band: {bb['lower']}"
    )


@tool(args_schema=PriceTrendInput, return_direct=True)
def get_price_trend(symbol: str, interval: str = "days", amount: int = 7):
    """
    Determine price trend (upward, downward, stable) for a coin.

    Returns:
        str: Formatted string describing trend.
    """
    trend = calculate_price_trend(symbol, interval, amount)
    return f"{symbol.upper()} Price Trend over last {amount} {interval}: {trend}"