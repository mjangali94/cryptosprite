from typing import List, Literal
from pydantic import BaseModel, Field

Interval = Literal["hours", "days", "months"]
Currency = Literal[
    # Major fiat currencies available in Coinbase Exchange products
    "USD",  # US Dollar
    "EUR",  # Euro
    "GBP",  # British Pound
]

class CryptoPrice(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'BTC'")
    currency: Currency = Field("USD", description="Currency for price, e.g., USD")


class ResolveSymbolInput(BaseModel):
    query: str = Field(..., description="Query string to resolve crypto symbol")


class CryptoHistoryInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'ETH'")
    interval: Interval = Field("days", description="Time interval for historical data")
    amount: int = Field(3, ge=1, description="Number of intervals to fetch (must be >=1)")


class CryptoTrendInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol to compute trend for")


class MultiCryptoInput(BaseModel):
    symbols: List[str] = Field(..., description="List of cryptocurrency symbols")
    interval: Interval = Field("days", description="Time interval for trend comparison")
    amount: int = Field(7, ge=1, description="Number of intervals to fetch (must be >=1)")