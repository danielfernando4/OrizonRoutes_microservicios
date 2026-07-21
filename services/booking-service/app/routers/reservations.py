import logging
import uuid
import zlib
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import conductor_required, pasajero_required
from app.models.payment import TransaccionPago
from app.models.reservation import Reserva
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
from app.services.catalog_client import (
    CatalogServiceUnavailableError,
    catalog_client,
)
from app.services.paypal import paypal_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/booking", tags=["Reservations"])


def _generate_reservation_code() -> str:
    return uuid.uuid4().hex[:8].upper()


@router.post("/reserve", status_code=201, response_model=ReserveResponse)
async def create_reservation(
    payload: ReserveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(pasajero_required),
):
    try:
        trip = await catalog_client.get_trip(str(payload.trip_id))
    except CatalogServiceUnavailableError:
        raise HTTPException(
            503, "El servicio de catálogo no está disponible. Intente más tarde."
        ) from None
    if not trip:
        raise HTTPException(404, "Viaje no encontrado")
    if trip.get("status") != "active":
        raise HTTPException(400, "El viaje no está activo")

    lock_key = zlib.crc32(f"reserve:{payload.trip_id}:{current_user['id']}".encode("utf-8"))
    await db.execute(select(func.pg_advisory_xact_lock(lock_key)))

    existing = await db.execute(
        select(Reserva).where(
            Reserva.trip_id == payload.trip_id,
            Reserva.passenger_id == current_user["id"],
            Reserva.status == "PENDING",
        ).with_for_update()
    )
    existing_reservation = existing.scalar_one_or_none()
    if existing_reservation:
        return await _reuse_reservation(
            existing_reservation, db, current_user
        )

    if trip.get("available_seats", 0) < payload.seats_requested:
        raise HTTPException(
            400,
            f"Solo hay {trip.get('available_seats', 0)} asientos disponibles",
        )

    total_price = Decimal(str(trip["price_per_seat"])) * payload.seats_requested

    held = await catalog_client.validate_and_hold_seats(
        str(payload.trip_id), payload.seats_requested
    )
    if not held:
        raise HTTPException(503, "Error al validar disponibilidad en catálogo")

    try:
        order_id, approval_link = await paypal_client.create_order(
            value=total_price,
            return_url=settings.PAYPAL_RETURN_URL,
            cancel_url=settings.PAYPAL_CANCEL_URL,
        )
    except Exception as e:
        await catalog_client.release_held_seats(
            str(payload.trip_id), payload.seats_requested
        )
        raise HTTPException(502, f"Error al conectar con PayPal: {e}") from e

    reservation = Reserva(
        trip_id=payload.trip_id,
        passenger_id=current_user["id"],
        seats_reserved=payload.seats_requested,
        total_price=float(total_price),
        status="PENDING",
    )
    db.add(reservation)
    await db.flush()

    transaccion = TransaccionPago(
        reserva_id=reservation.id,
        paypal_order_id=order_id,
        amount=float(total_price),
        status="CREATED",
    )
    db.add(transaccion)
    await db.commit()

    return ReserveResponse(
        reservation_id=reservation.id,
        status="PENDING",
        approval_url=approval_link,
    )


async def _reuse_reservation(
    reservation: Reserva,
    db: AsyncSession,
    current_user: dict,
) -> ReserveResponse:
    try:
        order_id, approval_link = await paypal_client.create_order(
            value=Decimal(str(reservation.total_price)),
            return_url=settings.PAYPAL_RETURN_URL,
            cancel_url=settings.PAYPAL_CANCEL_URL,
        )
    except Exception as e:
        raise HTTPException(502, f"Error al conectar con PayPal: {e}") from e

    # Lock the reservation row and verify it's still PENDING
    await db.refresh(reservation, with_for_update=True)
    if reservation.status != "PENDING":
        raise HTTPException(400, "La reserva ya no está pendiente")

    transaccion = TransaccionPago(
        reserva_id=reservation.id,
        paypal_order_id=order_id,
        amount=reservation.total_price,
        status="CREATED",
    )
    db.add(transaccion)
    await db.commit()

    return ReserveResponse(
        reservation_id=reservation.id,
        status="PENDING",
        approval_url=approval_link,
    )


@router.post("/confirm-payment", response_model=ConfirmPaymentResponse)
async def confirm_payment(
    payload: ConfirmPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(pasajero_required),
):
    result = await db.execute(
        select(TransaccionPago).where(
            TransaccionPago.paypal_order_id == payload.paypal_order_id,
        )
    )
    transaccion = result.scalar_one_or_none()
    if not transaccion:
        raise HTTPException(404, "Transacción de pago no encontrada")

    result = await db.execute(
        select(Reserva).where(
            Reserva.id == transaccion.reserva_id,
            Reserva.passenger_id == current_user["id"],
        ).with_for_update()
    )
    reservation = result.scalar_one_or_none()
    if not reservation:
        raise HTTPException(404, "Reserva no encontrada")

    if reservation.status != "PENDING":
        if reservation.status == "PAID":
            return ConfirmPaymentResponse(
                reservation_id=reservation.id,
                status=reservation.status,
                reservation_code=reservation.reservation_code,
                total_price=reservation.total_price,
                seats_reserved=reservation.seats_reserved,
                trip_id=reservation.trip_id,
            )
        raise HTTPException(400, "La reserva no está pendiente")

    try:
        capture_id, paypal_status = await paypal_client.capture_order(
            payload.paypal_order_id
        )
    except Exception as e:
        logger.error(f"PayPal capture failed: {e}")
        await db.refresh(reservation)
        if reservation.status != "PENDING":
            raise HTTPException(400, "La reserva ya fue procesada por otro request")
        transaccion.status = "FAILED"
        reservation.status = "CANCELLED"
        await catalog_client.release_held_seats(
            str(reservation.trip_id), reservation.seats_reserved
        )
        await db.commit()
        raise HTTPException(502, f"Error al capturar el pago con PayPal: {e}") from e

    if paypal_status != "COMPLETED":
        transaccion.status = "FAILED"
        reservation.status = "CANCELLED"
        await catalog_client.release_held_seats(
            str(reservation.trip_id), reservation.seats_reserved
        )
        await db.commit()
        raise HTTPException(400, f"El pago no fue completado. Estado: {paypal_status}")

    transaccion.paypal_capture_id = capture_id
    transaccion.status = "COMPLETED"

    reservation.reservation_code = _generate_reservation_code()
    reservation.status = "PAID"
    await db.commit()

    seats_updated = await catalog_client.confirm_seats_deducted(
        str(reservation.trip_id), reservation.seats_reserved
    )
    if not seats_updated:
        logger.error(
            "Failed to notify Catalog about seat deduction for trip %s",
            reservation.trip_id,
        )

    return ConfirmPaymentResponse(
        reservation_id=reservation.id,
        status=reservation.status,
        reservation_code=reservation.reservation_code,
        total_price=reservation.total_price,
        seats_reserved=reservation.seats_reserved,
        trip_id=reservation.trip_id,
    )


@router.get("/my-reservations", response_model=PaginatedReservations)
async def get_my_reservations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(pasajero_required),
):
    count_result = await db.execute(
        select(func.count(Reserva.id)).where(
            Reserva.passenger_id == current_user["id"]
        )
    )
    total = count_result.scalar()

    offset = (page - 1) * page_size
    result = await db.execute(
        select(Reserva)
        .where(Reserva.passenger_id == current_user["id"])
        .order_by(Reserva.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    reservations = result.scalars().all()

    items = []
    for res in reservations:
        trip = None
        try:
            trip = await catalog_client.get_trip(str(res.trip_id))
        except CatalogServiceUnavailableError:
            logger.warning(f"Catalog unavailable for trip {res.trip_id}")

        item = ReservationOut(
            reservation_id=res.id,
            trip_id=res.trip_id,
            origin=trip.get("origin") if trip else None,
            destination=trip.get("destination") if trip else None,
            departure_datetime=trip.get("departure_time") if trip else None,
            seats_reserved=res.seats_reserved,
            total_price=res.total_price,
            status=res.status,
            reservation_code=res.reservation_code,
            driver_name=trip.get("driver_name") if trip else None,
            driver_id=trip.get("driver_id") if trip else None,
            created_at=res.created_at,
        )
        items.append(item)

    return PaginatedReservations(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/reservations/{reservation_id}", response_model=ReservationOut)
async def get_reservation_detail(
    reservation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(pasajero_required),
):
    result = await db.execute(
        select(Reserva).where(
            Reserva.id == reservation_id,
            Reserva.passenger_id == current_user["id"],
        )
    )
    reservation = result.scalar_one_or_none()
    if not reservation:
        raise HTTPException(404, "Reserva no encontrada")

    trip = None
    try:
        trip = await catalog_client.get_trip(str(reservation.trip_id))
    except CatalogServiceUnavailableError:
        logger.warning(f"Catalog unavailable for trip {reservation.trip_id}")

    return ReservationOut(
        reservation_id=reservation.id,
        trip_id=reservation.trip_id,
        origin=trip.get("origin") if trip else None,
        destination=trip.get("destination") if trip else None,
        departure_datetime=trip.get("departure_time") if trip else None,
        seats_reserved=reservation.seats_reserved,
        total_price=reservation.total_price,
        status=reservation.status,
        reservation_code=reservation.reservation_code,
        driver_name=trip.get("driver_name") if trip else None,
        driver_id=trip.get("driver_id") if trip else None,
        created_at=reservation.created_at,
    )


@router.post("/cancel", response_model=CancelResponse)
async def cancel_trip_reservations(
    payload: CancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(conductor_required),
):
    result = await db.execute(
        select(Reserva).where(
            Reserva.trip_id == payload.trip_id,
            Reserva.status == "PAID",
        )
    )
    reservations = result.scalars().all()

    refunded_count = 0
    for reservation in reservations:
        result = await db.execute(
            select(TransaccionPago).where(
                TransaccionPago.reserva_id == reservation.id,
                TransaccionPago.status == "COMPLETED",
                TransaccionPago.paypal_capture_id.isnot(None),
            )
        )
        transaccion = result.scalar_one_or_none()
        if not transaccion or not transaccion.paypal_capture_id:
            continue

        try:
            refund_id, refund_status = await paypal_client.refund_capture(
                transaccion.paypal_capture_id
            )
            if refund_status in ("COMPLETED", "PENDING"):
                transaccion.status = "REFUNDED"
                reservation.status = "REFUNDED"
                refunded_count += 1
                logger.info(
                    "Refund processed: reservation=%s, refund_id=%s",
                    reservation.id,
                    refund_id,
                )
            else:
                logger.error(
                    "Refund failed for capture %s: %s",
                    transaccion.paypal_capture_id,
                    refund_status,
                )
        except Exception as e:
            logger.error(
                f"PayPal refund error for capture {transaccion.paypal_capture_id}: {e}"
            )

    await db.commit()

    await catalog_client.cancel_trip_notify(str(payload.trip_id))

    return CancelResponse(
        message=f"Viaje cancelado. {refunded_count} reembolso(s) procesado(s).",
        refunded_count=refunded_count,
    )
