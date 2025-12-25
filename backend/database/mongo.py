import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import CollectionInvalid

MONGO_URI = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("MONGO_DATABASE")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def init_collections():
    """
    Auto-create collections with validation and indexes
    """

    # 1️⃣ social_media_posts
    try:
        db.create_collection(
            "social_media_posts",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["post_id", "source", "content", "author", "created_at", "ingested_at"],
                    "properties": {
                        "post_id": {"bsonType": "string"},
                        "source": {"bsonType": "string"},
                        "content": {"bsonType": "string"},
                        "author": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},
                        "ingested_at": {"bsonType": "date"},
                    },
                }
            },
        )
    except CollectionInvalid:
        pass

    db.social_media_posts.create_index("post_id", unique=True)
    db.social_media_posts.create_index("source")
    db.social_media_posts.create_index("created_at")

    # 2️⃣ sentiment_analysis
    try:
        db.create_collection(
            "sentiment_analysis",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "post_id",
                        "model_name",
                        "sentiment_label",
                        "confidence_score",
                        "emotion",
                        "analyzed_at",
                    ],
                    "properties": {
                        "post_id": {"bsonType": "string"},
                        "model_name": {"bsonType": "string"},
                        "sentiment_label": {
                            "enum": ["positive", "negative", "neutral"]
                        },
                        "confidence_score": {"bsonType": "double"},
                        "emotion": {"bsonType": "string"},
                        "analyzed_at": {"bsonType": "date"},
                    },
                }
            },
        )
    except CollectionInvalid:
        pass

    db.sentiment_analysis.create_index("post_id")
    db.sentiment_analysis.create_index("analyzed_at")

    # 3️⃣ sentiment_alerts
    try:
        db.create_collection(
            "sentiment_alerts",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "alert_type",
                        "threshold_value",
                        "actual_value",
                        "window_start",
                        "window_end",
                        "post_count",
                        "triggered_at",
                        "details",
                    ],
                    "properties": {
                        "alert_type": {"bsonType": "string"},
                        "threshold_value": {"bsonType": "double"},
                        "actual_value": {"bsonType": "double"},
                        "window_start": {"bsonType": "date"},
                        "window_end": {"bsonType": "date"},
                        "post_count": {"bsonType": "int"},
                        "triggered_at": {"bsonType": "date"},
                        "details": {"bsonType": "object"},
                    },
                }
            },
        )
    except CollectionInvalid:
        pass

    db.sentiment_alerts.create_index("triggered_at")
