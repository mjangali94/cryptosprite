import pytest
from ai.tools.technical_analysis import (
    get_market_summary,
    detect_top_movers,
    correlate_price_volume,
    detect_percentage_change,
    get_volatility,
    get_moving_average,
    get_historical_performance,
    compare_coins
)

@pytest.mark.parametrize("symbols", [["BTC"], ["ETH"]])
def test_get_market_summary(symbols):
    """Test fetching market summary for symbols."""
    result = get_market_summary.invoke({"symbols": symbols})  # plural
    assert result is not None

@pytest.mark.parametrize("symbols", [["BTC"], ["ETH"]])
def test_detect_top_movers(symbols):
    """Test detection of top movers for symbols."""
    result = detect_top_movers.invoke({"symbols": symbols})  # plural
    assert result is not None

@pytest.mark.parametrize("symbols", [["BTC"], ["ETH"]])
def test_correlate_price_volume(symbols):
    """Test correlation analysis between price and volume."""
    result = correlate_price_volume.invoke({
        "symbol": symbols[0],  # singular, correct here
        "interval": "days",
        "amount": 7
    })
    assert result is not None

@pytest.mark.parametrize("symbols", [["BTC"], ["ETH"]])
def test_detect_percentage_change(symbols):
    """Test detection of percentage change for symbols."""
    result = detect_percentage_change.invoke({
        "symbols": symbols,  # plural
        "interval": "days",
        "amount": 7
    })
    assert result is not None

@pytest.mark.parametrize("symbols", [["BTC"], ["ETH"]])
def test_get_volatility(symbols):
    """Test fetching volatility for a symbol."""
    result = get_volatility.invoke({
        "symbol": symbols[0],
        "interval": "days",
        "amount": 7
    })
    assert result is not None

@pytest.mark.parametrize("symbols", [["BTC"], ["ETH"]])
def test_get_moving_average(symbols):
    """Test fetching moving averages for a symbol."""
    result = get_moving_average.invoke({
        "symbol": symbols[0],
        "interval": "days",
        "amount": 7,
        "window": 3
    })
    assert result is not None

@pytest.mark.parametrize("symbols", [["BTC"], ["ETH"]])
def test_get_historical_performance(symbols):
    """Test historical performance summary for a symbol."""
    result = get_historical_performance.invoke({
        "symbol": symbols[0],
        "interval": "days",
        "amount": 7
    })
    assert result is not None

@pytest.mark.parametrize("symbols", [["BTC"], ["ETH"]])
def test_compare_coins(symbols):
    """Test comparison between coins."""
    result = compare_coins.invoke({"symbols": symbols})
    assert result is not None