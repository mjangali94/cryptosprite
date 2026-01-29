# ai/tools/CryptoAnalytics.py

import requests
from langchain_core.tools import tool
from pydantic import BaseModel
from utils.crypto_assets import resolve_asset_symbol
from ai.tools.CryptoPrice import get_price_history, compute_trend, get_spot_price
from ai.tools.CryptoVolume import get_volume_history

COINBASE_API_BASE = "https://api.exchange.coinbase.com"
REQUEST_TIMEOUT = 8

# -------------------------
# Helper Functions
# -------------------------
def fetch_coinbase(endpoint: str, params: dict | None = None) -> dict:
    url = f"{COINBASE_API_BASE}/{endpoint.lstrip('/')}"
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 429:
            return {"error": "Coinbase rate limit exceeded"}
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"error": "Coinbase request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

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
        prices = [p["price"] for p in price_data.get("history", [])]
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
        prices = [p["price"] for p in get_price_history(sym.upper(), "USD", interval, amount).get("history", [])]
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
    prices = [p["price"] for p in price_data.get("history",[])]
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
        prices = [p["price"] for p in get_price_history(sym.upper(), "USD", interval, amount).get("history",[])]
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
    prices = [p["price"] for p in get_price_history(symbol.upper(), "USD", interval, amount).get("history",[])]
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
    prices = [p["price"] for p in get_price_history(symbol.upper(), "USD", interval, mid_term).get("history",[])]
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
        prices = [p["price"] for p in get_price_history(symbol.upper(), "USD", interval, amount).get("history",[])]
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
        prices = [p["price"] for p in price_data.get("history",[])]
        vols = [v["volume"] for v in vol_data.get("history",[])]
        trend = compute_trend(prices, sym.upper())["trend"] if prices else "unknown"
        avg_vol = round(sum(vols)/len(vols),2) if vols else 0
        output.append(
            f"{sym.upper()} - Trend: {trend}, Avg Volume: {avg_vol}, Latest Price: {prices[-1] if prices else 'N/A'}"
        )
    return "Coin Comparison Report:\n" + "\n".join(output)