from langchain_core.tools import tool
from ai.services.domain_functions import get_spot_price, get_price_history
from ai.schemas.price import CryptoPrice, ResolveSymbolInput, CryptoHistoryInput
from utils.crypto_assets import resolve_asset_symbol


# =========================================================
# Constants & Helpers
# =========================================================

ALLOWED_INTERVALS = {"hours", "days", "months"}


def tool_error(message: str) -> dict:
    """Standardized error response for tools."""
    return {"error": message}


# =========================================================
# Tools (Data-only, No Analysis)
# =========================================================

@tool(args_schema=ResolveSymbolInput, return_direct=True)
def resolve_asset(query: str):
    """
    Resolve a user-provided asset name or ticker to a standardized crypto symbol.

    Use when:
    - user provides informal names (e.g., 'bitcoin', 'eth')
    - validating or normalizing symbols before price/history queries

    Returns:
    - resolved symbol metadata if found
    - structured error otherwise
    """
    if not query:
        return tool_error("Query not provided")

    result = resolve_asset_symbol(query)
    if result.get("symbol"):
        return result

    return tool_error(f"Could not resolve crypto symbol from '{query}'")


@tool(args_schema=CryptoPrice, return_direct=True)
def get_crypto_price(symbol: str, currency: str = "USD"):
    """
    Return the latest spot price for a cryptocurrency.

    Use when:
    - user asks for current price
    - agent needs real-time market value
    - composing higher-level market summaries

    Do NOT use for:
    - trend analysis
    - predictions or financial advice
    """
    if not symbol:
        return tool_error("Symbol not provided")

    return get_spot_price(symbol.upper(), currency.upper())


@tool(args_schema=CryptoHistoryInput, return_direct=True)
def get_crypto_history(symbol: str, interval: str = "days", amount: int = 3):
    """
    Return historical OHLCV candle data for a cryptocurrency.

    Use when:
    - computing trends or indicators
    - analyzing volatility or volume
    - feeding data into analytics or signal tools

    Parameters:
    - interval: 'hours', 'days', or 'months'
    - amount: number of intervals to fetch

    Do NOT use for:
    - direct price queries
    - financial advice or predictions
    """
    if not symbol:
        return tool_error("Symbol not provided")

    if interval not in ALLOWED_INTERVALS:
        return tool_error(
            f"Invalid interval '{interval}'. Use one of: hours, days, months."
        )

    return get_price_history(symbol.upper(), "USD", interval, amount)