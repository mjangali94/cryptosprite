# backend/ai/tools/TradingStrategiesTools.py
import math
from typing import List, Dict
from langchain_core.tools import tool
from ai.domain_functions.price import get_price_history

from ai.domain_functions.price import get_spot_price, compute_trend



# -----------------------------
# HISTORY FETCHER
# -----------------------------
def _get_history(symbol: str, interval="days", amount=30) -> List[Dict]:
    """
    Fetch OHLCV historical data for a cryptocurrency symbol.

    Args:
        symbol: Crypto symbol (e.g., BTC)
        interval: Interval of candles (hours/days/months)
        amount: Number of intervals to fetch

    Returns:
        List of OHLCV candles as dictionaries
    """
    result = get_price_history(symbol=symbol.upper(), currency="USD", interval=interval, amount=amount)
    if isinstance(result, dict) and "history" in result:
        return result["history"]
    return []

# -----------------------------
# 1. Trend-Following Strategies
# -----------------------------

@tool(description="Breakout Trading: Detects breakout above recent highs or below recent lows.")
def breakout_strategy(symbol: str) -> str:
    """Detects bullish or bearish breakouts based on recent highs/lows."""
    history = _get_history(symbol)
    if len(history) < 3:
        return "Not enough data for breakout strategy."
    highs = [c["high"] for c in history]
    lows = [c["low"] for c in history]
    last_close = history[-1]["close"]
    if last_close > max(highs[:-1]):
        return "Breakout strategy: bullish breakout."
    if last_close < min(lows[:-1]):
        return "Breakout strategy: bearish breakout."
    return "Breakout strategy: no clear signal."

@tool(description="Pullback/Retest: Detects price pulling back to previous support/resistance.")
def pullback_strategy(symbol: str) -> str:
    """Detects potential entries after a pullback in the trend direction."""
    history = _get_history(symbol)
    if len(history) < 3:
        return "Not enough data for pullback strategy."
    last = history[-1]["close"]
    prev = history[-2]["close"]
    if prev > last:
        return "Pullback strategy: possible bullish entry."
    if prev < last:
        return "Pullback strategy: possible bearish entry."
    return "Pullback strategy: no clear signal."

@tool(description="Trendline Trading: Detects bounces from trendline support/resistance.")
def trendline_strategy(symbol: str) -> str:
    """Uses simple moving averages to simulate trendline behavior for entries."""
    history = _get_history(symbol)
    if len(history) < 5:
        return "Not enough data for trendline strategy."
    closes = [c["close"] for c in history]
    avg = sum(closes[-5:]) / 5
    if closes[-1] > avg:
        return "Trendline strategy: bullish bounce."
    if closes[-1] < avg:
        return "Trendline strategy: bearish bounce."
    return "Trendline strategy: no clear signal."

@tool(description="Channel Trading: Buys near channel support, sells near channel resistance.")
def channel_strategy(symbol: str) -> str:
    """Detects price near channel support/resistance using recent highs/lows."""
    history = _get_history(symbol)
    if len(history) < 5:
        return "Not enough data for channel strategy."
    highs = [c["high"] for c in history[-5:]]
    lows = [c["low"] for c in history[-5:]]
    last_close = history[-1]["close"]
    if last_close <= min(lows):
        return "Channel strategy: buy near support."
    if last_close >= max(highs):
        return "Channel strategy: sell near resistance."
    return "Channel strategy: no clear signal."

# -----------------------------
# 2. Reversal Strategies
# -----------------------------

@tool(description="Double Top / Double Bottom: Detects reversal patterns based on failed levels.")
def double_top_bottom_strategy(symbol: str) -> str:
    """Detects potential reversal at double top or double bottom patterns."""
    history = _get_history(symbol)
    if len(history) < 4:
        return "Not enough data for double top/bottom strategy."
    last = history[-1]["close"]
    prev = history[-2]["close"]
    prev2 = history[-3]["close"]
    if last < prev and prev2 > prev:
        return "Double top detected: possible bearish reversal."
    if last > prev and prev2 < prev:
        return "Double bottom detected: possible bullish reversal."
    return "Double top/bottom strategy: no clear signal."

@tool(description="Head and Shoulders / Inverse Head and Shoulders pattern detection.")
def head_shoulders_strategy(symbol: str) -> str:
    """Detects head and shoulders or inverse head and shoulders reversal patterns."""
    history = _get_history(symbol)
    if len(history) < 5:
        return "Not enough data for head/shoulders strategy."
    closes = [c["close"] for c in history[-5:]]
    if closes[1] < closes[0] and closes[2] > closes[1] and closes[3] < closes[2]:
        return "Head and shoulders detected: bearish reversal."
    if closes[1] > closes[0] and closes[2] < closes[1] and closes[3] > closes[2]:
        return "Inverse head and shoulders detected: bullish reversal."
    return "Head/shoulders strategy: no clear signal."

@tool(description="Pin Bar / Hammer / Shooting Star: Detects candlestick reversal patterns.")
def pin_bar_strategy(symbol: str) -> str:
    """Detects candlestick reversal patterns from last candle."""
    history = _get_history(symbol)
    if not history:
        return "Not enough data for pin bar strategy."
    c = history[-1]
    body = abs(c["close"] - c["open"])
    upper_wick = c["high"] - max(c["close"], c["open"])
    lower_wick = min(c["close"], c["open"]) - c["low"]
    if upper_wick > 2 * body:
        return "Pin Bar: bearish reversal."
    if lower_wick > 2 * body:
        return "Pin Bar: bullish reversal."
    return "Pin Bar strategy: no clear signal."

@tool(description="Engulfing Patterns: Detects bullish or bearish engulfing candles.")
def engulfing_strategy(symbol: str) -> str:
    """Detects strong bullish or bearish reversal momentum via engulfing candles."""
    history = _get_history(symbol)
    if len(history) < 2:
        return "Not enough data for engulfing strategy."
    prev = history[-2]
    last = history[-1]
    if last["close"] > last["open"] and prev["close"] < prev["open"] and last["close"] > prev["open"]:
        return "Bullish engulfing detected."
    if last["close"] < last["open"] and prev["close"] > prev["open"] and last["close"] < prev["open"]:
        return "Bearish engulfing detected."
    return "Engulfing strategy: no clear signal."

@tool(description="Inside Bar Breakout: Detects breakout after inside bar.")
def inside_bar_strategy(symbol: str) -> str:
    """Detects potential reversal after inside bar breakout."""
    history = _get_history(symbol)
    if len(history) < 3:
        return "Not enough data for inside bar strategy."
    prev = history[-2]
    last = history[-1]
    if last["close"] > prev["high"]:
        return "Inside bar breakout: bullish."
    if last["close"] < prev["low"]:
        return "Inside bar breakout: bearish."
    return "Inside bar strategy: no clear signal."

# -----------------------------
# 3. Continuation Patterns
# -----------------------------

@tool(description="Flags and Pennants: Detects short-term consolidation patterns.")
def flag_pennant_strategy(symbol: str) -> str:
    """Detects continuation patterns during strong trend."""
    history = _get_history(symbol)
    if len(history) < 3:
        return "Not enough data for flag/pennant strategy."
    closes = [c["close"] for c in history[-3:]]
    if max(closes) - min(closes) < 0.01 * closes[-1]:
        return "Flag/pennant detected: possible trend continuation."
    return "Flag/pennant strategy: no clear signal."

@tool(description="Triangles: Detects ascending, descending, or symmetrical triangle patterns.")
def triangle_strategy(symbol: str) -> str:
    """Detects triangle consolidation patterns and potential continuation breakout."""
    history = _get_history(symbol)
    if len(history) < 3:
        return "Not enough data for triangle strategy."
    return "Triangle strategy: placeholder logic."

@tool(description="Rectangles: Detects range continuation patterns.")
def rectangle_strategy(symbol: str) -> str:
    """Detects rectangular consolidation patterns."""
    history = _get_history(symbol)
    if len(history) < 3:
        return "Not enough data for rectangle strategy."
    return "Rectangle strategy: placeholder logic."

# -----------------------------
# 4. Support & Resistance
# -----------------------------

@tool(description="Bounce Strategy: Buy at support, sell at resistance.")
def bounce_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    if len(history) < 5:
        return "Not enough data for bounce strategy."
    last_close = history[-1]["close"]
    support = min(c["low"] for c in history[-5:])
    resistance = max(c["high"] for c in history[-5:])
    if last_close <= support:
        return "Bounce strategy: buy at support."
    if last_close >= resistance:
        return "Bounce strategy: sell at resistance."
    return "Bounce strategy: no clear signal."

@tool(description="Break and Retest: Detects price break then retest of support/resistance.")
def break_retest_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    if len(history) < 5:
        return "Not enough data for break/retest strategy."
    last = history[-1]["close"]
    prev_high = max(c["high"] for c in history[-5:-1])
    prev_low = min(c["low"] for c in history[-5:-1])
    if last > prev_high:
        return "Break and retest: bullish breakout."
    if last < prev_low:
        return "Break and retest: bearish breakout."
    return "Break/retest strategy: no clear signal."

@tool(description="Round Numbers / Psychological Levels: Detects reaction near major levels.")
def psychological_level_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    if not history:
        return "Not enough data for psychological level strategy."
    last_close = history[-1]["close"]
    rounded = round(last_close, -2)
    if abs(last_close - rounded) < 0.5:
        return f"Near psychological level {rounded}: watch for reversal or breakout."
    return "Psychological level strategy: no clear signal."

# -----------------------------
# 5. Price Action Candlestick Setups
# -----------------------------

@tool(description="Doji Patterns: Detects indecision candles.")
def doji_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    if not history:
        return "Not enough data for doji strategy."
    c = history[-1]
    body = abs(c["close"] - c["open"])
    range_ = c["high"] - c["low"]
    if body < 0.1 * range_:
        return "Doji detected: indecision."
    return "Doji strategy: no clear signal."

@tool(description="Three White Soldiers / Three Black Crows: Detects strong trend continuation/reversal.")
def three_soldiers_crows_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    if len(history) < 3:
        return "Not enough data."
    return "Three soldiers/crows strategy: placeholder."

@tool(description="Morning Star / Evening Star: Detects reversal candlestick formations.")
def morning_evening_star_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    if len(history) < 3:
        return "Not enough data."
    return "Morning/evening star strategy: placeholder."

@tool(description="Tweezers: Detects double top/bottom in candlestick form.")
def tweezers_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    if len(history) < 2:
        return "Not enough data."
    return "Tweezers strategy: placeholder."

@tool(description="Marubozu Candles: Detects strong trend continuation or breakout.")
def marubozu_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    if not history:
        return "Not enough data."
    return "Marubozu strategy: placeholder."

# -----------------------------
# 6. Volatility & Momentum
# -----------------------------

@tool(description="False Breakout / Fakeout: Detects reversal after fake breakout.")
def false_breakout_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    return "False breakout strategy: placeholder."

@tool(description="Momentum Push Strategy: Detects strong directional moves after consolidation.")
def momentum_push_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    return "Momentum push strategy: placeholder."

@tool(description="Swing Highs / Lows: Buys near higher lows or sells near lower highs.")
def swing_high_low_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    return "Swing high/low strategy: placeholder."

# -----------------------------
# 7. Miscellaneous / Advanced
# -----------------------------

@tool(description="Order Block / Supply and Demand Zones: Detects smart money zones.")
def order_block_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    return "Order block strategy: placeholder."

@tool(description="Market Structure Shift: Detects changes in highs/lows sequence.")
def market_structure_shift_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    return "Market structure shift strategy: placeholder."


@tool(description="Liquidity Grab / Stop Hunt: Detects moves triggering stops before reversal.")
def liquidity_grab_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    return "Liquidity grab strategy: placeholder."

@tool(description="Wyckoff Method: Detects accumulation and distribution phases.")
def wyckoff_strategy(symbol: str) -> str:
    history = _get_history(symbol)
    return "Wyckoff strategy: placeholder."



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
# EXPORT TOOLS
# -----------------------------
all_price_action_tools = [
    breakout_strategy,
    pullback_strategy,
    trendline_strategy,
    channel_strategy,
    double_top_bottom_strategy,
    head_shoulders_strategy,
    pin_bar_strategy,
    engulfing_strategy,
    inside_bar_strategy,
    flag_pennant_strategy,
    triangle_strategy,
    rectangle_strategy,
    bounce_strategy,
    break_retest_strategy,
    doji_strategy,
    three_soldiers_crows_strategy,
    morning_evening_star_strategy,
    tweezers_strategy,
    marubozu_strategy,
    false_breakout_strategy,
    momentum_push_strategy,
    swing_high_low_strategy,
    order_block_strategy,
    market_structure_shift_strategy,
    liquidity_grab_strategy,
    wyckoff_strategy,
    moving_average_strategy,
    rsi_strategy,
    bollinger_bands_strategy,
    macd_strategy,
    stochastic_strategy,
    market_analysis,
]