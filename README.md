# Real-Time Social Media Sentiment & Emotion Analysis Platform

## 📌 Project Overview
This project is a real-time, scalable platform that ingests social media–like text data, performs sentiment and emotion analysis using AI models, and provides live insights via REST APIs and WebSockets.

The system is built using a microservices architecture with Docker, Redis Streams, MongoDB, FastAPI, and AI models.

🏗 Architecture

Ingester → Redis Streams → Worker → MongoDB
                              ↓
                        WebSocket API
                              ↓
                         React Dashboard


🧩 System Components
1. Ingester Service
Generates or fetches social media posts

Pushes posts into Redis Streams

2. Redis Streams
Acts as a message queue

Ensures reliable and ordered message processing

Supports consumer groups for scalability

3. Worker Service
Consumes messages from Redis Streams

Performs sentiment & emotion analysis

Stores results in MongoDB

Acknowledges messages after successful processing

4. Backend (FastAPI)
REST APIs:

/api/health

/api/posts

/api/sentiment/distribution

WebSocket endpoint:

/ws/sentiment (real-time sentiment updates)

5. Database (MongoDB)
Stores raw posts and analyzed sentiment data

Flexible schema for unstructured text data

6. Frontend (React)
Connects to WebSocket endpoint

Displays real-time sentiment distribution

Updates UI instantly without polling

🐳 Dockerized Deployment
All services are containerized and orchestrated using Docker Compose:

backend

ingester

worker

redis

mongodb

frontend

Run the project

docker compose build
docker compose up -d

🧪 Testing
Backend tested using PyTest

Health endpoint validation

Code coverage reports generated using pytest-cov

🎯 Key Highlights
Event-driven architecture
Real-time WebSocket communication

Asynchronous processing pipeline

Scalable microservices design

Production-style containerization

🧠 Why This Project Matters
This project demonstrates real-world backend engineering concepts such as:

Distributed systems

Message queues

Real-time data streaming

Microservices architecture

Infrastructure automation

