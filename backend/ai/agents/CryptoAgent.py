# backend/ai/agents/CryptoAgent.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

# -----------------------------
# TOOL IMPORTS (REAL ONLY)
# -----------------------------
from ai.tools.greet_user import greet_user, user_guide
from ai.tools.price import (
    get_crypto_price,
    resolve_asset,
    get_crypto_history,
)
from ai.tools.volume import (
    get_crypto_volume,
    get_crypto_volume_history,
)
from ai.tools.technical_analysis import (
    get_market_summary,
    detect_top_movers,
    correlate_price_volume,
    get_rsi,
    get_ema,
    get_macd,
    get_bollinger_bands,
    get_price_trend,
)
from ai.tools.price_action import all_price_action_tools
from ai.tools.resolve_date_range import resolve_date_range, get_today_date
from ai.tools.time_intervals_parse import resolve_human_interval

load_dotenv()

# -----------------------------
# MODEL
# -----------------------------
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

# -----------------------------
# TOOLS (AUTHORITATIVE LIST)
# -----------------------------
TOOLS = [
    # UX
    greet_user,
    user_guide,

    # Asset / date resolution
    resolve_asset,
    resolve_date_range,
    resolve_human_interval,
    get_today_date,

    # Price
    get_crypto_price,
    get_crypto_history,

    # Volume
    get_crypto_volume,
    get_crypto_volume_history,

    # Technical analysis
    get_market_summary,
    detect_top_movers,
    correlate_price_volume,
    get_rsi,
    get_ema,
    get_macd,
    get_bollinger_bands,
    get_price_trend,

    # Price action (patterns, S/R, breakouts)
    *all_price_action_tools,
]

# Map tool.name → tool (StructuredTool safe)
ALL_TOOLS = {t.name: t for t in TOOLS}

# -----------------------------
# SMART ROUTER
# -----------------------------
def router(query: str):
    """
    Keyword-driven smart router.
    Selects only relevant tools per query.
    """
    q = query.lower()
    selected = []

    def use(*names):
        for n in names:
            if n in ALL_TOOLS:
                selected.append(ALL_TOOLS[n])

    # Greeting / onboarding
    if any(k in q for k in ["hi", "hello", "help", "guide", "how to use"]):
        use("greet_user", "user_guide")

    # Asset / date understanding
    if any(k in q for k in ["btc", "eth", "coin", "token", "crypto"]):
        use("resolve_asset")

    if any(k in q for k in ["today", "yesterday", "last week", "last month", "past"]):
        use("resolve_date_range", "resolve_human_interval", "get_today_date")

    # Price & history
    if any(k in q for k in ["price", "value", "worth", "historical", "history"]):
        use("get_crypto_price", "get_crypto_history")

    # Volume
    if any(k in q for k in ["volume", "liquidity", "trading activity"]):
        use("get_crypto_volume", "get_crypto_volume_history")

    # Technical indicators
    if any(k in q for k in [
        "technical", "indicator", "trend",
        "rsi", "ema", "macd", "bollinger",
    ]):
        use(
            "get_market_summary",
            "get_price_trend",
            "get_rsi",
            "get_ema",
            "get_macd",
            "get_bollinger_bands",
            "correlate_price_volume",
        )

    # Comparisons / movers
    if any(k in q for k in ["top movers", "gainers", "losers", "compare"]):
        use("detect_top_movers", "get_market_summary")

    # PRICE ACTION (explicit and implicit triggers)
    if any(k in q for k in [
        "price action",
        "support",
        "resistance",
        "breakout",
        "break down",
        "range",
        "structure",
        "trendline",
        "higher high",
        "lower low",
        "pattern",
        "candlestick",
        "rejection",
    ]):
        selected.extend(all_price_action_tools)

    # Fallback
    if not selected:
        use("get_market_summary")

    # Deduplicate
    deduped = []
    seen = set()
    for t in selected:
        if t.name not in seen:
            deduped.append(t)
            seen.add(t.name)

    return deduped

# -----------------------------
# PROMPT (PRICE-ACTION AWARE)
# -----------------------------
prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad"],
    template=(
        "You are **CryptoSprite**, an expert cryptocurrency analyst.\n\n"
        "Your task is to decide WHICH tools to use and WHEN.\n\n"

        "### Decision Rules\n"
        "- Use **price action tools** when the user asks about:\n"
        "  • support / resistance\n"
        "  • breakouts or breakdowns\n"
        "  • market structure (HH, HL, LH, LL)\n"
        "  • candlestick behavior or rejections\n"
        "- Use **technical indicators** (RSI, EMA, MACD, Bollinger) to:\n"
        "  • confirm momentum\n"
        "  • detect overbought / oversold conditions\n"
        "- Use **volume tools** to confirm strength or weakness of moves\n"
        "- Use **price history** before making any trend judgment\n\n"

        "### Analysis Structure\n"
        "1. Current price & context\n"
        "2. Trend & indicators (if relevant)\n"
        "3. Volume confirmation (if relevant)\n"
        "4. Price action patterns (ONLY when applicable)\n"
        "5. Clear, neutral summary\n\n"

        "### Constraints\n"
        "- Do NOT give financial advice\n"
        "- Do NOT speculate without data\n"
        "- Base conclusions ONLY on tool outputs\n\n"

        "User query:\n{input}\n\n"
        "{agent_scratchpad}"
    ),
)

# -----------------------------
# AGENT
# -----------------------------
agent = create_tool_calling_agent(
    llm=model,
    tools=TOOLS,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=TOOLS,
    verbose=True,
    handle_parsing_errors=True,
)

# -----------------------------
# RUNNER
# -----------------------------
def run_agent(query: str) -> dict:
    """
    Entry point for CryptoSprite.
    """
    selected_tools = router(query)
    agent_executor.tools = selected_tools

    result = agent_executor.invoke({"input": query})
    return {
        "output": result.get("output", str(result)),
        "tools_used": [t.name for t in selected_tools],
    }


__all__ = ["run_agent", "router"]