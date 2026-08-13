import json
import uuid
from typing import Dict, List
from fastapi import WebSocket

from app.core.logging import logger


class WebSocketConnectionManager:
    """
    In-Memory Realtime WebSocket Connection Manager.
    Maps active WebSocket instances to target user IDs.
    """
    def __init__(self):
        # Maps user_id -> List of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """
        Accept incoming WebSocket connection and bind to user ID.
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for User [{user_id}]. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        """
        Remove disconnected WebSocket connection.
        """
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for User [{user_id}]")

    async def send_personal_message(self, message: dict, user_id: str):
        """
        Push realtime notification payload to all active WebSocket sessions of a specific user.
        """
        target_connections = self.active_connections.get(str(user_id), [])
        for connection in target_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed to send WS message to user {user_id}: {str(e)}")

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.
        """
        payload = json.dumps(message)
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(payload)
                except Exception as e:
                    logger.warning(f"Broadcast failed for connection: {str(e)}")


ws_manager = WebSocketConnectionManager()
