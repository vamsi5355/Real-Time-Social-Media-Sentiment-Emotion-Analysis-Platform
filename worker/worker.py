import os
import time
import json
import logging

import redis
from dotenv import load_dotenv

from processor import save_post_and_analysis

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Worker")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = os.getenv("REDIS_STREAM_NAME")
GROUP_NAME = os.getenv("REDIS_CONSUMER_GROUP")
CONSUMER_NAME = f"worker-{os.getpid()}"

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


def create_consumer_group():
    try:
        redis_client.xgroup_create(
            STREAM_NAME,
            GROUP_NAME,
            id="0",
            mkstream=True
        )
        logger.info("Consumer group created")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            logger.info("Consumer group already exists")
        else:
            raise


def mock_sentiment_analysis(text: str) -> dict:
    """
    TEMP stub – real AI comes in STEP 5
    """
    text = text.lower()

    if any(w in text for w in ["love", "amazing", "great", "happy"]):
        return {
            "sentiment_label": "positive",
            "confidence_score": 0.9,
            "model_name": "mock-model"
        }
    if any(w in text for w in ["terrible", "hate", "disappointed"]):
        return {
            "sentiment_label": "negative",
            "confidence_score": 0.85,
            "model_name": "mock-model"
        }

    return {
        "sentiment_label": "neutral",
        "confidence_score": 0.75,
        "model_name": "mock-model"
    }


def mock_emotion_analysis(text: str) -> dict:
    return {
        "emotion": "neutral",
        "confidence_score": 0.8,
        "model_name": "mock-model"
    }


def process_message(message_id, data) -> bool:
    try:
        sentiment = mock_sentiment_analysis(data["content"])
        emotion = mock_emotion_analysis(data["content"])

        save_post_and_analysis(data, sentiment, emotion)

        redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
        logger.info(f"Processed & ACKed {message_id}")
        return True

    except Exception as e:
        logger.error(f"Failed processing {message_id}: {e}")
        return False


def run():
    create_consumer_group()
    logger.info("Worker started")

    while True:
        messages = redis_client.xreadgroup(
            GROUP_NAME,
            CONSUMER_NAME,
            {STREAM_NAME: ">"},
            count=10,
            block=5000
        )

        for stream, entries in messages:
            for message_id, data in entries:
                process_message(message_id, data)


if __name__ == "__main__":
    run()
