import type { Message } from "../types";
import { MessageBubble } from "./MessageBubble";
import "./ChatArena.css";

type ChatArenaProps = {
  messages: Message[];
  currentUser: string;
};

export const ChatArena = ({ messages, currentUser }: ChatArenaProps) => {
  return (
    <div className="chat-arena">
      {messages.length === 0 ? (
        <div className="chat-arena-empty">No messages yet. Say a Hii !!!</div>
      ) : (
        messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isMine={message.sender === currentUser}
          />
        ))
      )}
    </div>
  );
};