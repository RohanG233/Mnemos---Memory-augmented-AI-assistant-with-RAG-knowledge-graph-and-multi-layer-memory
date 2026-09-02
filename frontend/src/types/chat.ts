export interface ChatRequest {
  message: string;
  conversation_id: string;
}

export interface ChatResponse {
  answer: string;
  retrieved_chunks: string[];
  memories: string[];
  episodes: string[];
  procedures: string[];
  graph_facts: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRoom {
  /** Local UI identifier (random UUID, not sent to backend) */
  id: string;

  /**
   * Server-assigned conversation ID returned by POST /chat/conversations.
   * This is what the backend expects in ChatRequest.conversation_id.
   * Undefined only for rooms restored from old localStorage data
   * that predate this fix.
   */
  conversationId?: string;

  title: string;
  messages: ChatMessage[];
  createdAt: number;
  updatedAt: number;
}
