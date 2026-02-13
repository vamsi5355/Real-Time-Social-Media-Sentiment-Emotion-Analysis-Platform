import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("MetricsAggregator")

MONGO_URI = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("MONGO_DATABASE", "sentiment_db")


class MetricsAggregator:
    """
    Service for aggregating sentiment metrics across different time windows.
    """

    def __init__(self):
        """Initialize the MetricsAggregator."""
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client[DB_NAME]

    def get_overall_stats(self) -> Dict:
        """
        Get overall sentiment statistics across all posts.
        
        Returns:
            Dictionary with overall metrics
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$sentiment_label",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence_score"}
                    }
                }
            ]
            
            results = list(self.db.sentiment_analysis.aggregate(pipeline))
            
            total = sum(r["count"] for r in results)
            if total == 0:
                return {
                    "total_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "positive_percentage": 0.0,
                    "negative_percentage": 0.0,
                    "neutral_percentage": 0.0,
                    "average_confidence": 0.0
                }
            
            positive_count = next((r["count"] for r in results if r["_id"] == "positive"), 0)
            negative_count = next((r["count"] for r in results if r["_id"] == "negative"), 0)
            neutral_count = next((r["count"] for r in results if r["_id"] == "neutral"), 0)
            
            avg_confidence = sum(
                r["avg_confidence"] * r["count"] for r in results
            ) / total if total > 0 else 0
            
            return {
                "total_count": total,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_percentage": (positive_count / total * 100),
                "negative_percentage": (negative_count / total * 100),
                "neutral_percentage": (neutral_count / total * 100),
                "average_confidence": avg_confidence
            }
        except Exception as e:
            logger.error(f"Error calculating overall stats: {e}")
            return {}

    def get_time_window_stats(self, minutes: int = 60) -> Dict:
        """
        Get sentiment statistics for a specific time window.
        
        Args:
            minutes: Time window in minutes
            
        Returns:
            Dictionary with time-window metrics
        """
        try:
            window_start = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            
            pipeline = [
                {
                    "$match": {
                        "analyzed_at": {
                            "$gte": window_start
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$sentiment_label",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence_score"}
                    }
                }
            ]
            
            results = list(self.db.sentiment_analysis.aggregate(pipeline))
            
            total = sum(r["count"] for r in results)
            if total == 0:
                return {
                    "window_minutes": minutes,
                    "total_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "positive_percentage": 0.0,
                    "negative_percentage": 0.0,
                    "neutral_percentage": 0.0,
                    "average_confidence": 0.0
                }
            
            positive_count = next((r["count"] for r in results if r["_id"] == "positive"), 0)
            negative_count = next((r["count"] for r in results if r["_id"] == "negative"), 0)
            neutral_count = next((r["count"] for r in results if r["_id"] == "neutral"), 0)
            
            avg_confidence = sum(
                r["avg_confidence"] * r["count"] for r in results
            ) / total if total > 0 else 0
            
            return {
                "window_minutes": minutes,
                "total_count": total,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_percentage": (positive_count / total * 100),
                "negative_percentage": (negative_count / total * 100),
                "neutral_percentage": (neutral_count / total * 100),
                "average_confidence": avg_confidence
            }
        except Exception as e:
            logger.error(f"Error calculating time window stats: {e}")
            return {}

    def get_distribution(self) -> Dict:
        """
        Get sentiment distribution with percentages.
        
        Returns:
            Dictionary with distribution data
        """
        try:
            stats = self.get_overall_stats()
            
            return {
                "total": stats.get("total_count", 0),
                "distribution": {
                    "positive": {
                        "count": stats.get("positive_count", 0),
                        "percentage": stats.get("positive_percentage", 0.0)
                    },
                    "negative": {
                        "count": stats.get("negative_count", 0),
                        "percentage": stats.get("negative_percentage", 0.0)
                    },
                    "neutral": {
                        "count": stats.get("neutral_count", 0),
                        "percentage": stats.get("neutral_percentage", 0.0)
                    }
                },
                "percentages": {
                    "positive_percentage": stats.get("positive_percentage", 0.0),
                    "negative_percentage": stats.get("negative_percentage", 0.0),
                    "neutral_percentage": stats.get("neutral_percentage", 0.0)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating distribution: {e}")
            return {}

    def get_trend(self, interval_minutes: int = 5, periods: int = 12) -> List[Dict]:
        """
        Get sentiment trend over time.
        
        Args:
            interval_minutes: Time interval for each data point
            periods: Number of periods to retrieve
            
        Returns:
            List of sentiment data points over time
        """
        try:
            trend = []
            now = datetime.now(timezone.utc)
            
            for i in range(periods - 1, -1, -1):
                window_start = now - timedelta(minutes=interval_minutes * (i + 1))
                window_end = now - timedelta(minutes=interval_minutes * i)
                
                pipeline = [
                    {
                        "$match": {
                            "analyzed_at": {
                                "$gte": window_start,
                                "$lt": window_end
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$sentiment_label",
                            "count": {"$sum": 1}
                        }
                    }
                ]
                
                results = list(self.db.sentiment_analysis.aggregate(pipeline))
                
                total = sum(r["count"] for r in results)
                
                trend.append({
                    "timestamp": window_end.isoformat(),
                    "total": total,
                    "positive": next((r["count"] for r in results if r["_id"] == "positive"), 0),
                    "negative": next((r["count"] for r in results if r["_id"] == "negative"), 0),
                    "neutral": next((r["count"] for r in results if r["_id"] == "neutral"), 0)
                })
            
            return trend
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return []

    def close(self):
        """Close MongoDB connection."""
        if self.mongo_client:
            self.mongo_client.close()
