# tests/test_ai_tools_technicalanalysis.py
import pytest
from ai.tools.technical_analysis import *

# -------------------------
# Test Parameters
# -------------------------

TEST_SYMBOLS = ["BTC", "ETH"]
TEST_SYMBOL = "BTC"
TEST_INTERVALS = ["hours", "days", "months"]
TEST_AMOUNT = 5
TEST_THRESHOLD = 0.0
TEST_SHORT_TERM = 3
TEST_MID_TERM = 5
TEST_LONG_TERM = 5
TEST_SIGNAL = 2
TEST_PERIOD = 5
TEST_STD_DEV = 2.0

# -------------------------
# Market / Trend Tools
# -------------------------

def test_get_market_summary():
    result = get_market_summary.func(TEST_SYMBOLS, interval="days", amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert "Market Summary" in result
    for sym in TEST_SYMBOLS:
        assert sym in result
        assert "Trend" in result
        assert "Avg Volume" in result
        assert "Latest Price" in result


def test_detect_top_movers():
    result = detect_top_movers.func(TEST_SYMBOLS, interval="days", amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert "Top Movers" in result
    for sym in TEST_SYMBOLS:
        assert sym in result
        assert "%" in result


def test_correlate_price_volume():
    result = correlate_price_volume.func(TEST_SYMBOL, interval="days", amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "correlation" in result.lower()
    assert any(x in result for x in ["positive", "negative"])


def test_get_price_trend():
    result = get_price_trend.func(TEST_SYMBOL, interval="days", amount=TEST_AMOUNT)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert any(trend in result.lower() for trend in ["upward", "downward", "stable"])


# -------------------------
# RSI / EMA / MACD / Bollinger
# -------------------------

def test_get_rsi():
    result = get_rsi.func(TEST_SYMBOL, interval="days", amount=14)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "RSI" in result


def test_get_ema():
    result = get_ema.func(TEST_SYMBOL, period=TEST_AMOUNT, interval="days")
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "EMA" in result


def test_get_macd():
    result = get_macd.func(TEST_SYMBOL, short_term=TEST_SHORT_TERM, long_term=TEST_LONG_TERM, signal=TEST_SIGNAL, interval="days")
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "MACD Line" in result
    assert "Signal Line" in result
    assert "Histogram" in result


def test_get_bollinger_bands():
    result = get_bollinger_bands.func(TEST_SYMBOL, period=TEST_PERIOD, interval="days", std_dev_multiplier=TEST_STD_DEV)
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "Middle Band" in result
    assert "Upper Band" in result
    assert "Lower Band" in result


# -------------------------
# Edge Cases
# -------------------------

def test_empty_symbol_list_market_summary():
    result = get_market_summary.func([], interval="days", amount=TEST_AMOUNT)
    assert "Market Summary" in result
    assert result.strip() == "Market Summary:"

def test_invalid_amount_top_movers():
    result = detect_top_movers.func(TEST_SYMBOLS, interval="days", amount=0)
    assert isinstance(result, str)
    assert "Top Movers" in result  # should gracefully return empty list

def test_negative_periods_rsi():
    result = get_rsi.func(TEST_SYMBOL, interval="days", amount=-5)
    assert isinstance(result, str)
    assert "Insufficient data" in result or "RSI" in result

def test_large_periods_ema():
    result = get_ema.func(TEST_SYMBOL, period=1000, interval="days")
    assert isinstance(result, str)
    assert TEST_SYMBOL in result
    assert "EMA" in result

def test_macd_short_greater_long():
    # MACD with invalid parameters (short >= long)
    result = get_macd.func(TEST_SYMBOL, short_term=10, long_term=5, signal=3, interval="days")
    assert "Insufficient data" in result or TEST_SYMBOL in result

