from typing import List, Optional

from ai.domain_functions.price import get_price_history, compute_trend
from ai.domain_functions.volume import get_volume_history


def calculate_moving_average(prices: list[float], period: int) -> float:
    """
    Calculate the moving average of the last `period` prices.

    Args:
        prices (list[float]): List of historical prices.
        period (int): Number of periods to average.

    Returns:
        float: Rounded moving average. Returns 0 if prices are empty or period <= 0.
    """
    if not prices or period <= 0:
        return 0
    return round(sum(prices[-period:]) / min(len(prices), period), 2)


def summarize_market(symbols: List[str], interval: str, amount: int) -> List[dict]:
    """
    Summarize price trend, average volume, and latest price for multiple coins.

    Args:
        symbols (List[str]): List of cryptocurrency symbols.
        interval (str): Time interval ("hours", "days", "months").
        amount (int): Number of periods to retrieve.

    Returns:
        List[dict]: Each dict contains `symbol`, `trend`, `avg_volume`, `latest_price`.
    """
    summaries = []
    for sym in symbols:
        price_data = get_price_history(sym.upper(), "USD", interval, amount)
        vol_data = get_volume_history(sym.upper(), "USD", interval, amount)
        prices = [p["close"] for p in price_data.get("history", [])]
        vols = [v["volume"] for v in vol_data.get("history", [])]
        trend = compute_trend(prices, sym.upper())["trend"] if prices else "unknown"
        avg_volume = round(sum(vols)/len(vols), 2) if vols else 0
        summaries.append({
            "symbol": sym.upper(),
            "trend": trend,
            "avg_volume": avg_volume,
            "latest_price": prices[-1] if prices else None
        })
    return summaries


def detect_top_movers_logic(symbols: List[str], interval: str, amount: int) -> List[tuple]:
    """
    Calculate percentage change for multiple coins and sort by highest change.

    Returns:
        List[tuple]: Sorted list of tuples (symbol, change_percentage) descending.
    """
    changes = []
    for sym in symbols:
        prices = [p["close"] for p in get_price_history(sym.upper(), "USD", interval, amount).get("history", [])]
        if not prices:
            continue
        change = (prices[-1] - prices[0]) / prices[0] * 100 if prices[0] != 0 else 0
        changes.append((sym.upper(), round(change, 2)))
    changes.sort(key=lambda x: x[1], reverse=True)
    return changes


def price_volume_correlation(symbol: str, interval: str, amount: int) -> Optional[str]:
    """
    Determine correlation between price changes and volume changes.

    Returns:
        str: "positive" or "negative" correlation. Returns None if no data.
    """
    price_data = get_price_history(symbol.upper(), "USD", interval, amount)
    vol_data = get_volume_history(symbol.upper(), "USD", interval, amount)
    prices = [p["close"] for p in price_data.get("history", [])]
    vols = [v["volume"] for v in vol_data.get("history", [])]
    if not prices or not vols:
        return None
    correlation = "positive" if (prices[-1] - prices[0]) * (vols[-1] - vols[0]) > 0 else "negative"
    return correlation


def detect_percentage_change_logic(symbols: List[str], threshold: float, interval: str, amount: int) -> List[dict]:
    """
    Detect coins exceeding a given percentage change threshold.

    Returns:
        List[dict]: Each dict contains `symbol` and `change`.
    """
    alerts = []
    for sym in symbols:
        prices = [p["close"] for p in get_price_history(sym.upper(), "USD", interval, amount).get("history", [])]
        if not prices:
            continue
        change = (prices[-1] - prices[0]) / prices[0] * 100 if prices[0] != 0 else 0
        if abs(change) >= threshold:
            alerts.append({"symbol": sym.upper(), "change": round(change, 2)})
    return alerts


def get_volatility_logic(symbol: str, interval: str, amount: int) -> Optional[dict]:
    """
    Compute high, low, and net price change for a coin over a period.

    Returns:
        dict: {"high": float, "low": float, "net_change": float} or None if no data.
    """
    prices = [p["close"] for p in get_price_history(symbol.upper(), "USD", interval, amount).get("history", [])]
    if not prices:
        return None
    return {
        "high": max(prices),
        "low": min(prices),
        "net_change": (prices[-1] - prices[0]) / prices[0] * 100 if prices[0] != 0 else 0
    }


def moving_average_logic(symbol: str, short_term: int, mid_term: int, interval: str) -> Optional[dict]:
    """
    Calculate short-term and mid-term moving averages for a coin.

    Returns:
        dict: {"short_avg": float, "mid_avg": float} or None if no price data.
    """
    prices = [p["close"] for p in get_price_history(symbol.upper(), "USD", interval, mid_term).get("history", [])]
    if not prices:
        return None
    return {"short_avg": calculate_moving_average(prices, short_term),
            "mid_avg": calculate_moving_average(prices, mid_term)}


def historical_performance_logic(symbol: str, intervals: List[str], amounts: List[int]) -> dict:
    """
    Compute trend performance over multiple intervals.

    Returns:
        dict: Keyed by interval, each containing {"amount": int, "trend": str}.
    """
    performance = {}
    for interval, amount in zip(intervals, amounts):
        prices = [p["close"] for p in get_price_history(symbol.upper(), "USD", interval, amount).get("history", [])]
        trend = compute_trend(prices, symbol.upper())["trend"] if prices else "unknown"
        performance[interval] = {"amount": amount, "trend": trend}
    return performance


def compare_coins_logic(symbols: List[str], interval: str, amount: int) -> List[dict]:
    """
    Compare multiple coins across trend, average volume, and latest price.

    Returns:
        List[dict]: Each dict contains {"symbol", "trend", "avg_volume", "latest_price"}.
    """
    output = []
    for sym in symbols:
        price_data = get_price_history(sym.upper(), "USD", interval, amount)
        vol_data = get_volume_history(sym.upper(), "USD", interval, amount)
        prices = [p["close"] for p in price_data.get("history", [])]
        vols = [v["volume"] for v in vol_data.get("history", [])]
        trend = compute_trend(prices, sym.upper())["trend"] if prices else "unknown"
        avg_vol = round(sum(vols)/len(vols), 2) if vols else 0
        output.append({
            "symbol": sym.upper(),
            "trend": trend,
            "avg_volume": avg_vol,
            "latest_price": prices[-1] if prices else None
        })
    return output