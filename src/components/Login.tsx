import { useState, type FormEvent } from "react";
import "./Login.css"; // NEW: load the styles
import type { GlobalProps } from "../types";

type LoginProps = {
  onStart: (values: GlobalProps) => void;

};

export const Login = ({ onStart }: LoginProps) => {
  const [name, setName] = useState("");
  const [ipAddress, setIPAddress] = useState("");

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (name.trim() === "" || ipAddress.trim() === "") return;
    const values : GlobalProps = {name : name.trim(), ipAddress : ipAddress.trim()} 
    onStart(values);
  };

  return (
    <div className="login-page"> 
      {/* NEW: wrapper for the whole screen */}
      <form className="login-card" onSubmit={handleSubmit}>
        <h1 className="login-title">Join the chat</h1>
        <input
          className="login-input"
          type="text"
          placeholder="Display name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          className="login-input"
          type="text"
          placeholder="IP Address"
          value={ipAddress}
          onChange={(e) => setIPAddress(e.target.value)}
        />
        <button className="login-button" type="submit">
          Start chatting
        </button>
      </form>
    </div>
  );
};