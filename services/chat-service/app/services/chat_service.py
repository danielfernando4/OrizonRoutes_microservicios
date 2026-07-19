from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

ROOMS_COLLECTION = "salas"
MESSAGES_COLLECTION = "mensajes"


class ChatService:
    """Encapsula el acceso a las colecciones `salas` y `mensajes` de db_chat.

    Nota (límite de este módulo): no se valida aquí si el usuario que se
    conecta tiene una reserva vigente sobre el viaje; esa validación,
    según la arquitectura, la hace el frontend o un middleware externo.
    Este servicio solo garantiza persistencia y entrega de mensajes.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.rooms = db[ROOMS_COLLECTION]
        self.messages = db[MESSAGES_COLLECTION]

    async def get_or_create_room(self, trip_id: str, user_id: str) -> dict:
        room = await self.rooms.find_one({"trip_id": trip_id})

        if room is None:
            room = {
                "trip_id": trip_id,
                "participants": [user_id],
                "created_at": datetime.now(UTC),
            }
            result = await self.rooms.insert_one(room)
            room["_id"] = result.inserted_id
            return room

        if user_id not in room.get("participants", []):
            await self.rooms.update_one(
                {"_id": room["_id"]},
                {"$addToSet": {"participants": user_id}},
            )
            room["participants"] = [*room.get("participants", []), user_id]

        return room

    async def save_message(
        self, room_id, trip_id: str, sender_id: str, content: str
    ) -> dict:
        message = {
            "room_id": room_id,
            "trip_id": trip_id,
            "sender_id": sender_id,
            "content": content,
            "timestamp": datetime.now(UTC),
        }
        result = await self.messages.insert_one(message)
        message["_id"] = result.inserted_id
        return message

    async def get_history(
        self, trip_id: str, page: int = 1, page_size: int = 50
    ) -> tuple[list[dict], int]:
        skip = (page - 1) * page_size
        cursor = (
            self.messages.find({"trip_id": trip_id})
            .sort("timestamp", 1)
            .skip(skip)
            .limit(page_size)
        )
        items = [doc async for doc in cursor]
        total = await self.messages.count_documents({"trip_id": trip_id})
        return items, total


def message_to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "trip_id": doc["trip_id"],
        "sender_id": doc["sender_id"],
        "content": doc["content"],
        "timestamp": doc["timestamp"],
    }
