# backend/ai/agents/CryptoAgent.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from ..tools.greet_user import greet_user, user_guide
from ..tools.price import get_crypto_price, resolve_asset, get_crypto_history
from ..tools.volume import *
from ..tools.technical_analysis import *
from ..tools.price_action import all_price_action_tools
from ..tools.resolve_date_range import resolve_date_range, get_today_date
from ..tools.time_intervals_parse import resolve_human_interval

load_dotenv()

# -----------------------------
# MODEL
# -----------------------------
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

# -----------------------------
# TOOLS
# -----------------------------
TOOLS = [
    greet_user,
    user_guide,
    get_crypto_price,
    resolve_asset,
    get_crypto_history,
    get_today_date,
    resolve_date_range,
    resolve_human_interval,
    get_crypto_volume,
    get_crypto_volume_history,
    get_market_summary,
    detect_top_movers,
    correlate_price_volume,
    get_rsi,
    get_macd,
    get_bollinger_bands,
    get_price_trend,
    *all_price_action_tools,
]

# Map name to tool
ALL_TOOLS = {t.name: t for t in TOOLS}

# -----------------------------
# SMART ROUTER
# -----------------------------
def router(query: str):
    """
    Smart routing: selects tools dynamically based on query content.
    Returns a deduplicated list of StructuredTool objects.
    """
    q = query.lower()
    selected_tools = []

    # Greetings / guide
    if any(k in q for k in ["hello", "hi", "help", "guide"]):
        for t in ["greet_user", "user_guide"]:
            if t in ALL_TOOLS:
                selected_tools.append(ALL_TOOLS[t])

    # Price & history
    if any(k in q for k in ["price", "current price", "value", "history", "historical prices", "past prices"]):
        for t in ["get_crypto_price", "resolve_asset", "get_crypto_history"]:
            if t in ALL_TOOLS:
                selected_tools.append(ALL_TOOLS[t])

    # Volume analysis
    if any(k in q for k in ["volume", "trading volume", "avg volume", "spike"]):
        for t in [
            "get_crypto_volume",
            "get_crypto_volume_history",
            "get_crypto_average_volume",
            "compare_crypto_volumes",
            "compare_average_volumes",
        ]:
            if t in ALL_TOOLS:
                selected_tools.append(ALL_TOOLS[t])

    # Technical indicators
    if any(k in q for k in [
        "trend", "technical analysis", "market summary", "compare coins",
        "rsi", "macd", "bollinger", "moving average", "volatility"
    ]):
        for t in [
            "get_market_summary",
            "detect_top_movers",
            "correlate_price_volume",
            "detect_percentage_change",
            "get_volatility",
            "get_moving_average",
            "get_historical_performance",
            "compare_coins",
            "get_rsi",
            "get_macd",
            "get_bollinger_bands",
            "get_price_trend",
        ]:
            if t in ALL_TOOLS:
                selected_tools.append(ALL_TOOLS[t])

    # Price action patterns
    if any(k in q for k in ["pattern", "price action", "breakout", "support", "resistance"]):
        selected_tools.extend(all_price_action_tools)

    # Default fallback
    if not selected_tools:
        selected_tools.append(ALL_TOOLS["get_market_summary"])

    # Deduplicate by name
    seen = set()
    deduped_tools = []
    for t in selected_tools:
        if t.name not in seen:
            deduped_tools.append(t)
            seen.add(t.name)
    return deduped_tools

# -----------------------------
# PROMPT
# -----------------------------
prompt = PromptTemplate(
    template=(
        "You are CryptoSprite, an AI cryptocurrency analyst.\n"
        "Use the selected tools to provide **a full analysis**. Follow this strictly:\n\n"
        "1. **Current Price**: Report latest price, including symbol and currency.\n"
        "2. **Trends & Technicals**: Use historical data, RSI, MACD, Bollinger Bands, moving averages, and volatility to analyze short, mid, and long-term trends.\n"
        "3. **Volume Analysis**: Detect spikes, compare average volumes, explain unusual activity.\n"
        "4. **Price Action Patterns**: Identify breakouts, support/resistance, candlestick patterns.\n"
        "5. **Market Summary**: Combine all findings into clear sections.\n"
        "6. **Conclusion**: Provide a concise summary with trend, market sentiment, and strategy relevance.\n\n"
        "Do NOT speculate or give personal financial advice. Base your response entirely on tool data.\n\n"
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
    tools=TOOLS,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=TOOLS,
    verbose=True,
    handle_parsing_errors=True
)

# -----------------------------
# RUNNER
# -----------------------------
def run_agent(query: str) -> dict:
    """
    Run CryptoSprite agent.

    1. Router selects relevant tools based on the query.
    2. Agent calls selected tools to generate full crypto analysis.
    """
    selected_tools = router(query)
    agent_executor.tools = selected_tools  # dynamically update tools
    result = agent_executor.invoke({"input": query})
    return {"result": result.get("output", str(result))}


__all__ = ["run_agent", "router"]