# ai/tools/volume.py

import requests
from langchain_core.tools import tool
from pydantic import BaseModel

from ai.fetch.fetch_coinbase import fetch_coinbase


# -------------------------
# Domain Functions
# -------------------------
def get_current_volume(symbol: str, currency: str = "USD") -> dict:
    """Fetch current 24h trading volume from Coinbase."""
    data = fetch_coinbase(f"products/{symbol}-{currency}/ticker")
    if "error" in data:
        return data
    return {
        "symbol": symbol,
        "volume": float(data.get("volume", 0)),
        "price": float(data.get("price", 0)),
    }

def get_volume_history(symbol: str, currency: str, interval: str, amount: int) -> dict:
    """Return historical volume data."""
    if interval == "hours":
        granularity = 3600
        points = amount
    elif interval == "days":
        granularity = 86400
        points = amount
    elif interval == "months":
        granularity = 86400
        points = amount * 30
    else:
        return {"error": "Invalid interval (use hours/days/months)"}

    data = fetch_coinbase(
        f"products/{symbol}-{currency}/candles",
        params={"granularity": granularity},
    )
    if "error" in data:
        return data

    candles = data[:points]
    candles.reverse()
    history = [{"volume": c[5]} for c in candles]  # index 5 = volume in Coinbase API

    return {
        "symbol": symbol,
        "currency": currency,
        "interval": interval,
        "points": len(history),
        "history": history,
    }

def summarize_volume(symbol: str, history: list[dict]) -> str:
    """Create a detailed natural-language summary for volume history."""
    if not history:
        return f"No volume data available for {symbol}."

    vols = [v["volume"] for v in history]
    first, last = vols[0], vols[-1]
    change = (last - first) / first * 100 if first != 0 else 0
    trend = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"

    summary = (
        f"### {symbol.upper()} Trading Volume Summary\n"
        f"- **Recent Volume**: {last:,.2f} USD over the last period.\n"
        f"- **Trend**: The volume has been {trend} ({change:.2f}% change from the start of this period).\n"
        f"- **Highest Volume**: {max(vols):,.2f} USD\n"
        f"- **Lowest Volume**: {min(vols):,.2f} USD\n"
        f"- **Data Points**: {len(vols)} periods analyzed."
    )
    return summary

def compare_volumes(symbols: list[str], interval: str = "days", amount: int = 7) -> str:
    """Compare trading volumes of multiple coins with detailed summaries."""
    summaries = []
    for sym in symbols:
        data = get_volume_history(sym.upper(), "USD", interval, amount)
        summary = summarize_volume(sym.upper(), data.get("history", []))
        summaries.append(summary)
    return "\n\n".join(summaries)

# -------------------------
# Pydantic Schemas
# -------------------------
class CryptoVolumeInput(BaseModel):
    symbol: str
    currency: str = "USD"

class CryptoVolumeHistoryInput(BaseModel):
    symbol: str
    interval: str
    amount: int

class CompareVolumesInput(BaseModel):
    symbols: list[str]
    interval: str = "days"
    amount: int = 7

# -------------------------
# Tools
# -------------------------
@tool(args_schema=CryptoVolumeInput, return_direct=True)
def get_crypto_volume(symbol: str, currency: str = "USD"):
    """Get current 24h trading volume with detailed summary."""
    result = get_current_volume(symbol.upper(), currency.upper())
    if "error" in result:
        return f"❌ Volume fetch failed: {result['error']}"
    # wrap current volume in a simple summary
    return (
        f"💹 {result['symbol']} 24h Volume: {result['volume']:,.2f} {currency.upper()}\n"
        f"Current Price: ${result['price']:,.2f} USD"
    )

@tool(args_schema=CryptoVolumeHistoryInput, return_direct=True)
def get_crypto_volume_history(symbol: str, interval: str, amount: int):
    """Get historical trading volume with natural-language summary."""
    result = get_volume_history(symbol.upper(), "USD", interval, amount)
    if "error" in result:
        return f"❌ Volume history fetch failed: {result['error']}"
    return summarize_volume(symbol.upper(), result.get("history", []))

@tool(args_schema=CompareVolumesInput, return_direct=True)
def compare_crypto_volumes(symbols: list[str], interval: str = "days", amount: int = 7):
    """Compare volume trends across multiple coins with detailed summaries."""
    return compare_volumes(symbols, interval, amount)


@tool(args_schema=CryptoVolumeHistoryInput, return_direct=True)
def get_crypto_average_volume(symbol: str, interval: str, amount: int):
    """Compute the average trading volume for a given coin over a specified period."""
    data = get_volume_history(symbol.upper(), "USD", interval, amount)
    history = data.get("history", [])
    if not history:
        return f"No volume data available for {symbol.upper()} over the last {amount} {interval}."

    vols = [v["volume"] for v in history]
    avg_volume = sum(vols) / len(vols)
    return (
        f"📊 Average Volume Summary for {symbol.upper()}:\n"
        f"- **Average Volume**: {avg_volume:,.2f} USD over the last {len(vols)} {interval} periods.\n"
        f"- **Highest Volume**: {max(vols):,.2f} USD\n"
        f"- **Lowest Volume**: {min(vols):,.2f} USD\n"
        f"- **Trend**: {'increasing' if vols[-1] > vols[0] else 'decreasing' if vols[-1] < vols[0] else 'stable'}"
    )


@tool(args_schema=CryptoVolumeHistoryInput, return_direct=True)
def detect_volume_spikes(symbol: str, interval: str, amount: int):
    """Detect significant spikes or drops in trading volume."""
    data = get_volume_history(symbol.upper(), "USD", interval, amount)
    history = data.get("history", [])
    if not history:
        return f"No volume data available for {symbol.upper()}."

    vols = [v["volume"] for v in history]
    first = vols[0]
    last = vols[-1]
    spike_threshold = 0.2  # 20% change considered significant
    change_pct = (last - first) / first if first != 0 else 0

    if abs(change_pct) > spike_threshold:
        trend = "spike" if change_pct > 0 else "drop"
        message = f"⚡ Significant volume {trend} detected for {symbol.upper()}! Change: {change_pct*100:.2f}%"
    else:
        message = f"No major volume spikes detected for {symbol.upper()}. Change: {change_pct*100:.2f}%"

    return message



class CompareAverageVolumesInput(BaseModel):
    symbols: list[str]
    interval: str = "days"
    amount: int = 7

@tool(args_schema=CompareAverageVolumesInput, return_direct=True)
def compare_average_volumes(symbols: list[str], interval: str = "days", amount: int = 7):
    """Compare average trading volumes for multiple coins."""
    summaries = []
    for sym in symbols:
        data = get_volume_history(sym.upper(), "USD", interval, amount)
        history = data.get("history", [])
        if not history:
            summaries.append(f"{sym.upper()}: no data")
            continue
        vols = [v["volume"] for v in history]
        avg = sum(vols) / len(vols)
        summaries.append(f"{sym.upper()}: Average Volume = {avg:,.2f} USD")
    return "Average Volumes:\n" + "\n".join(summaries)