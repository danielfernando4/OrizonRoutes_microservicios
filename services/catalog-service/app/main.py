from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import vehicles, trips

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Catalog Service - Orizon Routes")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles.router, prefix="/api/catalog/vehicles", tags=["Vehicles"])
app.include_router(trips.router, prefix="/api/catalog/trips", tags=["Trips"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "catalog-service"}
