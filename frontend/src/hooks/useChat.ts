import { useEffect, useRef, useState } from "react";

import { useAuth } from "../context/AuthContext";

import {
  sendMessage,
  createConversation,
  renameConversation,
  deleteConversation,
} from "../services/chatService";

import {
  getChatRooms,
  saveChatRooms,
} from "../services/chatStorage";

import type { ChatMessage, ChatRoom } from "../types/chat";


export function useChat() {

  const { accessToken } = useAuth();

  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [activeRoomId, setActiveRoomId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // True once the initial localStorage load has completed.
  // The auto-create effect must not fire before this is true.
  const [loadComplete, setLoadComplete] = useState(false);

  // Prevent double-init in React StrictMode
  const initialised = useRef(false);


  // --------------------------------
  // Load rooms from localStorage once
  // --------------------------------

  useEffect(() => {
    if (initialised.current) return;
    initialised.current = true;

    const saved = getChatRooms();

    if (saved.length > 0) {
      setRooms(saved);
      setActiveRoomId(saved[0].id);
    }

    // Signal that the load phase is done regardless of whether
    // rooms were found — the auto-create effect waits for this.
    setLoadComplete(true);
  }, []);


  // --------------------------------
  // Helpers
  // --------------------------------

  const activeRoom = rooms.find((r) => r.id === activeRoomId) ?? null;
  const messages = activeRoom?.messages ?? [];

  function updateRooms(updated: ChatRoom[]) {
    setRooms(updated);
    saveChatRooms(updated);
  }


  // --------------------------------
  // Create a new room
  // --------------------------------

  async function createNewRoom() {
    // Don't create another empty room if the active one is already empty
    if (activeRoom && activeRoom.messages.length === 0) {
      return;
    }

    if (!accessToken) {
      setError("You are not authenticated.");
      return;
    }

    try {
      const created = await createConversation(accessToken);

      const now = Date.now();

      const room: ChatRoom = {
        id: crypto.randomUUID(),
        conversationId: created.conversation_id,
        title: "New Chat",
        messages: [],
        createdAt: now,
        updatedAt: now,
      };

      // Read current rooms from the setter callback to avoid
      // capturing a stale closure value.
      setRooms((current) => {
        const updated = [room, ...current];
        saveChatRooms(updated);
        return updated;
      });

      setActiveRoomId(room.id);
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create new chat."
      );
    }
  }


  // --------------------------------
  // Auto-create the first room only
  // after localStorage load is done
  // AND only if no rooms were found
  // --------------------------------

  useEffect(() => {
    // Wait until both conditions are true before deciding to create:
    //   1. The localStorage read has completed (loadComplete)
    //   2. We have an access token to call the backend
    if (!loadComplete || !accessToken) return;

    if (rooms.length === 0) {
      createNewRoom();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadComplete, accessToken]);


  // --------------------------------
  // Select room
  // --------------------------------

  function selectRoom(roomId: string) {
    setActiveRoomId(roomId);
    setError(null);
  }


  // --------------------------------
  // Rename room
  // --------------------------------

  async function renameRoom(roomId: string, newTitle: string) {
    const title = newTitle.trim();
    if (!title) return;

    const room = rooms.find((r) => r.id === roomId);

    const updated = rooms.map((r) =>
      r.id === roomId ? { ...r, title, updatedAt: Date.now() } : r
    );
    updateRooms(updated);

    if (room?.conversationId && accessToken) {
      try {
        await renameConversation(room.conversationId, title, accessToken);
      } catch (err) {
        console.warn("Failed to sync rename to backend:", err);
      }
    }
  }


  // --------------------------------
  // Delete room
  // --------------------------------

  async function deleteRoom(roomId: string) {
    const room = rooms.find((r) => r.id === roomId);

    const updated = rooms.filter((r) => r.id !== roomId);

    if (updated.length === 0) {
      updateRooms([]);
      setActiveRoomId(null);
      setError(null);
      if (accessToken) {
        createNewRoom();
      }
    } else {
      updateRooms(updated);
      if (roomId === activeRoomId) {
        setActiveRoomId(updated[0].id);
      }
    }

    setError(null);

    if (room?.conversationId && accessToken) {
      try {
        await deleteConversation(room.conversationId, accessToken);
      } catch (err) {
        console.warn("Failed to sync delete to backend:", err);
      }
    }
  }


  // --------------------------------
  // Send message
  // --------------------------------

  async function send(message: string) {
    if (!message.trim() || loading) return;

    if (!activeRoom) {
      setError("No active chat selected.");
      return;
    }

    if (!activeRoom.conversationId) {
      setError(
        "This chat has no server conversation ID. Please create a new chat."
      );
      return;
    }

    if (!accessToken) {
      setError("You are not authenticated.");
      return;
    }

    setError(null);

    const userMessage: ChatMessage = { role: "user", content: message };

    const afterUser = rooms.map((r) =>
      r.id === activeRoom.id
        ? {
            ...r,
            messages: [...r.messages, userMessage],
            title:
              r.messages.length === 0
                ? message.slice(0, 40)
                : r.title,
            updatedAt: Date.now(),
          }
        : r
    );

    updateRooms(afterUser);
    setLoading(true);

    try {
      const response = await sendMessage(
        message,
        activeRoom.conversationId,
        accessToken
      );

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.answer,
      };

      const afterAssistant = afterUser.map((r) =>
        r.id === activeRoom.id
          ? {
              ...r,
              messages: [...r.messages, assistantMessage],
              updatedAt: Date.now(),
            }
          : r
      );

      updateRooms(afterAssistant);

    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }


  return {
    rooms,
    activeRoomId,
    messages,
    loading,
    error,
    send,
    createNewRoom,
    selectRoom,
    renameRoom,
    deleteRoom,
  };
}
