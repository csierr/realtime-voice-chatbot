import { useState, useEffect, useRef } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const useWebSocket = (url: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnecting, setIsConnecting] = useState(true);
  const [audioQueue, setAudioQueue] = useState<string[]>([]);
  const [isAudioFinished, setIsAudioFinished] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log("WebSocket connected");
      setIsConnecting(false);
    };

    ws.current.onmessage = (event) => {
      const receivedMessage = JSON.parse(event.data);

      if (receivedMessage.text) {
        const newMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: receivedMessage.text,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, newMessage]);
      }

      if (receivedMessage.type === "audio") {
        setAudioQueue((prev) => [...prev, receivedMessage.data]);
      }

      if (receivedMessage.type === "audio_done") {
        setIsAudioFinished(true);
      }
    };

    ws.current.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnecting(false);
    };

    ws.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      setIsConnecting(false);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  const sendMessage = (text: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      setAudioQueue([]);
      setIsAudioFinished(false);
      const messagePayload = { type: "text", data: text };
      ws.current.send(JSON.stringify(messagePayload));
      const newMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: text,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, newMessage]);
    }
  };

  return { messages, sendMessage, isConnecting, audioQueue, setAudioQueue, isAudioFinished };
};

export default useWebSocket;
