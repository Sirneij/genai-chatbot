import { useState, useEffect, useCallback } from "react";

type WebSocketMessage = {
  type: "auto" | "error";
  question: string;
};

export const useWebSocket = (
  url: string,
  onMessage: (content: string, isComplete?: boolean) => void
) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log("WebSocket Connected");
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Received:", data.answer);

        // Handle the streaming response
        if (data.answer === "") {
          // "[END]"
          onMessage("", true); // Signal completion
        } else {
          onMessage(data.answer, false);
        }
      } catch (e) {
        console.error("Error parsing message:", e);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket Disconnected");
      setIsConnected(false);
      setTimeout(() => setSocket(new WebSocket(url)), 3000);
    };

    ws.onerror = (event) => {
      console.error("WebSocket error:", event);
      setError("WebSocket error occurred");
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [url, onMessage]);

  const sendMessage = useCallback(
    (message: string) => {
      if (socket && isConnected) {
        const payload: WebSocketMessage = {
          type: "auto",
          question: message,
        };
        console.log("Sending:", payload);
        socket.send(JSON.stringify(payload));
      } else {
        console.log("Socket not ready:", {
          isConnected,
          socketExists: !!socket,
        });
      }
    },
    [socket, isConnected]
  );

  return { sendMessage, isConnected, error };
};
