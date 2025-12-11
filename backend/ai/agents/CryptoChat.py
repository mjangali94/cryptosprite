from dotenv import load_dotenv
from langchain_classic import hub
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from ..tools.CryptoPrice import (
    get_crypto_price,
    get_crypto_price_by_date,
    get_crypto_price_percentage_change,
    resolve_asset,
    get_crypto_history
)

from ..tools.ResolveDateRange import resolve_date_range, get_today_date
from ..tools.GreetUser import greet_user
from ..tools.TimeIntervalsParse import resolve_human_interval

load_dotenv()

# --- USE OPENAI MODEL HERE ---
model = ChatOpenAI(
    model="gpt-4o-mini",   # or "gpt-4.1" or "gpt-4o"
    temperature=0,
)

# -----------------------------
# TOOLS
# -----------------------------
tools = [
    greet_user,
    get_crypto_price,
    get_crypto_price_by_date,
    get_crypto_price_percentage_change,
    resolve_asset,
    get_crypto_history,
    resolve_human_interval,
    resolve_date_range,
    get_today_date
]

model_with_tools = model.bind_tools(tools)

# -----------------------------
# PROMPT
# -----------------------------
prompt = hub.pull("hwchase17/openai-tools-agent")
prompt = prompt.partial(
    tools=tools,
    tool_names=[t.name for t in tools]
)

# -----------------------------
# AGENT
# -----------------------------
agent = create_tool_calling_agent(
    llm=model_with_tools,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)

# -----------------------------
# RUN
# -----------------------------
def run_agent(query: str):
    result = agent_executor.invoke({"input": query})
    return {
        "result": result.get("output")
                  or result.get("output_text")
                  or str(result)
    }


__all__ = ["run_agent"]