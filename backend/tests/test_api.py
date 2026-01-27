import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from api.routes import router

# ----------------------------
# Test App Setup
# ----------------------------
app = FastAPI()
app.include_router(router)

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
    assert data["currency"] == "usd"


@pytest.mark.asyncio
async def test_crypto_price_default_currency():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_price/BTC")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert data["currency"] == "usd"


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


@pytest.mark.asyncio
async def test_crypto_history_response_structure():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_history/days/BTC/2")
    data = response.json()
    assert "history" in data
    assert isinstance(data["history"], list)
    assert "timestamp" in data["history"][0]
    assert "price" in data["history"][0]

# ----------------------------
# Crypto Signals Tests
# ----------------------------
@pytest.mark.asyncio
async def test_crypto_signals_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_signals/BTC/USD")
    assert response.status_code == 200
    data = response.json()
    assert "price" in data
    assert "volume" in data
    assert "price_change_24h_percent" in data


@pytest.mark.asyncio
async def test_crypto_signals_invalid_symbol():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_signals/FAKE/USD")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

# ----------------------------
# Crypto Agent Tests
# ----------------------------
@pytest.mark.asyncio
async def test_crypto_agent_basic():
    payload = {"query": "What is the price of Bitcoin?"}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/crypto_agent", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert isinstance(data["result"], str)