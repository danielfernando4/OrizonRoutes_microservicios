import pytest
from starlette.websockets import WebSocketDisconnect


def test_websocket_rejects_invalid_token(client, trip_id):
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect(f"/ws/chat/{trip_id}/invalid-token"),
    ):
        pass


def test_websocket_send_and_receive_broadcast(client, passenger_token, trip_id):
    with client.websocket_connect(f"/ws/chat/{trip_id}/{passenger_token}") as ws:
        ws.send_json({"content": "Hola, ¿ya vas en camino?"})
        data = ws.receive_json()

        assert data["trip_id"] == trip_id
        assert data["content"] == "Hola, ¿ya vas en camino?"
        assert "sender_id" in data
        assert "timestamp" in data


def test_websocket_rejects_invalid_payload(client, passenger_token, trip_id):
    with client.websocket_connect(f"/ws/chat/{trip_id}/{passenger_token}") as ws:
        ws.send_json({"content": ""})
        data = ws.receive_json()

        assert "error" in data
