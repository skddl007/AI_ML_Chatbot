import { useEffect, useState } from "react";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [threads, setThreads] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false); // State for loading
  const [extractedData, setExtractedData] = useState([]); // State for extracted data

  useEffect(() => {
    // Simulate loading threads from a backend
    setThreads([{ id: 1, title: "What is AI?", isActive: true }]);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return; // Avoid multiple API calls

    setLoading(true);

    const newMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");

    // Create a new thread if it's the first message
    if (messages.length === 0) {
      const newThread = {
        id: threads.length + 1,
        title: input.slice(0, 30) + (input.length > 30 ? "..." : ""),
        isActive: true,
      };
      setThreads((prev) => [
        newThread,
        ...prev.map((thread) => ({ ...thread, isActive: false })),
      ]);
    }

    try {
      const response = await fetch("http://127.0.0.1:3002/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();
      console.log("Response from backend:", data);

      if (response.ok) {
        const extractedItems =
          data.top_three_relative_ans?.map((item) => ({
            id: item[0],
            author: item[1],
            title: item[2],
            url: item[3],
            context: item[8], // Extracted context
            allFields: item, // Include all fields as a fallback
          })) || [];

        setExtractedData(extractedItems); // Store all extracted data

        const aiMessage = {
          role: "assistant",
          content: data.response,
          alternativeResponses: extractedItems,
        };
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "An error occurred. Please try again." },
        ]);
      }
    } catch (error) {
      console.error("Error connecting to backend:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Failed to connect to the server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    const newThread = {
      id: threads.length + 1,
      title: "New Chat",
      isActive: true,
    };
    setThreads((prev) => [
      newThread,
      ...prev.map((thread) => ({ ...thread, isActive: false })),
    ]);
    setMessages([]);
    setExtractedData([]); // Clear extracted data when starting a new chat
  };

  const handleRenameThread = (id) => {
    const newTitle = prompt("Enter new thread title:");
    if (newTitle) {
      setThreads((prev) =>
        prev.map((thread) =>
          thread.id === id ? { ...thread, title: newTitle } : thread
        )
      );
    }
  };

  const handleDeleteThread = (id) => {
    if (window.confirm("Are you sure you want to delete this thread?")) {
      setThreads((prev) => prev.filter((thread) => thread.id !== id));
    }
  };

  const handleThreadClick = (id) => {
    setThreads((prev) =>
      prev.map((thread) => ({ ...thread, isActive: thread.id === id }))
    );
    setMessages([]);
    setExtractedData([]);
  };

  return {
    messages,
    threads,
    input,
    extractedData, // All data sent to frontend
    loading,
    setInput,
    handleSend,
    handleNewChat,
    handleRenameThread,
    handleDeleteThread,
    handleThreadClick,
  };
}
