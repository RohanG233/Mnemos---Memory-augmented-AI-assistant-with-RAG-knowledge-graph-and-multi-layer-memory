import type { ChatRoom } from "../types/chat";

const STORAGE_KEY = "acai_chat_rooms";

export function getChatRooms(): ChatRoom[] {
  const stored = localStorage.getItem(STORAGE_KEY);

  if (!stored) {
    return [];
  }

  try {
    return JSON.parse(stored) as ChatRoom[];
  } catch {
    return [];
  }
}

export function saveChatRooms(rooms: ChatRoom[]): void {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(rooms)
  );
}