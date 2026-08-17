import type { ChatResponse } from "../../types/chat";

interface ChatDetailsProps {
  response: ChatResponse | null;
}

function ChatDetails({ response }: ChatDetailsProps) {
  if (!response) {
    return null;
  }

  return (
    <aside className="chat-details">
      <h3>Response Details</h3>

      <p>Retrieved chunks: {response.retrieved_chunks.length}</p>

      <p>Memories: {response.memories.length}</p>

      <p>Episodes: {response.episodes.length}</p>

      <p>Procedures: {response.procedures.length}</p>

      <p>Graph facts: {response.graph_facts.length}</p>
    </aside>
  );
}

export default ChatDetails;
