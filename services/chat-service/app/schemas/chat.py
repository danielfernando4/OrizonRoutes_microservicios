from datetime import datetime

from pydantic import BaseModel, Field


class MessageOut(BaseModel):
    id: str
    trip_id: str
    sender_id: str
    content: str
    timestamp: datetime


class ChatHistoryResponse(BaseModel):
    trip_id: str
    items: list[MessageOut]
    total: int
    page: int
    page_size: int


class IncomingWSMessage(BaseModel):
    """Payload que el cliente envía por el WebSocket."""

    content: str = Field(..., min_length=1, max_length=2000)


class OutgoingWSMessage(BaseModel):
    """Payload que el servidor emite (broadcast) a los sockets conectados."""

    trip_id: str
    sender_id: str
    content: str
    timestamp: datetime
