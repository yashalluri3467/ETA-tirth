import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("eta-service.websocket")
router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        logger.info(f"WebSocket connected for device_id: {device_id}")

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            logger.info(f"WebSocket disconnected for device_id: {device_id}")

    async def send_json(self, device_id: str, data: dict):
        if device_id in self.active_connections:
            await self.active_connections[device_id].send_json(data)


manager = ConnectionManager()


@router.websocket("/ws/eta/{device_id}")
async def websocket_eta_endpoint(websocket: WebSocket, device_id: str):
    """
    WebSocket endpoint for streaming real-time location & receiving instant ETA recalibrations.
    """
    await manager.connect(device_id, websocket)
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)

            # Echo updated ETA ping
            response = {
                "status": "connected",
                "device_id": device_id,
                "received_location": data.get("current_location"),
                "live_queue_wait_mins": 35.0,
                "alert": "Crowd density increasing near Main Gate 1",
            }
            await websocket.send_json(response)
    except WebSocketDisconnect:
        manager.disconnect(device_id)
    except Exception as e:
        logger.error(f"WebSocket error for {device_id}: {e}")
        manager.disconnect(device_id)
