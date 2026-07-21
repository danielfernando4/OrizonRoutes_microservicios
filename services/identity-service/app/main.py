from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator import routing as pfi_routing
from app.routers import auth
from app.database import Base, engine


_original_get_route_name = pfi_routing._get_route_name


def _safe_get_route_name(scope, routes):
    try:
        return _original_get_route_name(scope, routes)
    except AttributeError:
        return "unknown"


pfi_routing._get_route_name = _safe_get_route_name

# Create tables for standard run (not used in tests because conftest overrides it)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Identity Service", description="Orizon Routes Identity API")

app.include_router(auth.router)

Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    return {"message": "Identity Service is running"}
