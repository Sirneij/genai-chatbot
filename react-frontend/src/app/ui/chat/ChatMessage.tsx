import { marked } from "marked";
import type { Tokens } from "marked";
import { Message } from "$/app/lib/types";
import { ThinkingAnimation } from "$/app/ui/reusables";

// Configure marked for inline rendering
marked.setOptions({
  gfm: true,
  breaks: true,
  pedantic: false,
});

// Custom renderer to handle streaming better
const renderer = new marked.Renderer();
renderer.paragraph = function (paragraph: Tokens.Paragraph): string {
  return `<span>${paragraph.text}</span>`;
};

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
        {message.loading ? (
          <ThinkingAnimation />
        ) : (
          <div className="prose dark:prose-invert max-w-none">
            {message.sender === "bot" ? (
              <>
                <span
                  dangerouslySetInnerHTML={{
                    __html: marked(message.text, { renderer }),
                  }}
                />
                {!message.complete && (
                  <span className="ml-1 animate-pulse">|</span>
                )}
              </>
            ) : (
              <span
                dangerouslySetInnerHTML={{
                  __html: marked(message.text, { renderer }),
                }}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
