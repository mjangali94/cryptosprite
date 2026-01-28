import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from api.routes.price import router as price_router
from api.routes.history import router as history_router
from api.routes.signals import router as signals_router
from utils.crypto_assets import asset_symbols

# ----------------------------
# Test App Setup
# ----------------------------
app = FastAPI()
# Include all routes from your backend
app.include_router(price_router)
app.include_router(history_router)
app.include_router(signals_router)


# ----------------------------
# Crypto Price Tests
# ----------------------------
@pytest.mark.asyncio
async def test_crypto_price_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_price/BTC/USD")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert "price" in data
    assert data["currency"] == "USD"


@pytest.mark.asyncio
async def test_crypto_price_default_currency():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_price/BTC")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert "price" in data
    assert data["currency"] == "USD"


@pytest.mark.asyncio
async def test_crypto_price_invalid_symbol():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_price/INVALID/USD")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


# ----------------------------
# Crypto History Tests
# ----------------------------
@pytest.mark.asyncio
async def test_crypto_history_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_history/days/BTC/3")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert len(data["history"]) > 0
    for h in data["history"]:
        assert "timestamp" in h
        assert "price" in h
        assert "high" in h
        assert "low" in h


@pytest.mark.asyncio
async def test_crypto_history_invalid_interval():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_history/weeks/BTC/3")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_crypto_history_invalid_symbol():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_history/days/FAKE/3")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


# ----------------------------
# Crypto Signals Tests
# ----------------------------
@pytest.mark.asyncio
async def test_crypto_signals_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_signals/BTC/USD")
    assert response.status_code == 200
    data = response.json()
    # Updated to match refactored crypto_signals
    assert "trend" in data
    assert "high" in data
    assert "low" in data
    assert "points" in data
    assert "price_change_percent" in data


@pytest.mark.asyncio
async def test_crypto_signals_invalid_symbol():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_signals/FAKE/USD")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


# ----------------------------
# Crypto Trends Tests
# ----------------------------
@pytest.mark.asyncio
async def test_crypto_trends_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_trends/BTC")
    assert response.status_code == 200
    data = response.json()
    for term in ["short_term", "mid_term", "long_term"]:
        assert term in data
        info = data[term]
        assert "trend" in info
        # high, low, points may exist if data is valid
        if info["trend"] != "unknown":
            assert "high" in info
            assert "low" in info
            assert "points" in info


# ----------------------------
# Crypto Agent Tests
# ----------------------------
from ai.agents.CryptoChat import run_agent

@pytest.mark.asyncio
async def test_crypto_agent_basic():
    payload = {"query": "What is the price of Bitcoin?"}
    result = run_agent(payload["query"])
    assert result is not None
    assert isinstance(result["result"], str)
    assert any(word in result["result"].lower() for word in ["bitcoin", "btc"])


@pytest.mark.asyncio
async def test_crypto_agent_signals_and_trends():
    query = "Show me BTC signals and trends"
    result = run_agent(query)
    output = result["result"]
    assert output is not None
    assert isinstance(output, str)
    # Should mention trend keywords
    assert any(word in output.lower() for word in ["upward", "downward", "sideways"])


@pytest.mark.asyncio
async def test_crypto_agent_unknown_symbol():
    """Test agent response for unknown or invalid crypto symbol."""
    query = "Show me signals for ABCD"
    result = run_agent(query)
    output = result["result"]

    assert output is not None
    assert isinstance(output, str)
    # Check for realistic phrases the agent uses for unknown symbols
    assert any(
        phrase in output.lower()
        for phrase in ["couldn't find", "no information", "check the name", "try again"]
    )


@pytest.mark.asyncio
async def test_crypto_agent_multi_asset_query():
    query = "Compare BTC and ETH trends"
    result = run_agent(query)
    output = result["result"]
    assert output is not None
    assert isinstance(output, str)
    # Should mention both BTC and ETH
    assert all(sym in output for sym in ["BTC", "ETH"])


@pytest.mark.asyncio
async def test_crypto_agent_plain_language():
    query = "Explain BTC trends in simple words"
    result = run_agent(query)
    output = result["result"]
    assert output is not None
    assert isinstance(output, str)
    # Should not include raw JSON
    assert "{" not in output and "}" not in output