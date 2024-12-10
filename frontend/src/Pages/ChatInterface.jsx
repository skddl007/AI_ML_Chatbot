"use client";

import { Home, MessageSquare, Plus, Send } from "lucide-react";
import { useState } from "react";
import { ChatThread, FeedbackForm, MessageList } from "../components/ChatComponents";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { ScrollArea } from "../components/ui/ScrollArea";
import { useChat } from "../components/useChat";

function Shimmer() {
  return (
    <div className="animate-pulse">
      <div className="bg-gray-700 h-6 w-2/4 mb-2 ml-4 rounded-md"></div>
      <div className="bg-gray-700 h-6 w-1/2 mb-2 ml-4 rounded-md"></div>
      <div className="bg-gray-700 h-6 w-5/6 rounded-md"></div>
    </div>
  );
}

export default function ChatInterface() {
  const [isFeedbackOpen, setFeedbackOpen] = useState(false);
  const {
    messages,
    threads,
    input,
    setInput,
    loading,
    extractedData,
    handleSend,
    handleNewChat,
    handleRenameThread,
    handleDeleteThread,
    handleThreadClick,
  } = useChat();

  return (
    <div className="flex h-screen bg-[#0f172a] text-white">
      {/* Sidebar */}
      <div className="w-64 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <Button variant="ghost" size="icon" className="text-gray-400 hover:text-white group">
              <Home className="h-5 w-5 group-hover:text-gray-900" />
            </Button>
            <span className="text-sm font-medium">EVE</span>
          </div>
        </div>
        <div className="p-4">
          <Button onClick={handleNewChat} className="w-full justify-start gap-2 bg-gray-700 hover:bg-gray-600">
            <Plus className="h-4 w-4" />
            <span>New chat</span>
          </Button>
        </div>

        <ScrollArea className="flex-1 px-4">
          {threads.map((thread) => (
            <ChatThread
              key={thread.id}
              thread={thread}
              isSelected={thread.isActive}
              onRename={handleRenameThread}
              onDelete={handleDeleteThread}
              onClick={handleThreadClick}
            />
          ))}
        </ScrollArea>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Feedback Button */}
        <div className="p-4 flex justify-end">
          <Button
            onClick={() => setFeedbackOpen(true)}
            variant="outline"
            className="flex items-center justify-center mr-4 bg-cyan-500 text-white border-cyan-500 hover:bg-cyan-600 hover:border-cyan-600 group"
          >
            <MessageSquare className="h-4 w-4 mr-2 group-hover:text-white" />
            <span className="group-hover:text-white">Feedback</span>
          </Button>
        </div>

        {/* Feedback Modal */}
        {isFeedbackOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white rounded-lg shadow-lg w-96 p-6">
              <h2 className="text-lg font-medium text-gray-800 mb-4">Provide Feedback</h2>
              <FeedbackForm closeModal={() => setFeedbackOpen(false)} />
            </div>
          </div>
        )}

        <ScrollArea className="flex-1 p-4">
          <MessageList messages={messages} />
          {loading && (
            <div className="my-4">
              <Shimmer />
            </div>
          )}
        </ScrollArea>

        {/* Message Input */}
        <div className="p-1.5">
          <div className="relative max-w-3xl mx-auto mb-20">
            <Input
              placeholder="Type your message..."
              className="w-full bg-gray-900 border-gray-700 focus:border-blue-500 pr-12 rounded-full pl-4 text-gray-300 h-10 p-5 "
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
            />
            <Button
              size="icon"
              onClick={handleSend}
              disabled={loading}
              className={`absolute right-1 top-1/2 transform -translate-y-1/2 rounded-full h-8 w-8 ${
                loading ? "bg-gray-500" : "bg-blue-600/70 hover:bg-blue-700"
              }`}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
