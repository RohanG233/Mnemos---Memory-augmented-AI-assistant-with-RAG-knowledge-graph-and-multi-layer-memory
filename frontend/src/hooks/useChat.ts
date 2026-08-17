import { useEffect, useState } from "react";

import { sendMessage } from "../services/chatService";
import {
  getChatRooms,
  saveChatRooms,
} from "../services/chatStorage";

import type {
  ChatMessage,
  ChatResponse,
  ChatRoom,
} from "../types/chat";

function createRoom(): ChatRoom {
  const now = Date.now();

  return {
    id: crypto.randomUUID(),
    title: "New Chat",
    messages: [],
    createdAt: now,
    updatedAt: now,
  };
}

export function useChat() {
  const [rooms, setRooms] = useState<ChatRoom[]>([]);

  const [activeRoomId, setActiveRoomId] =
    useState<string | null>(null);

  const [lastResponse, setLastResponse] =
    useState<ChatResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    const savedRooms = getChatRooms();

    if (savedRooms.length > 0) {
      setRooms(savedRooms);
      setActiveRoomId(savedRooms[0].id);
    } else {
      const room = createRoom();

      setRooms([room]);
      setActiveRoomId(room.id);

      saveChatRooms([room]);
    }
  }, []);

  const activeRoom =
    rooms.find(
      (room) => room.id === activeRoomId
    ) ?? null;

  const messages =
    activeRoom?.messages ?? [];

  function updateRooms(
    updatedRooms: ChatRoom[]
  ) {
    setRooms(updatedRooms);
    saveChatRooms(updatedRooms);
  }

  function createNewRoom() {
    const activeRoom =
        rooms.find(
        (room) => room.id === activeRoomId
        );

    if (
        activeRoom &&
        activeRoom.messages.length === 0
    ) {
        return;
    }

    const room = createRoom();

    const updatedRooms = [
        room,
        ...rooms,
    ];

    updateRooms(updatedRooms);

    setActiveRoomId(room.id);
    setLastResponse(null);
    setError(null);
    }

  function selectRoom(roomId: string) {
    setActiveRoomId(roomId);
    setLastResponse(null);
    setError(null);
  }

  function renameRoom(
    roomId: string,
    newTitle: string
    ) {
    const title = newTitle.trim();

    if (!title) {
        return;
    }

    const updatedRooms = rooms.map((room) =>
        room.id === roomId
        ? {
            ...room,
            title,
            updatedAt: Date.now(),
            }
        : room
    );

    updateRooms(updatedRooms);
    }

    function deleteRoom(roomId: string) {
    const updatedRooms = rooms.filter(
        (room) => room.id !== roomId
    );

    if (updatedRooms.length === 0) {
        const room = createRoom();

        updateRooms([room]);
        setActiveRoomId(room.id);
    } else {
        updateRooms(updatedRooms);

        if (roomId === activeRoomId) {
        setActiveRoomId(updatedRooms[0].id);
        }
    }

    setLastResponse(null);
    setError(null);
    }

  async function send(message: string) {
    if (!message.trim() || loading || !activeRoom) {
      return;
    }

    setError(null);

    const userMessage: ChatMessage = {
      role: "user",
      content: message,
    };

    const updatedAfterUserMessage =
      rooms.map((room) =>
        room.id === activeRoom.id
          ? {
              ...room,
              messages: [
                ...room.messages,
                userMessage,
              ],
              title:
                room.messages.length === 0
                  ? message.slice(0, 40)
                  : room.title,
              updatedAt: Date.now(),
            }
          : room
      );

    updateRooms(
      updatedAfterUserMessage
    );

    setLoading(true);

    try {
      const response =
        await sendMessage(message);

      setLastResponse(response);

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.answer,
      };

      const updatedAfterResponse =
        updatedAfterUserMessage.map(
          (room) =>
            room.id === activeRoom.id
              ? {
                  ...room,
                  messages: [
                    ...room.messages,
                    userMessage,
                    assistantMessage,
                  ],
                  updatedAt: Date.now(),
                }
              : room
        );

      updateRooms(
        updatedAfterResponse
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );

    } finally {
      setLoading(false);
    }
  }

  return {
    rooms,
    activeRoomId,
    messages,
    lastResponse,
    loading,
    error,
    send,
    createNewRoom,
    selectRoom,
    renameRoom,
    deleteRoom,
  };
}