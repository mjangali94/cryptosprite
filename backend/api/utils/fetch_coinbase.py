# coinbase_client.py
import requests

COINBASE_API_BASE = "https://api.exchange.coinbase.com"
TIMEOUT_SECONDS = 3


def fetch_coinbase(endpoint: str, params: dict | None = None) -> dict:
    url = f"{COINBASE_API_BASE}/{endpoint}"

    # print(f"[DEBUG][Coinbase] GET {url} params={params}")

    try:
        response = requests.get(
            url,
            params=params,
            timeout=TIMEOUT_SECONDS,
            headers={
                "User-Agent": "crypto-debug/1.0",
                "Accept": "application/json"
            }
        )

        # print(f"[DEBUG][Coinbase] Status: {response.status_code}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        # print("[DEBUG][Coinbase] ❌ Timeout")
        return {"error": "timeout"}

    except requests.exceptions.HTTPError as e:
        # print(f"[DEBUG][Coinbase] ❌ HTTP error: {e}")
        return {
            "error": "http_error",
            "status_code": response.status_code,
            "body": response.text
        }

    except requests.exceptions.RequestException as e:
        # print(f"[DEBUG][Coinbase] ❌ Request failed: {e}")
        return {"error": "request_failed"}