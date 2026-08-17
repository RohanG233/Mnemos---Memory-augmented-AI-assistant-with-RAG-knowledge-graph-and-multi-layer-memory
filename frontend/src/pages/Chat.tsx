import { useChat } from "../hooks/useChat";

import ChatSidebar from "../components/chat/ChatSidebar";
import ChatWindow from "../components/chat/ChatWindow";

function Chat() {
  const {
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
  } = useChat();

  return (
    <main className="chat-page">
      <h1>ACAI</h1>

      <div className="chat-container">
        <ChatSidebar
          rooms={rooms}
          activeRoomId={activeRoomId}
          onNewChat={createNewRoom}
          onSelectRoom={selectRoom}
          onRenameRoom={renameRoom}
          onDeleteRoom={deleteRoom}
        />

        <div className="chat-content">
          <ChatWindow
            messages={messages}
            response={null}
            loading={loading}
            onSend={send}
          />

          {error && <p>{error}</p>}
        </div>
      </div>
    </main>
  );
}

export default Chat;
