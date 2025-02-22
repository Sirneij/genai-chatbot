"use client";

import { useState } from "react";
import {
  SendIcon,
  SearchIcon,
  ThinkIcon,
  AttachIcon,
} from "$/app/ui/icons/base";

type ChatInputProps = {
  onSend: (message: string, type: string) => void;
  messageCount: number;
};

export default function ChatInput({ onSend, messageCount }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [useMasked, setUseMasked] = useState(false);
  const [useAuto, setUseAuto] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSend(message, useMasked ? "masked" : "auto");
      setMessage("");
    }
  };
  return (
    <form
      onSubmit={handleSubmit}
      className={`transition-all duration-300 ease-in-out ${
        messageCount > 0
          ? "fixed bottom-0 left-1/2 -translate-x-1/2 w-10/12 bg-[#ffffff] dark:bg-[#0a0a0a] border-t border-[#f0f0f0] dark:border-[#1a1a1a]"
          : "max-w-4xl mx-auto"
      }`}
    >
      <div className="p-4">
        <div className="relative bg-[#f5f5f5] dark:bg-[#141414] rounded-lg border border-[#e5e5e5] dark:border-[#262626] focus-within:ring-2 focus-within:ring-[#262626] dark:focus-within:ring-[#404040]">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            rows={2}
            className="w-full p-4 bg-transparent text-[#171717] dark:text-[#ededed] focus:outline-none resize-none"
          />

          <div className="flex items-center justify-between px-4 py-2 border-t border-[#e5e5e5] dark:border-[#262626]">
            <div className="flex gap-3">
              <label
                className={`
                flex items-center gap-2 px-2 py-1 rounded-md cursor-pointer
                ${
                  useMasked
                    ? "bg-[#e5e5e5] dark:bg-[#262626]"
                    : "hover:bg-[#e5e5e5]/50 dark:hover:bg-[#262626]/50"
                }
                transition-colors
              `}
              >
                <input
                  type="checkbox"
                  checked={useMasked}
                  onChange={() => {
                    setUseMasked(!useMasked);
                    setUseAuto(useMasked); // Toggle Auto off when Masked is on
                  }}
                  className="hidden"
                />
                <SearchIcon className="h-4 w-4" />
                <span className="text-sm">Masked</span>
              </label>

              <label
                className={`
                flex items-center gap-2 px-2 py-1 rounded-md cursor-pointer
                ${
                  useAuto
                    ? "bg-[#e5e5e5] dark:bg-[#262626]"
                    : "hover:bg-[#e5e5e5]/50 dark:hover:bg-[#262626]/50"
                }
                transition-colors
              `}
              >
                <input
                  type="checkbox"
                  checked={useAuto}
                  onChange={() => {
                    setUseAuto(!useAuto);
                    setUseMasked(useAuto); // Toggle Masked off when Auto is on
                  }}
                  className="hidden"
                />
                <ThinkIcon className="h-4 w-4" />
                <span className="text-sm">Auto</span>
              </label>
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                disabled={!useMasked} // Disable when not in Masked mode
                className={`
                  flex items-center gap-2 px-2 py-1 rounded-md 
                  ${
                    useMasked
                      ? "hover:bg-[#e5e5e5]/50 dark:hover:bg-[#262626]/50"
                      : "opacity-50 cursor-not-allowed"
                  }
                  transition-colors
                `}
              >
                <AttachIcon className="h-4 w-4" />
                <span className="text-sm">Attach</span>
              </button>
              <button
                type="submit"
                disabled={!message.trim()}
                className="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-[#e5e5e5]/50 dark:hover:bg-[#262626]/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <SendIcon className="h-4 w-4" />
                <span className="text-sm">Send</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </form>
  );
}
