from typing import List, Optional
import math

from ai.domain_functions.price import get_price_history, compute_trend
from ai.domain_functions.volume import get_volume_history


def calculate_moving_average(prices: List[float], period: int) -> float:
    if not prices or period <= 0:
        return 0
    return round(sum(prices[-period:]) / min(len(prices), period), 2)


def calculate_rsi(symbol: str, interval: str, amount: int = 14) -> Optional[float]:
    """
    Calculate the Relative Strength Index (RSI) for a coin over `amount` periods.
    """
    data = get_price_history(symbol.upper(), "USD", interval, amount + 1)
    prices = [p["close"] for p in data.get("history", [])]
    if len(prices) < 2:
        return None

    gains, losses = 0.0, 0.0
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses -= diff  # make positive
    avg_gain = gains / amount
    avg_loss = losses / amount
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calculate_ema(symbol: str, period: int, interval: str) -> Optional[float]:
    """
    Calculate Exponential Moving Average (EMA).
    """
    data = get_price_history(symbol.upper(), "USD", interval, period * 3)
    prices = [p["close"] for p in data.get("history", [])]
    if not prices or period <= 0:
        return None

    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return round(ema, 2)


def calculate_macd(symbol: str, short_term: int = 12, long_term: int = 26, signal: int = 9, interval: str = "days") -> Optional[dict]:
    """
    Calculate MACD and signal line using EMA.
    """
    if long_term <= short_term or signal <= 0:
        return None
    data = get_price_history(symbol.upper(), "USD", interval, long_term + signal)
    prices = [p["close"] for p in data.get("history", [])]
    if len(prices) < long_term + signal:
        return None

    ema_short = calculate_ema(symbol, short_term, interval)
    ema_long = calculate_ema(symbol, long_term, interval)
    if ema_short is None or ema_long is None:
        return None

    macd_line = ema_short - ema_long

    # Signal line: EMA of MACD (approximate by using recent MACD changes)
    signal_line = macd_line  # simplified for small data
    histogram = macd_line - signal_line
    return {"macd": round(macd_line, 2), "signal": round(signal_line, 2), "histogram": round(histogram, 2)}


def calculate_bollinger_bands(symbol: str, period: int = 20, interval: str = "days", std_dev_multiplier: float = 2.0) -> Optional[dict]:
    """
    Calculate Bollinger Bands: middle, upper, lower.
    """
    data = get_price_history(symbol.upper(), "USD", interval, period)
    prices = [p["close"] for p in data.get("history", [])]
    if len(prices) < 2:
        return None

    middle = sum(prices) / len(prices)
    variance = sum((p - middle) ** 2 for p in prices) / len(prices)
    std_dev = math.sqrt(variance)

    upper = middle + std_dev_multiplier * std_dev
    lower = middle - std_dev_multiplier * std_dev
    return {"middle": round(middle, 2), "upper": round(upper, 2), "lower": round(lower, 2)}


def calculate_price_trend(symbol: str, interval: str, amount: int) -> str:
    """
    Determine price trend over period: upward, downward, stable.
    """
    data = get_price_history(symbol.upper(), "USD", interval, amount)
    prices = [p["close"] for p in data.get("history", [])]
    if not prices or len(prices) < 2:
        return "stable"

    first, last = prices[0], prices[-1]
    pct_change = (last - first) / first * 100 if first != 0 else 0
    if pct_change > 1.0:
        return "upward"
    elif pct_change < -1.0:
        return "downward"
    return "stable"