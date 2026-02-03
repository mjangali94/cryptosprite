# backend/ai/tools/TradingStrategiesTools.py
import math
from typing import List, Dict
from langchain_core.tools import tool
from ai.domain_functions.price import get_price_history, get_spot_price, compute_trend

# -----------------------------
# HISTORY FETCHER
# -----------------------------
def _get_history(symbol: str, interval="days", amount=30) -> List[Dict]:
    """
    Fetch OHLCV historical data for a cryptocurrency symbol.

    Args:
        symbol (str): Cryptocurrency symbol (e.g., BTC)
        interval (str, optional): Interval of candles (hours/days/months). Defaults to "days".
        amount (int, optional): Number of candles to fetch. Defaults to 30.

    Returns:
        List[Dict]: List of OHLCV candles with keys ["open", "high", "low", "close", "volume"].
    """
    result = get_price_history(symbol=symbol.upper(), currency="USD", interval=interval, amount=amount)
    if isinstance(result, dict) and "history" in result:
        return result["history"]
    return []

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------
def _last_n_closes(history: List[Dict], n: int) -> List[float]:
    return [c["close"] for c in history[-n:] if "close" in c]

def _last_n_highs(history: List[Dict], n: int) -> List[float]:
    return [c["high"] for c in history[-n:] if "high" in c]

def _last_n_lows(history: List[Dict], n: int) -> List[float]:
    return [c["low"] for c in history[-n:] if "low" in c]

# -----------------------------
# 1. TREND-FOLLOWING STRATEGIES
# -----------------------------
@tool(description="Breakout Trading: Detects breakout above recent highs or below recent lows.")
def breakout_strategy(symbol: str) -> str:
    """
    Detects bullish or bearish breakout signals.

    Logic:
        - Last close > max previous highs → bullish breakout
        - Last close < min previous lows → bearish breakout

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=10)
    if len(history) < 3: return "Not enough data"
    last = history[-1]["close"]
    prev_high = max(_last_n_highs(history, 5)[:-1])
    prev_low = min(_last_n_lows(history, 5)[:-1])
    if last > prev_high: return "Breakout strategy: bullish breakout"
    if last < prev_low: return "Breakout strategy: bearish breakout"
    return "Breakout strategy: no clear signal"

@tool(description="Pullback/Retest: Detects price pulling back to previous support/resistance.")
def pullback_strategy(symbol: str) -> str:
    """
    Detects potential bullish/bearish entries after pullbacks.

    Logic:
        - Previous close > last close → bullish pullback
        - Previous close < last close → bearish pullback

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 3: return "Not enough data"
    last, prev = history[-1]["close"], history[-2]["close"]
    if prev > last: return "Pullback strategy: possible bullish entry"
    if prev < last: return "Pullback strategy: possible bearish entry"
    return "Pullback strategy: no clear signal"

@tool(description="Trendline Trading: Detects bounces from trendline support/resistance.")
def trendline_strategy(symbol: str) -> str:
    """
    Detects bounce off trendline using 5-period SMA.

    Logic:
        - SMA of last 5 closes
        - Last close > SMA → bullish
        - Last close < SMA → bearish

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 5: return "Not enough data"
    closes = _last_n_closes(history, 5)
    avg = sum(closes) / 5
    last = closes[-1]
    if last > avg: return "Trendline strategy: bullish bounce"
    if last < avg: return "Trendline strategy: bearish bounce"
    return "Trendline strategy: no clear signal"

@tool(description="Channel Trading: Buys near channel support, sells near channel resistance.")
def channel_strategy(symbol: str) -> str:
    """
    Detects price near channel support/resistance using last 5 candles.

    Logic:
        - Last close ≤ min(low) → buy near support
        - Last close ≥ max(high) → sell near resistance

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 5: return "Not enough data"
    highs, lows = _last_n_highs(history, 5), _last_n_lows(history, 5)
    last = history[-1]["close"]
    if last <= min(lows): return "Channel strategy: buy near support"
    if last >= max(highs): return "Channel strategy: sell near resistance"
    return "Channel strategy: no clear signal"

# -----------------------------
# 2. REVERSAL STRATEGIES
# -----------------------------
@tool(description="Double Top / Double Bottom: Detects reversal patterns based on failed levels.")
def double_top_bottom_strategy(symbol: str) -> str:
    """
    Detects double top/bottom patterns.

    Logic:
        - Compare last 3 closes
        - Last < prev & prev2 > prev → double top (bearish)
        - Last > prev & prev2 < prev → double bottom (bullish)

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 4: return "Not enough data"
    last, prev, prev2 = _last_n_closes(history, 3)
    if last < prev and prev2 > prev: return "Double top detected: bearish reversal"
    if last > prev and prev2 < prev: return "Double bottom detected: bullish reversal"
    return "Double top/bottom strategy: no clear signal"

@tool(description="Head and Shoulders / Inverse Head and Shoulders pattern detection.")
def head_shoulders_strategy(symbol: str) -> str:
    """
    Detects H&S or inverted H&S reversals.

    Logic:
        - Analyze last 5 closes
        - Pattern detection for bearish or bullish reversal

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 5: return "Not enough data"
    closes = _last_n_closes(history, 5)
    if closes[0] < closes[1] > closes[2] < closes[3]: return "Head & Shoulders detected: bearish"
    if closes[0] > closes[1] < closes[2] > closes[3]: return "Inverse Head & Shoulders: bullish"
    return "Head/shoulders strategy: no clear signal"

@tool(description="Pin Bar / Hammer / Shooting Star candlestick detection.")
def pin_bar_strategy(symbol: str) -> str:
    """
    Detects Pin Bar, Hammer, or Shooting Star for reversals.

    Logic:
        - Body vs upper/lower wicks
        - Upper wick > 2*body → bearish
        - Lower wick > 2*body → bullish

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=2)
    if len(history) < 2: return "Not enough data"
    c = history[-1]
    body = abs(c["close"] - c["open"])
    upper = c["high"] - max(c["close"], c["open"])
    lower = min(c["close"], c["open"]) - c["low"]
    if upper > 2 * body: return "Pin Bar: bearish"
    if lower > 2 * body: return "Pin Bar: bullish"
    return "Pin Bar strategy: no clear signal"

# -----------------------------
# 3. CONTINUATION PATTERNS
# -----------------------------
@tool(description="Flag/Pennant continuation patterns.")
def flag_pennant_strategy(symbol: str) -> str:
    """
    Detects flags or pennants for trend continuation.

    Logic:
        - Last 3 closes range <1% of last close → flag/pennant
        - Trend continuation expected

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Signal description.
    """
    history = _get_history(symbol, amount=3)
    if len(history) < 3: return "Not enough data"
    closes = _last_n_closes(history, 3)
    if max(closes) - min(closes) < 0.01 * closes[-1]: return "Flag/pennant detected: trend continuation"
    return "Flag/pennant strategy: no clear signal"

# -----------------------------
# 4. SUPPORT & RESISTANCE STRATEGIES
# -----------------------------
@tool(description="Bounce strategy at support/resistance levels.")
def bounce_strategy(symbol: str) -> str:
    """
    Buys near support, sells near resistance.

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 5: return "Not enough data"
    last = history[-1]["close"]
    support, resistance = min(_last_n_lows(history,5)), max(_last_n_highs(history,5))
    if last <= support: return "Bounce: buy at support"
    if last >= resistance: return "Bounce: sell at resistance"
    return "Bounce strategy: no clear signal"

# -----------------------------
# 5. CANDLESTICK FORMATIONS
# -----------------------------
@tool(description="Doji pattern detection.")
def doji_strategy(symbol: str) -> str:
    """
    Detects Doji candlestick (indecision).

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Signal description.
    """
    history = _get_history(symbol, amount=2)
    if len(history) < 2: return "Not enough data"
    c = history[-1]
    body = abs(c["close"] - c["open"])
    range_ = c["high"] - c["low"]
    if body < 0.1 * range_: return "Doji detected: indecision"
    return "Doji strategy: no clear signal"

# -----------------------------
# 5. CANDLESTICK FORMATIONS (continued)
# -----------------------------
@tool(description="Three White Soldiers / Three Black Crows pattern detection.")
def three_soldiers_crows_strategy(symbol: str) -> str:
    """
    Detects strong trend continuation or reversal via Three White Soldiers (bullish)
    or Three Black Crows (bearish) candlestick patterns.

    Logic:
        - Three consecutive bullish candles with higher closes → Three White Soldiers
        - Three consecutive bearish candles with lower closes → Three Black Crows

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=4)
    if len(history) < 3: return "Not enough data"
    closes = _last_n_closes(history, 3)
    opens = [c["open"] for c in history[-3:]]
    # Check Three White Soldiers
    if all(closes[i] > opens[i] for i in range(3)) and closes[0] < closes[1] < closes[2]:
        return "Three White Soldiers detected: strong bullish trend"
    # Check Three Black Crows
    if all(closes[i] < opens[i] for i in range(3)) and closes[0] > closes[1] > closes[2]:
        return "Three Black Crows detected: strong bearish trend"
    return "No Three Soldiers/Crows pattern detected"

@tool(description="Morning Star / Evening Star candlestick pattern detection.")
def morning_evening_star_strategy(symbol: str) -> str:
    """
    Detects Morning Star (bullish reversal) and Evening Star (bearish reversal)
    formations using 3-candle sequences.

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 3: return "Not enough data"
    closes = _last_n_closes(history, 3)
    opens = [c["open"] for c in history[-3:]]
    # Morning Star: first bearish, small middle candle, last bullish
    if closes[0] < opens[0] and abs(closes[1]-opens[1]) < 0.25*abs(closes[0]-opens[0]) and closes[2] > opens[2]:
        return "Morning Star detected: bullish reversal"
    # Evening Star: first bullish, small middle candle, last bearish
    if closes[0] > opens[0] and abs(closes[1]-opens[1]) < 0.25*abs(closes[0]-opens[0]) and closes[2] < opens[2]:
        return "Evening Star detected: bearish reversal"
    return "No Morning/Evening Star detected"

@tool(description="Tweezers candlestick pattern detection.")
def tweezers_strategy(symbol: str) -> str:
    """
    Detects Tweezer Top/Bottom formations indicating reversals.

    Logic:
        - Tweezer Top: last two highs roughly equal → bearish reversal
        - Tweezer Bottom: last two lows roughly equal → bullish reversal

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=3)
    if len(history) < 2: return "Not enough data"
    highs = _last_n_highs(history,2)
    lows = _last_n_lows(history,2)
    if abs(highs[0]-highs[1]) < 0.01*highs[1]: return "Tweezer Top detected: bearish reversal"
    if abs(lows[0]-lows[1]) < 0.01*lows[1]: return "Tweezer Bottom detected: bullish reversal"
    return "No Tweezer pattern detected"

@tool(description="Marubozu candlestick detection.")
def marubozu_strategy(symbol: str) -> str:
    """
    Detects Marubozu candles indicating strong trend continuation.

    Logic:
        - No upper/lower wicks
        - Close > Open → bullish Marubozu
        - Close < Open → bearish Marubozu

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=1)
    if not history: return "Not enough data"
    c = history[-1]
    body = abs(c["close"]-c["open"])
    wick_upper = c["high"] - max(c["close"],c["open"])
    wick_lower = min(c["close"],c["open"]) - c["low"]
    if wick_upper < 0.01*body and wick_lower < 0.01*body:
        return "Bullish Marubozu" if c["close"] > c["open"] else "Bearish Marubozu"
    return "No Marubozu detected"

# -----------------------------
# 6. VOLATILITY & MOMENTUM
# -----------------------------
@tool(description="False Breakout / Fakeout detection.")
def false_breakout_strategy(symbol: str) -> str:
    """
    Detects false breakouts when price quickly reverses after breaching previous highs/lows.

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history)<3: return "Not enough data"
    last, prev = history[-1]["close"], history[-2]["close"]
    if (last>max(_last_n_highs(history,5)[:-1]) and prev<last): return "Possible false bullish breakout"
    if (last<min(_last_n_lows(history,5)[:-1]) and prev>last): return "Possible false bearish breakout"
    return "No false breakout detected"

@tool(description="Momentum Push Strategy detection.")
def momentum_push_strategy(symbol: str) -> str:
    """
    Detects strong directional moves after consolidation.

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    closes = _last_n_closes(history,5)
    if max(closes)-min(closes) < 0.01*closes[-1]:  # consolidation
        if closes[-1] > closes[-2]: return "Bullish momentum push"
        if closes[-1] < closes[-2]: return "Bearish momentum push"
    return "No momentum push detected"

@tool(description="Swing Highs/Lows detection.")
def swing_high_low_strategy(symbol: str) -> str:
    """
    Detects price bouncing from swing highs or swing lows.

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    last = history[-1]["close"]
    highs = _last_n_highs(history,5)
    lows = _last_n_lows(history,5)
    if last <= min(lows): return "Buy near swing low"
    if last >= max(highs): return "Sell near swing high"
    return "No swing signal"

# -----------------------------
# 7. MISCELLANEOUS / ADVANCED
# -----------------------------
@tool(description="Order Block detection (Supply/Demand zones).")
def order_block_strategy(symbol: str) -> str:
    """
    Detects potential institutional order blocks (support/resistance zones).

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    closes = _last_n_closes(history,5)
    if closes[-1]<min(closes[:-1]): return "Potential demand zone (buy)"
    if closes[-1]>max(closes[:-1]): return "Potential supply zone (sell)"
    return "No order block detected"

@tool(description="Market Structure Shift detection.")
def market_structure_shift_strategy(symbol: str) -> str:
    """
    Detects changes in higher highs/lower lows trend structure.

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    closes = _last_n_closes(history,5)
    if closes[-1]>closes[-2]>closes[-3]: return "Uptrend confirmed"
    if closes[-1]<closes[-2]<closes[-3]: return "Downtrend confirmed"
    return "No market structure shift"

@tool(description="Liquidity Grab / Stop Hunt detection.")
def liquidity_grab_strategy(symbol: str) -> str:
    """
    Detects moves triggering stops before reversal.

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    last, prev = history[-1]["close"], history[-2]["close"]
    highs = _last_n_highs(history,5)
    lows = _last_n_lows(history,5)
    if last>max(highs[:-1]) and prev<last: return "Possible liquidity grab above resistance"
    if last<min(lows[:-1]) and prev>last: return "Possible liquidity grab below support"
    return "No liquidity grab detected"

@tool(description="Wyckoff accumulation/distribution detection.")
def wyckoff_strategy(symbol: str) -> str:
    """
    Detects Wyckoff phases (accumulation or distribution) from price action.

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=6)
    closes = _last_n_closes(history,6)
    if max(closes)-min(closes)<0.02*closes[-1]: return "Accumulation/Distribution zone detected"
    if closes[-1]>closes[-2]: return "Price moving up from zone"
    return "Price moving down from zone"


@tool(description="Break and Retest: Detects price break then retest of support/resistance.")
def break_retest_strategy(symbol: str) -> str:
    """
    Detects breakouts and retests of support/resistance levels.

    Logic:
        - Last close > previous high → bullish breakout
        - Last close < previous low → bearish breakout
        - Otherwise → no signal

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 5: return "Not enough data"
    last = history[-1]["close"]
    prev_high = max(_last_n_highs(history,5)[:-1])
    prev_low = min(_last_n_lows(history,5)[:-1])
    if last > prev_high: return "Break and Retest: bullish breakout"
    if last < prev_low: return "Break and Retest: bearish breakout"
    return "Break/retest strategy: no clear signal"

@tool(description="Psychological Levels: Detects price near major rounded numbers.")
def psychological_level_strategy(symbol: str) -> str:
    """
    Detects reactions near psychological/round-number levels.

    Logic:
        - Round price to nearest 100 → watch for reversal or breakout
        - Otherwise → no signal

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if not history: return "Not enough data"
    last = history[-1]["close"]
    rounded = round(last, -2)
    if abs(last - rounded) < 0.5: return f"Near psychological level {rounded}: watch for reversal or breakout"
    return "Psychological level strategy: no clear signal"

@tool(description="Triangle pattern detection.")
def triangle_strategy(symbol: str) -> str:
    """
    Detects ascending, descending, or symmetrical triangle consolidation patterns.

    Logic:
        - Look at last 5 highs/lows
        - Compare slope of highs vs slope of lows
        - Ascending, descending, symmetrical triangles → potential breakout

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 5: return "Not enough data"
    highs = _last_n_highs(history,5)
    lows = _last_n_lows(history,5)
    if all(highs[i] < highs[i+1] for i in range(4)) and all(lows[i] < lows[i+1] for i in range(4)):
        return "Ascending triangle detected: potential breakout"
    if all(highs[i] > highs[i+1] for i in range(4)) and all(lows[i] > lows[i+1] for i in range(4)):
        return "Descending triangle detected: potential breakout"
    return "Triangle pattern: no clear signal"

@tool(description="Rectangle / Range pattern detection.")
def rectangle_strategy(symbol: str) -> str:
    """
    Detects range-bound rectangular consolidation patterns.

    Logic:
        - Last 5 highs ≈ same level
        - Last 5 lows ≈ same level
        - Price oscillates → rectangle/range

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=5)
    if len(history) < 5: return "Not enough data"
    highs = _last_n_highs(history,5)
    lows = _last_n_lows(history,5)
    if max(highs)-min(highs) < 0.02*max(highs) and max(lows)-min(lows) < 0.02*max(lows):
        return "Rectangle/range pattern detected: watch for breakout"
    return "Rectangle pattern: no clear signal"

@tool(description="Engulfing candlestick pattern detection.")
def engulfing_strategy(symbol: str) -> str:
    """
    Detects bullish or bearish engulfing candlestick patterns.

    Logic:
        - Bullish engulfing: previous bearish candle followed by larger bullish candle
        - Bearish engulfing: previous bullish candle followed by larger bearish candle

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=2)
    if len(history) < 2: return "Not enough data"
    prev, last = history[-2], history[-1]
    if prev["close"] < prev["open"] and last["close"] > last["open"] and last["close"] > prev["open"]:
        return "Bullish engulfing detected"
    if prev["close"] > prev["open"] and last["close"] < last["open"] and last["close"] < prev["open"]:
        return "Bearish engulfing detected"
    return "No engulfing pattern detected"

@tool(description="Inside Bar Breakout detection.")
def inside_bar_strategy(symbol: str) -> str:
    """
    Detects breakout after an inside bar formation.

    Logic:
        - Last candle breaks high of previous candle → bullish
        - Last candle breaks low of previous candle → bearish

    Args:
        symbol (str): Cryptocurrency symbol.

    Returns:
        str: Strategy signal.
    """
    history = _get_history(symbol, amount=3)
    if len(history) < 3: return "Not enough data"
    prev, last = history[-2], history[-1]
    if last["close"] > prev["high"]: return "Inside bar breakout: bullish"
    if last["close"] < prev["low"]: return "Inside bar breakout: bearish"
    return "Inside bar strategy: no clear signal"



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
    psychological_level_strategy,
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
]