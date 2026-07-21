import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status

from app.database import get_db
from app.main import app


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"


class TestReserveEndpoint:
    ENDPOINT = "/api/booking/reserve"

    def test_reserve_success(self, auth_client, mock_trip_data, passenger_id, db_session):
        reservation_id = uuid.uuid4()
        added_objects = []

        def add_side_effect(obj):
            added_objects.append(obj)
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = reservation_id

        db_session.add = MagicMock(side_effect=add_side_effect)
        db_session.flush = AsyncMock()

        async def execute_side_effect(*args, **kwargs):
            result = MagicMock()
            result.scalar_one_or_none = MagicMock(return_value=None)
            return result

        db_session.execute = AsyncMock(side_effect=execute_side_effect)

        app.dependency_overrides[get_db] = lambda: db_session

        payload = {"trip_id": mock_trip_data["id"], "seats_requested": 2}
        response = auth_client.post(self.ENDPOINT, json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "PENDING"
        assert "approval_url" in data
        assert "reservation_id" in data

    def test_reserve_unavailable_seats(self, auth_client, mock_catalog_client, mock_trip_data):
        trip = dict(mock_trip_data)
        trip["available_seats"] = 1

        mock_catalog_client.get_trip = AsyncMock(return_value=trip)

        with patch("app.routers.reservations.catalog_client", mock_catalog_client):
            payload = {"trip_id": mock_trip_data["id"], "seats_requested": 2}
            response = auth_client.post(self.ENDPOINT, json=payload)
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reserve_inactive_trip(self, auth_client, mock_catalog_client, mock_trip_data):
        trip = dict(mock_trip_data)
        trip["status"] = "cancelled"

        mock_catalog_client.get_trip = AsyncMock(return_value=trip)

        with patch("app.routers.reservations.catalog_client", mock_catalog_client):
            payload = {"trip_id": mock_trip_data["id"], "seats_requested": 2}
            response = auth_client.post(self.ENDPOINT, json=payload)
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reserve_trip_not_found(self, auth_client, mock_catalog_client):
        mock_catalog_client.get_trip = AsyncMock(return_value=None)

        with patch("app.routers.reservations.catalog_client", mock_catalog_client):
            payload = {"trip_id": str(uuid.uuid4()), "seats_requested": 2}
            response = auth_client.post(self.ENDPOINT, json=payload)
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_reserve_catalog_unavailable(self, auth_client, mock_catalog_client):
        from app.services.catalog_client import CatalogServiceUnavailableError

        mock_catalog_client.get_trip = AsyncMock(
            side_effect=CatalogServiceUnavailableError("Catalog down")
        )

        with patch("app.routers.reservations.catalog_client", mock_catalog_client):
            payload = {"trip_id": str(uuid.uuid4()), "seats_requested": 2}
            response = auth_client.post(self.ENDPOINT, json=payload)
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_reserve_paypal_failure_releases_seats(
        self, auth_client, mock_catalog_client, mock_paypal_client, mock_trip_data
    ):
        mock_catalog_client.get_trip = AsyncMock(return_value=mock_trip_data)
        mock_catalog_client.validate_and_hold_seats = AsyncMock(return_value=True)
        mock_catalog_client.release_held_seats = AsyncMock(return_value=True)
        mock_paypal_client.create_order = AsyncMock(side_effect=Exception("PayPal error"))

        with (
            patch("app.routers.reservations.catalog_client", mock_catalog_client),
            patch("app.routers.reservations.paypal_client", mock_paypal_client),
        ):
            payload = {"trip_id": mock_trip_data["id"], "seats_requested": 2}
            response = auth_client.post(self.ENDPOINT, json=payload)
            assert response.status_code == status.HTTP_502_BAD_GATEWAY
            mock_catalog_client.release_held_seats.assert_called_once()

    def test_reserve_without_auth(self, client, mock_trip_data):
        payload = {"trip_id": mock_trip_data["id"], "seats_requested": 2}
        response = client.post(self.ENDPOINT, json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_reserve_conductor_forbidden(self, conductor_auth_client, mock_trip_data):
        payload = {"trip_id": mock_trip_data["id"], "seats_requested": 2}
        response = conductor_auth_client.post(self.ENDPOINT, json=payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestConfirmPaymentEndpoint:
    ENDPOINT = "/api/booking/confirm-payment"

    def test_confirm_success(self, auth_client, mock_catalog_client, mock_paypal_client, db_session):
        reservation_id = uuid.uuid4()

        mock_reservation = MagicMock()
        mock_reservation.id = reservation_id
        mock_reservation.trip_id = uuid.uuid4()
        mock_reservation.passenger_id = uuid.uuid4()
        mock_reservation.seats_reserved = 2
        mock_reservation.total_price = 50.0
        mock_reservation.status = "PENDING"
        mock_reservation.reservation_code = None
        mock_reservation.created_at = "2026-07-18T20:00:00Z"

        mock_transaccion = MagicMock()
        mock_transaccion.id = uuid.uuid4()
        mock_transaccion.reserva_id = reservation_id
        mock_transaccion.paypal_order_id = "ORDER123"
        mock_transaccion.paypal_capture_id = None
        mock_transaccion.status = "CREATED"

        async def execute_side_effect(*args, **kwargs):
            select_cls = args[0] if args else None
            result = MagicMock()
            if hasattr(select_cls, 'column_descriptions') and len(select_cls.column_descriptions) > 0:
                pass
            if mock_transaccion.paypal_order_id in str(kwargs) or "ORDER123" in str(kwargs):
                result.scalar_one_or_none = MagicMock(return_value=mock_transaccion)
            else:
                result.scalar_one_or_none = MagicMock(return_value=mock_reservation)
            return result

        db_session.execute = AsyncMock(side_effect=execute_side_effect)
        db_session.commit = AsyncMock()

        app.dependency_overrides[get_db] = lambda: db_session

        with (
            patch("app.routers.reservations.catalog_client", mock_catalog_client),
            patch("app.routers.reservations.paypal_client", mock_paypal_client),
        ):
            payload = {
                "paypal_order_id": "ORDER123",
                "reservation_id": str(reservation_id),
            }
            response = auth_client.post(self.ENDPOINT, json=payload)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "PAID"
            assert data["reservation_code"] is not None

    def test_confirm_reservation_not_found(self, auth_client, db_session):
        async def execute_side_effect(*args, **kwargs):
            result = MagicMock()
            result.scalar_one_or_none = MagicMock(return_value=None)
            return result

        db_session.execute = AsyncMock(side_effect=execute_side_effect)
        app.dependency_overrides[get_db] = lambda: db_session

        payload = {"paypal_order_id": "ORDER123", "reservation_id": str(uuid.uuid4())}
        response = auth_client.post(self.ENDPOINT, json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_confirm_without_auth(self, client):
        payload = {"paypal_order_id": "ORDER123", "reservation_id": str(uuid.uuid4())}
        response = client.post(self.ENDPOINT, json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMyReservationsEndpoint:
    ENDPOINT = "/api/booking/my-reservations"

    def test_my_reservations_empty(self, auth_client, db_session):
        mock_scalar = MagicMock()
        mock_scalar.scalar = MagicMock(return_value=0)
        mock_scalars = MagicMock()
        mock_scalars.scalars.return_value.all = MagicMock(return_value=[])

        call_count = 0

        async def execute_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_scalar
            return mock_scalars

        db_session.execute = AsyncMock(side_effect=execute_side_effect)
        app.dependency_overrides[get_db] = lambda: db_session

        response = auth_client.get(self.ENDPOINT)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestCancelEndpoint:
    ENDPOINT = "/api/booking/cancel"

    def test_cancel_success(self, conductor_auth_client, mock_catalog_client, mock_paypal_client, db_session):
        mock_reservation = MagicMock()
        mock_reservation.id = uuid.uuid4()
        mock_reservation.trip_id = uuid.uuid4()
        mock_reservation.status = "PAID"
        mock_reservation.seats_reserved = 2
        mock_reservation.total_price = 50.0

        mock_transaccion = MagicMock()
        mock_transaccion.id = uuid.uuid4()
        mock_transaccion.reserva_id = mock_reservation.id
        mock_transaccion.paypal_capture_id = "CAPTURE123"
        mock_transaccion.status = "COMPLETED"

        async def execute_side_effect(*args, **kwargs):
            result = MagicMock()
            result.scalars.return_value.all = MagicMock(return_value=[mock_reservation])
            result.scalar_one_or_none = MagicMock(return_value=mock_transaccion)
            return result

        db_session.execute = AsyncMock(side_effect=execute_side_effect)
        db_session.commit = AsyncMock()

        app.dependency_overrides[get_db] = lambda: db_session

        with (
            patch("app.routers.reservations.catalog_client", mock_catalog_client),
            patch("app.routers.reservations.paypal_client", mock_paypal_client),
        ):
            payload = {"trip_id": str(uuid.uuid4())}
            response = conductor_auth_client.post(self.ENDPOINT, json=payload)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["refunded_count"] == 1

    def test_cancel_without_auth(self, client):
        payload = {"trip_id": str(uuid.uuid4())}
        response = client.post(self.ENDPOINT, json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
