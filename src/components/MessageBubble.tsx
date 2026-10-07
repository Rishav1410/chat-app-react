import type { Message } from "../types";
import "./MessageBubble.css"

type MessageBubbleProps = {
  message: Message;
  isMine: boolean;
};

export const MessageBubble = ({ message, isMine }: MessageBubbleProps) => {
  return (
      <div className={`bubble bubble-${isMine}`}>
        {!isMine && <div className="bubble-sender">{message.sender}</div>}
        <div className="bubble-text">{message.text}</div>
        <div className="bubble-time">{message.time}</div>
      </div>
    
  );
};