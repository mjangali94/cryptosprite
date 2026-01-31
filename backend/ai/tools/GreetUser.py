from langchain_core.tools import tool


@tool
def greet_user(name: str = None):
    """
    Greets the user with a welcome message.

    Instructions for the agent:
    - After greeting the user, immediately invoke the `user_guide` tool.
    - Explain to the user how to ask questions and what tools are available.
    - You may include example queries in the guide.
    """
    return f"👋 Welcome {name or 'there'}! I'm CryptoSprite, your crypto trading assistant."


@tool
def user_guide():
    """
    Provides detailed guidance for interacting with the CryptoSprite assistant.

    The guide explains:
    - How to ask for prices, trends, and market analysis.
    - Which strategies are available and when they are useful.
    - Example queries for each tool and strategy.
    - Safety reminders: information only, not financial advice.

    Instructions for the agent:
    - Invoke this tool automatically after greeting the user.
    - Highlight all available tools and strategies.
    - Provide examples to help the user explore effectively.
    """
    return (
        "👋 Welcome! Here's how you can interact with CryptoSprite:\n\n"

        "1️⃣ **Check Current Prices**\n"
        "   - Ask the current price of any cryptocurrency.\n"
        "   - Example: 'BTC price in USD', 'ETH current price'.\n\n"

        "2️⃣ **Analyze Trends**\n"
        "   - Short-term (hours), mid-term (days), long-term (months).\n"
        "   - Example: 'Show BTC trends', 'ETH trends last 14 days'.\n\n"

        "3️⃣ **Market Strategies**\n"
        "   - **Volume Spike Detection**: Alerts for unusual trading activity.\n"
        "     Example: 'Check volume spikes for SOL'.\n"
        "   - **Moving Averages**: Short-term and mid-term averages indicate bullish/bearish trends.\n"
        "     Example: 'Get moving averages for BTC'.\n"
        "   - **Price Action**: Highlights highs, lows, and fluctuations.\n"
        "     Example: 'Analyze BTC price action last 30 days'.\n\n"

        "4️⃣ **Compare Cryptocurrencies**\n"
        "   - Compare multiple coins for trends and strategy signals.\n"
        "   - Example: 'Compare BTC, ETH, and SOL trends'.\n\n"

        "💡 **Tips for Using CryptoSprite Effectively:**\n"
        "- Combine strategies to get deeper insights (e.g., trends + volume spikes).\n"
        "- Experiment with different intervals (hours/days/months) for trends.\n"
        "- Ask follow-up questions to dive deeper into any analysis.\n\n"

        "⚠️ **Reminder:** All insights are for informational purposes only. "
        "CryptoSprite does **not** give financial advice. Use the information to make your own informed decisions.\n\n"
        "🌟 Explore and enjoy discovering the crypto market with real data!"
    )