"use client";

import { useCallback, useState } from "react";
import ChatContainer from "$/app/ui/chat/ChatContainer";
import ChatInput from "$/app/ui/chat/ChatInput";
import { Logo } from "$/app/ui/icons/base";
import { useWebSocket } from "$/app/lib/hooks/useWebSocket";
import { Message } from "./lib/types";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);

  const handleBotMessage = useCallback(
    (content: string, isComplete?: boolean) => {
      setMessages((prev) => {
        const lastMessage = prev[prev.length - 1];

        if (isComplete && lastMessage?.sender === "bot") {
          // Mark the last message as complete
          const updatedMessages = [...prev];
          updatedMessages[prev.length - 1] = {
            ...lastMessage,
            complete: true,
          };
          return updatedMessages;
        }

        if (!content) return prev; // Skip empty content

        if (
          !lastMessage ||
          lastMessage.sender !== "bot" ||
          lastMessage.complete
        ) {
          return [
            ...prev,
            {
              id: Date.now(),
              text: content,
              sender: "bot",
              complete: false,
            },
          ];
        }

        // Update the last message with new content
        const updatedMessages = [...prev];
        updatedMessages[prev.length - 1] = {
          ...lastMessage,
          text: lastMessage.text + content,
        };

        return updatedMessages;
      });
    },
    []
  );

  const { sendMessage, isConnected, error } = useWebSocket(
    "ws://localhost:8000/ws",
    handleBotMessage
  );

  const handleSend = (message: string) => {
    const newMessage = {
      id: Date.now(),
      text: message,
      sender: "user" as const,
    };
    setMessages((prev) => [...prev, newMessage]);
    sendMessage(message);
  };

  return (
    <div className="h-screen flex flex-col">
      {!messages.length ? (
        <div className="flex flex-col items-center justify-center flex-1">
          <div className="flex flex-col items-center max-w-3xl w-full mx-auto">
            <Logo className="h-16 w-16 mb-6 text-[#171717] dark:text-[#ededed]" />
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              Ask me anything! I'm here to help.
            </p>
            <div className="w-full">
              <ChatInput onSend={handleSend} messageCount={messages.length} />
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="flex-1 overflow-y-auto">
            <ChatContainer messages={messages} />
          </div>
          <ChatInput onSend={handleSend} messageCount={messages.length} />
        </>
      )}
    </div>
  );
}
