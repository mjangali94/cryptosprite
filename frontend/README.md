# CryptoSprite Frontend

This is the frontend application for **CryptoSprite**, an AI-powered cryptocurrency market analysis agent.

The UI is intentionally minimal and focused: a single **chat interface** for interacting with the CryptoSprite agent — no dashboards, no charts, no manual controls.


## Tech Stack

- Next.js (App Router)
- TypeScript
- Tailwind CSS
- Fetch-based API client
- Agent-driven UX

---

## Getting Started

Install dependencies:

```bash
npm install
```

or
```bash
yarn
```

or

```bash
pnpm install
```


Run the development server:

```bash
npm run dev
```

or

```bash
yarn dev
```

or

```bash
pnpm dev
```

Open the app in your browser:

http://localhost:3000



## Project Structure

src/
├── app/
│   └── page.tsx
├── components/
│   ├── Header.tsx
│   ├── AgentMessage.tsx
│   ├── MessageList.tsx
│   ├── ChatInput.tsx
│   └── TypingIndicator.tsx
├── hooks/
│   └── useChat.ts
└── api/
    └── chat.ts



## How It Works

1. The user types a message into the chat input
2. The message is sent to the backend CryptoSprite agent
3. The agent:
   - Detects intent
   - Selects tools (price, volume, indicators, price action)
   - Runs a structured analysis
4. The final response is returned as natural language
5. The UI renders the response as a chat message

The frontend does **not** control logic — the agent does.



## Backend Dependency

This frontend expects the CryptoSprite backend to be running.

Endpoint:

```bash
POST /api/crypto_agent
```

Request body example:

```bash
{
  "query": "Analyze BTC using price action and technical indicators"
}
```

Response example:

```bash
{
  "result": "Full market analysis text..."
}
```


## Customization

You can customize behavior and appearance here:

- components/AgentMessage.tsx  
  Controls chat bubble styling

- components/Header.tsx  
  App title and header layout

- components/ChatInput.tsx  
  Input UX and submit behavior

- hooks/useChat.ts  
  Chat state management and API calls


## Design Philosophy

CryptoSprite follows an **agent-first** design:

- No buttons
- No toggles
- No manual indicators
- No opinionated UI logic

The agent decides everything.

The UI simply listens.



## Status

CryptoSprite Frontend v1.0  
Production-ready minimal chat interface
