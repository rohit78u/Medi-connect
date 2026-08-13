import pytest
from app.websocket.manager import WebSocketConnectionManager


@pytest.mark.asyncio
async def test_websocket_manager_lifecycle():
    """
    Test in-memory WebSocket manager connect, send_personal_message, and disconnect lifecycle.
    """
    manager = WebSocketConnectionManager()
    user_id = "test-user-123"

    assert user_id not in manager.active_connections

    # Mock WebSocket object
    class DummyWebSocket:
        def __init__(self):
            self.accepted = False
            self.sent_messages = []

        async def accept(self):
            self.accepted = True

        async def send_text(self, text: str):
            self.sent_messages.append(text)

    dummy_ws = DummyWebSocket()
    await manager.connect(user_id, dummy_ws)
    assert dummy_ws.accepted is True
    assert user_id in manager.active_connections
    assert len(manager.active_connections[user_id]) == 1

    # Send personal message
    msg_payload = {"type": "NOTIFICATION", "content": "Appointment booked"}
    await manager.send_personal_message(msg_payload, user_id)
    assert len(dummy_ws.sent_messages) == 1
    assert "Appointment booked" in dummy_ws.sent_messages[0]

    # Disconnect
    manager.disconnect(user_id, dummy_ws)
    assert user_id not in manager.active_connections
