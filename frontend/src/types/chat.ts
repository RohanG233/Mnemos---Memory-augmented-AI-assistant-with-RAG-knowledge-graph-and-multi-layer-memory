export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  answer: string;
  retrieved_chunks: unknown[];
  memories: unknown[];
  episodes: unknown[];
  procedures: unknown[];
  graph_facts: unknown[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRoom {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
  updatedAt: number;
}