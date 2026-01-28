# api/routes/agent.py
from fastapi import APIRouter
from pydantic import BaseModel
from ai.agents.CryptoChat import run_agent

router = APIRouter(prefix="/api", tags=["agent"])


class AgentRequest(BaseModel):
    query: str


@router.post("/crypto_agent")
async def crypto_agent(payload: AgentRequest):
    """
    Receives a user query and passes it to the CryptoChat agent.
    Returns the agent's response.
    """
    # Make sure run_agent can handle async or blocking properly
    # If run_agent is blocking, it might be better to run in a thread:
    # from fastapi.concurrency import run_in_threadpool
    # return await run_in_threadpool(run_agent, payload.query)

    return run_agent(payload.query)