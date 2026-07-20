from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.vehicle import Vehicle
from app.models.trip import Trip

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy.pool import StaticPool

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "catalog-service"}

def test_create_vehicle():
    response = client.post("/api/catalog/vehicles/", json={
        "brand": "Toyota",
        "model": "Corolla",
        "capacity": 4
    })
    assert response.status_code == 201
    data = response.json()
    assert data["brand"] == "Toyota"
    assert data["capacity"] == 4
    assert "id" in data
    
    # Check listing
    resp_list = client.get("/api/catalog/vehicles/")
    assert len(resp_list.json()) == 1

def test_create_trip():
    # 1. Create a vehicle
    vehicle_resp = client.post("/api/catalog/vehicles/", json={
        "brand": "Honda",
        "model": "Civic",
        "capacity": 3
    })
    vehicle_id = vehicle_resp.json()["id"]
    
    # 2. Create a trip
    trip_data = {
        "vehicle_id": vehicle_id,
        "origin": "Quito",
        "destination": "Guayaquil",
        "departure_time": "2026-10-15T08:00:00Z",
        "price_per_seat": 15.5
    }
    
    response = client.post("/api/catalog/trips/", json=trip_data)
    assert response.status_code == 201
    data = response.json()
    assert data["total_seats"] == 3
    assert data["available_seats"] == 3
    assert data["distance_km"] == 120.5  # Mocked in osrm.py
