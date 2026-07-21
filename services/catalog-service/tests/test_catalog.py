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

def test_create_and_delete_vehicle_cascade():
    token = _conductor_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create vehicle
    resp = client.post("/api/catalog/vehicles/", json={
        "brand": "Nissan", "model": "Sentra", "capacity": 5
    }, headers=headers)
    assert resp.status_code == 201
    vehicle_id = resp.json()["id"]

    # Create a trip referencing the vehicle
    trip_resp = client.post("/api/catalog/trips/", json={
        "vehicle_id": vehicle_id,
        "origin": "Quito",
        "destination": "Cuenca",
        "departure_time": "2026-11-01T08:00:00Z",
        "price_per_seat": 20.0,
    }, headers=headers)
    assert trip_resp.status_code == 201
    trip_id = trip_resp.json()["id"]

    # Delete the vehicle
    del_resp = client.delete(f"/api/catalog/vehicles/{vehicle_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verify vehicle is gone
    get_resp = client.get(f"/api/catalog/vehicles/{vehicle_id}")
    assert get_resp.status_code == 404

    # Verify trips are cascade-deleted
    trips_resp = client.get("/api/catalog/trips/", params={"driver_id": "test-driver"})
    trip_ids = [t["id"] for t in trips_resp.json()]
    assert trip_id not in trip_ids


def test_update_vehicle():
    headers = _auth_headers()

    # Create vehicle
    resp = client.post("/api/catalog/vehicles/", json={
        "brand": "Mazda", "model": "3", "capacity": 4
    }, headers=headers)
    vehicle_id = resp.json()["id"]

    # Update brand only
    resp = client.put(f"/api/catalog/vehicles/{vehicle_id}", json={
        "brand": "Mazda Updated"
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["brand"] == "Mazda Updated"
    assert data["model"] == "3"
    assert data["capacity"] == 4

    # Update multiple fields
    resp = client.put(f"/api/catalog/vehicles/{vehicle_id}", json={
        "model": "CX-5", "capacity": 5
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["model"] == "CX-5"
    assert data["capacity"] == 5
    assert data["brand"] == "Mazda Updated"


def test_update_vehicle_not_found():
    headers = _auth_headers()
    resp = client.put("/api/catalog/vehicles/nonexistent-id", json={
        "brand": "Test"
    }, headers=headers)
    assert resp.status_code == 404


def test_update_vehicle_not_owner():
    token1 = _conductor_token()
    headers1 = {"Authorization": f"Bearer {token1}"}
    other_token = jwt.encode(
        {"user_id": "other-driver", "role": "conductor", "email": "other@test.com"},
        JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
    )
    headers2 = {"Authorization": f"Bearer {other_token}"}

    resp = client.post("/api/catalog/vehicles/", json={
        "brand": "Ford", "model": "Focus", "capacity": 4
    }, headers=headers1)
    vehicle_id = resp.json()["id"]

    resp = client.put(f"/api/catalog/vehicles/{vehicle_id}", json={
        "brand": "Hacked"
    }, headers=headers2)
    assert resp.status_code == 404

def test_update_vehicle_empty_body():
    headers = _auth_headers()
    resp = client.post("/api/catalog/vehicles/", json={
        "brand": "Chevy", "model": "Aveo", "capacity": 4
    }, headers=headers)
    vehicle_id = resp.json()["id"]

    resp = client.put(f"/api/catalog/vehicles/{vehicle_id}", json={}, headers=headers)
    assert resp.status_code == 400


def test_delete_vehicle_not_found():
    headers = _auth_headers()
    resp = client.delete("/api/catalog/vehicles/nonexistent-id", headers=headers)
    assert resp.status_code == 404


def test_delete_vehicle_not_owner():
    token1 = _conductor_token()
    headers1 = {"Authorization": f"Bearer {token1}"}
    other_token = jwt.encode(
        {"user_id": "other-driver", "role": "conductor", "email": "other@test.com"},
        JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
    )
    headers2 = {"Authorization": f"Bearer {other_token}"}

    resp = client.post("/api/catalog/vehicles/", json={
        "brand": "Suzuki", "model": "Swift", "capacity": 4
    }, headers=headers1)
    vehicle_id = resp.json()["id"]

    resp = client.delete(f"/api/catalog/vehicles/{vehicle_id}", headers=headers2)
    assert resp.status_code == 404
