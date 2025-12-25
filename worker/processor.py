import os
from datetime import datetime, timezone
from pymongo import MongoClient, UpdateOne

MONGO_URI = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("MONGO_DATABASE")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def save_post_and_analysis(post: dict, sentiment: dict, emotion: dict):
    """
    Save post + analysis to MongoDB.
    If post already exists, update ingested_at.
    """

    now = datetime.now(timezone.utc)

    # 1️⃣ Upsert post
    db.social_media_posts.update_one(
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

    # 2️⃣ Insert sentiment analysis
    db.sentiment_analysis.insert_one(
        {
            "post_id": post["post_id"],
            "model_name": sentiment["model_name"],
            "sentiment_label": sentiment["sentiment_label"],
            "confidence_score": sentiment["confidence_score"],
            "emotion": emotion["emotion"],
            "analyzed_at": now,
        }
    )
