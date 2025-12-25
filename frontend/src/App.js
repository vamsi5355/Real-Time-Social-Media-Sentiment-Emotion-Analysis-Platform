import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [status, setStatus] = useState("disconnected");
  const [sentiment, setSentiment] = useState({
    positive: 0,
    neutral: 0,
    negative: 0,
  });

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/sentiment");

    socket.onopen = () => {
      setStatus("connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      setSentiment({
        positive: data.positive || 0,
        neutral: data.neutral || 0,
        negative: data.negative || 0,
      });
    };

    socket.onclose = () => {
      setStatus("disconnected");
    };

    return () => socket.close();
  }, []);

  return (
    <div className="container">
      <h1>Real-Time Social Media Sentiment Dashboard</h1>
      <p className={`status ${status}`}>
        WebSocket Status: {status}
      </p>

      <div className="cards">
        <div className="card positive">
          <h2>Positive</h2>
          <p>{sentiment.positive}</p>
        </div>

        <div className="card neutral">
          <h2>Neutral</h2>
          <p>{sentiment.neutral}</p>
        </div>

        <div className="card negative">
          <h2>Negative</h2>
          <p>{sentiment.negative}</p>
        </div>
      </div>
    </div>
  );
}

export default App;