export const connectSentimentSocket = (onMessage) => {
  // Get backend URL and convert to WS protocol
  const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
  const wsUrl = backendUrl.replace("http://", "ws://").replace("https://", "wss://");
  const socketUrl = `${wsUrl}/ws/sentiment`;

  const socket = new WebSocket(socketUrl);

  socket.onopen = () => {
    console.log("✅ WebSocket connected to:", socketUrl);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage && typeof onMessage === 'function') {
        onMessage(data);
      }
    } catch (err) {
      console.error("Error parsing WebSocket message:", err);
    }
  };

  socket.onerror = (err) => {
    console.error("❌ WebSocket error:", err);
  };

  socket.onclose = () => {
    console.warn("🔌 WebSocket disconnected");
  };

  return socket;
};
