import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.reservation import (
    CancelRequest,
    CancelResponse,
    ConfirmPaymentRequest,
    ConfirmPaymentResponse,
    PaginatedReservations,
    ReservationOut,
    ReserveRequest,
    ReserveResponse,
)


class TestReserveRequest:
    def test_valid_request(self):
        data = {"trip_id": str(uuid.uuid4()), "seats_requested": 2}
        req = ReserveRequest(**data)
        assert req.seats_requested == 2

    def test_seats_must_be_positive(self):
        data = {"trip_id": str(uuid.uuid4()), "seats_requested": 0}
        with pytest.raises(ValidationError):
            ReserveRequest(**data)

    def test_seats_cannot_be_negative(self):
        data = {"trip_id": str(uuid.uuid4()), "seats_requested": -1}
        with pytest.raises(ValidationError):
            ReserveRequest(**data)


class TestConfirmPaymentRequest:
    def test_valid_request(self):
        data = {"paypal_order_id": "ORDER123", "reservation_id": str(uuid.uuid4())}
        req = ConfirmPaymentRequest(**data)
        assert req.paypal_order_id == "ORDER123"

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            ConfirmPaymentRequest(**{})


class TestCancelRequest:
    def test_valid_request(self):
        data = {"trip_id": str(uuid.uuid4())}
        req = CancelRequest(**data)
        assert req.trip_id is not None


class TestReservationOut:
    def test_valid_response(self):
        data = {
            "reservation_id": str(uuid.uuid4()),
            "trip_id": str(uuid.uuid4()),
            "seats_reserved": 2,
            "total_price": 50.0,
            "status": "PAID",
            "created_at": datetime.now(UTC).isoformat(),
        }
        out = ReservationOut(**data)
        assert out.status == "PAID"
        assert out.seats_reserved == 2

    def test_with_optional_fields(self):
        data = {
            "reservation_id": str(uuid.uuid4()),
            "trip_id": str(uuid.uuid4()),
            "origin": "Quito",
            "destination": "Guayaquil",
            "seats_reserved": 1,
            "total_price": 25.0,
            "status": "PAID",
            "reservation_code": "A1B2C3D4",
            "driver_name": "Juan",
            "driver_id": str(uuid.uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
        }
        out = ReservationOut(**data)
        assert out.origin == "Quito"
        assert out.reservation_code == "A1B2C3D4"


class TestReserveResponse:
    def test_valid_response(self):
        data = {
            "reservation_id": str(uuid.uuid4()),
            "status": "PENDING",
            "approval_url": "https://paypal.com/approve/123",
        }
        resp = ReserveResponse(**data)
        assert resp.status == "PENDING"
        assert resp.approval_url == "https://paypal.com/approve/123"


class TestConfirmPaymentResponse:
    def test_valid_response(self):
        data = {
            "reservation_id": str(uuid.uuid4()),
            "status": "PAID",
            "total_price": 50.0,
            "seats_reserved": 2,
            "trip_id": str(uuid.uuid4()),
        }
        resp = ConfirmPaymentResponse(**data)
        assert resp.status == "PAID"


class TestCancelResponse:
    def test_valid_response(self):
        data = {"message": "Viaje cancelado. 3 reembolso(s) procesado(s).", "refunded_count": 3}
        resp = CancelResponse(**data)
        assert resp.refunded_count == 3


class TestPaginatedReservations:
    def test_pagination(self):
        data = {
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
        }
        pag = PaginatedReservations(**data)
        assert pag.total == 0
        assert pag.page == 1
