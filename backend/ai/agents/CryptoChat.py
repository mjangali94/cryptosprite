from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from ..tools.CryptoPrice import get_crypto_price, resolve_asset, get_crypto_history, get_crypto_signals

load_dotenv()

# -----------------------------
# OPENAI MODEL
# -----------------------------
model = ChatOpenAI(
    model="gpt-4o-mini",  # or "gpt-4.1" or "gpt-4o"
    temperature=0,
)

# -----------------------------
# TOOLS
# -----------------------------
tools = [
    get_crypto_price,
    resolve_asset,
    get_crypto_history,
    get_crypto_signals,
]

model_with_tools = model.bind_tools(tools)

# -----------------------------
# PROMPT
# -----------------------------
# Must include all required input variables: 'input', 'tools', 'tool_names', 'agent_scratchpad'
prompt_template_text = (
    "You are CryptoSprite, an AI assistant that explains the current state of crypto assets. "
    "Use only deterministic data from the tools provided. "
    "Do NOT predict prices or give financial advice. "
    "Explain the price, volume behavior, and simple signals in plain language. "
    "\n\nUser query: {input}\n\n{agent_scratchpad}"
)

prompt = PromptTemplate(
    template=prompt_template_text,
    input_variables=["input", "tools", "tool_names", "agent_scratchpad"]
)

# Partially fill in tools for the agent
prompt = prompt.partial(
    tools=tools,
    tool_names=[t.name for t in tools]
)

# -----------------------------
# CREATE AGENT
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
# RUN AGENT
# -----------------------------
def run_agent(query: str):
    """
    Run the CryptoSprite agent on a user query.
    Returns structured explanation using deterministic signals.
    """
    result = agent_executor.invoke({"input": query})
    return {
        "result": result.get("output")
                  or result.get("output_text")
                  or str(result)
    }

__all__ = ["run_agent"]