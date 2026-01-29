# backend/ai/tools/TradingStrategies.py
from typing import List, Dict
import requests
from datetime import datetime, timedelta
from langchain_core.tools import tool

COINBASE_API = "https://api.pro.coinbase.com"


# -----------------------------
# HELPER FUNCTIONS (COINBASE)
# -----------------------------
def fetch_market_data(symbol: str, granularity: int = 86400, days: int = 180) -> dict:
    """
    Fetch market data for a symbol from Coinbase, ensuring enough history for strategy analysis.
    granularity: seconds per candle (86400 = 1 day)
    days: number of past days to fetch
    """
    price = None
    trends = {}
    history = []

    pair = f"{symbol}-USD"

    # Get current price
    try:
        resp = requests.get(f"{COINBASE_API}/products/{pair}/ticker", timeout=5)
        resp.raise_for_status()
        price_data = resp.json()
        price = float(price_data.get("price", 0))
    except Exception:
        price = None

    # Calculate max allowed days for requested granularity (max 300 candles)
    max_candles = 300
    max_days = max_candles * granularity / 86400
    if days > max_days:
        days = int(max_days)

    # Get historical candles
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        params = {
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "granularity": granularity,
        }
        resp = requests.get(f"{COINBASE_API}/products/{pair}/candles", params=params, timeout=10)
        resp.raise_for_status()
        candles = resp.json()
        if candles:
            # Coinbase returns [time, low, high, open, close, volume]
            history = [
                {
                    "time": c[0],
                    "low": c[1],
                    "high": c[2],
                    "open": c[3],
                    "close": c[4],
                    "volume": c[5],
                }
                for c in sorted(candles, key=lambda x: x[0])
            ]
    except Exception:
        history = []

    # Simple trend calculation
    try:
        if len(history) >= 30:
            last_close = history[-1]["close"]
            short_ma = sum(c["close"] for c in history[-7:]) / 7
            long_ma = sum(c["close"] for c in history[-30:]) / 30
            trends["short_vs_long"] = "bullish" if short_ma > long_ma else "bearish"
            trends["change_pct"] = ((last_close - history[-30]["close"]) / history[-30]["close"]) * 100
    except Exception:
        trends = {}

    return {"price": price, "trends": trends, "history": history}

# -----------------------------
# STRATEGY LOGIC (PURE PYTHON)
# -----------------------------
def _pin_bar_logic(history: List[Dict]) -> str:
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
# LANGCHAIN TOOLS
# -----------------------------
@tool
def pin_bar_strategy(symbol: str) -> str:
    """Detects Pin Bar patterns for possible trend reversals using Coinbase OHLCV data."""
    data = fetch_market_data(symbol)
    return _pin_bar_logic(data["history"])


@tool
def moving_average_strategy(symbol: str) -> str:
    """Detects trend direction using short-term vs long-term moving averages."""
    data = fetch_market_data(symbol)
    return _moving_average_logic(data["history"])


@tool
def rsi_strategy(symbol: str) -> str:
    """Calculates RSI to detect overbought or oversold conditions."""
    data = fetch_market_data(symbol)
    return _rsi_logic(data["history"])


@tool
def market_analysis(symbol: str) -> str:
    """Aggregates price, trend, and strategy analysis for a crypto asset."""
    data = fetch_market_data(symbol)
    price_line = (
        f"💰 {symbol} price: ${data['price']:.2f}" if isinstance(data["price"], (int, float)) else "Price not available."
    )
    trends_block = (
        "\n".join(f"- {k}: {v}" for k, v in data["trends"].items()) if data["trends"] else "No trend data."
    )
    return "\n".join(
        [
            price_line,
            "### Trends",
            trends_block,
            "### Strategy Analysis",
            f"- {_pin_bar_logic(data['history'])}",
            f"- {_moving_average_logic(data['history'])}",
            f"- {_rsi_logic(data['history'])}",
        ]
    )


# -----------------------------
# EXPORT ALL TOOLS
# -----------------------------
all_strategy_tools = [
    pin_bar_strategy,
    moving_average_strategy,
    rsi_strategy,
    market_analysis,
]