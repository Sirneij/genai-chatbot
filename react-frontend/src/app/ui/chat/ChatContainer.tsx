import React from "react";
import ChatMessage from "$/app/ui/chat/ChatMessage";
import { Message } from "$/app/lib/types";

interface ChatContainerProps {
  messages: Message[];
}

const ChatContainer: React.FC<ChatContainerProps> = ({ messages }) => {
  return (
    <div className="flex flex-col h-full overflow-y-auto p-4">
      <div className="flex-1 overflow-y-scroll">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
      </div>
    </div>
  );
};

export default ChatContainer;
