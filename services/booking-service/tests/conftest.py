import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database import get_db
from app.main import app
from app.services.catalog_client import CatalogClient
from app.services.paypal import PayPalClient


def _generate_token(user_id: str, role: str = "pasajero") -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "email": f"{role}@test.com",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def passenger_token() -> str:
    return _generate_token(str(uuid.uuid4()), "pasajero")


@pytest.fixture
def conductor_token() -> str:
    return _generate_token(str(uuid.uuid4()), "conductor")


@pytest.fixture
def passenger_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def trip_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def mock_trip_data(trip_id: str) -> dict:
    return {
        "id": trip_id,
        "driver_id": str(uuid.uuid4()),
        "driver_name": "Juan Pérez",
        "origin": "Quito",
        "destination": "Guayaquil",
        "departure_datetime": "2026-08-15T08:00:00Z",
        "price_per_seat": 25.0,
        "available_seats": 10,
        "total_seats": 10,
        "status": "active",
        "distance_km": 380.0,
        "duration_min": 240,
    }


@pytest.fixture
def mock_catalog_client(mock_trip_data: dict) -> MagicMock:
    client = MagicMock(spec=CatalogClient)
    client.get_trip = AsyncMock(return_value=mock_trip_data)
    client.validate_and_hold_seats = AsyncMock(return_value=True)
    client.confirm_seats_deducted = AsyncMock(return_value=True)
    client.release_held_seats = AsyncMock(return_value=True)
    client.cancel_trip_notify = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_paypal_client() -> MagicMock:
    client = MagicMock(spec=PayPalClient)
    client.create_order = AsyncMock(return_value=("ORDER123", "https://paypal.com/approve/ORDER123"))
    client.capture_order = AsyncMock(return_value=("CAPTURE123", "COMPLETED"))
    client.refund_capture = AsyncMock(return_value=("REFUND123", "COMPLETED"))
    return client


@pytest.fixture
def override_deps(
    mock_catalog_client: MagicMock,
    mock_paypal_client: MagicMock,
    passenger_id: str,
):
    with (
        patch("app.routers.reservations.catalog_client", mock_catalog_client),
        patch("app.routers.reservations.paypal_client", mock_paypal_client),
    ):
        yield


@pytest.fixture
def db_session():
    session = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()

    scalar_mock = MagicMock()
    scalar_mock.scalar_one_or_none = MagicMock(return_value=None)
    scalars_mock = MagicMock()
    scalars_mock.scalars.return_value = MagicMock()
    scalars_mock.scalars.return_value.all = MagicMock(return_value=[])

    scalar_result = MagicMock()
    scalar_result.scalar = MagicMock(return_value=0)

    async def execute_side_effect(*args, **kwargs):
        return scalars_mock

    session.execute = AsyncMock(side_effect=execute_side_effect)
    return session


@pytest.fixture
def client(override_deps, db_session) -> TestClient:
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client: TestClient, passenger_token: str) -> TestClient:
    client.headers.update({"Authorization": f"Bearer {passenger_token}"})
    return client


@pytest.fixture
def conductor_auth_client(client: TestClient, conductor_token: str) -> TestClient:
    client.headers.update({"Authorization": f"Bearer {conductor_token}"})
    return client
