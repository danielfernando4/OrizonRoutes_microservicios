from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PaymentOut(BaseModel):
    id: UUID
    reservation_id: UUID
    paypal_order_id: str
    paypal_capture_id: str | None = None
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
