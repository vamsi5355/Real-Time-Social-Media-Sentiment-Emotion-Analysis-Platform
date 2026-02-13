from fastapi import APIRouter, Query
from datetime import datetime, timedelta, timezone
from typing import Optional
from database.mongo import db
from services.aggregator import MetricsAggregator
from services.alerting import AlertService
from bson import ObjectId


def serialize_mongo(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string."""
    doc["_id"] = str(doc["_id"])
    return doc


router = APIRouter(prefix="/api")
aggregator = MetricsAggregator()
alert_service = AlertService()


@router.get("/health")
def health():
    """Health check endpoint with service status."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "services": {
            "database": "connected",
            "redis": "connected",
            "sentiment_analysis": "operational"
        },
        "stats": aggregator.get_overall_stats()
    }


@router.get("/posts")
def get_posts(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sentiment: Optional[str] = None
):
    """Get posts with pagination and optional sentiment filter."""
    query = {}
    if sentiment and sentiment in ["positive", "negative", "neutral"]:
        query["sentiment_label"] = sentiment

    cursor = db.sentiment_analysis.aggregate([
        {"$match": query},
        {"$skip": offset},
        {"$limit": limit},
        {"$sort": {"analyzed_at": -1}}
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
def sentiment_distribution(hours: int = Query(24, ge=1, le=720)):
    """Get sentiment distribution for a time period."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    pipeline = [
        {"$match": {"analyzed_at": {"$gte": since}}},
        {"$group": {
            "_id": "$sentiment_label",
            "count": {"$sum": 1},
            "avg_confidence": {"$avg": "$confidence_score"}
        }}
    ]

    results = list(db.sentiment_analysis.aggregate(pipeline))

    total = sum(r["count"] for r in results)
    
    if total == 0:
        return {
            "timeframe_hours": hours,
            "total": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "positive_percentage": 0.0,
            "negative_percentage": 0.0,
            "neutral_percentage": 0.0,
            "percentages": {
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "neutral_percentage": 0.0
            }
        }

    positive_count = next((r["count"] for r in results if r["_id"] == "positive"), 0)
    negative_count = next((r["count"] for r in results if r["_id"] == "negative"), 0)
    neutral_count = next((r["count"] for r in results if r["_id"] == "neutral"), 0)

    return {
        "timeframe_hours": hours,
        "total": total,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "positive_percentage": (positive_count / total * 100) if total > 0 else 0,
        "negative_percentage": (negative_count / total * 100) if total > 0 else 0,
        "neutral_percentage": (neutral_count / total * 100) if total > 0 else 0,
        "percentages": {
            "positive_percentage": (positive_count / total * 100) if total > 0 else 0,
            "negative_percentage": (negative_count / total * 100) if total > 0 else 0,
            "neutral_percentage": (neutral_count / total * 100) if total > 0 else 0
        }
    }


@router.get("/sentiment/stats")
def sentiment_stats():
    """Get overall sentiment statistics."""
    return aggregator.get_overall_stats()


@router.get("/sentiment/trend")
def sentiment_trend(interval_minutes: int = Query(5, ge=1, le=60), periods: int = Query(12, ge=1, le=48)):
    """Get sentiment trend over time."""
    return {
        "trend": aggregator.get_trend(interval_minutes, periods),
        "interval_minutes": interval_minutes,
        "periods": periods
    }


@router.get("/alerts")
def get_alerts(limit: int = Query(10, ge=1, le=100)):
    """Get recent alerts."""
    return {
        "alerts": alert_service.get_recent_alerts(limit),
        "count": len(alert_service.get_recent_alerts(limit))
    }


@router.post("/alerts/check")
def check_alerts():
    """Manually trigger alert checks."""
    alerts = []
    
    negative_alert = alert_service.check_negative_sentiment_threshold()
    if negative_alert:
        alerts.append(negative_alert)
    
    spike_alert = alert_service.check_spike()
    if spike_alert:
        alerts.append(spike_alert)
    
    return {
        "alerts_triggered": len(alerts),
        "alerts": alerts
    }
