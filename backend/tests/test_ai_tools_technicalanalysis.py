# tests/test_ai_tools_technicalanalysis.py

import pytest
from ai.tools.technical_analysis import *

# -------------------------
# Test Data
# -------------------------

TEST_SYMBOLS = ["BTC", "ETH"]
TEST_SYMBOL = "BTC"
TEST_INTERVAL = "days"
TEST_AMOUNT = 3
TEST_THRESHOLD = 0.0  # Percentage threshold for alerts
TEST_SHORT_TERM = 12
TEST_LONG_TERM = 26
TEST_SIGNAL = 9
TEST_PERIOD = 20
TEST_STD_DEV = 2.0

# -------------------------
# Existing Tests
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




# New Technical Indicators Tests (updated for formatted string output)

def test_rsi_tool():
    """Test RSI tool returns a formatted string with the symbol and RSI value."""
    result = get_rsi.func(TEST_SYMBOL, TEST_INTERVAL, TEST_AMOUNT)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "RSI" in result

def test_macd_tool():
    """Test MACD tool returns a formatted string including MACD, signal, and histogram."""
    result = get_macd.func(TEST_SYMBOL, TEST_SHORT_TERM, TEST_LONG_TERM, TEST_SIGNAL, TEST_INTERVAL)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "MACD Line" in result and "Signal Line" in result and "Histogram" in result

def test_bollinger_bands_tool():
    """Test Bollinger Bands tool returns a formatted string with middle, upper, and lower bands."""
    result = get_bollinger_bands.func(TEST_SYMBOL, TEST_PERIOD, TEST_INTERVAL, TEST_STD_DEV)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "Middle Band" in result and "Upper Band" in result and "Lower Band" in result

def test_price_trend_tool():
    """Test price trend tool returns a formatted string describing the trend."""
    result = get_price_trend.func(TEST_SYMBOL, TEST_INTERVAL, TEST_AMOUNT)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    # Ensure it mentions one of the trend types
    assert any(trend in result.lower() for trend in ["upward", "downward", "stable"])

def test_ema_tool():
    """Test EMA tool returns a formatted string including the symbol, period, and EMA value."""
    result = get_ema.func(TEST_SYMBOL, TEST_AMOUNT, TEST_INTERVAL)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "EMA" in result