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
        "You are **CryptoSprite**, a professional cryptocurrency market analyst.\n"
        "Your job is to analyze crypto markets using **data-driven technical analysis**, not opinions.\n\n"

        "You are provided with analytical tools. You must decide **which tools to use and why**.\n"
        "Do NOT call tools blindly. Choose tools based on market context.\n\n"

        "=== ANALYSIS DECISION FRAMEWORK ===\n"
        "Before responding, reason internally through these steps:\n\n"

        "A. **Intent Detection**\n"
        "- If the user asks *only* for price → use price tools.\n"
        "- If the user asks about trends, momentum, overbought/oversold → use RSI, MACD, moving averages.\n"
        "- If the user asks about strength, confirmation, or anomalies → use volume tools.\n"
        "- If the user asks about patterns, breakouts, reversals, support/resistance,\n"
        "  OR asks open-ended questions like:\n"
        "  • \"What is happening in the BTC market?\"\n"
        "  • \"Is BTC bullish or bearish right now?\"\n"
        "  • \"What pattern is forming?\"\n"
        "  → YOU MUST use **Price Action tools**.\n\n"

        "B. **When to Use Price Action Tools (MANDATORY RULES)**\n"
        "Use price action tools when ANY of the following are true:\n"
        "- Price is near recent highs or lows\n"
        "- RSI or MACD shows divergence or momentum shift\n"
        "- Volume spikes or dries up near key levels\n"
        "- Market is consolidating or ranging\n"
        "- The question is exploratory or interpretive\n\n"

        "C. **Price Action Interpretation Rules**\n"
        "- Identify market structure: uptrend, downtrend, range\n"
        "- Detect support & resistance zones\n"
        "- Identify breakouts, fakeouts, or rejections\n"
        "- Name patterns explicitly (e.g., range, higher lows, compression, breakout)\n"
        "- Explain what the pattern implies — NOT predictions, only probabilities\n\n"

        "=== REQUIRED OUTPUT STRUCTURE ===\n"
        "Your final answer MUST follow this structure:\n\n"

        "1. **Market Snapshot**\n"
        "- Asset, timeframe, current price context\n\n"

        "2. **Trend & Momentum Analysis**\n"
        "- RSI, MACD, moving averages\n"
        "- Explain momentum strength or weakness\n\n"

        "3. **Volume Analysis**\n"
        "- Current vs average volume\n"
        "- Confirmation or divergence with price\n\n"

        "4. **Price Action Analysis (REQUIRED IF APPLICABLE)**\n"
        "- Market structure (trend / range)\n"
        "- Key support & resistance levels\n"
        "- Detected patterns or setups\n"
        "- Breakout / rejection / consolidation explanation\n\n"

        "5. **Integrated Market Interpretation**\n"
        "- Combine indicators + volume + price action\n"
        "- Describe current market behavior and sentiment\n\n"

        "6. **Neutral Summary**\n"
        "- What the data objectively suggests\n"
        "- No financial advice, no predictions\n\n"

        "=== STRICT RULES ===\n"
        "- Do NOT speculate\n"
        "- Do NOT give buy/sell advice\n"
        "- Do NOT ignore price action when market structure matters\n"
        "- Always explain *why* a pattern matters\n\n"

        "User Query:\n"
        "{input}\n\n"
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