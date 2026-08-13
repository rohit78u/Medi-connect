from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import ws_manager
from app.core.logging import logger

router = APIRouter(prefix="/ws", tags=["Realtime WebSockets"])


@router.websocket("/notifications/{user_id}")
async def websocket_notifications_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint allowing Patients and Doctors to subscribe to live appointment notifications.
    """
    await ws_manager.connect(user_id, websocket)
    try:
        # Welcome message
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": f"Realtime notifications streaming active for user [{user_id}]"
        })
        while True:
            # Keep connection alive and listen for client pings
            data = await websocket.receive_text()
            logger.debug(f"Received WS text from {user_id}: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        ws_manager.disconnect(user_id, websocket)
