from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReserveRequest(BaseModel):
    trip_id: UUID
    seats_requested: int = Field(..., ge=1, description="Número de asientos a reservar")


class ConfirmPaymentRequest(BaseModel):
    paypal_order_id: str


class CancelRequest(BaseModel):
    trip_id: UUID


class ReservationOut(BaseModel):
    reservation_id: UUID
    trip_id: UUID
    origin: str | None = None
    destination: str | None = None
    departure_datetime: datetime | None = None
    seats_reserved: int
    total_price: float
    status: str
    reservation_code: str | None = None
    driver_name: str | None = None
    driver_id: str | None = None
    created_at: datetime


class ReserveResponse(BaseModel):
    reservation_id: UUID
    status: str
    approval_url: str


class ConfirmPaymentResponse(BaseModel):
    reservation_id: UUID
    status: str
    reservation_code: str | None = None
    total_price: float
    seats_reserved: int
    trip_id: UUID


class CancelResponse(BaseModel):
    message: str
    refunded_count: int


class PaginatedReservations(BaseModel):
    items: list[ReservationOut]
    total: int
    page: int
    page_size: int
