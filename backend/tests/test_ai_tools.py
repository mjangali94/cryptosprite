import time
import pytest
from ai.tools.CryptoPrice import get_crypto_price, get_crypto_history, get_crypto_signals, resolve_asset

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