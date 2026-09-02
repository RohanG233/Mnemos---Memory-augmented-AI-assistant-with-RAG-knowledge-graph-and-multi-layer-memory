import { useState } from "react";
import type { ChatMessage } from "../../types/chat";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

interface ChatWindowProps {
  messages: ChatMessage[];
  loading: boolean;
  onSend: (message: string) => void;
}

function ChatWindow({ messages, loading, onSend }: ChatWindowProps) {
  // Hint chips pre-fill the input — we lift a "pending hint" state
  // and clear it once the user edits or submits
  const [pendingHint, setPendingHint] = useState<string | null>(null);

  function handleHintClick(hint: string) {
    setPendingHint(hint);
  }

  function handleSend(message: string) {
    setPendingHint(null);
    onSend(message);
  }

  return (
    <div className="chat-window">
      <div className="chat-main">
        <MessageList
          messages={messages}
          loading={loading}
          onHintClick={handleHintClick}
        />
        <ChatInput
          onSend={handleSend}
          loading={loading}
          initialValue={pendingHint ?? undefined}
          onInitialValueConsumed={() => setPendingHint(null)}
        />
      </div>
    </div>
  );
}

export default ChatWindow;
