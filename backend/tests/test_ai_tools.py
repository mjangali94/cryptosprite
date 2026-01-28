import time
import pytest
from ai.tools.CryptoPrice import get_crypto_price, get_crypto_history, get_crypto_signals, resolve_asset, get_crypto_trends_tool

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

def test_get_crypto_signals():
    result = get_crypto_signals.invoke({"interval": "days", "symbol": "BTC", "amount": 3})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, dict)
    assert result.get("symbol") == "BTC"

def test_resolve_asset():
    result = resolve_asset.invoke({"query": "Bitcoin"})
    assert result is not None
    assert isinstance(result, dict)
    assert result.get("symbol") == "BTC"



def test_get_crypto_trends_tool():
    """Test fetching short, mid, long-term trends for BTC."""
    result = get_crypto_trends_tool.invoke({"symbol": "BTC"})

    # Tool should return a non-empty string
    assert result is not None
    assert isinstance(result, str)
    assert "Trends for BTC:" in result

    # Check that all three terms appear in output
    assert "Short Term" in result or "Short_Term" in result
    assert "Mid Term" in result or "Mid_Term" in result
    assert "Long Term" in result or "Long_Term" in result

    # Optional: print for debugging
    print("\n--- BTC Trends Output ---")
    print(result)
