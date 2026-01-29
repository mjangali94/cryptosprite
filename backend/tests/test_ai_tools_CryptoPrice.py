import time
import pytest
from ai.tools.CryptoPrice import (
    get_crypto_price,
    get_crypto_history,
    get_crypto_signals,
    resolve_asset,
    get_crypto_trends_tool,
)

# -----------------------------
# Basic single-coin tests
# -----------------------------
def test_get_crypto_price():
    result = get_crypto_price.invoke({"symbol": "BTC", "currency": "USD"})
    time.sleep(1)  # prevent hitting rate limit
    assert result is not None
    assert isinstance(result, str)
    assert "BTC" in result

def test_get_crypto_history():
    result = get_crypto_history.invoke({"interval": "days", "symbol": "BTC", "amount": 3})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, dict)
    assert result.get("symbol") == "BTC"
    assert "history" in result

def test_get_crypto_signals():
    result = get_crypto_signals.invoke({"interval": "days", "symbol": "BTC", "amount": 3})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, dict)
    assert result.get("symbol") == "BTC"
    assert "trend" in result

def test_resolve_asset():
    result = resolve_asset.invoke({"query": "Bitcoin"})
    assert result is not None
    assert isinstance(result, dict)
    assert result.get("symbol") == "BTC"

def test_get_crypto_trends_tool():
    """Test fetching short, mid, long-term trends for BTC."""
    result = get_crypto_trends_tool.invoke({"symbol": "BTC"})
    time.sleep(1)

    assert result is not None
    assert isinstance(result, str)
    assert "Trends for BTC:" in result
    assert "Short Term" in result or "Short_Term" in result
    assert "Mid Term" in result or "Mid_Term" in result
    assert "Long Term" in result or "Long_Term" in result

    print("\n--- BTC Trends Output ---")
    print(result)

# -----------------------------
# Multi-coin dynamic tests
# -----------------------------
@pytest.mark.parametrize("coins", [
    ["BTC", "ETH", "SOL"],
    ["BTC", "ETH", "SOL", "ADA", "DOGE"],
])
def test_multi_coin_trends(coins):
    """Test that the trends tool works for multiple coins dynamically."""
    summaries = []

    for coin in coins:
        summary = get_crypto_trends_tool.invoke({"symbol": coin})
        time.sleep(1)  # avoid API rate limit
        summaries.append(summary)

        assert summary is not None
        assert isinstance(summary, str)
        assert f"Trends for {coin}:" in summary
        assert "Short Term" in summary or "Short_Term" in summary
        assert "Mid Term" in summary or "Mid_Term" in summary
        assert "Long Term" in summary or "Long_Term" in summary

    # Optional: print all summaries
    print("\n--- Multi-Coin Trends Output ---")
    for s in summaries:
        print(s)

# -----------------------------
# N-coin summary generation test
# -----------------------------
def test_dynamic_n_coin_summary():
    """Simulate generating a full summary for N coins."""
    coins = ["BTC", "ETH", "SOL"]
    full_summary = []

    for coin in coins:
        # Get current price
        price_str = get_crypto_price.invoke({"symbol": coin})
        time.sleep(1)
        assert coin in price_str

        # Get trends
        trends = get_crypto_trends_tool.invoke({"symbol": coin})
        time.sleep(1)
        full_summary.append(f"{price_str}\n{trends}")

    summary_text = "\n\n".join(full_summary)
    assert len(summary_text) > 0
    assert "BTC" in summary_text
    assert "ETH" in summary_text
    assert "SOL" in summary_text

    print("\n--- Full N-Coin Summary ---")
    print(summary_text)