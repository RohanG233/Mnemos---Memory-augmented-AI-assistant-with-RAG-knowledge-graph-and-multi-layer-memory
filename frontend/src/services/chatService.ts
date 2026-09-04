import type { ChatRequest, ChatResponse } from "../types/chat";
import { apiFetch } from "./api";


// --------------------------------
// Create Conversation
// --------------------------------

export interface ConversationCreated {
  conversation_id: string;
  title: string;
  created_at: string;
}

export async function createConversation(
  accessToken: string | null
): Promise<ConversationCreated> {

  const response = await apiFetch(
    "/chat/conversations",
    { method: "POST" },
    accessToken
  );

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail ?? `Failed to create conversation: ${response.status}`
    );
  }

  return response.json();
}


// --------------------------------
// List Conversations
// --------------------------------

export async function listConversations(
  accessToken: string | null
): Promise<{ conversations: ConversationMeta[] }> {

  const response = await apiFetch(
    "/chat/conversations",
    { method: "GET" },
    accessToken
  );

  if (!response.ok) {
    throw new Error(`Failed to list conversations: ${response.status}`);
  }

  return response.json();
}

export interface ConversationMeta {
  conversation_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}


// --------------------------------
// Rename Conversation
// --------------------------------

export async function renameConversation(
  conversationId: string,
  title: string,
  accessToken: string | null
): Promise<void> {

  const response = await apiFetch(
    `/chat/conversations/${conversationId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    },
    accessToken
  );

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail ?? `Failed to rename conversation: ${response.status}`
    );
  }
}


// --------------------------------
// Delete Conversation
// --------------------------------

export async function deleteConversation(
  conversationId: string,
  accessToken: string | null
): Promise<void> {

  const response = await apiFetch(
    `/chat/conversations/${conversationId}`,
    { method: "DELETE" },
    accessToken
  );

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail ?? `Failed to delete conversation: ${response.status}`
    );
  }
}


// --------------------------------
// Send Message
// --------------------------------

export async function sendMessage(
  message: string,
  conversationId: string,
  accessToken: string | null
): Promise<ChatResponse> {

  const request: ChatRequest = {
    message,
    conversation_id: conversationId,
  };

  const response = await apiFetch(
    "/chat",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
    accessToken
  );

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail ?? `Chat request failed: ${response.status}`
    );
  }

  return response.json();
}


// --------------------------------
// Get Messages for a Conversation
// --------------------------------

export interface ServerMessage {
  role: "user" | "assistant";
  content: string;
}

export async function getConversationMessages(
  conversationId: string,
  accessToken: string | null
): Promise<ServerMessage[]> {

  const response = await apiFetch(
    `/chat/conversations/${conversationId}/messages`,
    { method: "GET" },
    accessToken
  );

  if (!response.ok) {
    throw new Error(`Failed to load messages: ${response.status}`);
  }

  const data = await response.json();
  return data.messages ?? [];
}
