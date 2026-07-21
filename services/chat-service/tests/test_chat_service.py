import pytest
from bson import ObjectId

from app.services.chat_service import ChatService, message_to_out
from .conftest import _AsyncCursor


@pytest.mark.asyncio
async def test_get_or_create_room_creates_new_room_when_missing(mock_db, trip_id):
    service = ChatService(mock_db)

    room = await service.get_or_create_room(trip_id, "user-1")

    mock_db.rooms_collection.insert_one.assert_awaited_once()
    assert room["trip_id"] == trip_id
    assert room["passenger_id"] == "user-1"


@pytest.mark.asyncio
async def test_get_or_create_room_returns_existing_room(mock_db, trip_id):
    existing = {
        "_id": ObjectId(),
        "trip_id": trip_id,
        "passenger_id": "passenger-1",
        "created_at": "2026-07-19T00:00:00Z",
    }
    mock_db.rooms_collection.find_one.return_value = existing

    service = ChatService(mock_db)
    room = await service.get_or_create_room(trip_id, "passenger-1")

    mock_db.rooms_collection.insert_one.assert_not_awaited()
    assert room["passenger_id"] == "passenger-1"


@pytest.mark.asyncio
async def test_save_message_persists_document(mock_db, trip_id):
    service = ChatService(mock_db)
    room_id = ObjectId()

    message = await service.save_message(
        room_id=room_id, trip_id=trip_id, sender_id="user-1", content="Hola"
    )

    mock_db.messages_collection.insert_one.assert_awaited_once()
    assert message["content"] == "Hola"
    assert message["sender_id"] == "user-1"


@pytest.mark.asyncio
async def test_get_history_returns_items_and_total(mock_db, trip_id, mock_messages):
    service = ChatService(mock_db)
    room_id = ObjectId()

    items, total = await service.get_history(room_id)

    assert total == len(mock_messages)
    assert len(items) == len(mock_messages)


@pytest.mark.asyncio
async def test_get_rooms_for_trips_returns_matching_rooms(mock_db, trip_id, mock_rooms):
    service = ChatService(mock_db)
    trip_ids = [trip_id, "other-trip"]
    rooms = await service.get_rooms_for_trips(trip_ids)

    mock_db.rooms_collection.find.assert_called_once_with(
        {"trip_id": {"$in": trip_ids}}
    )
    assert len(rooms) == len(mock_rooms)
    assert rooms[0]["trip_id"] == trip_id
    assert "passenger_id" in rooms[0]


@pytest.mark.asyncio
async def test_get_rooms_for_passenger_returns_matching_rooms(mock_db, mock_rooms):
    service = ChatService(mock_db)
    rooms = await service.get_rooms_for_passenger("passenger-1")

    mock_db.rooms_collection.find.assert_called_once_with(
        {"passenger_id": "passenger-1"}
    )
    assert len(rooms) == len(mock_rooms)


@pytest.mark.asyncio
async def test_get_rooms_for_trips_empty_list_returns_empty(mock_db):
    mock_db.rooms_collection.find.return_value = _AsyncCursor([])
    service = ChatService(mock_db)
    rooms = await service.get_rooms_for_trips([])

    assert rooms == []


def test_message_to_out_serializes_object_id():
    doc = {
        "_id": ObjectId(),
        "trip_id": "trip-1",
        "sender_id": "user-1",
        "content": "Hola",
        "timestamp": "2026-07-19T00:00:00Z",
    }

    out = message_to_out(doc)

    assert out["id"] == str(doc["_id"])
    assert isinstance(out["id"], str)
