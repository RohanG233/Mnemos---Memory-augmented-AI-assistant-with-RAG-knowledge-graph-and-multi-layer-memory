import { useEffect, useRef, useState } from "react";

import { useAuth } from "../context/AuthContext";

import {
  sendMessage,
  createConversation,
  listConversations,
  getConversationMessages,
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

  // True once the server-side conversation list has been loaded
  const [loadComplete, setLoadComplete] = useState(false);
  const initialised = useRef(false);


  // --------------------------------
  // Load conversations from MongoDB
  // and merge with localStorage cache
  // --------------------------------
  //
  // Source of truth for which conversations EXIST:  MongoDB
  // Source of truth for message content:            localStorage
  //
  // On every mount (page load / navigate to /chat):
  //   1. Fetch the user's conversations from the server
  //   2. Load any cached rooms from localStorage
  //   3. For each server conversation, find the matching local room
  //      and carry over its messages — they are the only copy of
  //      message content (messages are stored to MongoDB too, but
  //      we don't re-fetch them on mount to keep it fast)
  //   4. Discard local rooms whose conversationId no longer exists
  //      on the server (deleted from another device / DB reset)
  //   5. If the server has conversations but none are in localStorage,
  //      show them as empty rooms — user can still send new messages
  //   6. Save the merged result back to localStorage

  useEffect(() => {
    if (initialised.current || !accessToken) return;
    initialised.current = true;

    async function loadFromServer() {
      try {
        const { conversations } = await listConversations(accessToken);

        if (!conversations || conversations.length === 0) {
          setLoadComplete(true);
          return;
        }

        // Load whatever message cache we have locally
        const localRooms = getChatRooms();
        const localByConvId = new Map(
          localRooms
            .filter((r) => r.conversationId)
            .map((r) => [r.conversationId!, r])
        );

        // Fetch messages for every conversation in parallel.
        // Use local cache if available (avoids a network round-trip),
        // fall back to server if the cache is empty or missing.
        const merged: ChatRoom[] = await Promise.all(
          conversations.map(async (conv) => {
            const local = localByConvId.get(conv.conversation_id);

            // If we already have messages cached locally, use them
            const cachedMessages = local?.messages ?? [];

            let messages = cachedMessages;

            // Only fetch from server if the local cache has no messages
            if (cachedMessages.length === 0) {
              try {
                const serverMessages = await getConversationMessages(
                  conv.conversation_id,
                  accessToken
                );
                // Map server messages to the ChatMessage shape
                messages = serverMessages.map((m) => ({
                  role: m.role,
                  content: m.content,
                }));
              } catch {
                // Network error — just show empty messages
                messages = [];
              }
            }

            return {
              id: local?.id ?? crypto.randomUUID(),
              conversationId: conv.conversation_id,
              title: local?.title ?? conv.title ?? "New Chat",
              messages,
              createdAt: local?.createdAt ?? Date.parse(conv.created_at),
              updatedAt: local?.updatedAt ?? Date.parse(conv.updated_at),
            };
          })
        );

        saveChatRooms(merged);
        setRooms(merged);
        setActiveRoomId(merged[0].id);

      } catch {
        // Server unreachable — fall back to localStorage
        const local = getChatRooms();
        if (local.length > 0) {
          setRooms(local);
          setActiveRoomId(local[0].id);
        }
      } finally {
        setLoadComplete(true);
      }
    }

    loadFromServer();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken]);


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
  // Auto-create first room only if
  // server returned zero conversations
  // --------------------------------

  useEffect(() => {
    if (!loadComplete || !accessToken) return;
    if (rooms.length === 0) {
      createNewRoom();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadComplete, accessToken]);


  // --------------------------------
  // Repair a stale conversationId
  // --------------------------------

  async function repairRoom(
    roomId: string,
    token: string,
  ): Promise<string | null> {
    try {
      const created = await createConversation(token);
      const newConversationId = created.conversation_id;

      setRooms((current) => {
        const patched = current.map((r) =>
          r.id === roomId
            ? { ...r, conversationId: newConversationId, updatedAt: Date.now() }
            : r
        );
        saveChatRooms(patched);
        return patched;
      });

      return newConversationId;
    } catch {
      return null;
    }
  }


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
  // Send message — public entry point
  // --------------------------------

  async function send(userInput: string) {
    if (!userInput.trim() || loading) return;

    if (!activeRoom) {
      setError("No active chat selected.");
      return;
    }

    if (!accessToken) {
      setError("You are not authenticated.");
      return;
    }

    if (!activeRoom.conversationId) {
      const newId = await repairRoom(activeRoom.id, accessToken);
      if (!newId) {
        setError("Could not create a conversation. Please try again.");
        return;
      }
      await _send(userInput, newId, activeRoom.id);
      return;
    }

    await _send(userInput, activeRoom.conversationId, activeRoom.id);
  }


  // --------------------------------
  // _send — internal
  // --------------------------------

  async function _send(
    userInput: string,
    conversationId: string,
    roomId: string,
    isRetry = false,
  ): Promise<void> {
    if (!accessToken) return;

    setError(null);

    const userMessage: ChatMessage = { role: "user", content: userInput };

    setLoading(true);

    // Compute autoTitle BEFORE the setRooms call so the closure
    // captures it correctly. Read messages.length from the live
    // current state via a separate setRooms-style read to avoid
    // stale closure — we capture from rooms here which is fine
    // for a pre-flight check (worst case title doesn't update,
    // which is non-critical). The real guard is inside setRooms.
    const preMessages = rooms.find((r) => r.id === roomId)?.messages ?? [];
    const isFirstMessage = preMessages.length === 0;
    const autoTitle = isFirstMessage ? userInput.slice(0, 40) : null;

    let snapshot: ChatRoom[] = [];

    setRooms((current) => {
      snapshot = current.map((r) =>
        r.id === roomId
          ? {
              ...r,
              messages: [...r.messages, userMessage],
              // Use current (live) messages for the first-message check
              title: r.messages.length === 0 ? (autoTitle ?? r.title) : r.title,
              updatedAt: Date.now(),
            }
          : r
      );
      saveChatRooms(snapshot);
      return snapshot;
    });

    try {
      const response = await sendMessage(userInput, conversationId, accessToken);

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.answer,
      };

      setRooms((current) => {
        const updated = current.map((r) =>
          r.id === roomId
            ? {
                ...r,
                messages: [...r.messages, assistantMessage],
                updatedAt: Date.now(),
              }
            : r
        );
        saveChatRooms(updated);
        return updated;
      });

      // Sync the auto-generated title to MongoDB so it persists
      // across browsers and devices
      if (autoTitle && accessToken) {
        renameConversation(conversationId, autoTitle, accessToken).catch(
          () => {} // non-critical — title can be wrong, conversation still works
        );
      }

    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";

      const isStaleId =
        msg.includes("Conversation not found") ||
        msg.includes("does not belong") ||
        msg.includes("404");

      if (isStaleId && !isRetry) {
        setRooms((current) => {
          const restored = current.map((r) =>
            r.id === roomId
              ? { ...r, messages: r.messages.slice(0, -1) }
              : r
          );
          saveChatRooms(restored);
          return restored;
        });

        setLoading(false);

        const newId = await repairRoom(roomId, accessToken);
        if (newId) {
          await _send(userInput, newId, roomId, true);
          return;
        }
        setError("Could not connect to this conversation. Please create a new chat.");
        return;
      }

      setError(msg);
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
