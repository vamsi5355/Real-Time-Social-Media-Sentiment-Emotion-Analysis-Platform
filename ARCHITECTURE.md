Real-Time Social Media Sentiment & Emotion Analysis Platform

1. System Overview
This project implements a real-time, event-driven sentiment and emotion analysis platform for social media–style posts.
The system is designed using loosely coupled services, asynchronous processing, and real-time streaming to ensure scalability, fault tolerance, and low-latency updates.
All services are containerized and orchestrated using Docker Compose, enabling one-command startup with zero manual configuration.
2. High-Level Architecture Diagram

┌──────────────────┐
│  Ingestor Service│
│  (Post Producer) │
└─────────┬────────┘
          │  XADD
          ▼
┌──────────────────┐
│   Redis Streams   │
│ (Event Backbone) │
└─────────┬────────┘
          │  XREADGROUP
          ▼
┌──────────────────┐
│   Worker Service  │
│ Sentiment + Emotion
│   Analysis Engine │
└─────────┬────────┘
          │  Insert / Update
          ▼
┌──────────────────┐
│     MongoDB       │
│  Persistent Store │
└─────────┬────────┘
          │  Query
          ▼
┌──────────────────┐
│  FastAPI Backend  │
│ REST + WebSockets │
└─────────┬────────┘
          │  Push (WS)
          ▼
┌──────────────────┐
│  React Frontend   │
│ Live Dashboard    │
└──────────────────┘
3. Core Components
3.1 Ingestor Service
Simulates ingestion of social media posts (e.g., Reddit/Twitter-like content).
Publishes posts into Redis Streams using XADD.
Designed as a producer in an event-driven architecture.
Design decision:
Redis Streams were chosen to decouple ingestion from processing and to guarantee message durability.
3.2 Redis Streams (Messaging Layer)
Acts as the central event pipeline.
Stores incoming posts reliably.
Supports consumer groups for horizontal scalability.
Prevents data loss during worker restarts.
Key properties:
At-least-once delivery
Ordered message processing
Backpressure handling
3.3 Worker Service
Consumes posts from Redis Streams using XREADGROUP.
Performs:
Sentiment classification (positive / neutral / negative)
Emotion detection
Stores results in MongoDB.
Acknowledges messages (XACK) after successful processing.
Design decision:
Workers are stateless and can be scaled horizontally to increase throughput.
3.4 MongoDB (Persistence Layer)
Stores:
Raw social media posts
Sentiment and emotion analysis results
Timestamps and metadata
Collections:
social_media_posts
sentiment_analysis
Why MongoDB?
Flexible document schema
Efficient handling of text-heavy data
Easy horizontal scaling
3.5 Backend API (FastAPI)
Acts as the orchestration and aggregation layer.
Responsibilities:
Exposes REST APIs:
/api/health
/api/posts
/api/sentiment/distribution
Manages WebSocket connections
Aggregates sentiment statistics
Handles filtering and pagination
Why FastAPI?
Async-first architecture
High performance
Native WebSocket support
3.6 WebSocket Layer
Pushes real-time sentiment updates to connected clients.
Eliminates polling from the frontend.
Broadcasts updates to all connected dashboards.
This enables true real-time UI updates.
3.7 Frontend (React)
Displays live sentiment distribution.
Connects to backend via WebSocket.
Shows system health and connection status.
Updates charts in real time without page reloads.
4. End-to-End Data Flow
Ingestor generates a social media post.
Post is published to Redis Streams.
Worker consumes the post.
Sentiment and emotion are analyzed.
Results are stored in MongoDB.
Backend queries updated analytics.
Backend pushes updates via WebSocket.
Frontend dashboard updates instantly.
5. Scalability Considerations
Worker services can be scaled horizontally.
Redis Streams support multiple consumers.
Backend and frontend are independently deployable.
MongoDB can be replaced with a managed cluster.
6. Fault Tolerance & Robustness
Redis ensures message durability.
Worker crashes do not cause data loss.
Services restart automatically via Docker.
System continues operating even if individual services restart.
7. Technology Stack
Layer
Technology
Backend
FastAPI (Python)
Frontend
React
Messaging
Redis Streams
Database
MongoDB
Real-time
WebSockets
Containerization
Docker, Docker Compose
Testing
Pytest
8. Design Decisions Summary
Redis Streams for reliable event-driven processing
Asynchronous workers for scalability
WebSockets for real-time UI updates
Docker Compose for reproducibility and zero-config startup
Clear separation of concerns across services
9. Conclusion
This architecture demonstrates a production-style, real-time data pipeline using modern backend, messaging, and frontend technologies.
The system is scalable, fault-tolerant, and designed