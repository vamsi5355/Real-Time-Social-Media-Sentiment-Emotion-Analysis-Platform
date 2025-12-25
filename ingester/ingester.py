import os
import time
import json
import random
import logging
from datetime import datetime, timezone

import redis
from dotenv import load_dotenv

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Ingester")

# Redis config
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("REDIS_STREAM_NAME", "social_posts_stream")

POSTS_PER_MINUTE = int(os.getenv("POSTS_PER_MINUTE", 60))
SLEEP_INTERVAL = 60 / POSTS_PER_MINUTE


class DataIngester:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

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
            "content": content * random.randint(3, 8),  # ensure 50–500 chars
            "author": f"user_{random.randint(1000, 9999)}",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    def publish_post(self, post: dict) -> bool:
        try:
            self.redis.xadd(STREAM_NAME, post)
            logger.info(f"Published post {post['post_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish post: {e}")
            return False

    def start(self):
        logger.info("Starting Data Ingester...")
        while True:
            post = self.generate_post()
            self.publish_post(post)
            time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    ingester = DataIngester()
    ingester.start()
