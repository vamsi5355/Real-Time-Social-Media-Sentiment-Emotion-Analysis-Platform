from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_websocket_connect():
    with client.websocket_connect("/ws/sentiment") as ws:
        ws.send_text("ping")
        msg = ws.receive_text()
        assert msg is not None