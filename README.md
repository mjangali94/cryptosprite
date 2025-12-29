# 💎 CryptoSprite Dashboard

A cryptocurrency dashboard enhanced with an **AI Agent** for fetching real-time and historical pricing data through natural language queries.

---

## ✨ Features

* **Real-time & Historical Prices:** Fetches current and past prices for major assets (e.g., **BTC, ETH, SOL**).
* **AI Agent Querying:** Supports natural language queries for historical data using custom **LangChain tools**, such as:
    * `"BTC price yesterday"`
    * `"ETH price 5 days ago"`
    * `"Price for Solana last Friday"`
* **Market Analysis:** Calculates and displays **percentage change** (today vs. yesterday).
* **Visualization:** Interactive frontend with dedicated price cards and charts powered by **Chart.js**.
* **Structured API:** Robust **FastAPI** backend integrated with CoinGecko for reliable data.

---

## 💻 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React, Next.js, **Tailwind CSS** |
| **Backend** | **FastAPI**, Python 3.11 |
| **AI Agent** | **LangChain** + Custom Tools |
| **Data Source** | CoinGecko |
| **Charts** | Chart.js |

---

## 🌐 API Endpoints

The backend exposes the following REST endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/crypto_price/{symbol}/{currency}` | Get the current price of a cryptocurrency. |
| `GET` | `/api/crypto_price/{symbol}/{currency}/{date}` | Get the historical price on a specific date (`YYYY-MM-DD`). |
| `GET` | `/api/crypto_price/percentage_change/{symbol}/{currency}` | Get the 24-hour price change summary. |
| `POST` | `/api/crypto_agent` | Send a natural language query (e.g., `"BTC price yesterday"`) to the AI agent. |

---

## 💡 Future Features

* **Relative Date Parsing:** Enhance the AI agent's tool to support more complex relative date strings.
* **Multi-Period Comparison:** Implement percentage change calculation for weekly, monthly, and yearly periods.
* **Live Updates:** Integrate **WebSockets** for real-time price streaming to the dashboard.
