import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator import routing as pfi_routing
from .database import Base, engine
from .routers import vehicles, trips

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


_original_get_route_name = pfi_routing._get_route_name


def _safe_get_route_name(scope, routes):
    try:
        return _original_get_route_name(scope, routes)
    except AttributeError:
        return "unknown"


pfi_routing._get_route_name = _safe_get_route_name

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Catalog Service - Orizon Routes")

# NOTA: el CORS se maneja centralizado en api-gateway/nginx.conf.
# Si este servicio también agrega CORSMiddleware, el navegador recibe el
# header 'Access-Control-Allow-Origin' duplicado (uno del gateway, otro
# de aquí) y lo rechaza por completo, incluso si ambos traen el mismo
# valor. Por eso no se agrega CORSMiddleware en los microservicios
# individuales, solo en el gateway.

app.include_router(vehicles.router, prefix="/api/catalog/vehicles", tags=["Vehicles"])
app.include_router(trips.router, prefix="/api/catalog/trips", tags=["Trips"])

Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "catalog-service"}
