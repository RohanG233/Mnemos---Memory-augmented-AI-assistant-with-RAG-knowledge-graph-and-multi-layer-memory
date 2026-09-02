function LoadingMessage() {
  return (
    <div className="message-row assistant-row">
      <div className="message-bubble assistant-bubble loading-bubble">
        <div className="message-role">AI</div>
        <div className="loading-dots">
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  );
}

export default LoadingMessage;
