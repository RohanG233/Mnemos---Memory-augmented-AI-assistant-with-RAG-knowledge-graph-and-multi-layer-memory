import type { ChatRoom } from "../types/chat";

const STORAGE_KEY = "mnemos_chat_rooms";

export function getChatRooms(): ChatRoom[] {
  const stored = localStorage.getItem(STORAGE_KEY);

  if (!stored) {
    return [];
  }

  try {
    const rooms = JSON.parse(stored) as ChatRoom[];

    // Filter out legacy rooms that have no conversationId —
    // they cannot be used for new messages and would confuse the UI.
    // The hook will create a fresh room with a proper conversationId.
    return rooms.filter((r) => r.conversationId);

  } catch {
    return [];
  }
}

export function saveChatRooms(rooms: ChatRoom[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(rooms));
}
