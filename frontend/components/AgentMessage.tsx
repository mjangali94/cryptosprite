interface AgentMessageProps {
  from: "user" | "agent";
  text: string;
}

export default function AgentMessage({ from, text }: AgentMessageProps) {
  const isUser = from === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} my-2`}>
      <div
        className={`max-w-[70%] px-5 py-3 rounded-2xl shadow-md text-sm font-sans break-words
        ${isUser ? "bg-blue-600 text-white rounded-br-none" : "bg-gray-200 text-gray-900 rounded-bl-none"}`}
      >
        {text}
      </div>
    </div>
  );
}