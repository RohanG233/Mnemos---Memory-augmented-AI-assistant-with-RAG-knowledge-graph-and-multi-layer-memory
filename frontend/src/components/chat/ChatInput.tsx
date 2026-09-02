import { useEffect, useRef, useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  loading: boolean;
  initialValue?: string;
  onInitialValueConsumed?: () => void;
}

function ChatInput({ onSend, loading, initialValue, onInitialValueConsumed }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Pre-fill from hint chip
  useEffect(() => {
    if (initialValue !== undefined && initialValue !== "") {
      setMessage(initialValue);
      textareaRef.current?.focus();
      onInitialValueConsumed?.();
    }
  }, [initialValue, onInitialValueConsumed]);

  // Auto-resize
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  }, [message]);

  function submit() {
    const trimmed = message.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setMessage("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  return (
    <form className="chat-input-container" onSubmit={(e) => { e.preventDefault(); submit(); }}>
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
        }}
        placeholder="Ask something… (Enter to send, Shift+Enter for new line)"
        disabled={loading}
        rows={1}
        aria-label="Chat message"
      />
      <button
        type="submit"
        className="send-button"
        disabled={loading || !message.trim()}
        aria-label="Send message"
      >
        {loading ? (
          <>
            <span
              className="loading-spinner"
              style={{ width: 14, height: 14, borderWidth: 2, marginRight: 2 }}
            />
            Thinking
          </>
        ) : (
          "Send ↑"
        )}
      </button>
    </form>
  );
}

export default ChatInput;
