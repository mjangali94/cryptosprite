# tests/test_crypto_volume_tools.py

import time
import pytest
from ai.tools.volume import (
    get_crypto_volume,
    get_crypto_volume_history,
    compare_crypto_volumes,
    get_crypto_average_volume,
    detect_volume_spikes,
    compare_average_volumes,
)

# -------------------------
# Test current 24h volume
# -------------------------
def test_get_crypto_volume():
    result = get_crypto_volume.invoke({"symbol": "BTC", "currency": "USD"})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, str)
    assert "BTC" in result
    assert "Volume" in result

# -------------------------
# Test historical volume (updated for string output)
# -------------------------
def test_get_crypto_volume_history():
    result = get_crypto_volume_history.invoke({"symbol": "BTC", "interval": "days", "amount": 3})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, str)  # now we expect a string
    assert "BTC" in result
    assert "Trend" in result
    assert "Highest Volume" in result
    assert "Lowest Volume" in result
    assert "Data Points" in result
    print("\n--- get_crypto_volume_history ---")
    print(result)

# -------------------------
# Test compare multiple coins volume
# -------------------------
def test_compare_crypto_volumes():
    result = compare_crypto_volumes.invoke({"symbols": ["BTC", "ETH"], "interval": "days", "amount": 3})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, str)
    assert "BTC" in result and "ETH" in result
    print("\n--- compare_crypto_volumes ---")
    print(result)

# -------------------------
# Test average volume
# -------------------------
def test_get_crypto_average_volume():
    result = get_crypto_average_volume.invoke({"symbol": "BTC", "interval": "days", "amount": 3})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, str)
    assert "Average Volume" in result
    print("\n--- get_crypto_average_volume ---")
    print(result)

# -------------------------
# Test volume spike detection
# -------------------------
def test_detect_volume_spikes():
    result = detect_volume_spikes.invoke({"symbol": "BTC", "interval": "days", "amount": 3})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, str)
    assert "volume" in result.lower()
    print("\n--- detect_volume_spikes ---")
    print(result)

# -------------------------
# Test average volume comparison for multiple coins
# -------------------------
def test_compare_average_volumes():
    result = compare_average_volumes.invoke({"symbols": ["BTC", "ETH"], "interval": "days", "amount": 3})
    time.sleep(1)
    assert result is not None
    assert isinstance(result, str)
    assert "BTC" in result and "ETH" in result
    assert "Average Volume" in result
    print("\n--- compare_average_volumes ---")
    print(result)