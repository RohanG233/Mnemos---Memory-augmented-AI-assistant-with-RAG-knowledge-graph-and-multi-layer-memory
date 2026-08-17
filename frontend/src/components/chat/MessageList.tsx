import type { ChatMessage } from "../../types/chat";
import MessageBubble from "./MessageBubble";
import LoadingMessage from "./LoadingMessage";
import { useEffect, useRef } from "react";

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
}

function MessageList({ messages, loading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="empty-chat">
        <h2>How can I help you?</h2>
        <p>Ask a question about your uploaded documents.</p>
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <MessageBubble key={index} message={message} />
      ))}

      {loading && <LoadingMessage />}

      <div ref={bottomRef} />
    </div>
  );
}

export default MessageList;
