from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional
from database.mongo import db
from bson import ObjectId

def serialize_mongo(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": "connected",
            "redis": "connected"
        }
    }

@router.get("/posts")
def get_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sentiment: Optional[str] = None
):
    query = {}
    if sentiment:
        query["sentiment_label"] = sentiment

    cursor = db.sentiment_analysis.aggregate([
        {"$match": query},
        {"$skip": offset},
        {"$limit": limit}
    ])

    posts = [serialize_mongo(p) for p in cursor]
    total = db.sentiment_analysis.count_documents(query)

    return {
        "posts": posts,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/sentiment/distribution")
def sentiment_distribution(hours: int = 24):
    since = datetime.utcnow() - timedelta(hours=hours)

    pipeline = [
        {"$match": {"analyzed_at": {"$gte": since}}},
        {"$group": {"_id": "$sentiment_label", "count": {"$sum": 1}}}
    ]

    results = db.sentiment_analysis.aggregate(pipeline)

    distribution = {"positive": 0, "negative": 0, "neutral": 0}
    total = 0

    for r in results:
        distribution[r["_id"]] = r["count"]
        total += r["count"]

    return {
        "timeframe_hours": hours,
        "distribution": distribution,
        "total": total
    }
