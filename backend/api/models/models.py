from typing import Optional
from pydantic import BaseModel

# ----------------- LLM Agent Models -----------------
class AgentChatRequest(BaseModel):
    query: str  # User query for the interpretation layer

class AgentChatResponse(BaseModel):
    result: str  # LLM-generated explanation of market data

