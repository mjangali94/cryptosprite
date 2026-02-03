# tests/test_ai_tools_price.py
import pytest
from ai.tools.price import get_crypto_price, get_crypto_history, resolve_asset


# -------------------------
# resolve_asset tests
# -------------------------
def test_resolve_asset_success():
    """Test resolving a known asset returns correct dict structure."""
    result = resolve_asset.invoke({"query": "bitcoin"})
    assert isinstance(result, dict)
    assert "id" in result
    assert "symbol" in result
    assert "name" in result
    assert result["symbol"].upper() == "BTC"


def test_resolve_asset_failure():
    """Test resolving an unknown asset returns a fallback or error dict."""
    result = resolve_asset.invoke({"query": "fakecoin"})
    assert isinstance(result, dict)
    # Depending on implementation, it may return a fallback asset or error
    assert "symbol" in result or "error" in result


def test_resolve_asset_empty_query():
    """Test resolving with empty string returns error dict."""
    result = resolve_asset.invoke({"query": ""})
    assert isinstance(result, dict)
    assert "error" in result
    assert "query" in result["error"].lower()


# -------------------------
# get_crypto_price tests
# -------------------------
def test_get_crypto_price_success():
    """Test successful price fetch returns correct keys and types."""
    result = get_crypto_price.invoke({"symbol": "BTC", "currency": "USD"})
    assert isinstance(result, dict)
    assert result["symbol"].upper() == "BTC"
    assert result["currency"].upper() == "USD"
    assert isinstance(result["price"], (float, int))


def test_get_crypto_price_missing_symbol():
    """Test behavior when symbol is missing returns error dict."""
    result = get_crypto_price.invoke({"symbol": "", "currency": "USD"})
    assert isinstance(result, dict)
    assert "error" in result
    assert "symbol" in result["error"].lower()


def test_get_crypto_price_invalid_currency_schema():
    """Test invalid currency (not allowed by schema) raises exception."""
    with pytest.raises(Exception):
        get_crypto_price.invoke({"symbol": "BTC", "currency": "XYZ"})


# -------------------------
# get_crypto_history tests
# -------------------------
def test_get_crypto_history_success():
    """Test successful historical data fetch returns dict with history."""
    result = get_crypto_history.invoke({"symbol": "BTC", "interval": "days", "amount": 2})
    assert isinstance(result, dict)
    assert "history" in result
    assert isinstance(result["history"], list)
    assert len(result["history"]) == 2
    assert all("open" in candle for candle in result["history"])


def test_get_crypto_history_invalid_symbol():
    """Test behavior when an invalid symbol is passed returns error dict."""
    result = get_crypto_history.invoke({"symbol": "FAKECOIN", "interval": "days", "amount": 2})
    assert isinstance(result, dict)
    assert "error" in result
    assert "failed" in result["error"].lower()


def test_get_crypto_history_invalid_interval_schema():
    """Test invalid interval (not allowed by schema) raises exception."""
    with pytest.raises(Exception):
        get_crypto_history.invoke({"symbol": "BTC", "interval": "years", "amount": 2})


def test_get_crypto_history_min_amount():
    """Test minimum valid amount (1) returns correct number of points."""
    result = get_crypto_history.invoke({"symbol": "BTC", "interval": "days", "amount": 1})
    assert isinstance(result, dict)
    assert "history" in result
    assert len(result["history"]) == 1