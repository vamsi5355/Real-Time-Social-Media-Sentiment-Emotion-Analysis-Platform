from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_sentiment_distribution():
    response = client.get("/api/sentiment/distribution")
    assert response.status_code == 200

    data = response.json()
    assert "distribution" in data

    dist = data["distribution"]
    assert "positive" in dist
    assert "neutral" in dist
    assert "negative" in dist