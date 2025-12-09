"use client";

import { useState } from "react";
import AgentMessage from "../../components/AgentMessage";

export default function AgentsPage() {
  const [messages, setMessages] = useState([
    { from: "agent", text: "Hello! I’m your crypto trading assistant. How can I help?" }
  ]);

  const [input, setInput] = useState("");

async function sendMessage() {
  if (!input.trim()) return;

  const userMsg = { from: "user", text: input };
  setMessages((m) => [...m, userMsg]);

  const messageToSend = input;
  setInput("");

  try {
    const res = await fetch("http://localhost:8000/api/crypto_agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: messageToSend }),
    });

    const data = await res.json();

    const agentMsg = { from: "agent", text: data.result };
    setMessages((m) => [...m, agentMsg]);
  } catch (err) {
    const errorMsg = { from: "agent", text: "Error: Could not reach backend." };
    setMessages((m) => [...m, errorMsg]);
    console.error(err);
  }
}

  return (
    <div className="flex flex-col h-full max-h-[80vh]">

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-white rounded-2xl shadow-sm">
        {messages.map((m, i) => (
          <AgentMessage key={i} from={m.from as any} text={m.text} />
        ))}
      </div>

      {/* Input Area */}
      <div className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          className="flex-1 p-3 rounded-xl border border-gray-300 focus:outline-none"
          placeholder="Ask your crypto agent..."
        />
        <button
          onClick={sendMessage}
          className="px-6 py-3 bg-blue-600 text-white rounded-xl shadow-sm"
        >
          Send
        </button>
      </div>

    </div>
  );
}