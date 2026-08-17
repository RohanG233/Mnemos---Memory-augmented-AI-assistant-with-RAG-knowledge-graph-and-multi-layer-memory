import type { ChatMessage } from "../../types/chat";

interface MessageBubbleProps {
  message: ChatMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      <div
        className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}
      >
        <div className="message-role">{isUser ? "You" : "AI"}</div>
        <div className="message-content">{message.content}</div>
      </div>
    </div>
  );
}

export default MessageBubble;
