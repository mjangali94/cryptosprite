# tests/test_ai_tools_volume.py
import pytest
from ai.tools.volume import get_crypto_volume, get_crypto_volume_history


# -------------------------
# get_crypto_volume tests
# -------------------------
def test_get_crypto_volume_real():
    """Test real current volume fetch for BTC."""
    result = get_crypto_volume.invoke({"symbol": "BTC", "currency": "USD"})
    assert isinstance(result, str)
    assert "BTC" in result
    assert "Volume" in result
    assert "Current Price" in result


def test_get_crypto_volume_invalid_symbol_real():
    """Test behavior for invalid symbol."""
    result = get_crypto_volume.invoke({"symbol": "FAKECOIN", "currency": "USD"})
    assert isinstance(result, str)
    assert "failed" in result.lower() or "error" in result.lower()


# -------------------------
# get_crypto_volume_history tests
# -------------------------
def test_get_crypto_volume_history_real():
    """Test real historical volume fetch for BTC."""
    result = get_crypto_volume_history.invoke({"symbol": "BTC", "interval": "days", "amount": 3})
    assert isinstance(result, str)
    assert "BTC" in result
    assert len(result) > 0


def test_get_crypto_volume_history_invalid_symbol():
    """Test historical volume fetch with invalid symbol."""
    result = get_crypto_volume_history.invoke({"symbol": "FAKECOIN", "interval": "days", "amount": 3})
    assert isinstance(result, str)
    assert "failed" in result.lower() or "error" in result.lower()


def test_get_crypto_volume_history_min_amount():
    """Test historical volume fetch with minimum valid amount (1)."""
    result = get_crypto_volume_history.invoke({"symbol": "BTC", "interval": "days", "amount": 1})
    assert isinstance(result, str)
    assert "BTC" in result