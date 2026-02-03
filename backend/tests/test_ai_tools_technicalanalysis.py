# tests/test_ai_tools_technicalanalysis.py

import pytest
from ai.tools.technical_analysis import (
    get_market_summary,
    detect_top_movers,
    correlate_price_volume,
    detect_percentage_change,
    get_volatility,
    get_moving_average,
    get_historical_performance,
    compare_coins,
    compare_crypto_volumes,
    get_crypto_average_volume,
    compare_average_volumes
)

# -------------------------
# Test Data
# -------------------------

TEST_SYMBOLS = ["BTC", "ETH"]
TEST_SYMBOL = "BTC"
TEST_INTERVAL = "days"
TEST_AMOUNT = 3
TEST_THRESHOLD = 0.0  # Percentage threshold for alerts

# -------------------------
# Tests
# -------------------------

def test_get_market_summary():
    """Test market summary tool returns formatted string with all symbols."""
    result = get_market_summary.func(TEST_SYMBOLS, interval=TEST_INTERVAL, amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert "Market Summary" in result
    for sym in TEST_SYMBOLS:
        assert sym in result

def test_detect_top_movers():
    """Test top movers tool returns formatted string with symbols and percentage changes."""
    result = detect_top_movers.func(TEST_SYMBOLS, interval=TEST_INTERVAL, amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert "Top Movers" in result
    for sym in TEST_SYMBOLS:
        assert sym in result

def test_correlate_price_volume():
    """Test price-volume correlation tool returns a descriptive string."""
    result = correlate_price_volume.func(TEST_SYMBOL, interval=TEST_INTERVAL, amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "correlation" in result.lower()

def test_detect_percentage_change():
    """Test percentage change detection tool returns alert or no-alert message."""
    result = detect_percentage_change.func(
        TEST_SYMBOLS, threshold=TEST_THRESHOLD, interval=TEST_INTERVAL, amount=TEST_AMOUNT
    )
    assert isinstance(result, str)
    assert "Percentage Change Alerts" in result or "No coins exceeded" in result
    for sym in TEST_SYMBOLS:
        if "Percentage Change Alerts" in result:
            assert sym in result

def test_get_volatility():
    """Test volatility overview tool returns a summary string with net change and trend."""
    result = get_volatility.func(TEST_SYMBOL, interval=TEST_INTERVAL, amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "High" in result and "Low" in result and "Trend" in result

def test_get_moving_average():
    """Test moving averages tool returns short-term and mid-term averages."""
    result = get_moving_average.func(TEST_SYMBOL, short_term=2, mid_term=3, interval=TEST_INTERVAL)
    assert isinstance(result, str)
    assert "Short Term" in result and "Mid Term" in result
    assert TEST_SYMBOL in result

def test_get_historical_performance():
    """Test historical performance tool returns trend summary for given intervals."""
    result = get_historical_performance.func(TEST_SYMBOL, intervals=["days"], amounts=[TEST_AMOUNT])
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "trend" in result.lower()

def test_compare_coins():
    """Test coin comparison tool returns formatted report string with all symbols."""
    result = compare_coins.func(TEST_SYMBOLS, interval=TEST_INTERVAL, amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert "Coin Comparison Report" in result
    for sym in TEST_SYMBOLS:
        assert sym in result

def test_compare_crypto_volumes():
    """Test volume comparison tool returns dictionary with history and summary per symbol."""
    result = compare_crypto_volumes.func(TEST_SYMBOLS, interval=TEST_INTERVAL, amount=TEST_AMOUNT)
    assert isinstance(result, dict)
    for sym in TEST_SYMBOLS:
        assert sym in result
        assert isinstance(result[sym], dict)
        assert "history" in result[sym]
        assert "summary" in result[sym]
        assert isinstance(result[sym]["history"], list)
        assert isinstance(result[sym]["summary"], str)

def test_get_crypto_average_volume():
    """Test average volume tool returns string with average and trend."""
    result = get_crypto_average_volume.func(TEST_SYMBOL, interval=TEST_INTERVAL, amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "Avg Volume" in result and "Trend" in result

def test_compare_average_volumes():
    """Test average volumes comparison tool returns summary string for multiple symbols."""
    result = compare_average_volumes.func(TEST_SYMBOLS, interval=TEST_INTERVAL, amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert "Average Volumes" in result
    for sym in TEST_SYMBOLS:
        assert sym in result