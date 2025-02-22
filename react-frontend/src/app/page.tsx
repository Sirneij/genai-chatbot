"use client";

import { useCallback, useState } from "react";
import ChatContainer from "$/app/ui/chat/ChatContainer";
import ChatInput from "$/app/ui/chat/ChatInput";
import { Logo } from "$/app/ui/icons/base";
import { useWebSocket } from "$/app/lib/hooks/useWebSocket";
import { Message } from "$/app/lib/types";
import { useAutoScroll } from "$/app/lib/hooks/useAutoScroll";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const scrollRef = useAutoScroll<HTMLDivElement>(messages);

  const handleSend = (message: string) => {
    const newMessage = {
      id: Date.now(),
      text: message,
      sender: "user" as const,
    };

    // Add a loading message for the bot
    const loadingMessage = {
      id: Date.now() + 1,
      text: "",
      sender: "bot" as const,
      loading: true,
      complete: false,
    };

    setMessages((prev) => [...prev, newMessage, loadingMessage]);
    sendMessage(message);
  };

  const handleBotMessage = useCallback(
    (content: string, isComplete?: boolean) => {
      setMessages((prev) => {
        const lastMessage = prev[prev.length - 1];

        if (isComplete && lastMessage?.sender === "bot") {
          const updatedMessages = [...prev];
          updatedMessages[prev.length - 1] = {
            ...lastMessage,
            complete: true,
            loading: false,
          };
          return updatedMessages;
        }

        if (!content) return prev;

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
              loading: false,
            },
          ];
        }

        const updatedMessages = [...prev];
        updatedMessages[prev.length - 1] = {
          ...lastMessage,
          text: lastMessage.text + content,
          loading: false,
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

  return (
    <div className="flex flex-col flex-1 h-[calc(100vh-10rem)]">
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
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700"
          >
            <ChatContainer messages={messages} />
          </div>
          <ChatInput onSend={handleSend} messageCount={messages.length} />
        </>
      )}
    </div>
  );
}
