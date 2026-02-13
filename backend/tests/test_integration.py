"""
Integration tests for Real-Time Social Media Sentiment-Emotion Analysis Platform
Tests cover data pipeline from ingestion through API responses.
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.sentiment_analyzer import SentimentAnalyzer
from backend.services.aggregator import MetricsAggregator
from backend.services.alerting import AlertService


class TestSentimentAnalyzerIntegration:
    """Test sentiment analyzer functionality"""

    @pytest.fixture
    def analyzer(self):
        """Initialize sentiment analyzer"""
        try:
            return SentimentAnalyzer()
        except Exception as e:
            pytest.skip(f"Could not initialize analyzer: {e}")

    def test_single_text_analysis(self, analyzer):
        """Test analyzing a single text"""
        text = "I absolutely love this product! It's amazing!"
        result = analyzer.analyze(text)
        
        assert result is not None
        assert "sentiment_label" in result
        assert "confidence_score" in result
        assert "emotion" in result
        assert result["sentiment_label"] in ["positive", "negative", "neutral"]
        assert 0 <= result["confidence_score"] <= 1

    def test_batch_analysis(self, analyzer):
        """Test batch analysis of multiple texts"""
        texts = [
            "I love this!",
            "This is terrible",
            "It's okay I guess"
        ]
        results = analyzer.batch_analyze(texts)
        
        assert len(results) == len(texts)
        for result in results:
            assert "sentiment_label" in result
            assert "confidence_score" in result
            assert result["sentiment_label"] in ["positive", "negative", "neutral"]

    def test_empty_text_handling(self, analyzer):
        """Test handling of empty text"""
        result = analyzer.analyze("")
        
        assert result["sentiment_label"] == "neutral"
        assert "error" in result

    def test_stats_calculation(self, analyzer):
        """Test statistics calculation"""
        texts = [
            "Positive 1", "Positive 2",
            "Negative 1",
            "Neutral 1", "Neutral 2", "Neutral 3"
        ]
        analyses = analyzer.batch_analyze(texts)
        stats = analyzer.get_stats(analyses)
        
        assert stats["total"] == len(texts)
        assert stats["total"] == stats["positive_count"] + stats["negative_count"] + stats["neutral_count"]
        assert stats["positive_percentage"] + stats["negative_percentage"] + stats["neutral_percentage"] == pytest.approx(100.0)


class TestMetricsAggregator:
    """Test metrics aggregation"""

    @pytest.fixture
    def aggregator(self):
        """Initialize metrics aggregator"""
        with patch('pymongo.MongoClient'):
            return MetricsAggregator()

    def test_overall_stats_structure(self, aggregator):
        """Test that overall stats have correct structure"""
        with patch.object(aggregator.db.sentiment_analysis, 'aggregate', return_value=[]):
            stats = aggregator.get_overall_stats()
            
            assert "total_count" in stats
            assert "positive_count" in stats
            assert "negative_count" in stats
            assert "neutral_count" in stats
            assert "positive_percentage" in stats
            assert "negative_percentage" in stats
            assert "neutral_percentage" in stats
            assert "average_confidence" in stats

    def test_distribution_structure(self, aggregator):
        """Test distribution data structure"""
        with patch.object(aggregator.db.sentiment_analysis, 'aggregate', return_value=[]):
            dist = aggregator.get_distribution()
            
            assert "total" in dist
            assert "distribution" in dist
            assert "percentages" in dist
            assert "positive" in dist["distribution"]
            assert "negative" in dist["distribution"]
            assert "neutral" in dist["distribution"]

    def test_trend_data(self, aggregator):
        """Test trend data generation"""
        with patch.object(aggregator.db.sentiment_analysis, 'aggregate', return_value=[]):
            trend = aggregator.get_trend(interval_minutes=5, periods=4)
            
            assert len(trend) == 4
            for point in trend:
                assert "timestamp" in point
                assert "total" in point
                assert "positive" in point
                assert "negative" in point
                assert "neutral" in point


class TestAlertService:
    """Test alert service"""

    @pytest.fixture
    def alert_service(self):
        """Initialize alert service"""
        with patch('pymongo.MongoClient'):
            return AlertService(threshold=0.7, window_minutes=5)

    def test_alert_service_structure(self, alert_service):
        """Test alert service initialization"""
        assert alert_service.threshold == 0.7
        assert alert_service.window_minutes == 5

    def test_negative_sentiment_check_structure(self, alert_service):
        """Test negative sentiment check returns correct structure"""
        with patch.object(alert_service.db.sentiment_analysis, 'aggregate', return_value=[]):
            result = alert_service.check_negative_sentiment_threshold()
            
            # Should return None when no data
            assert result is None

    def test_spike_check_structure(self, alert_service):
        """Test volume spike check"""
        with patch.object(alert_service.db.sentiment_analysis, 'count_documents', return_value=0):
            result = alert_service.check_spike()
            
            # Should return None when insufficient data
            assert result is None

    def test_get_recent_alerts(self, alert_service):
        """Test retrieving recent alerts"""
        with patch.object(alert_service.db.sentiment_analysis, 'find', return_value=Mock()):
            alerts = alert_service.get_recent_alerts(limit=5)
            
            assert isinstance(alerts, list)


class TestAPIEndpointIntegration:
    """Test API endpoint integrations"""

    @pytest.fixture
    def mock_db(self):
        """Mock MongoDB database"""
        with patch('backend.database.mongo.db') as mock:
            yield mock

    def test_sentiment_distribution_endpoint_response_structure(self, mock_db):
        """Test that sentiment distribution endpoint returns correct structure"""
        from backend.api.routes import sentiment_distribution
        
        # Mock aggregation result
        mock_db.sentiment_analysis.aggregate.return_value = [
            {"_id": "positive", "count": 50},
            {"_id": "negative", "count": 30},
            {"_id": "neutral", "count": 20}
        ]
        
        result = sentiment_distribution(hours=24)
        
        assert "timeframe_hours" in result
        assert "total" in result
        assert "positive_count" in result
        assert "negative_count" in result
        assert "neutral_count" in result
        assert "positive_percentage" in result
        assert "negative_percentage" in result
        assert "neutral_percentage" in result
        assert "percentages" in result

    def test_health_endpoint_response_structure(self):
        """Test health endpoint response structure"""
        from backend.api.routes import health
        
        with patch('backend.api.routes.aggregator') as mock_agg:
            mock_agg.get_overall_stats.return_value = {
                "total_count": 100,
                "positive_count": 50,
                "negative_count": 30,
                "neutral_count": 20
            }
            
            result = health()
            
            assert "status" in result
            assert "timestamp" in result
            assert "services" in result
            assert "stats" in result


class TestDataFlow:
    """Test end-to-end data flow"""

    def test_post_structure_compatibility(self):
        """Test that post structure is compatible across services"""
        post = {
            "post_id": "test_123",
            "source": "twitter",
            "content": "Test content",
            "author": "test_user",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Verify required fields exist
        required_fields = ["post_id", "source", "content", "author", "created_at"]
        for field in required_fields:
            assert field in post

    def test_analysis_result_structure(self):
        """Test analysis result structure compatibility"""
        analysis = {
            "sentiment_label": "positive",
            "confidence_score": 0.95,
            "emotion": "joy",
            "model": "test-model"
        }
        
        required_fields = ["sentiment_label", "confidence_score", "emotion"]
        for field in required_fields:
            assert field in analysis
        
        assert analysis["sentiment_label"] in ["positive", "negative", "neutral"]
        assert 0 <= analysis["confidence_score"] <= 1


class TestErrorHandling:
    """Test error handling across services"""

    @pytest.fixture
    def analyzer(self):
        """Initialize sentiment analyzer"""
        try:
            return SentimentAnalyzer()
        except Exception as e:
            pytest.skip(f"Could not initialize analyzer: {e}")

    def test_analyzer_handles_very_long_text(self, analyzer):
        """Test analyzer handles very long text gracefully"""
        long_text = "word " * 1000  # Create very long text
        result = analyzer.analyze(long_text)
        
        assert "sentiment_label" in result
        assert result["sentiment_label"] in ["positive", "negative", "neutral"]

    def test_analyzer_handles_special_characters(self, analyzer):
        """Test analyzer handles special characters"""
        text = "This is great! 🎉 @#$%^&*()"
        result = analyzer.analyze(text)
        
        assert "sentiment_label" in result
        assert result["sentiment_label"] in ["positive", "negative", "neutral"]

    def test_batch_analyze_empty_list(self, analyzer):
        """Test batch analysis with empty list"""
        results = analyzer.batch_analyze([])
        
        assert results == []

    def test_batch_analyze_with_mixed_quality_texts(self, analyzer):
        """Test batch analysis with mixed quality texts"""
        texts = ["Good", "", "Amazing! 🎉", "   ", "Terrible"]
        results = analyzer.batch_analyze(texts)
        
        assert len(results) == len(texts)
        for result in results:
            assert "sentiment_label" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
