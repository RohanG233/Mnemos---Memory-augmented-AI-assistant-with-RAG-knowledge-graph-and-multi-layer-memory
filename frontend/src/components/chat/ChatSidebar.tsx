import { useState } from "react";

import type { ChatRoom } from "../../types/chat";

interface ChatSidebarProps {
  rooms: ChatRoom[];
  activeRoomId: string | null;
  onNewChat: () => void;
  onSelectRoom: (roomId: string) => void;
  onRenameRoom: (roomId: string, newTitle: string) => void;
  onDeleteRoom: (roomId: string) => void;
}

function ChatSidebar({
  rooms,
  activeRoomId,
  onNewChat,
  onSelectRoom,
  onRenameRoom,
  onDeleteRoom,
}: ChatSidebarProps) {
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [roomToDelete, setRoomToDelete] = useState<ChatRoom | null>(null);
  const [roomToRename, setRoomToRename] = useState<ChatRoom | null>(null);
  const [renameValue, setRenameValue] = useState("");

  function handleRenameClick(room: ChatRoom) {
    setOpenMenuId(null);
    setRoomToRename(room);
    setRenameValue(room.title);
  }

  function confirmRename() {
    if (!roomToRename) {
      return;
    }

    const title = renameValue.trim();

    if (!title) {
      return;
    }

    onRenameRoom(roomToRename.id, title);

    setRoomToRename(null);
    setRenameValue("");
  }

  function cancelRename() {
    setRoomToRename(null);
    setRenameValue("");
  }

  function handleDeleteClick(room: ChatRoom) {
    setOpenMenuId(null);
    setRoomToDelete(room);
  }

  function confirmDelete() {
    if (!roomToDelete) {
      return;
    }

    onDeleteRoom(roomToDelete.id);
    setRoomToDelete(null);
  }

  function cancelDelete() {
    setRoomToDelete(null);
  }

  return (
    <>
      <aside className="chat-sidebar">
        <button type="button" className="new-chat-button" onClick={onNewChat}>
          + New Chat
        </button>

        <div className="chat-room-list">
          {rooms.map((room) => (
            <div
              key={room.id}
              className={
                room.id === activeRoomId
                  ? "chat-room-wrapper active"
                  : "chat-room-wrapper"
              }
            >
              <button
                type="button"
                className="chat-room"
                onClick={() => onSelectRoom(room.id)}
              >
                {room.title}
              </button>

              <div className="chat-room-menu-container">
                <button
                  type="button"
                  className="chat-room-menu-button"
                  onClick={(event) => {
                    event.stopPropagation();

                    setOpenMenuId(openMenuId === room.id ? null : room.id);
                  }}
                >
                  ⋯
                </button>

                {openMenuId === room.id && (
                  <div className="chat-room-menu">
                    <button
                      type="button"
                      onClick={() => handleRenameClick(room)}
                    >
                      Rename
                    </button>

                    <button
                      type="button"
                      onClick={() => handleDeleteClick(room)}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </aside>

      {roomToDelete && (
        <div className="delete-modal-overlay" onClick={cancelDelete}>
          <div
            className="delete-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <h2>Delete chat?</h2>

            <p>
              Are you sure you want to delete{" "}
              <strong>"{roomToDelete.title}"</strong>?
            </p>

            <div className="delete-modal-actions">
              <button
                type="button"
                className="cancel-delete-button"
                onClick={cancelDelete}
              >
                Cancel
              </button>

              <button
                type="button"
                className="confirm-delete-button"
                onClick={confirmDelete}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {roomToRename && (
        <div className="rename-modal-overlay" onClick={cancelRename}>
          <div
            className="rename-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <h2>Rename chat</h2>

            <input
              type="text"
              value={renameValue}
              onChange={(event) => setRenameValue(event.target.value)}
              autoFocus
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  confirmRename();
                }

                if (event.key === "Escape") {
                  cancelRename();
                }
              }}
            />

            <div className="rename-modal-actions">
              <button
                type="button"
                className="cancel-rename-button"
                onClick={cancelRename}
              >
                Cancel
              </button>

              <button
                type="button"
                className="confirm-rename-button"
                onClick={confirmRename}
                disabled={!renameValue.trim()}
              >
                Rename
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ChatSidebar;
