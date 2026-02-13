import { useEffect, useState } from "react";
import { connectSentimentSocket } from "../websocket/sentimentSocket";

export const useWebSocket = (onMessage) => {
  const [wsData, setWsData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const handleMessage = (data) => {
      setWsData(data);
      if (onMessage) {
        onMessage(data);
      }
    };

    const socket = connectSentimentSocket(handleMessage);
    
    // Track connection status
    socket.addEventListener('open', () => setConnected(true));
    socket.addEventListener('close', () => setConnected(false));

    return () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [onMessage]);

  return wsData;
};
