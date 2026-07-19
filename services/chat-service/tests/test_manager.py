from unittest.mock import AsyncMock

import pytest

from app.websocket.manager import ConnectionManager


@pytest.mark.asyncio
async def test_broadcast_sends_to_all_connections_in_room():
    manager = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    manager._active_connections["trip-1"] = [ws1, ws2]

    await manager.broadcast("trip-1", {"content": "hola"})

    ws1.send_json.assert_awaited_once_with({"content": "hola"})
    ws2.send_json.assert_awaited_once_with({"content": "hola"})


@pytest.mark.asyncio
async def test_broadcast_only_reaches_the_matching_trip():
    manager = ConnectionManager()
    ws_trip_1 = AsyncMock()
    ws_trip_2 = AsyncMock()
    manager._active_connections["trip-1"] = [ws_trip_1]
    manager._active_connections["trip-2"] = [ws_trip_2]

    await manager.broadcast("trip-1", {"content": "hola"})

    ws_trip_1.send_json.assert_awaited_once()
    ws_trip_2.send_json.assert_not_awaited()


@pytest.mark.asyncio
async def test_disconnect_removes_connection_and_cleans_up_empty_room():
    manager = ConnectionManager()
    ws1 = AsyncMock()
    manager._active_connections["trip-1"] = [ws1]

    manager.disconnect("trip-1", ws1)

    assert "trip-1" not in manager._active_connections


@pytest.mark.asyncio
async def test_broadcast_drops_socket_that_fails_to_send():
    manager = ConnectionManager()
    broken_ws = AsyncMock()
    broken_ws.send_json.side_effect = RuntimeError("connection closed")
    manager._active_connections["trip-1"] = [broken_ws]

    await manager.broadcast("trip-1", {"content": "hola"})

    assert "trip-1" not in manager._active_connections
