import ReactMarkdown from "react-markdown";
import type { ChatMessage } from "../../types/chat";

interface MessageBubbleProps {
  message: ChatMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      <div className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}>

        <div className="message-role">
          {isUser ? "You" : "ACAI"}
        </div>

        {isUser ? (
          /* User messages are always plain text — no Markdown parsing */
          <div className="message-content">{message.content}</div>
        ) : (
          /* Assistant messages are rendered as Markdown */
          <div className="message-content md-content">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

      </div>
    </div>
  );
}

export default MessageBubble;
