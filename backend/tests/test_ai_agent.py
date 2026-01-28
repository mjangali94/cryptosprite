from ai.agents.CryptoChat import run_agent
from dotenv import load_dotenv

load_dotenv()

def test_agent_basic_price():
    """Test agent explaining current price of BTC in plain language."""
    query = "What's the current price of BTC?"
    result = run_agent(query)
    output = result["result"]

    assert output is not None
    # If output is dict, convert to string for testing
    if isinstance(output, dict):
        output = str(output)
    assert isinstance(output, str)
    assert "BTC" in output or "Bitcoin" in output
    assert any(word in output.lower() for word in ["current", "price", "usd"])


def test_agent_signals_and_trends():
    """Test agent explaining signals and trends for BTC."""
    query = "Show me BTC signals and trends for the last 7 days"
    result = run_agent(query)
    output = result["result"]

    assert output is not None
    if isinstance(output, dict):
        output = str(output)
    assert isinstance(output, str)
    assert "BTC" in output or "Bitcoin" in output

    # Check for trend keywords, allow both plain or numeric keywords
    assert any(trend in output.lower() for trend in ["upward", "downward", "sideways", "rising", "falling", "moving sideways"])

    # Check for mention of highs/lows
    assert any(word in output.lower() for word in ["high", "low", "points", "data points"])


def test_agent_unknown_symbol():
    """Test agent response for unknown or invalid crypto symbol."""
    query = "Show me signals for ABCD"

    try:
        # Run the agent
        result = run_agent(query)
        output = result["result"]
    except Exception as e:
        # Convert exceptions (like missing fields) to a string for testing
        output = str(e)

    assert output is not None
    if isinstance(output, dict):
        output = output.get("error", str(output))
    assert isinstance(output, str)

    # Check that output mentions it couldn't find the asset
    failure_phrases = [
        "could not resolve",
        "check the name",
        "no information",
        "unknown symbol",
        "not found",
        "sorry"
    ]
    assert any(phrase.lower() in output.lower() for phrase in failure_phrases)

def test_agent_multi_asset_query():
    """Test agent handling a query about multiple assets."""
    query = "Compare BTC and ETH signals and trends"
    result = run_agent(query)
    output = result["result"]

    assert output is not None
    if isinstance(output, dict):
        output = str(output)
    assert isinstance(output, str)
    assert "BTC" in output or "Bitcoin" in output
    assert "ETH" in output or "Ethereum" in output

    # Should include trends
    assert any(trend in output.lower() for trend in ["upward", "downward", "sideways", "rising", "falling", "moving sideways"])
    # Should include highs/lows
    assert any(word in output.lower() for word in ["high", "low"])

def test_agent_plain_language():
    """Test that agent explains trends in plain, non-technical language."""
    query = "Explain BTC trends in simple words"
    result = run_agent(query)
    output = result["result"]

    assert output is not None
    if isinstance(output, dict):
        output = str(output)
    assert isinstance(output, str)

    # Ensure no code-like or API jargon
    forbidden_words = ["api", "json", "endpoint", "curl"]
    for word in forbidden_words:
        assert word not in output.lower()

    # Only check that output mentions BTC or Bitcoin
    assert "btc" in output.lower() or "bitcoin" in output.lower()