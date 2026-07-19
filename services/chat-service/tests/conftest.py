import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.config import settings
from app.database import get_db
from app.main import app


def _generate_token(user_id: str, role: str = "pasajero") -> str:
    payload = {"user_id": user_id, "role": role, "email": f"{role}@test.com"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def passenger_token() -> str:
    return _generate_token(str(uuid.uuid4()), "pasajero")


@pytest.fixture
def conductor_token() -> str:
    return _generate_token(str(uuid.uuid4()), "conductor")


@pytest.fixture
def trip_id() -> str:
    return str(uuid.uuid4())


class _AsyncCursor:
    """Emula un cursor asíncrono de Motor (find().sort().skip().limit())."""

    def __init__(self, items: list[dict]):
        self._items = list(items)

    def sort(self, *args, **kwargs):
        return self

    def skip(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def __aiter__(self):
        self._iterator = iter(self._items)
        return self

    async def __anext__(self):
        try:
            return next(self._iterator)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


@pytest.fixture
def mock_messages(trip_id: str) -> list[dict]:
    room_id = ObjectId()
    return [
        {
            "_id": ObjectId(),
            "room_id": room_id,
            "trip_id": trip_id,
            "sender_id": "user-1",
            "content": "Hola, ¿ya vas en camino?",
            "timestamp": datetime.now(UTC),
        },
        {
            "_id": ObjectId(),
            "room_id": room_id,
            "trip_id": trip_id,
            "sender_id": "user-2",
            "content": "Sí, llego en 5 minutos",
            "timestamp": datetime.now(UTC),
        },
    ]


@pytest.fixture
def mock_db(mock_messages: list[dict]) -> MagicMock:
    """Simula la AsyncIOMotorDatabase con las colecciones 'salas' y 'mensajes'."""
    rooms_collection = MagicMock()
    rooms_collection.find_one = AsyncMock(return_value=None)
    insert_room_result = MagicMock()
    insert_room_result.inserted_id = ObjectId()
    rooms_collection.insert_one = AsyncMock(return_value=insert_room_result)
    rooms_collection.update_one = AsyncMock()

    messages_collection = MagicMock()
    messages_collection.find = MagicMock(return_value=_AsyncCursor(mock_messages))
    messages_collection.count_documents = AsyncMock(return_value=len(mock_messages))
    insert_message_result = MagicMock()
    insert_message_result.inserted_id = ObjectId()
    messages_collection.insert_one = AsyncMock(return_value=insert_message_result)

    collections = {"salas": rooms_collection, "mensajes": messages_collection}

    db = MagicMock()
    db.__getitem__.side_effect = lambda name: collections[name]
    db.rooms_collection = rooms_collection
    db.messages_collection = messages_collection
    return db


@pytest.fixture
def client(mock_db: MagicMock) -> TestClient:
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client: TestClient, passenger_token: str) -> TestClient:
    client.headers.update({"Authorization": f"Bearer {passenger_token}"})
    return client
