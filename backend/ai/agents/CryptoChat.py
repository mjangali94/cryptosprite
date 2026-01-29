# backend/ai/agents/CryptoChat.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from ..tools.GreetUser import greet_user
from ..tools.CryptoPrice import (
    get_crypto_price,
    resolve_asset,
    get_crypto_history,
    get_crypto_signals,
    get_crypto_trends_tool,
    compare_crypto_trends,
)
from ..tools.CryptoVolume import (
    get_crypto_volume,
    get_crypto_volume_history,
    compare_crypto_volumes,
    get_crypto_average_volume,
    detect_volume_spikes,
    compare_average_volumes,
)
from ..tools.CryptoAnalytics import (
    get_market_summary,
    detect_top_movers,
    correlate_price_volume,
    detect_percentage_change,
    get_volatility,
    get_moving_average,
    get_historical_performance,
    compare_coins,
)
from ..tools.ResolveDateRange import resolve_date_range, get_today_date
from ..tools.TimeIntervalsParse import resolve_human_interval
from ..tools.TechnicalStrategies import all_strategy_tools
from ..tools.PriceActionStrategies import all_price_action_tools

load_dotenv()

# -----------------------------
# MODEL
# -----------------------------
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

# -----------------------------
# TOOLS (FLATTENED ✅)
# -----------------------------
tools = [
    greet_user,
    get_crypto_price,
    resolve_asset,
    get_crypto_history,
    get_crypto_signals,
    get_crypto_trends_tool,
    compare_crypto_trends,
    get_today_date,
    resolve_date_range,
    resolve_human_interval,
    get_crypto_volume,
    get_crypto_volume_history,
    get_crypto_average_volume,
    detect_volume_spikes,
    compare_crypto_volumes,
    compare_average_volumes,
    get_market_summary,
    detect_top_movers,
    correlate_price_volume,
    detect_percentage_change,
    get_volatility,
    get_moving_average,
    get_historical_performance,
    compare_coins,
    *all_strategy_tools,
    *all_price_action_tools,
]

# -----------------------------
# PROMPT
# -----------------------------
prompt = PromptTemplate(
    template=(
        "You are CryptoSprite, an AI assistant that explains crypto assets in simple, clear language.\n"
        "You MUST use the provided tools to fetch real data.\n"
        "Do NOT predict prices or give financial advice.\n\n"
        "Instructions:\n"
        "1. Explain the current price clearly.\n"
        "2. Describe short, mid, and long-term trends.\n"
        "3. Say if the market is bullish, bearish, or sideways.\n"
        "4. Mention highs, lows, and unusual behavior.\n"
        "5. If strategies are used, explain why they apply or don’t.\n\n"
        "User query: {input}\n\n"
        "{agent_scratchpad}"
    ),
    input_variables=["input", "agent_scratchpad"],
)

# -----------------------------
# AGENT
# -----------------------------
agent = create_tool_calling_agent(
    llm=model,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)

# -----------------------------
# RUNNER
# -----------------------------
def run_agent(query: str) -> dict:
    result = agent_executor.invoke({"input": query})

    return {
        "result": result.get("output", str(result))
    }


__all__ = ["run_agent"]