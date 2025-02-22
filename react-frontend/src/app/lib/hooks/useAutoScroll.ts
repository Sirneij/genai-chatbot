import { useEffect, useRef } from "react";

export function useAutoScroll<T extends HTMLElement>(dependency: any) {
  const scrollRef = useRef<T>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [dependency]);

  return scrollRef;
}
