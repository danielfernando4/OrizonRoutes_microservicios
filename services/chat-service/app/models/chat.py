"""Representación de los documentos de MongoDB usados por el Chat Service.

No se usa un ODM (Beanie) para mantener el servicio ligero: se trabaja
directamente con diccionarios sobre las colecciones de Motor, y estos
helpers centralizan la forma exacta de cada documento.

Colecciones (db_chat):
- salas:    {_id, trip_id, participants: [user_id, ...], created_at}
- mensajes: {_id, room_id, trip_id, sender_id, content, timestamp}
"""

from datetime import UTC, datetime


def new_room_document(trip_id: str, first_participant_id: str) -> dict:
    return {
        "trip_id": trip_id,
        "participants": [first_participant_id],
        "created_at": datetime.now(UTC),
    }


def new_message_document(room_id, trip_id: str, sender_id: str, content: str) -> dict:
    return {
        "room_id": room_id,
        "trip_id": trip_id,
        "sender_id": sender_id,
        "content": content,
        "timestamp": datetime.now(UTC),
    }
