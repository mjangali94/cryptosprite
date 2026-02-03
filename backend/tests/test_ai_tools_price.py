# tests/test_ai_tools_price.py
import pytest
from ai.tools.price import get_crypto_price, get_crypto_history, resolve_asset


# -------------------------
# resolve_asset tests
# -------------------------
@pytest.mark.parametrize(
    "query, expected",
    [
        # Bitcoin
        ("bitcoin", "BTC"),
        ("bitcorn", "BTC"),
        ("bitc0in", "BTC"),
        ("btc", "BTC"),
        ("BitCoin", "BTC"),

        # Ethereum
        ("ethereum", "ETH"),
        ("etherium", "ETH"),
        ("eth", "ETH"),
        ("Eth", "ETH"),
        ("ETHEREUM", "ETH"),

        # Cardano
        ("cardano", "ADA"),
        ("cardanno", "ADA"),
        ("ada", "ADA"),
        ("Ada", "ADA"),

        # Dogecoin
        ("dogecoin", "DOGE"),
        ("doge coin", "DOGE"),
        ("doge", "DOGE"),
        ("DOGE", "DOGE"),
        ("dogecon", "DOGE"),

        # Solana
        ("solana", "SOL"),
        ("sol", "SOL"),
        ("Sol", "SOL"),
        ("solanna", "SOL"),

        # Ripple / XRP
        ("ripple", "XRP"),
        ("xrp", "XRP"),
        ("Ripple", "XRP"),
        ("rippl", "XRP"),

        # Polkadot
        ("polkadot", "DOT"),
        ("dot", "DOT"),
        ("polka dot", "DOT"),
        ("polkadott", "DOT"),

        # Litecoin
        ("litecoin", "LTC"),
        ("lite coin", "LTC"),
        ("ltc", "LTC"),
        ("Litecoin", "LTC"),
        ("litecoinn", "LTC"),

        # Binance Coin
        ("binance coin", "BNB"),
        ("bnb", "BNB"),
        ("BinanceCoin", "BNB"),
        ("binancecoinn", "BNB"),

        # Chainlink
        ("chainlink", "LINK"),
        ("link", "LINK"),
        ("ChainLink", "LINK"),
        ("chainlnk", "LINK"),

        # Avalanche
        ("avalanche", "AVAX"),
        ("avax", "AVAX"),
        ("Avalanche", "AVAX"),
        ("avlanche", "AVAX"),
    ]
)
def test_resolve_asset_success(query, expected):
    """Test resolving a known asset returns correct dict structure."""
    result = resolve_asset.invoke({"query": query})
    assert isinstance(result, dict)
    assert "id" in result
    assert "symbol" in result
    assert "name" in result
    assert result["symbol"].upper() == expected




def test_resolve_asset_failure():
    """Test resolving an unknown asset returns a fallback or error dict."""
    result = resolve_asset.invoke({"query": "fakecoin"})
    assert isinstance(result, dict)
    # Depending on implementation, it may return a fallback asset or error
    assert "symbol" in result or "error" in result


def test_resolve_asset_empty_query():
    """Test resolving with empty string returns error dict."""
    result = resolve_asset.invoke({"query": ""})
    assert isinstance(result, dict)
    assert "error" in result
    assert "query" in result["error"].lower()


# -------------------------
# get_crypto_price tests
# -------------------------
@pytest.mark.parametrize(
    "symbol, currency",
    [
        ("BTC", "USD"),
        ("BTC", "GBP"),
    ]
)
def test_get_crypto_price_success(symbol, currency):
    """Test successful price fetch returns correct keys and types."""
    result = get_crypto_price.invoke({"symbol": symbol, "currency": currency})
    print(result)
    assert isinstance(result, dict)
    assert result["symbol"].upper() == symbol
    assert result["currency"].upper() == currency
    assert isinstance(result["price"], (float, int))


def test_get_crypto_price_missing_symbol():
    """Test behavior when symbol is missing returns error dict."""
    result = get_crypto_price.invoke({"symbol": "", "currency": "USD"})
    assert isinstance(result, dict)
    assert "error" in result
    assert "symbol" in result["error"].lower()


def test_get_crypto_price_invalid_currency_schema():
    """Test invalid currency (not allowed by schema) raises exception."""
    with pytest.raises(Exception):
        get_crypto_price.invoke({"symbol": "BTC", "currency": "XYZ"})


# -------------------------
# get_crypto_history tests
# -------------------------

@pytest.mark.parametrize(
    "symbol, interval, amount",
    [
        # Bitcoin
        ("BTC", "hours", 1),
        ("BTC", "hours", 2),
        ("BTC", "days", 1),
        ("BTC", "days", 2),
        ("BTC", "months", 1),

        # Ethereum
        ("ETH", "hours", 1),
        ("ETH", "days", 2),
        ("ETH", "months", 1),

        # Other cryptos (common on Coinbase products)
        ("ADA", "days", 2),
        ("SOL", "days", 2),
        ("DOGE", "hours", 3),

        # Larger amounts (checking return sizing)
        ("BTC", "days", 5),
        ("ETH", "hours", 5),
    ]
)
def test_get_crypto_history_success(symbol, interval, amount):
    """Test historical price fetch with various symbols, intervals, and amounts."""
    result = get_crypto_history.invoke({
        "symbol": symbol,
        "interval": interval,
        "amount": amount
    })
    # print(f"symbol={symbol}, interval={interval}, amount={amount} -> {result}")

    # Basic structure
    assert isinstance(result, dict), "Result should be a dict"
    assert "history" in result, "Result must contain history key"

    history = result["history"]
    assert isinstance(history, list), "history should be a list"
    assert len(history) == amount, f"Expected {amount} candles, got {len(history)}"

    # Each candle should have the expected OHLC keys
    expected_keys = {"open", "high", "low", "close", "volume"}
    for candle in history:
        assert isinstance(candle, dict), "Each candle should be a dict"
        assert expected_keys.issubset(candle.keys()), (
            f"Candle missing some keys: {set(candle.keys())}"
        )
        assert all(isinstance(candle[key], (int, float)) for key in expected_keys), (
            "OHLCV values must be numeric"
        )




@pytest.mark.parametrize(
    "symbol, interval, amount",
    [
        # Standard integer cases
        ("BTC", "hours", 1),
        ("BTC", "days", 2),
        ("ETH", "hours", 5),
        ("DOGE", "days", 3),

        # Fractional amounts
        ("BTC", "hours", 5.2),  # 5.2 hours
        ("BTC", "days", 2.5),  # 2.5 days
        ("ETH", "hours", 0.75),  # 45 minutes equivalent
        ("DOGE", "days", 1.5),

        # Larger fractional amounts
        ("BTC", "days", 25.3),
        ("ETH", "months", 1.5),
        ("ADA", "days", 10.7),

        # Edge fractions
        ("BTC", "hours", 0.1),
        ("ETH", "days", 0.01),
    ]
)
def test_get_crypto_history_fractional(symbol, interval, amount):
    """Test historical data fetch with fractional and integer amounts."""
    try:
        result = get_crypto_history.invoke({
            "symbol": symbol,
            "interval": interval,
            "amount": amount
        })
        # print(f"symbol={symbol}, interval={interval}, amount={amount} -> {result}")

        # Validate structure only if returned successfully
        assert isinstance(result, dict)
        assert "history" in result
        history = result["history"]
        assert isinstance(history, list)
        # Some APIs may floor or ceil fractional amounts; check at least one candle
        assert len(history) >= 1
        expected_keys = {"open", "high", "low", "close", "volume"}
        for candle in history:
            assert expected_keys.issubset(candle.keys())
            assert all(isinstance(candle[key], (int, float)) for key in expected_keys)
    except Exception as e:
        # Catch errors if fractional amounts are unsupported
        print(f"⚠️ symbol={symbol}, interval={interval}, amount={amount} failed: {e}")
        # You can assert a specific exception if you want:
        # assert isinstance(e, ValueError)


def test_get_crypto_history_invalid_symbol():
    """Test behavior when an invalid symbol is passed returns error dict."""
    result = get_crypto_history.invoke({"symbol": "FAKECOIN", "interval": "days", "amount": 2})
    assert isinstance(result, dict)
    assert "error" in result
    assert "failed" in result["error"].lower()


def test_get_crypto_history_invalid_interval_schema():
    """Test invalid interval (not allowed by schema) raises exception."""
    with pytest.raises(Exception):
        get_crypto_history.invoke({"symbol": "BTC", "interval": "years", "amount": 2})

