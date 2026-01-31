from typing import List

from pydantic import BaseModel, Field


class CryptoPrice(BaseModel):
    symbol: str
    currency: str = "USD"


class ResolveSymbolInput(BaseModel):
    query: str


class CryptoHistoryInput(BaseModel):
    symbol: str
    interval: str = Field(default="days")
    amount: int = Field(default=3)


class CryptoTrendInput(BaseModel):
    symbol: str


class MultiCryptoInput(BaseModel):
    symbols: List[str]
    interval: str = Field("days")
    amount: int = Field(7)
