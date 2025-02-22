export function ThinkingAnimation() {
  return (
    <div className="flex items-center space-x-1.5">
      <div className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
      <div className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
      <div className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" />
    </div>
  );
}
