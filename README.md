# 🚀 CryptoSprite

**CryptoSprite** is an AI-powered cryptocurrency market analysis agent built using modern agent-based LLM architecture.  
It combines **live price data**, **technical indicators**, **volume analytics**, and **price action strategies** into a single intelligent system capable of reasoning about crypto markets through natural language prompts.

> ⚠️ CryptoSprite is for research, experimentation, and educational purposes only.  
> **Not financial advice.**



## ✨ Key Features

### 🤖 Intelligent AI Agent
- Tool-calling LLM agent (LangChain-based)
- Dynamically selects the right tools based on user intent
- Produces structured, explainable market analysis

### 📊 Market Data & Analysis
- Live crypto prices
- Historical OHLCV data
- Volume trends and summaries
- Market-wide summaries and top movers

### 📈 Technical Indicators
- RSI
- EMA
- MACD
- Bollinger Bands
- Price trend detection

### 🔍 Price Action Strategies
- Breakouts & break-and-retest
- Pullbacks
- Trendline reactions
- Double top / double bottom
- Head & shoulders
- Flags, pennants, triangles, rectangles
- Inside bars
- Pin bars
- Psychological price levels

### 🧠 Prompt-Driven Reasoning
- Natural language queries
- Multi-step reasoning using real market data
- Strategy-aware responses



## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI**
- **LangChain**
- **OpenAI / OpenAI-compatible LLMs**
- **Pydantic**
- **Pytest**


## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/mjangali94/cryptosprite.git
cd cryptosprite/backend
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
# venv\Scripts\activate   # Windows
```
### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Environment variables
```bash
OPENAI_API_KEY=your_api_key_here
```
### ▶️ Running the API
```bash
uvicorn main:app --reload
```


## 🔌 API Usage

### Endpoint
```bash
POST /api/crypto_agent
```

### Request body
```bash
{
  "query": "Analyze BTC using price action and technical indicators"
}
```

### Example response
```bash
{
  "result": "### Bitcoin (BTC) Market Analysis\n\nCurrent price...\n..."
}
```


## 🧪 Running Tests

Run pytest in verbose mode
``` bash
pytest -v -s
```

Tests are **prompt-driven** and focus on:
- Agent stability
- Tool routing behavior
- Output generation (not correctness of predictions)


## 🧠 Prompt Examples

Here are 20 example prompts you can try with CryptoSprite:

1. "What is the current price of Bitcoin (BTC)?"
2. "Give me the latest Ethereum (ETH) price and market context."
3. "Analyze BTC price action for the past 7 days."
4. "Identify support and resistance levels for BTC."
5. "Is BTC currently in a bullish or bearish trend?"
6. "Check if ETH is forming any breakout patterns."
7. "Summarize the last week of price movements for BTC."
8. "Detect any double top or double bottom patterns in BTC."
9. "Show me recent pullbacks in ETH and possible entries."
10. "Compare the price trends of BTC and ETH over the last month."
11. "Analyze the volume trends of BTC and highlight anomalies."
12. "Is BTC forming any head and shoulders or inverse head and shoulders patterns?"
13. "Provide a short-term market outlook for BTC using technical indicators."
14. "Look for triangle, flag, or pennant formations in ETH charts."
15. "Analyze BTC momentum using breakout and pullback strategies."
16. "What are the top 5 coins with strongest bullish patterns today?"
17. "Evaluate BTC and ETH for trendline bounces and price rejections."
18. "Give a combined price action and volume analysis for BTC."
19. "Check for reversal candlestick patterns in BTC over the past 3 days."
20. "Provide a detailed technical analysis for BTC including breakout, pullback, and trendline patterns."


These prompts can be fed directly to the agent to test different strategies, price patterns, and market insights.


## 🚧 Project Status

### ✅ v1.0.0 – Stable Release
- Core agent architecture complete
- Tool routing implemented
- Price action strategies integrated
- Test suite added

### 🔜 Planned Enhancements
- Multi-timeframe analysis
- Strategy confidence scoring
- Trade simulation & backtesting
- Web UI / dashboard
- Agent memory & session context
- Multi-asset comparison agent



## ⚠️ Disclaimer

CryptoSprite **does not provide financial advice**.

All outputs are:
- Informational
- Experimental
- Based solely on public market data and algorithmic analysis

You are fully responsible for any decisions you make.



## 👤 Author

Mostafa Jangali  
GitHub: https://github.com/mjangali94



## ⭐ Contributing

Contributions, ideas, and improvements are welcome.

If you’re experimenting with:
- AI agents
- Market analysis
- Prompt engineering
- Trading research

Feel free to open an issue or PR.


