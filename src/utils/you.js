import React, { useEffect, useState } from "react";
import ChatContainer from "./components/ChatContainer";
import LeftNav from "./components/LeftNav";
import Mobile from "./components/Mobile";
import "./App.css"; 

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add("dark");
      document.body.classList.remove("light");
    } else {
      document.body.classList.add("light");
      document.body.classList.remove("dark");
    }
  }, [isDarkMode]);

  return (
    <div className="overflow-hidden flex w-screen relative">
      <LeftNav />
      <ChatContainer />
      <span className="flex lg:hidden">
        <Mobile />
      </span>
      <button
        onClick={() => setIsDarkMode((prev) => !prev)}
        className="absolute top-4 right-4 p-2 bg-gray-800 rounded">
        {isDarkMode ? "🌙" : "☀️"}
      </button>
    </div>
  );
}

export default App;
