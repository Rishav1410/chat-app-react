import { useState } from "react";
import type { Message } from "../types";
import { ChatHeader } from "./ChatHeader";
import { ChatArena } from "./ChatArena";
import { MessageInput } from "./MessageInput";
import "./ChatScreen.css";

type ChatScreenProps = {
  userName: string;
  ipAddress : string
};

export const ChatScreen = ({ userName, ipAddress }: ChatScreenProps) => {
  const [messages, setMessages] = useState<Message[]>([
    //{ id: 1, sender: "Alex", text: "Hey! How are you?", time: "10:42" },
  ]);

  

  const handleSend = (text: string) => {
    const newMessage: Message = {
      id: Date.now(),
      sender: userName,
      text: text,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages([...messages, newMessage]);
  };

  return (
    <div className="chat-screen">
      <ChatHeader name= {ipAddress} isOnline={true} />
      <ChatArena messages={messages} currentUser={userName} />
      <MessageInput onSend={handleSend} />
    </div>
  );
};