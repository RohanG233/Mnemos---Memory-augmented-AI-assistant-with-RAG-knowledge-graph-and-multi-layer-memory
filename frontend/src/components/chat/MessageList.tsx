import { useEffect, useRef } from "react";
import type { ChatMessage } from "../../types/chat";
import MessageBubble from "./MessageBubble";
import LoadingMessage from "./LoadingMessage";

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
  onHintClick?: (hint: string) => void;
}

const HINTS = [
  "Summarise my documents",
  "What do you remember about me?",
  "What topics are in my knowledge graph?",
  "Help me brainstorm ideas",
];

function MessageList({ messages, loading, onHintClick }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const prevCountRef = useRef(messages.length);
  const firstRenderRef = useRef(true);

  useEffect(() => {
    if (firstRenderRef.current) {
      firstRenderRef.current = false;
      prevCountRef.current = messages.length;
      return;
    }
    if (messages.length > prevCountRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
    prevCountRef.current = messages.length;
  }, [messages.length]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="empty-chat">
        <div className="empty-chat-icon">✦</div>
        <h2>How can I help you?</h2>
        <p>
          Ask anything — I can search your documents, recall memories,
          and reason over your knowledge graph.
        </p>
        {onHintClick && (
          <div className="empty-chat-hints">
            {HINTS.map((hint) => (
              <button
                key={hint}
                type="button"
                className="empty-chat-hint"
                onClick={() => onHintClick(hint)}
              >
                {hint}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((msg, i) => (
        <MessageBubble key={`${msg.role}-${i}`} message={msg} />
      ))}
      {loading && <LoadingMessage />}
      <div ref={bottomRef} />
    </div>
  );
}

export default MessageList;
