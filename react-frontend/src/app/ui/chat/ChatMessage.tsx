import { marked } from "marked";
import { Message } from "$/app/lib/types";
import { ThinkingAnimation } from "$/app/ui/reusables";
import "katex/dist/katex.min.css";
import katex from "katex";

// Configure marked for inline rendering
marked.setOptions({
  gfm: true,
  breaks: true,
  pedantic: false,
});

// Custom renderer to handle streaming better
const renderer = new marked.Renderer();

// Add math support
const mathRenderer = {
  name: "math",
  level: "inline",
  start(src: string) {
    return src.match(/\$/)?.index;
  },
  tokenizer(src: string) {
    const match = src.match(/^\$\$([^$\n]+?)\$\$|^\$([^$\n]+?)\$/);
    if (match) {
      const isDisplay = match[0].startsWith("$$");
      return {
        type: "math",
        raw: match[0],
        text: (isDisplay ? match[1] : match[2]).trim(),
        isDisplay,
      };
    }
  },
  renderer(token: any) {
    try {
      return katex.renderToString(token.text, {
        throwOnError: false,
        displayMode: token.isDisplay,
      });
    } catch (err) {
      return token.raw;
    }
  },
};

marked.use({ extensions: [mathRenderer] });

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
          <div className="prose dark:prose-invert max-w-none animate-fade-in">
            {message.sender === "bot" ? (
              <span
                dangerouslySetInnerHTML={{
                  __html: marked(message.text, { renderer }),
                }}
              />
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
