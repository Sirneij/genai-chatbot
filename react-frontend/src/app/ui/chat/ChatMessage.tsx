import { Message } from "$/app/lib/types";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  return (
    <div
      className={`flex ${
        message.sender === "user" ? "justify-end" : "justify-start"
      } mb-4`}
    >
      <div
        className={`max-w-[80%] p-3 rounded-lg ${
          message.sender === "user"
            ? "bg-[#f5f5f5] text-[#171717] dark:bg-[#1a1a1a] dark:text-[#ededed]"
            : "bg-[#fafafa] text-[#171717] dark:bg-[#141414] dark:text-[#ededed]"
        }`}
      >
        {message.text}
        {!message.complete && message.sender === "bot" && (
          <span className="animate-pulse">|</span>
        )}
      </div>
    </div>
  );
}
