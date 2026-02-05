import { useEffect, useRef } from "react";
import AgentMessage from "./AgentMessage";

interface Message {
  from: "user" | "agent";
  text: string;
}

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4 bg-gray-50">
      {messages.length === 0 && (
        <div className="text-center text-gray-400 mt-20 text-sm">
          Ask CryptoSprite about BTC, ETH, trends, indicators, or price action.
        </div>
      )}

      {messages.map((msg, i) => (
        <AgentMessage key={i} from={msg.from} text={msg.text} />
      ))}

      <div ref={bottomRef} />
    </div>
  );
}