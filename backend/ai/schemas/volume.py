from pydantic import BaseModel, Field
from typing import List, Literal

Interval = Literal["hours", "days", "months"]
Currency = Literal["USD", "BTC", "ETH"]  # can extend to other currencies if needed

class CryptoVolumeInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'BTC'")
    currency: Currency = Field("USD", description="Currency to measure volume in")


class CryptoVolumeHistoryInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'ETH'")
    interval: Interval = Field("days", description="Time interval for volume data")
    amount: int = Field(3, ge=1, description="Number of intervals to fetch (must be >=1)")


class CompareVolumesInput(BaseModel):
    symbols: List[str] = Field(..., description="List of cryptocurrency symbols")
    interval: Interval = Field("days", description="Time interval for comparison")
    amount: int = Field(7, ge=1, description="Number of intervals to fetch (must be >=1)")