import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reserva


class TransaccionPago(Base):
    __tablename__ = "Transacciones_Pago"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reserva_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("Reservas.id", ondelete="CASCADE"),
        nullable=False,
    )
    paypal_order_id: Mapped[str] = mapped_column(String(255), nullable=False)
    paypal_capture_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "CREATED",
            "APPROVED",
            "COMPLETED",
            "FAILED",
            "REFUNDED",
            name="payment_status",
        ),
        default="CREATED",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    reserva: Mapped["Reserva"] = relationship(
        "Reserva", back_populates="transacciones"
    )
