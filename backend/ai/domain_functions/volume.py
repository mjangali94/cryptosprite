# ai/services/volume_domain.py

from typing import List, Dict, Optional, Tuple
from ai.fetch.fetch_coinbase import fetch_coinbase

# -------------------------
# Constants & Helpers
# -------------------------
INTERVAL_GRANULARITY = {
    "hours": 3600,
    "days": 86400,
    "months": 86400,
}


def resolve_granularity(interval: str, amount: int) -> Tuple[int, int]:
    """
    Convert interval string to Coinbase API granularity and compute the number of points.

    Args:
        interval (str): Interval for historical data. One of "hours", "days", "months".
        amount (int): Number of intervals requested.

    Returns:
        Tuple[int, int]: Granularity in seconds, number of points to fetch.

    Raises:
        ValueError: If the interval is invalid.
    """
    if interval not in INTERVAL_GRANULARITY:
        raise ValueError("Invalid interval (use hours/days/months)")
    granularity = INTERVAL_GRANULARITY[interval]
    points = amount * 30 if interval == "months" else amount
    return granularity, points


def calc_volume_trend(vols: List[float]) -> Dict[str, float | str]:
    """
    Compute trading volume trend metrics: first, last, percent change, and trend direction.

    Args:
        vols (List[float]): List of historical volumes.

    Returns:
        Dict[str, float | str]: Dictionary with first, last volumes, percent change, and trend ("increasing", "decreasing", "stable", or "unknown").
    """
    if not vols:
        return {"first": 0, "last": 0, "change_pct": 0, "trend": "unknown"}
    first, last = vols[0], vols[-1]
    change_pct = (last - first) / first if first != 0 else 0
    trend = "increasing" if change_pct > 0 else "decreasing" if change_pct < 0 else "stable"
    return {"first": first, "last": last, "change_pct": change_pct, "trend": trend}


def volume_stats(vols: List[float]) -> Dict[str, float]:
    """
    Compute basic statistical metrics of a volume list: average, max, min.

    Args:
        vols (List[float]): List of historical volumes.

    Returns:
        Dict[str, float]: Dictionary containing average, maximum, and minimum volume.
    """
    if not vols:
        return {"average": 0, "max": 0, "min": 0}
    return {"average": sum(vols) / len(vols), "max": max(vols), "min": min(vols)}


# -------------------------
# Domain Functions
# -------------------------
def get_current_volume(symbol: str, currency: str = "USD") -> Dict[str, float | str]:
    """
    Fetch the current 24-hour trading volume and price of a cryptocurrency from Coinbase.

    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC").
        currency (str, optional): Quote currency (default "USD").

    Returns:
        Dict[str, float | str]: Dictionary containing symbol, volume, price, and currency,
                                or an error message if the API call fails.
    """
    data = fetch_coinbase(f"products/{symbol}-{currency}/ticker")
    if "error" in data:
        return data
    return {
        "symbol": symbol.upper(),
        "volume": float(data.get("volume", 0)),
        "price": float(data.get("price", 0)),
        "currency": currency.upper(),
    }


def get_volume_history(
    symbol: str, currency: str, interval: str, amount: int
) -> Dict[str, object]:
    """
    Fetch historical trading volume data from Coinbase for a given cryptocurrency.

    Args:
        symbol (str): Cryptocurrency symbol (e.g., "ETH").
        currency (str): Quote currency (e.g., "USD").
        interval (str): Interval string: "hours", "days", or "months".
        amount (int): Number of intervals to fetch.

    Returns:
        Dict[str, object]: Dictionary containing symbol, currency, interval, number of points, and history of volumes,
                           or an error message if fetching fails.
    """
    try:
        granularity, points = resolve_granularity(interval, amount)
    except ValueError as e:
        return {"error": str(e)}

    data = fetch_coinbase(
        f"products/{symbol}-{currency}/candles",
        params={"granularity": granularity},
    )
    if "error" in data:
        return data

    candles = data[:points]
    candles.reverse()
    history = [{"volume": c[5]} for c in candles]  # index 5 = volume

    return {
        "symbol": symbol.upper(),
        "currency": currency.upper(),
        "interval": interval,
        "points": len(history),
        "history": history,
    }


def summarize_volume(
    symbol: str, history: List[Dict[str, float]], currency: str = "USD"
) -> str:
    """
    Generate a detailed human-readable summary for trading volume history.

    Args:
        symbol (str): Cryptocurrency symbol.
        history (List[Dict[str, float]]): List of historical volume dictionaries.
        currency (str, optional): Currency for display (default "USD").

    Returns:
        str: Natural language summary including latest volume, trend, max, min, and number of data points.
    """
    if not history:
        return f"No volume data available for {symbol.upper()}."

    vols = [v["volume"] for v in history]
    trend_data = calc_volume_trend(vols)
    stats = volume_stats(vols)

    return (
        f"### {symbol.upper()} Trading Volume Summary\n"
        f"- **Recent Volume**: {trend_data['last']:,.2f} {currency.upper()}\n"
        f"- **Trend**: The volume has been {trend_data['trend']} "
        f"({trend_data['change_pct']*100:.2f}% change from the start of this period).\n"
        f"- **Highest Volume**: {stats['max']:,.2f} {currency.upper()}\n"
        f"- **Lowest Volume**: {stats['min']:,.2f} {currency.upper()}\n"
        f"- **Data Points**: {len(vols)} periods analyzed."
    )


def compare_volumes(
    symbols: List[str], interval: str = "days", amount: int = 7, currency: str = "USD"
) -> Dict[str, Dict[str, object]]:
    """
    Compare trading volumes for multiple cryptocurrencies and generate structured summaries.

    Args:
        symbols (List[str]): List of cryptocurrency symbols.
        interval (str, optional): Interval string: "hours", "days", or "months". Defaults to "days".
        amount (int, optional): Number of intervals to fetch. Defaults to 7.
        currency (str, optional): Quote currency for all symbols. Defaults to "USD".

    Returns:
        Dict[str, Dict[str, object]]: Dictionary mapping each symbol to its volume summary and history.
    """
    comparison = {}
    for sym in symbols:
        data = get_volume_history(sym.upper(), currency.upper(), interval, amount)
        comparison[sym.upper()] = {
            "summary": summarize_volume(sym.upper(), data.get("history", []), currency),
            "history": data.get("history", []),
        }
    return comparison


def _extract_volumes(data: dict) -> Tuple[List[float], List[dict]]:
    """
    Extract volumes and raw history from fetched data for internal use.

    Args:
        data (dict): Dictionary returned by get_volume_history or get_current_volume.

    Returns:
        Tuple[List[float], List[dict]]: List of volume values and raw history.
    """
    history = data.get("history", [])
    volumes = [v["volume"] for v in history]
    return volumes, history


def _compute_trend_direction(volumes: List[float]) -> str:
    """
    Determine the trend direction from a list of volumes.

    Args:
        volumes (List[float]): Historical volume values.

    Returns:
        str: Trend direction: "increasing", "decreasing", or "stable". Returns "unknown" for insufficient data.
    """
    if not volumes or len(volumes) < 2:
        return "unknown"
    if volumes[-1] > volumes[0]:
        return "increasing"
    elif volumes[-1] < volumes[0]:
        return "decreasing"
    return "stable"