from typing import List

from langchain_core.tools import tool

from ai.schemas.price import CryptoHistoryInput, CryptoTrendInput, MultiCryptoInput
from ai.schemas.technical_analysis import (
    MarketSummaryInput, TopMoversInput, PriceVolumeCorrelationInput,
    PercentageChangeAlertInput, VolatilityOverviewInput, MovingAverageInput,
    HistoricalPerformanceInput, CoinComparisonInput
)
from ai.schemas.volume import CompareVolumesInput, CryptoVolumeHistoryInput, CompareAverageVolumesInput
from ai.domain_functions.technical_analysis import (
    calculate_moving_average,
    summarize_market,
    detect_top_movers_logic,
    price_volume_correlation,
    detect_percentage_change_logic,
    get_volatility_logic,
    moving_average_logic,
    historical_performance_logic,
    compare_coins_logic
)
from ai.domain_functions.volume import compare_volumes, get_volume_history
from ai.domain_functions.price import get_price_history, compute_trend


# -------------------------
# Tools
# -------------------------

@tool(args_schema=MarketSummaryInput, return_direct=True)
def get_market_summary(symbols: list[str], interval: str = "days", amount: int = 7):
    """
    Generate a summary of price trends and average trading volume for multiple cryptocurrencies.

    Args:
        symbols (list[str]): List of cryptocurrency symbols, e.g., ["BTC", "ETH"].
        interval (str, optional): Time interval for historical data ("hours", "days", "months"). Defaults to "days".
        amount (int, optional): Number of intervals to consider. Defaults to 7.

    Returns:
        str: Formatted string summarizing trend, average volume, and latest price for each coin.

    Example:
        >>> get_market_summary(["BTC","ETH"], interval="days", amount=7)
        Market Summary:
        BTC - Trend: upward, Avg Volume: 12345.67, Latest Price: 50000
        ETH - Trend: downward, Avg Volume: 2345.67, Latest Price: 4000
    """
    summaries = summarize_market(symbols, interval, amount)
    output = []
    for s in summaries:
        output.append(
            f"{s['symbol']} - Trend: {s['trend']}, Avg Volume: {s['avg_volume']}, Latest Price: {s['latest_price']}"
        )
    return "Market Summary:\n" + "\n".join(output)


@tool(args_schema=TopMoversInput, return_direct=True)
def detect_top_movers(symbols: list[str], interval: str = "days", amount: int = 7):
    """
    Identify cryptocurrencies with the largest percentage gains or losses over a given period.

    Args:
        symbols (list[str]): List of cryptocurrency symbols to analyze.
        interval (str, optional): Time interval for historical data. Defaults to "days".
        amount (int, optional): Number of intervals to consider. Defaults to 7.

    Returns:
        str: Formatted string listing each coin with its percentage change, sorted descending by change.

    Example:
        >>> detect_top_movers(["BTC","ETH"], "days", 7)
        Top Movers:
        BTC: +5.34%
        ETH: -2.12%
    """
    changes = detect_top_movers_logic(symbols, interval, amount)
    output = [f"{s}: {'+' if c>0 else ''}{c}%" for s, c in changes]
    return "Top Movers:\n" + "\n".join(output)


@tool(args_schema=PriceVolumeCorrelationInput, return_direct=True)
def correlate_price_volume(symbol: str, interval: str = "days", amount: int = 7):
    """
    Analyze correlation between price and volume for a single cryptocurrency.

    Args:
        symbol (str): Cryptocurrency symbol to analyze, e.g., "BTC".
        interval (str, optional): Time interval for historical data. Defaults to "days".
        amount (int, optional): Number of intervals to consider. Defaults to 7.

    Returns:
        str: Description of correlation as 'positive' or 'negative'. Returns a message if no data is available.

    Example:
        >>> correlate_price_volume("BTC", "days", 7)
        BTC shows a positive correlation between price and volume over the last 7 days.
    """
    corr = price_volume_correlation(symbol, interval, amount)
    if not corr:
        return f"No data available for {symbol.upper()}"
    return f"{symbol.upper()} shows a {corr} correlation between price and volume over the last {amount} {interval}."


@tool(args_schema=PercentageChangeAlertInput, return_direct=True)
def detect_percentage_change(symbols: list[str], threshold: float = 5.0, interval: str = "days", amount: int = 7):
    """
    Detect cryptocurrencies whose price changed beyond a specified percentage threshold.

    Args:
        symbols (list[str]): List of cryptocurrency symbols to check.
        threshold (float, optional): Percentage threshold for alerts. Defaults to 5.0.
        interval (str, optional): Time interval for historical data. Defaults to "days".
        amount (int, optional): Number of intervals to consider. Defaults to 7.

    Returns:
        str: Formatted string listing coins exceeding the threshold or a message if none did.

    Example:
        >>> detect_percentage_change(["BTC","ETH"], 5.0)
        Percentage Change Alerts:
        BTC: +6.23%
    """
    alerts = detect_percentage_change_logic(symbols, threshold, interval, amount)
    if not alerts:
        return f"No coins exceeded {threshold}% change in the last {amount} {interval}."
    output = [f"{a['symbol']}: {'+' if a['change']>0 else ''}{a['change']}%" for a in alerts]
    return "Percentage Change Alerts:\n" + "\n".join(output)


@tool(args_schema=VolatilityOverviewInput, return_direct=True)
def get_volatility(symbol: str, interval: str = "days", amount: int = 7):
    """
    Summarize price volatility for a cryptocurrency over a given period.

    Args:
        symbol (str): Cryptocurrency symbol.
        interval (str, optional): Time interval for historical data. Defaults to "days".
        amount (int, optional): Number of intervals to consider. Defaults to 7.

    Returns:
        str: Human-readable summary including highest, lowest, net change, and trend.

    Example:
        >>> get_volatility("BTC", "days", 7)
        BTC Volatility Overview:
        - Period: Last 7 days
        - High: 50000
        - Low: 48000
        - Net Change: 3.45%
        - Trend: upward
    """
    vol = get_volatility_logic(symbol, interval, amount)
    if not vol:
        return f"No price data for {symbol.upper()}"
    trend = "upward" if vol["net_change"]>0 else "downward" if vol["net_change"]<0 else "stable"
    return (
        f"{symbol.upper()} Volatility Overview:\n"
        f"- Period: Last {amount} {interval}\n"
        f"- High: {vol['high']}\n- Low: {vol['low']}\n- Net Change: {round(vol['net_change'],2)}%\n"
        f"- Trend: {trend}"
    )


@tool(args_schema=MovingAverageInput, return_direct=True)
def get_moving_average(symbol: str, short_term: int = 7, mid_term: int = 14, interval: str = "days"):
    """
    Calculate short-term and mid-term moving averages for a cryptocurrency.

    Args:
        symbol (str): Cryptocurrency symbol.
        short_term (int, optional): Short-term period. Defaults to 7.
        mid_term (int, optional): Mid-term period. Defaults to 14.
        interval (str, optional): Time interval for historical data. Defaults to "days".

    Returns:
        str: Formatted string with short-term and mid-term moving averages.

    Example:
        >>> get_moving_average("BTC", 7, 14, "days")
        BTC Moving Averages:
        - Short Term (7 periods): 49500
        - Mid Term (14 periods): 49000
    """
    ma = moving_average_logic(symbol, short_term, mid_term, interval)
    if not ma:
        return f"No data for {symbol.upper()}"
    return (
        f"{symbol.upper()} Moving Averages:\n"
        f"- Short Term ({short_term} periods): {ma['short_avg']}\n"
        f"- Mid Term ({mid_term} periods): {ma['mid_avg']}"
    )


@tool(args_schema=HistoricalPerformanceInput, return_direct=True)
def get_historical_performance(symbol: str, intervals: list[str] = ["hours","days","months"], amounts: list[int] = [12,14,12]):
    """
    Summarize historical performance for a cryptocurrency across multiple intervals.

    Args:
        symbol (str): Cryptocurrency symbol.
        intervals (list[str], optional): List of intervals to analyze. Defaults to ["hours","days","months"].
        amounts (list[int], optional): Number of periods per interval. Defaults to [12,14,12].

    Returns:
        str: Formatted string showing trend per interval.

    Example:
        >>> get_historical_performance("BTC")
        BTC Historical Performance:
        Hours (12): upward trend
        Days (14): downward trend
        Months (12): stable trend
    """
    perf = historical_performance_logic(symbol, intervals, amounts)
    output = [f"{i.capitalize()} ({v['amount']}): {v['trend']} trend" for i, v in perf.items()]
    return f"{symbol.upper()} Historical Performance:\n" + "\n".join(output)


@tool(args_schema=CoinComparisonInput, return_direct=True)
def compare_coins(symbols: list[str], interval: str = "days", amount: int = 7):
    """
    Compare multiple cryptocurrencies in terms of trend, average volume, and latest price.

    Args:
        symbols (list[str]): List of cryptocurrency symbols.
        interval (str, optional): Time interval for historical data. Defaults to "days".
        amount (int, optional): Number of periods to analyze. Defaults to 7.

    Returns:
        str: Formatted report comparing all coins.

    Example:
        >>> compare_coins(["BTC","ETH"])
        Coin Comparison Report:
        BTC - Trend: upward, Avg Volume: 12345.67, Latest Price: 50000
        ETH - Trend: downward, Avg Volume: 2345.67, Latest Price: 4000
    """
    results = compare_coins_logic(symbols, interval, amount)
    output = []
    for r in results:
        output.append(
            f"{r['symbol']} - Trend: {r['trend']}, Avg Volume: {r['avg_volume']}, Latest Price: {r['latest_price']}"
        )
    return "Coin Comparison Report:\n" + "\n".join(output)


# -------------------------
# Volume Tools
# -------------------------

@tool(args_schema=CompareVolumesInput, return_direct=True)
def compare_crypto_volumes(symbols: List[str], interval: str = "days", amount: int = 7) -> str:
    """
    Compare trading volume trends for multiple cryptocurrencies.

    Args:
        symbols (List[str]): List of cryptocurrency symbols.
        interval (str, optional): Interval granularity. Defaults to "days".
        amount (int, optional): Number of periods. Defaults to 7.

    Returns:
        str: Human-readable comparison of volume trends.
    """
    return compare_volumes(symbols, interval, amount)


@tool(args_schema=CryptoVolumeHistoryInput, return_direct=True)
def get_crypto_average_volume(symbol: str, interval: str, amount: int) -> str:
    """
    Compute the average trading volume for a cryptocurrency over a period.

    Args:
        symbol (str): Cryptocurrency symbol.
        interval (str): Interval granularity.
        amount (int): Number of intervals.

    Returns:
        str: Summary including average, trend direction, and basic statistics.
    """
    data = get_volume_history(symbol.upper(), "USD", interval, amount)
    volumes = [v["volume"] for v in data.get("history", [])]
    if not volumes:
        return f"No volume data for {symbol.upper()} over last {amount} {interval}."
    avg_volume = sum(volumes)/len(volumes)
    trend = "upward" if volumes[-1] > volumes[0] else "downward" if volumes[-1] < volumes[0] else "stable"
    return f"{symbol.upper()} Avg Volume: {avg_volume:,.2f} USD, Trend: {trend}"


@tool(args_schema=CompareAverageVolumesInput, return_direct=True)
def compare_average_volumes(symbols: List[str], interval: str = "days", amount: int = 7) -> str:
    """
    Compare average trading volumes for multiple cryptocurrencies.

    Args:
        symbols (List[str]): List of cryptocurrency symbols.
        interval (str, optional): Interval granularity. Defaults to "days".
        amount (int, optional): Number of intervals. Defaults to 7.

    Returns:
        str: Formatted summary of average volumes per coin.
    """
    summaries = []
    for symbol in symbols:
        data = get_volume_history(symbol.upper(), "USD", interval, amount)
        volumes = [v["volume"] for v in data.get("history", [])]
        if not volumes:
            summaries.append(f"{symbol.upper()}: no data")
            continue
        avg = sum(volumes)/len(volumes)
        summaries.append(f"{symbol.upper()}: Average Volume = {avg:,.2f} USD")
    return "Average Volumes:\n" + "\n".join(summaries)