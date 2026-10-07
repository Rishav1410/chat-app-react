import { useState, type FormEvent } from "react";
import "./MessageInput.css";

type MessageInputProps = {
  onSend: (text: string) => void;
};

export const MessageInput = ({ onSend }: MessageInputProps) => {
  const [text, setText] = useState("");

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (trimmed === "") return;
    onSend(trimmed);
    setText("");
  };

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <input
        className="message-input-box"
        type="text"
        placeholder="Type a message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        className="message-input-send"
        type="submit"
        disabled={text.trim() === ""}
      >
        Send
      </button>
    </form>
  );
};