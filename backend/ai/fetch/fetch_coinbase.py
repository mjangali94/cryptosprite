import requests

COINBASE_API_BASE = "https://api.exchange.coinbase.com"
REQUEST_TIMEOUT = 8

# -------------------------
# Coinbase Helper
# -------------------------
def fetch_coinbase(endpoint: str, params: dict | None = None) -> dict:
    url = f"{COINBASE_API_BASE}/{endpoint.lstrip('/')}"
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 429:
            return {"error": "Coinbase rate limit exceeded"}
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"error": "Coinbase request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}