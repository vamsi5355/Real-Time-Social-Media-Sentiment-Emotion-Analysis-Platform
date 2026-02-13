import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("AlertService")

MONGO_URI = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("MONGO_DATABASE", "sentiment_db")
NEGATIVE_SENTIMENT_THRESHOLD = float(os.getenv("NEGATIVE_SENTIMENT_THRESHOLD", 0.7))
ALERT_WINDOW_MINUTES = int(os.getenv("ALERT_WINDOW_MINUTES", 5))


class AlertService:
    """
    Service for monitoring sentiment metrics and triggering alerts.
    """

    def __init__(self, threshold: float = None, window_minutes: int = None):
        """
        Initialize the AlertService.
        
        Args:
            threshold: Negative sentiment percentage threshold (0-1)
            window_minutes: Time window for analysis in minutes
        """
        self.threshold = threshold or NEGATIVE_SENTIMENT_THRESHOLD
        self.window_minutes = window_minutes or ALERT_WINDOW_MINUTES
        
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client[DB_NAME]

    def check_negative_sentiment_threshold(self) -> Optional[Dict]:
        """
        Check if negative sentiment percentage exceeds threshold.
        
        Returns:
            Alert dict if threshold exceeded, None otherwise
        """
        window_start = datetime.now(timezone.utc) - timedelta(minutes=self.window_minutes)
        window_end = datetime.now(timezone.utc)
        
        try:
            # Aggregate sentiment counts within window
            pipeline = [
                {
                    "$match": {
                        "analyzed_at": {
                            "$gte": window_start,
                            "$lte": window_end
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
            if total == 0:
                return None
            
            negative_count = next((r["count"] for r in results if r["_id"] == "negative"), 0)
            negative_percentage = (negative_count / total) * 100
            
            if negative_percentage >= (self.threshold * 100):
                alert = {
                    "alert_type": "negative_sentiment_spike",
                    "threshold_value": self.threshold * 100,
                    "actual_value": negative_percentage,
                    "window_start": window_start,
                    "window_end": window_end,
                    "post_count": total,
                    "triggered_at": datetime.now(timezone.utc),
                    "details": {
                        "positive_count": next((r["count"] for r in results if r["_id"] == "positive"), 0),
                        "negative_count": negative_count,
                        "neutral_count": next((r["count"] for r in results if r["_id"] == "neutral"), 0),
                    }
                }
                
                # Store alert in database
                self.db.sentiment_alerts.insert_one(alert)
                logger.warning(f"Alert triggered: {alert['alert_type']} - {negative_percentage:.1f}%")
                
                return alert
            
            return None
        except Exception as e:
            logger.error(f"Error checking sentiment threshold: {e}")
            return None

    def check_spike(self, window_minutes: int = None) -> Optional[Dict]:
        """
        Check for sudden spike in post volume.
        
        Args:
            window_minutes: Time window for comparison
            
        Returns:
            Alert dict if spike detected, None otherwise
        """
        window = window_minutes or self.window_minutes
        current_window_start = datetime.now(timezone.utc) - timedelta(minutes=window)
        previous_window_start = current_window_start - timedelta(minutes=window)
        previous_window_end = current_window_start
        
        try:
            current_count = self.db.sentiment_analysis.count_documents({
                "analyzed_at": {"$gte": current_window_start}
            })
            
            previous_count = self.db.sentiment_analysis.count_documents({
                "analyzed_at": {
                    "$gte": previous_window_start,
                    "$lt": previous_window_end
                }
            })
            
            if previous_count == 0:
                return None
            
            spike_ratio = current_count / previous_count
            
            if spike_ratio > 2.0:  # More than 2x increase
                alert = {
                    "alert_type": "post_volume_spike",
                    "threshold_value": 2.0,
                    "actual_value": spike_ratio,
                    "window_start": current_window_start,
                    "window_end": datetime.now(timezone.utc),
                    "post_count": current_count,
                    "triggered_at": datetime.now(timezone.utc),
                    "details": {
                        "current_posts": current_count,
                        "previous_posts": previous_count
                    }
                }
                
                self.db.sentiment_alerts.insert_one(alert)
                logger.warning(f"Alert triggered: {alert['alert_type']} - {spike_ratio:.1f}x")
                
                return alert
            
            return None
        except Exception as e:
            logger.error(f"Error checking volume spike: {e}")
            return None

    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        try:
            alerts = list(self.db.sentiment_alerts.find()
                         .sort("triggered_at", -1)
                         .limit(limit))
            
            # Convert ObjectId to string
            for alert in alerts:
                alert["_id"] = str(alert["_id"])
            
            return alerts
        except Exception as e:
            logger.error(f"Error retrieving alerts: {e}")
            return []

    def close(self):
        """Close MongoDB connection."""
        if self.mongo_client:
            self.mongo_client.close()
