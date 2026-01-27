from ai.agents.CryptoChat import run_agent
from dotenv import load_dotenv
load_dotenv()

def test_run_agent_basic_query():
    result = run_agent("What's the current price of BTC?")
    assert "BTC" in result["result"] or "Bitcoin" in result["result"]

def test_run_agent_signals_query():
    result = run_agent("Show me BTC signals for the past 3 days")
    assert "trend" in result["result"] or "price_change" in result["result"]