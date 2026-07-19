import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Mantiene en memoria las conexiones WebSocket activas por trip_id.

    Equivalente al `Dict[room_id, List[WebSocket]]` especificado en la
    arquitectura. Si un destinatario no está conectado, el mensaje ya
    quedó persistido en Mongo (ver ChatService.save_message) y lo verá
    vía GET /api/chat/history/{trip_id} al abrir la app.
    """

    def __init__(self) -> None:
        self._active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, trip_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active_connections[trip_id].append(websocket)

    def disconnect(self, trip_id: str, websocket: WebSocket) -> None:
        connections = self._active_connections.get(trip_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and trip_id in self._active_connections:
            del self._active_connections[trip_id]

    async def broadcast(self, trip_id: str, message: dict) -> None:
        for connection in list(self._active_connections.get(trip_id, [])):
            try:
                await connection.send_json(message)
            except Exception:
                logger.exception("Fallo enviando mensaje, se descarta el socket")
                self.disconnect(trip_id, connection)


manager = ConnectionManager()
