import { useEffect, useRef } from "react";

import type { ChatMessage } from "../../types/chat";

import MessageBubble from "./MessageBubble";
import LoadingMessage from "./LoadingMessage";

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
}

function MessageList({ messages, loading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const previousCountRef = useRef(messages.length);
  const isFirstRenderRef = useRef(true);

  useEffect(() => {
    /*
     * Do nothing when the component initially receives
     * an existing conversation.
     */
    if (isFirstRenderRef.current) {
      isFirstRenderRef.current = false;
      previousCountRef.current = messages.length;
      return;
    }

    /*
     * Only scroll when messages have actually been added.
     */
    if (messages.length > previousCountRef.current) {
      bottomRef.current?.scrollIntoView({
        behavior: "smooth",
      });
    }

    previousCountRef.current = messages.length;
  }, [messages.length]);

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
        <MessageBubble key={`${message.role}-${index}`} message={message} />
      ))}

      {loading && <LoadingMessage />}

      <div ref={bottomRef} />
    </div>
  );
}

export default MessageList;
