from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class SocialMediaPost(BaseModel):
    post_id: str
    source: str
    content: str
    author: str
    created_at: datetime
    ingested_at: datetime


class SentimentAnalysis(BaseModel):
    post_id: str
    model_name: str
    sentiment_label: str
    confidence_score: float
    emotion: str
    analyzed_at: datetime


class SentimentAlert(BaseModel):
    alert_type: str
    threshold_value: float
    actual_value: float
    window_start: datetime
    window_end: datetime
    post_count: int
    triggered_at: datetime
    details: Dict
