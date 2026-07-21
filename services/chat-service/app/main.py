import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator import routing as pfi_routing

from app.config import settings
from app.database import close_db_connection, get_client
from app.routers import chat
from app.websocket import chat_ws

_original_get_route_name = pfi_routing._get_route_name


def _safe_get_route_name(scope, routes):
    try:
        return _original_get_route_name(scope, routes)
    except AttributeError:
        return "unknown"


pfi_routing._get_route_name = _safe_get_route_name

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    client = get_client()
    db = client[settings.MONGO_DB_NAME]
    try:
        await asyncio.wait_for(
            db.salas.create_index(
                [("trip_id", 1), ("passenger_id", 1)],
                unique=True,
                background=True,
            ),
            timeout=3.0,
        )
    except Exception:
        logging.warning("No se pudo crear el índice único en salas (posibles duplicados existentes)")
    yield
    close_db_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(chat.router)
app.include_router(chat_ws.router)

Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.APP_NAME}
