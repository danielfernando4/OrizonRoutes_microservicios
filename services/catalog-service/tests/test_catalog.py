import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

JWT_SECRET_KEY = "28088ae11d2e1571053fe33386cbfa6e"
JWT_ALGORITHM = "HS256"

def _conductor_token():
    payload = {"user_id": "test-driver", "role": "conductor", "email": "driver@test.com"}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def _auth_headers():
    return {"Authorization": f"Bearer {_conductor_token()}"}

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
    }, headers=_auth_headers())
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
    }, headers=_auth_headers())
    vehicle_id = vehicle_resp.json()["id"]
    
    # 2. Create a trip
    trip_data = {
        "vehicle_id": vehicle_id,
        "origin": "Quito",
        "destination": "Guayaquil",
        "departure_time": "2026-10-15T08:00:00Z",
        "price_per_seat": 15.5
    }
    
    response = client.post("/api/catalog/trips/", json=trip_data, headers=_auth_headers())
    assert response.status_code == 201
    data = response.json()
    assert data["total_seats"] == 3
    assert data["available_seats"] == 3
    assert data["distance_km"] == 120.5  # Mocked in osrm.py
