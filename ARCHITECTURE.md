# System Architecture

## Overview
The Real-Time Social Media Sentiment & Emotion Analysis Platform is a distributed, event-driven system designed to ingest social media posts, analyze sentiment and emotion asynchronously, and stream real-time insights to users through a web dashboard.

The system follows a microservices-inspired architecture using Docker Compose for orchestration.

---

## High-Level Architecture

[Social Media Source]
        |
        v
   Ingestor Service
        |
        v
     Redis Streams  <------------------+
        |                               |
        v                               |
   Worker Service                       |
 (Sentiment & Emotion Analysis)         |
        |                               |
        v                               |
     MongoDB                            |
        |                               |
        +----------> Backend API -------+
                        |
                        v
                 WebSocket Server
                        |
                        v
                   Frontend UI