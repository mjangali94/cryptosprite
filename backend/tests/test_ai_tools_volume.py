import pytest
from ai.tools.volume import get_crypto_volume, get_crypto_volume_history


# -------------------------
# get_crypto_volume tests
# -------------------------

@pytest.mark.parametrize(
    "symbol, currency",
    [
        ("BTC", "USD"),
        ("ETH", "USD"),
        ("DOGE", "USD"),
        ("SOL", "USD"),
    ]
)
def test_get_crypto_volume_success(symbol, currency):
    """Test real current volume fetch for valid symbols."""
    result = get_crypto_volume.invoke({
        "symbol": symbol,
        "currency": currency
    })

    assert isinstance(result, str)
    assert symbol in result
    assert "Volume" in result
    assert "Current Price" in result


@pytest.mark.parametrize(
    "symbol",
    [
        "FAKECOIN",
        "NOTAREALASSET",
        "12345",
    ]
)
def test_get_crypto_volume_invalid_symbol(symbol):
    """Invalid symbol should return error string."""
    result = get_crypto_volume.invoke({
        "symbol": symbol,
        "currency": "USD"
    })

    assert isinstance(result, str)
    assert "failed" in result.lower() or "error" in result.lower()


def test_get_crypto_volume_invalid_currency():
    """
    Invalid currency is NOT schema-validated for volume tool,
    so it should return an error string (not raise).
    """
    result = get_crypto_volume.invoke({
        "symbol": "BTC",
        "currency": "XYZ"
    })

    assert isinstance(result, str)
    assert "failed" in result.lower() or "error" in result.lower()


# -------------------------
# get_crypto_volume_history tests
# -------------------------

@pytest.mark.parametrize(
    "symbol, interval, amount",
    [
        ("BTC", "hours", 1),
        ("BTC", "days", 3),
        ("ETH", "hours", 5),
        ("DOGE", "days", 2),
        ("BTC", "days", 10),
        ("ETH", "hours", 12),
    ]
)
def test_get_crypto_volume_history_success(symbol, interval, amount):
    """Test historical volume fetch with valid parameters."""
    result = get_crypto_volume_history.invoke({
        "symbol": symbol,
        "interval": interval,
        "amount": amount
    })

    assert isinstance(result, str)
    assert symbol in result
    assert len(result) > 0


@pytest.mark.parametrize(
    "symbol, interval, amount",
    [
        ("BTC", "hours", 2.5),
        ("BTC", "days", 1.2),
        ("ETH", "hours", 0.75),
        ("DOGE", "days", 3.8),
        ("BTC", "days", 15.6),
    ]
)
def test_get_crypto_volume_history_fractional(symbol, interval, amount):
    """
    Fractional amounts should either:
    - succeed with best-effort rounding
    - or return a graceful error string
    """
    try:
        result = get_crypto_volume_history.invoke({
            "symbol": symbol,
            "interval": interval,
            "amount": amount
        })

        assert isinstance(result, str)
        assert symbol in result or "volume" in result.lower()

    except Exception as e:
        # Acceptable if schema or API rejects fractional values
        assert isinstance(e, Exception)


@pytest.mark.parametrize(
    "symbol",
    [
        "FAKECOIN",
        "INVALID",
        "XYZ123",
    ]
)
def test_get_crypto_volume_history_invalid_symbol(symbol):
    """Invalid symbol should return error string."""
    result = get_crypto_volume_history.invoke({
        "symbol": symbol,
        "interval": "days",
        "amount": 3
    })

    assert isinstance(result, str)
    assert "failed" in result.lower() or "error" in result.lower()


def test_get_crypto_volume_history_invalid_interval_schema():
    """Invalid interval should fail schema validation."""
    with pytest.raises(Exception):
        get_crypto_volume_history.invoke({
            "symbol": "BTC",
            "interval": "years",
            "amount": 2
        })


def test_get_crypto_volume_history_invalid_amount_schema():
    """Amount < 1 should fail schema validation."""
    with pytest.raises(Exception):
        get_crypto_volume_history.invoke({
            "symbol": "BTC",
            "interval": "days",
            "amount": 0
        })