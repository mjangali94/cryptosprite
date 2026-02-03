# tests/test_trading_strategies_complete.py
import pytest
from unittest.mock import patch
import backend.ai.tools.price_action as tools

# -----------------------------
# Helper to create mock OHLCV data
# -----------------------------
def mock_history(open_prices=None, high_prices=None, low_prices=None, close_prices=None, volume=None):
    n = len(close_prices or high_prices or low_prices or open_prices)
    open_prices = open_prices or [c for c in (close_prices or [10]*n)]
    high_prices = high_prices or open_prices
    low_prices = low_prices or open_prices
    close_prices = close_prices or open_prices
    volume = volume or [100]*n
    return [{"open": o, "high": h, "low": l, "close": c, "volume": v}
            for o, h, l, c, v in zip(open_prices, high_prices, low_prices, close_prices, volume)]

# -----------------------------
# Generic test function for bullish, bearish, neutral
# -----------------------------
def run_strategy(strategy_func, bullish_hist, bearish_hist, neutral_hist):
    """
    Patch _get_history and run strategy for bullish, bearish, and neutral mock data.

    Works with LangChain @tool (StructuredTool) objects by calling .func
    """
    for scenario, history in zip(["bullish", "bearish", "neutral"], [bullish_hist, bearish_hist, neutral_hist]):
        with patch("backend.ai.tools.price_action._get_history", return_value=history):
            # Call the original function inside StructuredTool
            result = strategy_func.func("BTC")
            print(f"{strategy_func.name} {scenario}: {result}")
            assert isinstance(result, str)
            assert result != ""

# -----------------------------
# Individual strategy tests
# -----------------------------
def test_breakout_strategy():
    bullish = mock_history(close_prices=[10,11,12,13,14,15])
    bearish = mock_history(close_prices=[15,14,13,12,11,10])
    neutral = mock_history(close_prices=[10,10,10,10,10,10])
    run_strategy(tools.breakout_strategy, bullish, bearish, neutral)

def test_pullback_strategy():
    bullish = mock_history(close_prices=[12,13])
    bearish = mock_history(close_prices=[13,12])
    neutral = mock_history(close_prices=[12,12])
    run_strategy(tools.pullback_strategy, bullish, bearish, neutral)

def test_trendline_strategy():
    bullish = mock_history(close_prices=[10,11,12,13,14])
    bearish = mock_history(close_prices=[14,13,12,11,10])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.trendline_strategy, bullish, bearish, neutral)

def test_channel_strategy():
    bullish = mock_history(close_prices=[10,10,10,10,9], low_prices=[9,9,9,9,8], high_prices=[11,11,11,11,10])
    bearish = mock_history(close_prices=[12,12,12,12,13], low_prices=[11,11,11,11,12], high_prices=[13,13,13,13,14])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.channel_strategy, bullish, bearish, neutral)

def test_double_top_bottom_strategy():
    bullish = mock_history(close_prices=[10,9,11])
    bearish = mock_history(close_prices=[11,12,10])
    neutral = mock_history(close_prices=[10,10,10])
    run_strategy(tools.double_top_bottom_strategy, bullish, bearish, neutral)

def test_head_shoulders_strategy():
    bullish = mock_history(close_prices=[14,12,15,13,16])
    bearish = mock_history(close_prices=[12,14,11,13,10])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.head_shoulders_strategy, bullish, bearish, neutral)

def test_pin_bar_strategy():
    bullish = mock_history(open_prices=[10,9], close_prices=[10.5,10], high_prices=[11,10.5], low_prices=[9,9.5])
    bearish = mock_history(open_prices=[10,11], close_prices=[9.5,10], high_prices=[11,11.5], low_prices=[9,10])
    neutral = mock_history(open_prices=[10,10], close_prices=[10,10], high_prices=[10,10], low_prices=[10,10])
    run_strategy(tools.pin_bar_strategy, bullish, bearish, neutral)

def test_flag_pennant_strategy():
    bullish = mock_history(close_prices=[10,10.01,10.005])
    bearish = mock_history(close_prices=[10,10.01,10.005])
    neutral = mock_history(close_prices=[10,10,10])
    run_strategy(tools.flag_pennant_strategy, bullish, bearish, neutral)

def test_bounce_strategy():
    bullish = mock_history(close_prices=[9,10,10,10,9])
    bearish = mock_history(close_prices=[12,12,12,12,13])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.bounce_strategy, bullish, bearish, neutral)

def test_doji_strategy():
    bullish = mock_history(open_prices=[10,10], close_prices=[10,10], high_prices=[10.1,10.1], low_prices=[9.9,9.9])
    bearish = mock_history(open_prices=[10,10], close_prices=[10,10], high_prices=[10.1,10.1], low_prices=[9.9,9.9])
    neutral = mock_history(open_prices=[10,10], close_prices=[10,10], high_prices=[10.1,10.1], low_prices=[9.9,9.9])
    run_strategy(tools.doji_strategy, bullish, bearish, neutral)

def test_three_soldiers_crows_strategy():
    bullish = mock_history(open_prices=[10,11,12], close_prices=[11,12,13])
    bearish = mock_history(open_prices=[13,12,11], close_prices=[12,11,10])
    neutral = mock_history(open_prices=[10,10,10], close_prices=[10,10,10])
    run_strategy(tools.three_soldiers_crows_strategy, bullish, bearish, neutral)

def test_morning_evening_star_strategy():
    bullish = mock_history(open_prices=[12,10,11], close_prices=[10,10.2,12])
    bearish = mock_history(open_prices=[10,12,11], close_prices=[12,11.8,10])
    neutral = mock_history(open_prices=[10,10,10], close_prices=[10,10,10])
    run_strategy(tools.morning_evening_star_strategy, bullish, bearish, neutral)

def test_tweezers_strategy():
    bullish = mock_history(low_prices=[10,10.01], close_prices=[10,10.02])
    bearish = mock_history(high_prices=[12,12.01], close_prices=[12,11.9])
    neutral = mock_history(high_prices=[10,10], low_prices=[10,10], close_prices=[10,10])
    run_strategy(tools.tweezers_strategy, bullish, bearish, neutral)

def test_marubozu_strategy():
    bullish = mock_history(open_prices=[10], close_prices=[12], high_prices=[12], low_prices=[10])
    bearish = mock_history(open_prices=[12], close_prices=[10], high_prices=[12], low_prices=[10])
    neutral = mock_history(open_prices=[10], close_prices=[10], high_prices=[10], low_prices=[10])
    run_strategy(tools.marubozu_strategy, bullish, bearish, neutral)

def test_false_breakout_strategy():
    bullish = mock_history(close_prices=[10,10,12,12,13])
    bearish = mock_history(close_prices=[12,12,10,10,9])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.false_breakout_strategy, bullish, bearish, neutral)

def test_momentum_push_strategy():
    bullish = mock_history(close_prices=[10,10,10,10,11])
    bearish = mock_history(close_prices=[10,10,10,10,9])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.momentum_push_strategy, bullish, bearish, neutral)

def test_swing_high_low_strategy():
    bullish = mock_history(close_prices=[9,10,11,12,13])
    bearish = mock_history(close_prices=[13,12,11,10,9])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.swing_high_low_strategy, bullish, bearish, neutral)

def test_order_block_strategy():
    bullish = mock_history(close_prices=[9,10,11,12,13])
    bearish = mock_history(close_prices=[13,12,11,10,9])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.order_block_strategy, bullish, bearish, neutral)

def test_market_structure_shift_strategy():
    bullish = mock_history(close_prices=[10,11,12,13,14])
    bearish = mock_history(close_prices=[14,13,12,11,10])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.market_structure_shift_strategy, bullish, bearish, neutral)

def test_liquidity_grab_strategy():
    bullish = mock_history(close_prices=[10,10,10,10,12])
    bearish = mock_history(close_prices=[12,12,12,12,10])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.liquidity_grab_strategy, bullish, bearish, neutral)

def test_wyckoff_strategy():
    bullish = mock_history(close_prices=[10,10.01,10.02,10.03,10.04,10.05])
    bearish = mock_history(close_prices=[10.05,10.04,10.03,10.02,10.01,10])
    neutral = mock_history(close_prices=[10,10,10,10,10,10])
    run_strategy(tools.wyckoff_strategy, bullish, bearish, neutral)

def test_break_retest_strategy():
    bullish = mock_history(close_prices=[10,11,12,13,14])
    bearish = mock_history(close_prices=[14,13,12,11,10])
    neutral = mock_history(close_prices=[10,10,10,10,10])
    run_strategy(tools.break_retest_strategy, bullish, bearish, neutral)

def test_psychological_level_strategy():
    bullish = mock_history(close_prices=[99,100,101,102,100])
    bearish = mock_history(close_prices=[199,198,197,200,200])
    neutral = mock_history(close_prices=[105,106,107,108,109])
    run_strategy(tools.psychological_level_strategy, bullish, bearish, neutral)

def test_triangle_strategy():
    bullish = mock_history(high_prices=[1,2,3,4,5], low_prices=[1,2,3,4,5])
    bearish = mock_history(high_prices=[5,4,3,2,1], low_prices=[5,4,3,2,1])
    neutral = mock_history(high_prices=[10,10,10,10,10], low_prices=[9,9,9,9,9])
    run_strategy(tools.triangle_strategy, bullish, bearish, neutral)

def test_rectangle_strategy():
    bullish = mock_history(high_prices=[10,10.01,10.02,10.03,10.04], low_prices=[9,9.01,9.02,9.03,9.04])
    bearish = mock_history(high_prices=[15,15.01,15.02,15.03,15.04], low_prices=[14,14.01,14.02,14.03,14.04])
    neutral = mock_history(high_prices=[10,10,10,10,10], low_prices=[10,10,10,10,10])
    run_strategy(tools.rectangle_strategy, bullish, bearish, neutral)

def test_engulfing_strategy():
    bullish = mock_history(open_prices=[10,9], close_prices=[9,11])
    bearish = mock_history(open_prices=[11,12], close_prices=[12,10])
    neutral = mock_history(open_prices=[10,10], close_prices=[10,10])
    run_strategy(tools.engulfing_strategy, bullish, bearish, neutral)

def test_inside_bar_strategy():
    bullish = mock_history(open_prices=[10,10,10], high_prices=[10,11,12], low_prices=[9,9,9], close_prices=[10,10,12])
    bearish = mock_history(open_prices=[10,10,10], high_prices=[12,12,12], low_prices=[9,9,8], close_prices=[10,10,8])
    neutral = mock_history(open_prices=[10,10,10], high_prices=[10,10,10], low_prices=[9,9,9], close_prices=[10,10,10])
    run_strategy(tools.inside_bar_strategy, bullish, bearish, neutral)