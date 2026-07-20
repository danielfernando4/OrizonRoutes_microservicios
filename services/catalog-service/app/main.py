from fastapi import FastAPI
from .database import Base, engine
from .routers import vehicles, trips

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

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "catalog-service"}
