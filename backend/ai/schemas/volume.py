from typing import List
from pydantic import BaseModel, Field


class CryptoVolumeInput(BaseModel):
    """
    Input schema for retrieving the current trading volume of a cryptocurrency.

    Attributes:
        symbol (str): Cryptocurrency symbol (e.g. "BTC", "ETH").
        currency (str): Fiat currency for normalization (default: "USD").
    """

    symbol: str = Field(..., min_length=1, description="Crypto symbol, e.g. BTC")
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=5,
        description="Fiat currency code (USD, EUR, etc.)",
    )


class CryptoVolumeHistoryInput(BaseModel):
    """
    Input schema for retrieving historical trading volume data.

    Attributes:
        symbol (str): Cryptocurrency symbol.
        interval (str): Time interval (e.g. 'days', 'hours').
        amount (int): Number of intervals to retrieve.
    """

    symbol: str = Field(..., min_length=1, description="Crypto symbol")
    interval: str = Field(
        ...,
        pattern="^(minutes|hours|days|weeks)$",
        description="Time interval granularity",
    )
    amount: int = Field(
        ...,
        gt=0,
        le=365,
        description="Number of intervals to retrieve",
    )


class CompareVolumesInput(BaseModel):
    """
    Input schema for comparing trading volumes across multiple cryptocurrencies.

    Attributes:
        symbols (List[str]): List of cryptocurrency symbols.
        interval (str): Time interval for comparison.
        amount (int): Number of intervals.
    """

    symbols: List[str] = Field(
        ...,
        min_items=2,
        description="List of crypto symbols to compare",
    )
    interval: str = Field(
        default="days",
        pattern="^(minutes|hours|days|weeks)$",
        description="Comparison interval",
    )
    amount: int = Field(
        default=7,
        gt=0,
        le=365,
        description="Number of intervals",
    )


class CompareAverageVolumesInput(BaseModel):
    """
    Input schema for comparing average trading volumes of multiple cryptocurrencies
    over a specified time window.

    Attributes:
        symbols (List[str]): List of cryptocurrency symbols.
        interval (str): Time interval used to calculate averages.
        amount (int): Number of intervals used in averaging.
    """

    symbols: List[str] = Field(
        ...,
        min_items=2,
        description="Crypto symbols for average volume comparison",
    )
    interval: str = Field(
        default="days",
        pattern="^(minutes|hours|days|weeks)$",
        description="Averaging interval",
    )
    amount: int = Field(
        default=30,
        gt=0,
        le=365,
        description="Intervals used to compute average volume",
    )