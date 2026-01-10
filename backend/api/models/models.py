import datetime
from typing import Optional
from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    query:str


class AgentChatResponse(BaseModel):
    result:str


class CryptoPrice(BaseModel):
    symbol: str
    name: str
    price: Optional[float]
    currency: str

class CryptoPriceDate(BaseModel):
    symbol: str
    name: str
    price: Optional[float]
    currency: str
    date: Optional[datetime.datetime]