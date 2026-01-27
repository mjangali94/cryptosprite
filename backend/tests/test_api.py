import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from api.routes import router  # adjust import based on your project

app = FastAPI()
app.include_router(router)

@pytest.mark.asyncio
async def test_crypto_price_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_price/BTC/USD")
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data["symbol"] == "BTC"
    assert "price" in data

@pytest.mark.asyncio
async def test_crypto_price_invalid_symbol():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_price/INVALID/USD")
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert "error" in data

@pytest.mark.asyncio
async def test_crypto_history_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_history/days/BTC/3")
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data["symbol"] == "BTC"
    assert len(data["history"]) > 0

@pytest.mark.asyncio
async def test_crypto_signals_success():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/crypto_signals/BTC/USD")
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert "trend" not in data or "price_change_24h_percent" in data