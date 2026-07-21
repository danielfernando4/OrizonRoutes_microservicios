import pytest
from bson import ObjectId

from app.services.chat_service import ChatService, message_to_out


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
