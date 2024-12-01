import { createContext, useEffect, useRef, useState } from "react";

export const ContextApp = createContext();

const AppContext = ({ children }) => {
  const [showSlide, setShowSlide] = useState(false);
  const [mobile, setMobile] = useState(false);
  const [chatValue, setChatValue] = useState("");
  const [message, setMessage] = useState([]); // Start with an empty array
  const [threads, setThreads] = useState([]);
  const [currentThread, setCurrentThread] = useState(null);
  const [theme, setTheme] = useState("dark");
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [threadToDelete, setThreadToDelete] = useState(null);
  const msgEnd = useRef(null);

  useEffect(() => {
    if (msgEnd.current) {
      msgEnd.current.scrollIntoView();
    }
  }, [message]);

  useEffect(() => {
    document.body.className = theme; // Apply theme to body
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "dark" ? "light" : "dark"));
  };

  // Handle Send
  const handleSend = () => {
    const text = chatValue.trim();
    if (text) {
      setChatValue("");
      const userMessage = { text, isBot: false, highlight: true }; // Highlight input
      const botMessage = { text: "This is a placeholder response.", isBot: true };

      setMessage((prev) => [...prev, userMessage, botMessage]);

      // Save to thread
      if (currentThread === null) {
        const newThread = {
          id: Date.now(),
          name: text.substring(0, 30),
          messages: [userMessage, botMessage],
        };
        setThreads((prevThreads) => [...prevThreads, newThread]);
        setCurrentThread(newThread.id);
      } else {
        setThreads((prevThreads) =>
          prevThreads.map((thread) =>
            thread.id === currentThread
              ? { ...thread, messages: [...thread.messages, userMessage, botMessage] }
              : thread
          )
        );
      }
    }
  };

  // Handle thread selection
  const handleQuery = (threadName) => {
    console.log(`Thread selected: ${threadName}`);
  };

  // Rename thread
  const renameThread = (thread, newName) => {
    setThreads((prevThreads) =>
      prevThreads.map((t) =>
        t.id === thread.id ? { ...t, name: newName } : t
      )
    );
  };

  // Delete thread
  const deleteThread = (thread) => {
    setThreads((prevThreads) => prevThreads.filter((t) => t.id !== thread.id));
    setShowDeletePopup(false); // Close the confirmation popup after deleting
  };

  // Confirm delete
  const handleConfirmDelete = () => {
    if (threadToDelete) {
      deleteThread(threadToDelete);
    }
  };

  return (
    <ContextApp.Provider
      value={{
        showSlide,
        setShowSlide,
        mobile,
        setMobile,
        chatValue,
        setChatValue,
        handleSend,
        message,
        msgEnd,
        threads,
        currentThread,
        theme,
        toggleTheme,
        handleQuery,
        renameThread,
        setShowDeletePopup,
        setThreadToDelete,
      }}
    >
      {children}
      {showDeletePopup && (
        <div className="fixed inset-0 flex justify-center items-center bg-gray-500 bg-opacity-50">
          <div className="bg-white p-4 rounded-lg shadow-lg">
            <h3 className="text-lg font-semibold mb-3">Are you sure you want to delete this thread?</h3>
            <div className="flex justify-between">
              <button
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                onClick={handleConfirmDelete}
              >
                Yes, Delete
              </button>
              <button
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                onClick={() => setShowDeletePopup(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </ContextApp.Provider>
  );
};

export default AppContext;
