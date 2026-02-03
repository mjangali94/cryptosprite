# backend/ai/agents/CryptoAgent.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from ..tools.greet_user import greet_user, user_guide
from ..tools.price import (
    get_crypto_price,
    resolve_asset,
    get_crypto_history,
)
from ..tools.volume import (
    get_crypto_volume,
    get_crypto_volume_history,
)
from ..tools.technical_analysis import (
    get_market_summary,
    detect_top_movers,
    correlate_price_volume,
    detect_percentage_change,
    get_volatility,
    get_moving_average,
    get_historical_performance,
    compare_coins, get_crypto_signals, get_crypto_trends_tool, compare_crypto_trends, compare_crypto_volumes,
    get_crypto_average_volume, detect_volume_spikes, compare_average_volumes,
)
from ..tools.resolve_date_range import resolve_date_range, get_today_date
from ..tools.time_intervals_parse import resolve_human_interval
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
    user_guide,
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
    *all_price_action_tools,
]

# -----------------------------
# PROMPT
# -----------------------------
prompt = PromptTemplate(
    template=(
        "You are CryptoSprite, an AI assistant specializing in cryptocurrency analysis.\n"
        "Your role is to provide a factual, clear, and structured report on any crypto asset.\n"
        "You MUST use the provided tools to fetch real-time data and historical information.\n"
        "Do NOT predict prices or give financial advice.\n\n"
        "Follow these instructions strictly:\n"
        "1. **Current Price**: Report the latest price using the tools. Include currency and symbol clearly.\n"
        "2. **Trends Analysis**: Describe short-term, mid-term, and long-term trends.\n"
        "   - Use historical data to calculate trends.\n"
        "   - Mention % price changes, highs, and lows.\n"
        "3. **Market Sentiment**: Determine if the market is bullish, bearish, or sideways based on the trends.\n"
        "4. **Volume Analysis**: Detect any unusual volume activity (spikes) and explain why it matters.\n"
        "5. **Moving Averages**: Compute short-term and mid-term moving averages.\n"
        "   - Explain how these indicate potential price momentum.\n"
        "   - Mention if the current price is above or below the averages and what that implies for trend strength.\n"
        "6. **Price Action Analysis**: Examine historical highs, lows, and price patterns.\n"
        "   - Explain any significant movements, breakouts, or consolidation patterns.\n"
        "7. **Strategy Relevance**: For each strategy used (moving averages, volume spikes, price action):\n"
        "   - Explain why the strategy is applied.\n"
        "   - Explain what the current data suggests according to the strategy.\n"
        "8. **Summary**: Provide a concise, easy-to-read conclusion combining price, trends, sentiment, and strategies.\n\n"
        "Always structure the response into clear sections with headings.\n"
        "Keep explanations factual, simple, and precise. Avoid speculation or personal advice.\n\n"
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