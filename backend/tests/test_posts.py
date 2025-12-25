from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_posts():
    response = client.get("/api/posts?limit=5")
    assert response.status_code == 200

    data = response.json()
    assert "posts" in data
    assert isinstance(data["posts"], list)

    if len(data["posts"]) > 0:
        post = data["posts"][0]
        assert "post_id" in post
        assert "content" in post
        assert "sentiment_label" in post


def test_get_posts_min_limit():
    response = client.get("/api/posts?limit=1")
    assert response.status_code == 200