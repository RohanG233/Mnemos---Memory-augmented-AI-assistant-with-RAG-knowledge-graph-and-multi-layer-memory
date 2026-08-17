import type { ChatMessage, ChatResponse } from "../../types/chat";

import MessageList from "./MessageList";
import ChatInput from "./ChatInput";
import ChatDetails from "./ChatDetails";

interface ChatWindowProps {
  messages: ChatMessage[];
  response: ChatResponse | null;
  loading: boolean;
  onSend: (message: string) => void;
}

function ChatWindow({ messages, response, loading, onSend }: ChatWindowProps) {
  return (
    <div className="chat-window">
      <div className="chat-main">
        <MessageList messages={messages} loading={loading} />

        <ChatInput onSend={onSend} loading={loading} />
      </div>

      <ChatDetails response={response} />
    </div>
  );
}

export default ChatWindow;
