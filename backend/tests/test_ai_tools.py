from ai.tools.CryptoPrice import get_crypto_price, get_crypto_history, get_crypto_signals, resolve_asset

def test_get_crypto_price():
    result = get_crypto_price(symbol="BTC")
    assert "BTC" in result

def test_get_crypto_history():
    result = get_crypto_history(interval="days", symbol="BTC", amount=3)
    assert result["symbol"] == "BTC"
    assert len(result["history"]) > 0

def test_get_crypto_signals():
    result = get_crypto_signals(interval="days", symbol="BTC", amount=3)
    assert "trend" in result
    assert "price_change_percent" in result

def test_resolve_asset():
    result = resolve_asset("Bitcoin")
    assert result["symbol"] == "BTC"