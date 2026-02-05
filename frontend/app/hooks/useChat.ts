import { useState } from "react";
import { sendPrompt } from "../api/chat";

interface Message {
  from: "user" | "agent";
  text: string;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text: string) => {
    setMessages((prev) => [...prev, { from: "user", text }]);
    setLoading(true);

    try {
      const reply = await sendPrompt(text);
      setMessages((prev) => [...prev, { from: "agent", text: reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          from: "agent",
          text: "⚠️ Something went wrong while analyzing the market.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return { messages, sendMessage, loading };
}