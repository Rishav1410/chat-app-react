import "./ChatHeader.css"

type ChatHeaderProps = {
  name: string;
  isOnline: boolean;
};

export const ChatHeader = ({ name, isOnline }: ChatHeaderProps) => {
  const initial = name.charAt(0).toUpperCase();

  return (
    <header className="chat-header">
      <div className="chat-avatar">{initial}</div>
      <div className="chat-header-info">
        <div className="chat-header-name">{name}</div>
        <div className="chat-header-status">
          {isOnline ? "● Online" : "○ Offline"}
        </div>
      </div>
    </header>
  );
};