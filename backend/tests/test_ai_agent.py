import pytest
from dotenv import load_dotenv

from ai.agents.CryptoAgent import run_agent

load_dotenv()

def run_and_print(query: str):
    print("\n" + "=" * 80)
    print(f"PROMPT:\n{query}")
    print("-" * 80)

    try:
        response = run_agent(query)
        print("AGENT RESPONSE:\n")
        print(response)
    except Exception as e:
        print("ERROR:")
        print(e)

    print("=" * 80 + "\n")


# -----------------------------
# BASIC PRICE / CONTEXT TESTS
# -----------------------------

def test_price_only():
    run_and_print("What is the current price of Bitcoin?")


def test_price_with_context():
    run_and_print("Give me the current BTC price and short market context")


# -----------------------------
# PRICE ACTION / PATTERNS
# -----------------------------

def test_price_action_general():
    run_and_print(
        "What price action pattern is currently forming in the BTC market?"
    )


def test_price_action_explicit_patterns():
    run_and_print(
        "Analyze BTC using price action. "
        "Look for breakouts, pullbacks, double tops/bottoms, and trendlines."
    )


def test_bullish_or_bearish_bias():
    run_and_print(
        "Is BTC currently more bullish or bearish based on price action?"
    )


# -----------------------------
# TECHNICAL ANALYSIS HEAVY
# -----------------------------

def test_full_technical_analysis():
    run_and_print(
        "Do a full technical analysis on BTC including trend, "
        "price action patterns, and volume confirmation."
    )


def test_volume_focus():
    run_and_print(
        "Analyze BTC volume behavior and explain what it confirms "
        "about the current trend."
    )


# -----------------------------
# STRATEGY / TRADING STYLE PROMPTS
# -----------------------------

def test_scalping_prompt():
    run_and_print(
        "If I were scalping BTC, what price action signals should I be aware of right now?"
    )


def test_swing_trading_prompt():
    run_and_print(
        "For swing trading BTC, what patterns and key levels matter most currently?"
    )


def test_breakout_trader_prompt():
    run_and_print(
        "Is BTC setting up for a breakout or fakeout? "
        "Explain using price action."
    )


# -----------------------------
# RISK & DECISION SUPPORT
# -----------------------------

def test_trade_decision_support():
    run_and_print(
        "Based on current BTC price action, would you be cautious, aggressive, "
        "or stay out of the market? Explain why."
    )


def test_confirmation_prompt():
    run_and_print(
        "What confirmation signals would you wait for before entering a BTC trade?"
    )


# -----------------------------
# EDGE / FUZZY PROMPTS
# -----------------------------

def test_vague_prompt():
    run_and_print("What’s going on with Bitcoin?")


def test_overloaded_prompt():
    run_and_print(
        "Check BTC price, analyze volume, detect price action patterns, "
        "and summarize the market in simple terms."
    )