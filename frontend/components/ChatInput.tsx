import { useState } from "react";

interface ChatInputProps {
  onSend: (text: string) => void;
  loading?: boolean;
}

export default function ChatInput({ onSend, loading }: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (!text.trim() || loading) return;
    onSend(text.trim());
    setText("");
  };

  return (
    <div className="border-t bg-white px-4 py-3 flex items-center gap-3">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
        placeholder="Ask about BTC, ETH, trends, RSI, price action..."
        className="flex-1 resize-none border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400"
        rows={1}
        disabled={loading}
      />

      <button
        onClick={handleSend}
        disabled={loading}
        className="bg-teal-500 text-white px-4 py-2 rounded-xl text-sm font-medium disabled:opacity-50"
      >
        Send
      </button>
    </div>
  );
}