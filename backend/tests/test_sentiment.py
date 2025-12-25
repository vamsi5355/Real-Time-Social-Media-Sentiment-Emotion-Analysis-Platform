from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_sentiment_distribution_structure():
    response = client.get("/api/sentiment/distribution")
    data = response.json()

    assert isinstance(data["distribution"]["positive"], int)
    assert isinstance(data["distribution"]["neutral"], int)
    assert isinstance(data["distribution"]["negative"], int)