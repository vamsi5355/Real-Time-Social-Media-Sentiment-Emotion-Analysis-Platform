import os
import sys
import time
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import redis
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.sentiment_analyzer import SentimentAnalyzer

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Worker")

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")
GROUP_NAME = os.getenv("REDIS_CONSUMER_GROUP", "sentiment_processor_group")
CONSUMER_NAME = f"worker-{os.getpid()}"

MONGO_URI = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("MONGO_DATABASE", "sentiment_db")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
PROCESS_TIMEOUT = int(os.getenv("PROCESS_TIMEOUT", 5000))


class SentimentWorker:
    """
    Worker that processes posts from Redis stream and stores sentiment analysis in MongoDB.
    """

    def __init__(self, redis_host: str = None, redis_port: int = None, batch_size: int = None):
        """
        Initialize the SentimentWorker.
        
        Args:
            redis_host: Redis hostname
            redis_port: Redis port
            batch_size: Batch size for processing
        """
        self.redis_host = redis_host or REDIS_HOST
        self.redis_port = redis_port or REDIS_PORT
        self.batch_size = batch_size or BATCH_SIZE
        
        # Initialize Redis client
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            decode_responses=True
        )
        
        # Initialize MongoDB client
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client[DB_NAME]
        
        # Initialize sentiment analyzer
        try:
            self.analyzer = SentimentAnalyzer()
            logger.info("Sentiment analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzer: {e}")
            raise

    def _create_consumer_group(self):
        """Create Redis consumer group if it doesn't exist."""
        try:
            self.redis_client.xgroup_create(
                STREAM_NAME,
                GROUP_NAME,
                id="0",
                mkstream=True
            )
            logger.info(f"Consumer group '{GROUP_NAME}' created")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group '{GROUP_NAME}' already exists")
            else:
                raise

    def _save_post_and_analysis(self, post: dict, analysis: dict) -> bool:
        """
        Save post and sentiment analysis to MongoDB.
        
        Args:
            post: Post data from Redis
            analysis: Sentiment analysis result
            
        Returns:
            True if successful, False otherwise
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Upsert post to collection
            self.db.social_media_posts.update_one(
                {"post_id": post["post_id"]},
                {
                    "$setOnInsert": {
                        "post_id": post["post_id"],
                        "source": post["source"],
                        "content": post["content"],
                        "author": post["author"],
                        "created_at": datetime.fromisoformat(post["created_at"]),
                    },
                    "$set": {"ingested_at": now},
                },
                upsert=True,
            )
            
            # Insert sentiment analysis record
            self.db.sentiment_analysis.insert_one({
                "post_id": post["post_id"],
                "model_name": analysis.get("model", "unknown"),
                "sentiment_label": analysis["sentiment_label"],
                "confidence_score": analysis["confidence_score"],
                "emotion": analysis["emotion"],
                "analyzed_at": now,
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to save post analysis: {e}")
            return False

    def _process_message(self, message_id: str, data: dict) -> bool:
        """
        Process a single message from the Redis stream.
        
        Args:
            message_id: Redis message ID
            data: Message data
            
        Returns:
            True if successfully processed and ACKed, False otherwise
        """
        try:
            # Extract content and perform sentiment analysis
            content = data.get("content", "")
            
            analysis = self.analyzer.analyze(content)
            
            # Save to MongoDB
            if not self._save_post_and_analysis(data, analysis):
                logger.error(f"Failed to save analysis for {message_id}")
                return False
            
            # Acknowledge message in Redis
            self.redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
            logger.info(f"Processed and ACKed message {message_id} - Sentiment: {analysis['sentiment_label']}")
            
            return True
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
            return False

    def _process_batch(self, messages: List[Tuple[str, dict]]) -> int:
        """
        Process a batch of messages concurrently.
        
        Args:
            messages: List of (message_id, data) tuples
            
        Returns:
            Number of successfully processed messages
        """
        processed_count = 0
        texts = [data.get("content", "") for _, data in messages]
        
        try:
            # Batch analyze all texts
            analyses = self.analyzer.batch_analyze(texts)
            
            # Save results to MongoDB
            for (message_id, data), analysis in zip(messages, analyses):
                if self._save_post_and_analysis(data, analysis):
                    self.redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
                    logger.info(f"Batch processed message {message_id}")
                    processed_count += 1
                else:
                    logger.error(f"Failed to save analysis for batch message {message_id}")
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
        
        return processed_count

    def process(self):
        """
        Main processing loop that reads from Redis stream and processes messages.
        """
        self._create_consumer_group()
        logger.info(f"Sentiment Worker started (batch_size={self.batch_size})")
        
        try:
            while True:
                # Read messages from Redis stream
                messages = self.redis_client.xreadgroup(
                    GROUP_NAME,
                    CONSUMER_NAME,
                    {STREAM_NAME: ">"},
                    count=self.batch_size,
                    block=PROCESS_TIMEOUT
                )
                
                if not messages:
                    continue
                
                # Extract messages
                message_list = []
                for stream, entries in messages:
                    for message_id, data in entries:
                        message_list.append((message_id, data))
                
                # Process batch
                if len(message_list) > 1:
                    logger.info(f"Processing batch of {len(message_list)} messages")
                    self._process_batch(message_list)
                else:
                    # Single message
                    for message_id, data in message_list:
                        self._process_message(message_id, data)
        
        except KeyboardInterrupt:
            logger.info("Shutting down worker...")
        except Exception as e:
            logger.error(f"Unexpected error in process loop: {e}")
        finally:
            self.mongo_client.close()
            logger.info("Worker stopped")

    def close(self):
        """Clean up resources."""
        if self.mongo_client:
            self.mongo_client.close()
        logger.info("Worker resources closed")


def main():
    worker = SentimentWorker()
    try:
        worker.process()
    finally:
        worker.close()


if __name__ == "__main__":
    main()
