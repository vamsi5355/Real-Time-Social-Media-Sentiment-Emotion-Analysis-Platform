import os
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

import torch
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("SentimentAnalyzer")

# Models configuration
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")


class SentimentAnalyzer:
    """
    Sentiment analyzer using HuggingFace transformers.
    Provides both individual and batch analysis with emotion detection.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize the sentiment analyzer.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name or HUGGINGFACE_MODEL
        device = 0 if torch.cuda.is_available() else -1
        
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=device
            )
            logger.info(f"Loaded sentiment model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            raise

    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment_label, confidence_score, emotion, and metadata
        """
        if not text or not text.strip():
            return {
                "sentiment_label": "neutral",
                "confidence_score": 0.0,
                "emotion": "neutral",
                "error": "Empty text"
            }

        try:
            result = self.sentiment_pipeline(text[:512])[0]
            
            # Normalize label
            label = result["label"].lower()
            if label == "positive":
                sentiment_label = "positive"
            elif label == "negative":
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            # Map to emotion
            emotion = self._map_to_emotion(sentiment_label, result["score"])
            
            return {
                "sentiment_label": sentiment_label,
                "confidence_score": float(result["score"]),
                "emotion": emotion,
                "model": self.model_name
            }
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                "sentiment_label": "neutral",
                "confidence_score": 0.0,
                "emotion": "neutral",
                "error": str(e)
            }

    def batch_analyze(self, texts: List[str], batch_size: int = 32) -> List[Dict]:
        """
        Analyze sentiment of multiple texts in batches.
        
        Args:
            texts: List of texts to analyze
            batch_size: Batch size for processing
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                batch_results = self.sentiment_pipeline(batch)
                
                for j, result in enumerate(batch_results):
                    label = result["label"].lower()
                    if label == "positive":
                        sentiment_label = "positive"
                    elif label == "negative":
                        sentiment_label = "negative"
                    else:
                        sentiment_label = "neutral"
                    
                    emotion = self._map_to_emotion(sentiment_label, result["score"])
                    
                    results.append({
                        "sentiment_label": sentiment_label,
                        "confidence_score": float(result["score"]),
                        "emotion": emotion,
                        "model": self.model_name
                    })
            except Exception as e:
                logger.error(f"Error in batch analysis: {e}")
                # Add error results for failed items
                for _ in batch:
                    results.append({
                        "sentiment_label": "neutral",
                        "confidence_score": 0.0,
                        "emotion": "neutral",
                        "error": str(e)
                    })
        
        return results

    def _map_to_emotion(self, sentiment: str, confidence: float) -> str:
        """
        Map sentiment to specific emotion.
        
        Args:
            sentiment: Sentiment label (positive, negative, neutral)
            confidence: Confidence score (0-1)
            
        Returns:
            Emotion label
        """
        if sentiment == "positive":
            if confidence > 0.9:
                return "joy"
            elif confidence > 0.7:
                return "happiness"
            else:
                return "contentment"
        elif sentiment == "negative":
            if confidence > 0.9:
                return "anger"
            elif confidence > 0.7:
                return "disappointment"
            else:
                return "sadness"
        else:
            return "neutral"

    def get_stats(self, analyses: List[Dict]) -> Dict:
        """
        Calculate statistics from multiple analyses.
        
        Args:
            analyses: List of analysis results
            
        Returns:
            Dictionary with aggregated statistics
        """
        if not analyses:
            return {
                "total": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "neutral_percentage": 0.0,
                "average_confidence": 0.0
            }
        
        total = len(analyses)
        positive_count = sum(1 for a in analyses if a.get("sentiment_label") == "positive")
        negative_count = sum(1 for a in analyses if a.get("sentiment_label") == "negative")
        neutral_count = sum(1 for a in analyses if a.get("sentiment_label") == "neutral")
        
        avg_confidence = sum(a.get("confidence_score", 0) for a in analyses) / total if total > 0 else 0
        
        return {
            "total": total,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_percentage": (positive_count / total * 100) if total > 0 else 0.0,
            "negative_percentage": (negative_count / total * 100) if total > 0 else 0.0,
            "neutral_percentage": (neutral_count / total * 100) if total > 0 else 0.0,
            "average_confidence": avg_confidence
        }
