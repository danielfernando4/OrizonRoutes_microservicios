from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    """Crea (una sola vez) y retorna el cliente global de Motor."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URL)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.MONGO_DB_NAME]


async def get_db() -> AsyncIOMotorDatabase:
    """Dependencia de FastAPI (HTTP y WebSocket) para inyectar la base de datos."""
    return get_database()


def close_db_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
