from fastapi import APIRouter, WebSocket
from datetime import datetime
import asyncio

ws_router = APIRouter()

clients = set()


@ws_router.websocket("/ws/sentiment")
async def sentiment_ws(ws: WebSocket):
    await ws.accept()
    clients.add(ws)

    await ws.send_json({
        "type": "connected",
        "message": "Connected to sentiment stream",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    try:
        while True:
            await asyncio.sleep(30)
            await ws.send_json({
                "type": "metrics_update",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "data": {
                    "status": "live"
                }
            })
    except Exception:
        clients.remove(ws)
