# ai/tools/technical_analysis.py
from typing import List

from langchain_core.tools import tool
from pydantic import BaseModel

from ai.schemas.price import CryptoHistoryInput, CryptoTrendInput, MultiCryptoInput
from ai.domain_functions.price import get_price_history, compute_trend
from ai.domain_functions.volume import get_volume_history, compare_volumes, _extract_volumes, _compute_trend_direction
from ai.schemas.volume import CompareVolumesInput, CryptoVolumeHistoryInput, CompareAverageVolumesInput


def calculate_moving_average(prices: list[float], period: int) -> float:
    if not prices or period <= 0:
        return 0
    return round(sum(prices[-period:]) / min(len(prices), period), 2)

# -------------------------
# Pydantic Schemas
# -------------------------
class MarketSummaryInput(BaseModel):
    symbols: list[str]
    interval: str = "days"
    amount: int = 7

class TopMoversInput(BaseModel):
    symbols: list[str]
    interval: str = "days"
    amount: int = 7

class PriceVolumeCorrelationInput(BaseModel):
    symbol: str
    interval: str = "days"
    amount: int = 7

class PercentageChangeAlertInput(BaseModel):
    symbols: list[str]
    threshold: float = 5.0
    interval: str = "days"
    amount: int = 7

class VolatilityOverviewInput(BaseModel):
    symbol: str
    interval: str = "days"
    amount: int = 7

class MovingAverageInput(BaseModel):
    symbol: str
    short_term: int = 7
    mid_term: int = 14
    interval: str = "days"

class HistoricalPerformanceInput(BaseModel):
    symbol: str
    intervals: list[str] = ["hours", "days", "months"]
    amounts: list[int] = [12, 14, 12]

class CoinComparisonInput(BaseModel):
    symbols: list[str]
    interval: str = "days"
    amount: int = 7

# -------------------------
# Tools
# -------------------------

@tool(args_schema=MarketSummaryInput, return_direct=True)
def get_market_summary(symbols: list[str], interval: str = "days", amount: int = 7):
    """Summarizes price and volume for multiple coins."""
    summaries = []
    for sym in symbols:
        price_data = get_price_history(sym.upper(), "USD", interval, amount)
        vol_data = get_volume_history(sym.upper(), "USD", interval, amount)
        prices = [p["close"] for p in price_data.get("history", [])]
        vols = [v["volume"] for v in vol_data.get("history", [])]
        trend = compute_trend(prices, sym.upper())["trend"] if prices else "unknown"
        avg_volume = round(sum(vols)/len(vols),2) if vols else 0
        summaries.append(
            f"{sym.upper()} - Price Trend: {trend}, Average Volume: {avg_volume}, Latest Price: {prices[-1] if prices else 'N/A'}"
        )
    return "Market Summary:\n" + "\n".join(summaries)

@tool(args_schema=TopMoversInput, return_direct=True)
def detect_top_movers(symbols: list[str], interval: str = "days", amount: int = 7):
    """Detect coins with highest percentage gains/losses."""
    changes = []
    for sym in symbols:
        prices = [p["close"] for p in get_price_history(sym.upper(), "USD", interval, amount).get("history", [])]
        if not prices: continue
        change = (prices[-1]-prices[0])/prices[0]*100 if prices[0] != 0 else 0
        changes.append((sym.upper(), round(change,2)))
    changes.sort(key=lambda x: x[1], reverse=True)
    output = [f"{s}: {'+' if c>0 else ''}{c}%" for s,c in changes]
    return "Top Movers:\n" + "\n".join(output)

@tool(args_schema=PriceVolumeCorrelationInput, return_direct=True)
def correlate_price_volume(symbol: str, interval: str = "days", amount: int = 7):
    """Explain how volume changes correlate with price changes."""
    price_data = get_price_history(symbol.upper(), "USD", interval, amount)
    vol_data = get_volume_history(symbol.upper(), "USD", interval, amount)
    prices = [p["close"] for p in price_data.get("history",[])]
    vols = [v["volume"] for v in vol_data.get("history",[])]
    if not prices or not vols:
        return f"No data available for {symbol.upper()}"
    correlation = "positive" if (prices[-1]-prices[0])*(vols[-1]-vols[0])>0 else "negative"
    return f"{symbol.upper()} shows a {correlation} correlation between price and volume over the last {amount} {interval}."

@tool(args_schema=PercentageChangeAlertInput, return_direct=True)
def detect_percentage_change(symbols: list[str], threshold: float = 5.0, interval: str = "days", amount: int = 7):
    """Highlight coins with changes above threshold."""
    alerts = []
    for sym in symbols:
        prices = [p["close"] for p in get_price_history(sym.upper(), "USD", interval, amount).get("history",[])]
        if not prices: continue
        change = (prices[-1]-prices[0])/prices[0]*100 if prices[0] != 0 else 0
        if abs(change) >= threshold:
            alerts.append(f"{sym.upper()}: {'+' if change>0 else ''}{round(change,2)}%")
    if not alerts:
        return f"No coins exceeded {threshold}% change in the last {amount} {interval}."
    return "Percentage Change Alerts:\n" + "\n".join(alerts)

@tool(args_schema=VolatilityOverviewInput, return_direct=True)
def get_volatility(symbol: str, interval: str = "days", amount: int = 7):
    """Summarize volatility of a coin."""
    prices = [p["close"] for p in get_price_history(symbol.upper(), "USD", interval, amount).get("history",[])]
    if not prices: return f"No price data for {symbol.upper()}"
    high, low = max(prices), min(prices)
    change = (prices[-1]-prices[0])/prices[0]*100 if prices[0]!=0 else 0
    return (
        f"{symbol.upper()} Volatility Overview:\n"
        f"- Period: Last {amount} {interval}\n"
        f"- High: {high}\n- Low: {low}\n- Net Change: {round(change,2)}%\n"
        f"- Trend: {'upward' if change>0 else 'downward' if change<0 else 'stable'}"
    )

@tool(args_schema=MovingAverageInput, return_direct=True)
def get_moving_average(symbol: str, short_term: int = 7, mid_term: int = 14, interval: str = "days"):
    """Calculate moving averages and summarize."""
    prices = [p["close"] for p in get_price_history(symbol.upper(), "USD", interval, mid_term).get("history",[])]
    if not prices: return f"No data for {symbol.upper()}"
    short_avg = calculate_moving_average(prices, short_term)
    mid_avg = calculate_moving_average(prices, mid_term)
    return (
        f"{symbol.upper()} Moving Averages:\n"
        f"- Short Term ({short_term} periods): {short_avg}\n"
        f"- Mid Term ({mid_term} periods): {mid_avg}"
    )

@tool(args_schema=HistoricalPerformanceInput, return_direct=True)
def get_historical_performance(symbol: str, intervals: list[str] = ["hours","days","months"], amounts: list[int] = [12,14,12]):
    """Summarize historical performance over multiple intervals."""
    output = []
    for interval, amount in zip(intervals, amounts):
        prices = [p["close"] for p in get_price_history(symbol.upper(), "USD", interval, amount).get("history",[])]
        trend = compute_trend(prices, symbol.upper())["trend"] if prices else "unknown"
        output.append(f"{interval.capitalize()} ({amount}): {trend} trend")
    return f"{symbol.upper()} Historical Performance:\n" + "\n".join(output)

@tool(args_schema=CoinComparisonInput, return_direct=True)
def compare_coins(symbols: list[str], interval: str = "days", amount: int = 7):
    """Compare multiple coins across price, volume, trend, volatility."""
    output = []
    for sym in symbols:
        price_data = get_price_history(sym.upper(), "USD", interval, amount)
        vol_data = get_volume_history(sym.upper(), "USD", interval, amount)
        prices = [p["close"] for p in price_data.get("history",[])]
        vols = [v["volume"] for v in vol_data.get("history",[])]
        trend = compute_trend(prices, sym.upper())["trend"] if prices else "unknown"
        avg_vol = round(sum(vols)/len(vols),2) if vols else 0
        output.append(
            f"{sym.upper()} - Trend: {trend}, Avg Volume: {avg_vol}, Latest Price: {prices[-1] if prices else 'N/A'}"
        )
    return "Coin Comparison Report:\n" + "\n".join(output)


@tool(args_schema=CryptoHistoryInput, return_direct=True)
def get_crypto_signals(symbol: str, interval: str = "days", amount: int = 3):
    """Return trend signal based on historical prices."""
    history = get_price_history(symbol.upper(), "USD", interval, amount)
    if "error" in history:
        return history

    prices = [c["close"] for c in history["history"]]
    return compute_trend(prices, symbol.upper())


@tool(args_schema=CryptoTrendInput, return_direct=True)
def get_crypto_trends_tool(symbol: str):
    """Return short, mid, and long term trends."""
    symbol = symbol.upper()

    configs = {
        "short_term": ("hours", 12, "Short Term (Last 12 hours)"),
        "mid_term": ("days", 14, "Mid Term (Last 14 days)"),
        "long_term": ("months", 12, "Long Term (Last ~12 months)"),
    }

    results = {}

    for key, (interval, amount, label) in configs.items():
        history = get_price_history(symbol, "USD", interval, amount)
        if "error" in history:
            results[key] = {"label": label, "trend": "unknown"}
        else:
            prices = [c["close"] for c in history["history"]]
            trend = compute_trend(prices, symbol)
            trend["label"] = label
            results[key] = trend

    return {
        "symbol": symbol,
        "trends": results,
    }


@tool(args_schema=MultiCryptoInput, return_direct=True)
def compare_crypto_trends(symbols: List[str], interval: str = "days", amount: int = 7):
    """Compare trends across multiple cryptocurrencies."""
    comparison = {}

    for symbol in symbols:
        symbol = symbol.upper()
        history = get_price_history(symbol, "USD", interval, amount)
        if "error" in history:
            comparison[symbol] = {"error": history["error"]}
            continue

        prices = [c["close"] for c in history["history"]]
        comparison[symbol] = compute_trend(prices, symbol)

    return {
        "interval": interval,
        "amount": amount,
        "comparison": comparison,
    }


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
