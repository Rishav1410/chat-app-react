import { useState } from "react";
import { Login } from "./components/Login";
import { ChatScreen } from "./components/ChatScreen";
import type { GlobalProps } from "./types";

function App() {
  const [globalProps, setGlobalProps] = useState<GlobalProps>({name : "", ipAddress : ""});
  
  if (!globalProps.name) {
    return <Login onStart={setGlobalProps} />;
  }

  return <ChatScreen userName= {globalProps.name} ipAddress= {globalProps.ipAddress}/>

  
}

export default App;
