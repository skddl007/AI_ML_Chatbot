import { useEffect, useState } from "react";


export function useChat() {
  const [messages, setMessages] = useState([]);
  const [threads, setThreads] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    // Simulate loading threads from a backend
    setThreads([{ id: 1, title: "What is AI?", isActive: true }]);
  }, []);

  const handleSend = () => {
    if (input.trim()) {
      const newMessage = { role: "user", content: input };
      setMessages([...messages, newMessage]);
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

      // Simulate AI response
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Here's a response to your query. How can I assist you further?",
            alternativeResponses: [
              "Here's an alternative way to address your question.",
              "Consider this different perspective on the matter.",
              "Let me offer another approach to your inquiry.",
            ],
          },
        ]);
      }, 1000);
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
    // Here you would typically load the messages for the selected thread
    // For this example, we'll just clear the messages
    setMessages([]);
  };

  return {
    messages,
    threads,
    input,
    setInput,
    handleSend,
    handleNewChat,
    handleRenameThread,
    handleDeleteThread,
    handleThreadClick,
  };
}
