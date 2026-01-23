from typing import Optional
from pydantic import BaseModel

# ----------------- LLM Agent Models -----------------
class AgentChatRequest(BaseModel):
    query: str  # User query for the interpretation layer

class AgentChatResponse(BaseModel):
    result: str  # LLM-generated explanation of market data


# ----------------- Crypto Price Model -----------------
class CryptoPrice(BaseModel):
    symbol: str            # Ticker symbol, e.g. BTC
    name: str              # Full asset name
    price: Optional[float] # Current price
    currency: str          # Currency code, e.g. USD