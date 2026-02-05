import Header from "../components/Header";
import MessageList from "../components/MessageList";
import ChatInput from "../components/ChatInput";
import TypingIndicator from "../components/TypingIndicator";
import { useChat } from "../hooks/useChat";

export default function Home() {
  const { messages, sendMessage, loading } = useChat();

  return (
    <div className="h-screen flex flex-col">
      <Header />

      <MessageList messages={messages} />

      {loading && <TypingIndicator />}

      <ChatInput onSend={sendMessage} loading={loading} />
    </div>
  );
}