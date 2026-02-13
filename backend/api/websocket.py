from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import asyncio
import logging

from services.aggregator import MetricsAggregator
from services.alerting import AlertService

logger = logging.getLogger("WebSocket")

ws_router = APIRouter()

clients = set()
aggregator = MetricsAggregator()
alert_service = AlertService()


@ws_router.websocket("/ws/sentiment")
async def sentiment_ws(websocket: WebSocket):
    """WebSocket endpoint for real-time sentiment metrics."""
    await websocket.accept()
    clients.add(websocket)
    logger.info(f"New WebSocket connection. Total clients: {len(clients)}")

    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to sentiment stream",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        })

        while True:
            # Send metrics update every 5 seconds
            await asyncio.sleep(5)
            
            stats = aggregator.get_overall_stats()
            alerts = alert_service.get_recent_alerts(limit=3)
            
            message = {
                "type": "metrics_update",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "data": {
                    "sentiment_label": "mixed",
                    "confidence_score": stats.get("average_confidence", 0),
                    "stats": {
                        "total_count": stats.get("total_count", 0),
                        "positive_count": stats.get("positive_count", 0),
                        "negative_count": stats.get("negative_count", 0),
                        "neutral_count": stats.get("neutral_count", 0),
                        "positive_percentage": stats.get("positive_percentage", 0),
                        "negative_percentage": stats.get("negative_percentage", 0),
                        "neutral_percentage": stats.get("neutral_percentage", 0)
                    },
                    "recent_alerts": alerts
                }
            }
            
            await websocket.send_json(message)
    
    except WebSocketDisconnect:
        clients.discard(websocket)
        logger.info(f"WebSocket disconnected. Remaining clients: {len(clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        clients.discard(websocket)
        try:
            await websocket.close()
        except:
            pass


async def broadcast_metrics_update(stats: dict):
    """Broadcast metrics update to all connected clients."""
    if not clients:
        return
    
    message = {
        "type": "metrics_update",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "data": stats
    }
    
    disconnected_clients = set()
    for client in clients:
        try:
            await client.send_json(message)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
            disconnected_clients.add(client)
    
    # Remove disconnected clients
    for client in disconnected_clients:
        clients.discard(client)
