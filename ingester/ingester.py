import os
import time
import json
import random
import logging
import asyncio
from datetime import datetime, timezone

import redis.asyncio as aioredis
from dotenv import load_dotenv

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Ingester")

# Redis config
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")

POSTS_PER_MINUTE = int(os.getenv("POSTS_PER_MINUTE", 60))
SLEEP_INTERVAL = 60 / POSTS_PER_MINUTE


class DataIngester:
    def __init__(self, redis_host: str = None, redis_port: int = None, posts_per_minute: int = None):
        """
        Initialize the DataIngester with async Redis client
        
        Args:
            redis_host: Redis hostname (defaults to env var)
            redis_port: Redis port (defaults to env var)
            posts_per_minute: Rate of post ingestion (defaults to env var)
        """
        self.redis_host = redis_host or REDIS_HOST
        self.redis_port = redis_port or REDIS_PORT
        self.posts_per_minute = posts_per_minute or POSTS_PER_MINUTE
        self.sleep_interval = 60 / self.posts_per_minute
        self.redis = None

        self.positive_templates = [
            "I absolutely love {product}! It works amazingly well.",
            "{product} exceeded my expectations. Fantastic experience!",
            "Super happy with {product}. Totally worth it."
        ]

        self.neutral_templates = [
            "I just tried {product} today.",
            "Using {product} for the first time.",
            "Received {product}. Testing it now."
        ]

        self.negative_templates = [
            "Very disappointed with {product}.",
            "Terrible experience using {product}.",
            "{product} did not meet my expectations at all."
        ]

        self.products = [
            "iPhone 16",
            "Tesla Model 3",
            "ChatGPT",
            "Netflix",
            "Amazon Prime",
            "Google Pixel",
            "Spotify"
        ]

    async def connect(self):
        """Initialize async Redis connection"""
        try:
            self.redis = await aioredis.from_url(
                f"redis://{self.redis_host}:{self.redis_port}",
                decode_responses=True
            )
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    def generate_post(self) -> dict:
        sentiment_roll = random.random()
        product = random.choice(self.products)

        if sentiment_roll < 0.4:
            template = random.choice(self.positive_templates)
        elif sentiment_roll < 0.7:
            template = random.choice(self.neutral_templates)
        else:
            template = random.choice(self.negative_templates)

        content = template.format(product=product)

        return {
            "post_id": f"post_{int(time.time() * 1000)}_{random.randint(1000,9999)}",
            "source": random.choice(["reddit", "twitter", "facebook"]),
            "content": content * random.randint(3, 8),
            "author": f"user_{random.randint(1000, 9999)}",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    async def publish_post(self, post: dict) -> bool:
        try:
            await self.redis.xadd(STREAM_NAME, post)
            logger.info(f"Published post {post['post_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish post: {e}")
            return False

    async def start(self):
        logger.info(f"Starting Data Ingester... (Posts/minute: {self.posts_per_minute})")
        await self.connect()
        try:
            while True:
                post = self.generate_post()
                await self.publish_post(post)
                await asyncio.sleep(self.sleep_interval)
        except KeyboardInterrupt:
            logger.info("Shutting down ingester...")
        finally:
            await self.disconnect()


async def main():
    ingester = DataIngester()
    await ingester.start()


if __name__ == "__main__":
    asyncio.run(main())
