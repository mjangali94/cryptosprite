from langchain_core.tools import tool


@tool
def greet_user(name: str | None = None):
    """
    Greets the user with a personalized welcome message for the CryptoSprite trading assistant.
    Handles cases where the user's name is not provided.

    Args:
        name (str | None): The name of the user. Can be None.

    Returns:
        str: A friendly, engaging greeting including a hint about the assistant's purpose.
    """
    user = name if name else "there"
    return (
        f"👋 Welcome, {user}! I'm CryptoSprite, your crypto trading assistant. "
        "I can help you check prices, analyze trends, detect volume spikes, "
        "and provide clear insights on cryptocurrencies. Let's explore the market together!"
    )



@tool
def user_guide():
    """
    Provides guidance to the user on how to interact with the CryptoSprite assistant,
    including example queries and explanation of available strategies.
    """
    return (
        "Here’s how you can interact with me:\n"
        "1️⃣ Ask for the current price of any crypto, e.g., 'BTC price in USD'.\n"
        "2️⃣ Ask for trends: short, mid, and long-term, e.g., 'BTC trends'.\n"
        "3️⃣ Ask about market strategies, e.g., 'Is there a volume spike for ETH?' or 'Check moving averages for SOL'.\n"
        "4️⃣ Ask for comparisons: 'Compare BTC, ETH, and SOL trends'.\n\n"
        "⚠️ Remember: I provide information and analysis, but not financial advice. "
        "Use the insights to make informed decisions.\n"
        "💡 Tip: You can explore different coins, intervals, and see how strategies apply in real time!"
    )