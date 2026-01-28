from ai.agents.CryptoChat import run_agent
from dotenv import load_dotenv


load_dotenv()
def test_agent_basic_price():
    """Test agent explaining current price of BTC in plain language."""
    query = "What's the current price of BTC?"
    result = run_agent(query)
    output = result["result"]

    assert output is not None
    assert isinstance(output, str)
    assert "BTC" in output or "Bitcoin" in output
    assert any(word in output.lower() for word in ["current", "price", "usd"])


def test_agent_signals_and_trends():
    """Test agent explaining signals and trends for BTC."""
    query = "Show me BTC signals and trends for the last 7 days"
    result = run_agent(query)
    output = result["result"]

    # Must be string and non-empty
    assert output is not None
    assert isinstance(output, str)
    assert "BTC" in output or "Bitcoin" in output

    # Check for trend keywords
    assert any(trend in output.lower() for trend in ["upward", "downward", "sideways"])

    # Check for mention of highs/lows
    assert any(word in output.lower() for word in ["high", "low", "points", "data points"])


def test_agent_unknown_symbol():
    """Test agent response for unknown or invalid crypto symbol."""
    query = "Show me signals for ABCD"
    result = run_agent(query)
    output = result["result"]

    # Should gracefully handle unknown symbol
    assert output is not None
    assert isinstance(output, str)

    # Check that output mentions it couldn't find the asset
    failure_phrases = [
        "couldn't find any information",
        "check the spelling",
        "no information",
        "unknown symbol",
        "not found"
    ]
    assert any(phrase.lower() in output.lower() for phrase in failure_phrases)


def test_agent_multi_asset_query():
    """Test agent handling a query about multiple assets."""
    query = "Compare BTC and ETH signals and trends"
    result = run_agent(query)
    output = result["result"]

    # Must mention both BTC and ETH
    assert output is not None
    assert isinstance(output, str)
    assert "BTC" in output or "Bitcoin" in output
    assert "ETH" in output or "Ethereum" in output

    # Should include trends
    assert any(trend in output.lower() for trend in ["upward", "downward", "sideways"])
    # Should include highs/lows
    assert any(word in output.lower() for word in ["high", "low"])


def test_agent_plain_language():
    """Test that agent explains trends in plain, non-technical language."""
    query = "Explain BTC trends in simple words"
    result = run_agent(query)
    output = result["result"]

    assert output is not None
    assert isinstance(output, str)

    # Ensure no code-like or API jargon
    forbidden_words = ["api", "json", "endpoint", "curl"]
    for word in forbidden_words:
        assert word not in output.lower()

    # Should include plain phrases like rising, falling, sideways
    assert any(word in output.lower() for word in ["rising", "falling", "sideways", "upward", "downward"])