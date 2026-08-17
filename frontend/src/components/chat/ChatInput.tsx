import { useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  loading: boolean;
}

function ChatInput({ onSend, loading }: ChatInputProps) {
  const [message, setMessage] = useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    if (!message.trim() || loading) {
      return;
    }

    onSend(message.trim());
    setMessage("");
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      if (!message.trim() || loading) {
        return;
      }

      onSend(message.trim());
      setMessage("");
    }
  }

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <textarea
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask something..."
        disabled={loading}
        rows={1}
      />

      <button type="submit" disabled={loading || !message.trim()}>
        {loading ? "Sending..." : "Send"}
      </button>
    </form>
  );
}

export default ChatInput;
