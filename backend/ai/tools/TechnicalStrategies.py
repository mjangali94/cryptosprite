# backend/ai/tools/TechnicalStrategies.py
from typing import List, Dict
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from utils.crypto_assets import resolve_asset_symbol
from ai.tools.CryptoPrice import get_price_history, compute_trend, get_spot_price
import math

# -----------------------------
# STRATEGY LOGIC (PURE PYTHON)
# -----------------------------
def _pin_bar_logic(history: List[Dict]) -> str:
    """
    Detects Pin Bar patterns in the latest candle for potential trend reversals.

    Args:
        history (List[Dict]): Historical OHLCV data.

    Returns:
        str: Strategy signal or explanation.
    """
    if not history or len(history) < 5:
        return "Pin Bar strategy: not enough data."

    c = history[-1]
    try:
        body = abs(c["close"] - c["open"])
        upper_wick = c["high"] - max(c["close"], c["open"])
        lower_wick = min(c["close"], c["open"]) - c["low"]
    except KeyError:
        return "Pin Bar strategy: invalid candle data."

    if upper_wick > 2 * body:
        return "Pin Bar strategy indicates potential bearish reversal."
    if lower_wick > 2 * body:
        return "Pin Bar strategy indicates potential bullish reversal."

    return "Pin Bar strategy does not give a clear signal."


def _moving_average_logic(history: List[Dict]) -> str:
    """
    Compares short-term and long-term moving averages to detect trend direction.

    Args:
        history (List[Dict]): Historical OHLCV data.

    Returns:
        str: Bullish, bearish, or unclear signal.
    """
    if not history or len(history) < 20:
        return "Moving Average strategy: not enough data."

    closes = [c["close"] for c in history if "close" in c]
    if len(closes) < 20:
        return "Moving Average strategy: insufficient clean data."

    short_ma = sum(closes[-5:]) / 5
    long_ma = sum(closes[-20:]) / 20

    if short_ma > long_ma:
        return "Moving Average strategy indicates bullish trend."
    if short_ma < long_ma:
        return "Moving Average strategy indicates bearish trend."

    return "Moving Average strategy does not give a clear signal."


def _rsi_logic(history: List[Dict]) -> str:
    """
    Calculates Relative Strength Index (RSI) to detect overbought/oversold conditions.

    Args:
        history (List[Dict]): Historical OHLCV data.

    Returns:
        str: RSI-based signal or explanation.
    """
    if not history or len(history) < 15:
        return "RSI strategy: not enough data."

    closes = [c["close"] for c in history if "close" in c]
    if len(closes) < 15:
        return "RSI strategy: insufficient clean data."

    gains, losses = 0.0, 0.0
    for i in range(-14, -1):
        delta = closes[i + 1] - closes[i]
        if delta > 0:
            gains += delta
        else:
            losses -= delta

    rsi = 100.0 if losses == 0 else 100 - (100 / (1 + gains / losses))

    if rsi > 70:
        return "RSI indicates overbought conditions (possible sell)."
    if rsi < 30:
        return "RSI indicates oversold conditions (possible buy)."

    return "RSI does not give a clear signal."


# -----------------------------
# NEW STRATEGIES
# -----------------------------
def _bollinger_bands_logic(history: List[Dict]) -> str:
    """
    Detects overbought or oversold conditions using Bollinger Bands.

    Args:
        history (List[Dict]): Last 20 OHLCV candles.

    Returns:
        str: Strategy signal or explanation.
    """
    if not history or len(history) < 20:
        return "Bollinger Bands strategy: not enough data."
    closes = [c["close"] for c in history[-20:]]
    mean = sum(closes) / len(closes)
    std_dev = math.sqrt(sum((x - mean) ** 2 for x in closes) / len(closes))
    upper = mean + 2 * std_dev
    lower = mean - 2 * std_dev
    last_close = closes[-1]

    if last_close > upper:
        return "Bollinger Bands indicates overbought (possible sell)."
    if last_close < lower:
        return "Bollinger Bands indicates oversold (possible buy)."
    return "Bollinger Bands does not give a clear signal."


def _macd_logic(history: List[Dict]) -> str:
    """
    Detects bullish/bearish signals using MACD crossover.

    Args:
        history (List[Dict]): Last 26 OHLCV candles.

    Returns:
        str: MACD-based signal or explanation.
    """
    if not history or len(history) < 26:
        return "MACD strategy: not enough data."
    closes = [c["close"] for c in history if "close" in c]
    ema12 = sum(closes[-12:]) / 12
    ema26 = sum(closes[-26:]) / 26
    macd = ema12 - ema26
    signal = sum(closes[-9:]) / 9 - ema26  # simplified signal line
    if macd > signal:
        return "MACD indicates bullish crossover."
    if macd < signal:
        return "MACD indicates bearish crossover."
    return "MACD does not give a clear signal."


def _stochastic_oscillator_logic(history: List[Dict]) -> str:
    """
    Detects overbought or oversold conditions using the Stochastic Oscillator.

    Args:
        history (List[Dict]): Last 14 OHLCV candles.

    Returns:
        str: Stochastic-based signal or explanation.
    """
    if not history or len(history) < 14:
        return "Stochastic strategy: not enough data."
    closes = [c["close"] for c in history[-14:]]
    lows = [c["low"] for c in history[-14:]]
    highs = [c["high"] for c in history[-14:]]
    last_close = closes[-1]
    lowest_low = min(lows)
    highest_high = max(highs)
    percent_k = ((last_close - lowest_low) / (highest_high - lowest_low)) * 100 if highest_high != lowest_low else 50
    if percent_k > 80:
        return "Stochastic indicates overbought (possible sell)."
    if percent_k < 20:
        return "Stochastic indicates oversold (possible buy)."
    return "Stochastic does not give a clear signal."


# -----------------------------
# HISTORY FETCHER
# -----------------------------
def _get_history(symbol: str, interval="days", amount=30) -> List[Dict]:
    """
    Fetch historical OHLCV data using get_price_history tool.

    Args:
        symbol (str): Cryptocurrency symbol (e.g., BTC).
        interval (str): Interval type ('hours', 'days', 'months').
        amount (int): Number of intervals to fetch.

    Returns:
        List[Dict]: List of OHLCV candle dicts.
    """
    result = get_price_history(symbol=symbol.upper(), currency="USD", interval=interval, amount=amount)
    if isinstance(result, dict) and "history" in result:
        return result["history"]
    return []


# -----------------------------
# LANGCHAIN TOOLS
# -----------------------------
@tool
def pin_bar_strategy(symbol: str) -> str:
    """Detects Pin Bar patterns for possible trend reversals."""
    history = _get_history(symbol)
    return _pin_bar_logic(history)


@tool
def moving_average_strategy(symbol: str) -> str:
    """Detects trend direction using short-term vs long-term moving averages."""
    history = _get_history(symbol, amount=30)
    return _moving_average_logic(history)


@tool
def rsi_strategy(symbol: str) -> str:
    """Calculates RSI to detect overbought or oversold conditions."""
    history = _get_history(symbol, amount=15)
    return _rsi_logic(history)


@tool
def bollinger_bands_strategy(symbol: str) -> str:
    """Detects overbought/oversold conditions using Bollinger Bands."""
    history = _get_history(symbol, amount=20)
    return _bollinger_bands_logic(history)


@tool
def macd_strategy(symbol: str) -> str:
    """Detects bullish/bearish signals using MACD crossover."""
    history = _get_history(symbol, amount=26)
    return _macd_logic(history)


@tool
def stochastic_strategy(symbol: str) -> str:
    """Detects overbought/oversold conditions using the Stochastic Oscillator."""
    history = _get_history(symbol, amount=14)
    return _stochastic_oscillator_logic(history)


@tool
def market_analysis(symbol: str) -> str:
    """
    Aggregates spot price, trend, and multiple strategies for a crypto asset.

    Args:
        symbol (str): Cryptocurrency symbol (e.g., BTC).

    Returns:
        str: Human-readable summary including trends and strategy signals.
    """
    history = _get_history(symbol, amount=30)
    price_data = get_spot_price(symbol, "USD")
    price_line = f"💰 {symbol} price: ${price_data['price']:.2f}" if "price" in price_data else "Price not available."
    closes = [c["close"] for c in history]
    trends = compute_trend(closes, symbol) if closes else {}

    return "\n".join([
        price_line,
        "### Trend",
        f"- Direction: {trends.get('trend', 'unknown')}",
        f"- Change %: {trends.get('price_change_percent', 0)}",
        f"- High: {trends.get('high', 0)}, Low: {trends.get('low', 0)}",
        "### Strategy Analysis",
        f"- {_pin_bar_logic(history)}",
        f"- {_moving_average_logic(history)}",
        f"- {_rsi_logic(history)}",
        f"- {_bollinger_bands_logic(history)}",
        f"- {_macd_logic(history)}",
        f"- {_stochastic_oscillator_logic(history)}"
    ])


# -----------------------------
# EXPORT ALL TOOLS
# -----------------------------
all_strategy_tools = [
    pin_bar_strategy,
    moving_average_strategy,
    rsi_strategy,
    bollinger_bands_strategy,
    macd_strategy,
    stochastic_strategy,
    market_analysis,
]