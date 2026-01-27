import pytest

from ai.tools.CryptoPrice import (
    get_crypto_price,
    get_crypto_history,
    get_crypto_signals,
    resolve_asset,
)


def test_get_crypto_price():
    """
    Crypto price tool can return:
    - dict (success)
    - str (rate limit / API error)
    """
    result = get_crypto_price.invoke({
        "symbol": "BTC"
    })

    assert result is not None

    # Success case
    if isinstance(result, dict):
        assert "symbol" in result
        assert result["symbol"] == "BTC"
        assert "price" in result

    # Error case (rate limit, API down)
    elif isinstance(result, str):
        assert "request" in result.lower() or "error" in result.lower()

    else:
        pytest.fail(f"Unexpected return type: {type(result)}")


def test_get_crypto_history():
    """
    History tool should always return a dict
    """
    result = get_crypto_history.invoke({
        "interval": "days",
        "symbol": "BTC",
        "amount": 3
    })

    assert isinstance(result, dict)
    assert result["symbol"] == "BTC"
    assert "history" in result
    assert isinstance(result["history"], list)
    assert len(result["history"]) > 0


def test_get_crypto_signals():
    """
    Signals tool returns deterministic analysis
    """
    result = get_crypto_signals.invoke({
        "interval": "days",
        "symbol": "BTC",
        "amount": 3
    })

    assert isinstance(result, dict)
    assert result["symbol"] == "BTC"


def test_resolve_asset():
    """
    Resolver returns structured asset info
    """
    result = resolve_asset.invoke({
        "query": "Bitcoin"
    })

    assert isinstance(result, dict)
    assert result["symbol"] == "BTC"
    assert result["name"].lower() == "bitcoin"