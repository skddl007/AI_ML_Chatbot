import {
  Bot,
  Copy,
  Edit,
  Star,
  ThumbsDown,
  ThumbsUp,
  Trash2,
  User,
  Volume2
} from "lucide-react";
import { useState } from "react";
import { Button } from "./ui/Button";
import { Card } from "./ui/Card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./ui/collapsible";
import { useChat } from "./useChat";

export function ChatThread({ thread, isSelected, onRename, onDelete, onClick }) {
  return (
    <div className="flex flex-col mb-1">
      <Button
        variant="ghost"
        className={`w-full justify-start ${
          isSelected ? "bg-gray-700 text-white" : "text-gray-400 hover:text-white"
        }`}
        onClick={() => onClick(thread.id)}
      >
        # {thread.title}
      </Button>
      {isSelected && (
        <div className="flex justify-end gap-2 mt-1">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onRename(thread.id)}
            className="text-blue-500 hover:bg-blue-100"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onDelete(thread.id)}
            className="text-red-500 hover:bg-red-100"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}

export function AlternativeResponse({ response, index, isOpen, onToggle }) {
  const [likes, setLikes] = useState(0);
  const [dislikes, setDislikes] = useState(0);

  const responseDetails = {
    book: "Artificial Intelligence: A Modern Approach Third Edition by Stuart J. Russell and Peter Norvig",
    chapter: "Intelligent Agents (Number: 1)",
    page: "49, Paragraph: 149",
    similarity: 0.4404580397833011,
  };

//   const copyToClipboard = (text) => navigator.clipboard.writeText(text);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(
      () => {
        alert("Text copied to clipboard!");
        // console.alert("Text copied to clipboard!")
      },
      (err) => {
        console.error("Could not copy text: ", err);
      }
    );
  };

  const speakText = (text) => {
    const speech = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(speech);
  };

  return (
    <Collapsible open={isOpen} onOpenChange={onToggle}>
      <CollapsibleTrigger className="flex items-center justify-between w-full p-2 bg-gray-700 hover:bg-gray-600 rounded-md">
        <span>Response {index + 1}</span>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <Card className="mt-2 p-4 bg-white text-gray-900">
          <p className="mb-4">{response}</p>
          <div className="text-sm text-gray-600 mb-4">
            <p>
              <strong>Book:</strong> {responseDetails.book}
            </p>
            <p>
              <strong>Chapter:</strong> {responseDetails.chapter}
            </p>
            <p>
              <strong>Page:</strong> {responseDetails.page}
            </p>
            <p>
              <strong>Similarity:</strong> {responseDetails.similarity.toFixed(4)}
            </p>
          </div>
          <div className="flex justify-end mt-2 space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setLikes(likes + 1)}
              className="text-blue-500 border-blue-500 hover:bg-blue-100"
            >
              <ThumbsUp className="h-4 w-4 mr-1" />
              {likes}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDislikes(dislikes + 1)}
              className="text-blue-500 border-blue-500 hover:bg-red-100"
            >
              <ThumbsDown className="h-4 w-4 mr-1" />
              {dislikes}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(response)}
              className="text-gray-500 border-gray-500 hover:bg-gray-100"
            >
              <Copy className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => speakText(response)}
              className="text-gray-500 border-gray-500 hover:bg-gray-100"
            >
              <Volume2 className="h-4 w-4" />
            </Button>
          </div>
        </Card>
      </CollapsibleContent>
    </Collapsible>
  );
}

export function MessageList({ messages }) {
  const { copyToClipboard, speakText } = useChat();
  const [openResponseIndex, setOpenResponseIndex] = useState(null);

  return (
    <div className="space-y-4 max-w-3xl mx-auto">
      {messages.map((message, index) => (
        <div key={index} className="space-y-2">
          <div className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            {message.role === "assistant" && (
              <div className="flex items-start">
                <div className="bg-blue-500 rounded-full p-1">
                  <Bot className="h-6 w-6 text-white" />
                </div>
              </div>
            )}
            <div
              className={`rounded-lg p-3 max-w-[80%] ${
                message.role === "user" ? "bg-blue-500/50 rounded-tr-none" : "bg-gray-800 rounded-tl-none"
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
            {message.role === "user" && (
              <div className="flex items-start">
                <div className="bg-green-500 rounded-full p-1">
                  <User className="h-6 w-6 text-white" />
                </div>
              </div>
            )}
          </div>
          {message.role === "assistant" && message.alternativeResponses && (
            <div className="mt-2">
              <Collapsible>
                <CollapsibleTrigger className="flex items-center justify-between w-full p-2 bg-gray-700 hover:bg-gray-600 rounded-t-md">
                  <span>Alternative Responses</span>
                </CollapsibleTrigger>
                <CollapsibleContent className="bg-gray-800 rounded-b-md p-2 space-y-2">
                  {message.alternativeResponses.map((response, idx) => (
                    <AlternativeResponse
                      key={idx}
                      response={response}
                      index={idx}
                      isOpen={openResponseIndex === idx}
                      onToggle={() =>
                        setOpenResponseIndex(openResponseIndex === idx ? null : idx)
                      }
                    />
                  ))}
                </CollapsibleContent>
              </Collapsible>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}


export function FeedbackForm({ closeModal }) {
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Feedback submitted:", { rating, feedback });
    alert("Thank you for your feedback!");
    closeModal(); // Close modal on submit
  };

  return (
    <>
      <style>
        {`
          .textarea-class {
            color: black; /* Text color */
            background-color: white; /* Background color */
            border: 1px solid #d1d5db; /* Light gray border */
            padding: 8px;
            border-radius: 4px;
            width: 100%;
            font-size: 14px;
          }
          .textarea-class:focus {
            outline: none;
            border-color: #2563eb; /* Blue border on focus */
          }
        `}
      </style>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="rating" className="block text-sm font-medium text-gray-700">
            Rating
          </label>
          <div className="flex items-center mt-1">
            {[1, 2, 3, 4, 5].map((value) => (
              <Button
                key={value}
                type="button"
                variant={rating >= value ? "default" : "outline"}
                size="sm"
                className="mr-1"
                onClick={() => setRating(value)}
              >
                <Star className={`h-4 w-4 ${rating >= value ? "text-yellow-400" : "text-gray-400"}`} />
              </Button>
            ))}
          </div>
        </div>
        <div>
          <label htmlFor="feedback" className="block text-sm font-medium text-gray-700">
            Feedback (optional)
          </label>
          <textarea
            id="feedback"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Please provide your feedback here..."
            className="textarea-class"
          />
        </div>
        <div className="flex justify-between">
          <Button
            onClick={closeModal}
            type="button"
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          >
            Close
          </Button>
          <Button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            Submit
          </Button>
        </div>
      </form>
    </>
  );
}
