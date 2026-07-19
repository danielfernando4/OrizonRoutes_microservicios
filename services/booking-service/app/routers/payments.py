import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.payment import TransaccionPago
from app.models.reservation import Reserva

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/booking", tags=["Payments"])


@router.post("/paypal-webhook")
async def paypal_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.json()
    event_type = payload.get("event_type")

    logger.info(f"PayPal webhook received: {event_type}")

    if event_type == "CHECKOUT.ORDER.APPROVED":
        order_id = payload.get("resource", {}).get("id")
        if order_id:
            result = await db.execute(
                select(TransaccionPago).where(
                    TransaccionPago.paypal_order_id == order_id
                )
            )
            transaccion = result.scalar_one_or_none()
            if transaccion:
                transaccion.status = "APPROVED"
                await db.commit()
                logger.info(f"TransaccionPago {transaccion.id} marked as APPROVED")

    elif event_type == "PAYMENT.CAPTURE.COMPLETED":
        capture_id = payload.get("resource", {}).get("id")
        if capture_id:
            result = await db.execute(
                select(TransaccionPago).where(
                    TransaccionPago.paypal_capture_id == capture_id
                )
            )
            transaccion = result.scalar_one_or_none()
            if transaccion:
                transaccion.status = "COMPLETED"
                result = await db.execute(
                    select(Reserva).where(Reserva.id == transaccion.reserva_id)
                )
                reserva = result.scalar_one_or_none()
                if reserva:
                    reserva.status = "PAID"
                await db.commit()
                logger.info(
                    "TransaccionPago %s marked as COMPLETED via webhook",
                    transaccion.id,
                )

    elif event_type == "PAYMENT.CAPTURE.REFUNDED":
        capture_id = payload.get("resource", {}).get("id")
        if capture_id:
            result = await db.execute(
                select(TransaccionPago).where(
                    TransaccionPago.paypal_capture_id == capture_id
                )
            )
            transaccion = result.scalar_one_or_none()
            if transaccion:
                transaccion.status = "REFUNDED"
                result = await db.execute(
                    select(Reserva).where(Reserva.id == transaccion.reserva_id)
                )
                reserva = result.scalar_one_or_none()
                if reserva:
                    reserva.status = "REFUNDED"
                await db.commit()
                logger.info(
                    "TransaccionPago %s marked as REFUNDED via webhook",
                    transaccion.id,
                )

    return {"status": "ok"}
