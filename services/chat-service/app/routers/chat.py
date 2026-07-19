from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.chat import ChatHistoryResponse
from app.services.chat_service import ChatService, message_to_out

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.get("/history/{trip_id}", response_model=ChatHistoryResponse)
async def get_history(
    trip_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ChatHistoryResponse:
    """Retorna el historial de mensajes antiguos de un viaje, paginado.

    Requiere JWT válido (el mismo emitido por el Identity Service); no se
    valida aquí si el usuario tiene una reserva sobre el viaje, ver los
    límites del módulo en la arquitectura.
    """
    del current_user  # solo se exige autenticación, no se usa el payload

    service = ChatService(db)
    items, total = await service.get_history(trip_id, page=page, page_size=page_size)

    return ChatHistoryResponse(
        trip_id=trip_id,
        items=[message_to_out(doc) for doc in items],
        total=total,
        page=page,
        page_size=page_size,
    )
