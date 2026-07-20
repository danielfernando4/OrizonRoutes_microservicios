import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError

from app.database import get_db
from app.dependencies import decode_token_or_none
from app.schemas.chat import IncomingWSMessage
from app.services.chat_service import ChatService
from app.websocket.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Código de cierre no estándar (rango privado 4000-4999) para token inválido.
WS_UNAUTHORIZED = 4401


@router.websocket("/ws/chat/{trip_id}/{passenger_id}/{token}")
async def chat_websocket(
    websocket: WebSocket,
    trip_id: str,
    passenger_id: str,
    token: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> None:
    """Conexión WebSocket bidireccional para un viaje específico.

    El JWT viaja en la URL (`{token}`) porque los navegadores no permiten
    enviar cabeceras `Authorization` al abrir un WebSocket. Se valida
    igual que en el resto de microservicios, contra la misma clave
    secreta emitida por el Identity Service.
    """
    user = decode_token_or_none(token)
    if user is None:
        await websocket.close(code=WS_UNAUTHORIZED)
        return

    service = ChatService(db)
    room = await service.get_or_create_room(trip_id, passenger_id)
    room_id = str(room["_id"])

    await manager.connect(room_id, websocket)
    try:
        while True:
            raw = await websocket.receive_json()
            try:
                incoming = IncomingWSMessage(**raw)
            except ValidationError:
                await websocket.send_json({"error": "Mensaje inválido"})
                continue

            message = await service.save_message(
                room_id=room["_id"],
                trip_id=trip_id,
                sender_id=user["id"],
                content=incoming.content,
            )

            await manager.broadcast(
                room_id,
                {
                    "id": str(message["_id"]),
                    "trip_id": trip_id,
                    "sender_id": user["id"],
                    "content": message["content"],
                    "timestamp": message["timestamp"].isoformat(),
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
    except Exception:
        logger.exception("Error en el WebSocket de chat para room_id=%s", room_id)
        manager.disconnect(room_id, websocket)
