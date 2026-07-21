from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.trip import Trip
from ..models.vehicle import Vehicle
from ..schemas.trip import TripCreate, TripOut
from ..services.osrm import calculate_distance_and_duration
from typing import List, Optional

from pydantic import BaseModel
from ..dependencies import conductor_required, authenticated

class SeatsUpdate(BaseModel):
    seats: int = None
    seats_reserved: int = None
    seats_released: int = None

router = APIRouter()

@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
async def create_trip(trip: TripCreate, current_user: dict = Depends(conductor_required), db: Session = Depends(get_db)):
    driver_id = current_user["id"]
    # Validate vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id, Vehicle.driver_id == driver_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or does not belong to you")
    
    # Calculate distance and duration using OSRM
    distance_km, duration_min = await calculate_distance_and_duration(trip.origin, trip.destination)
    
    db_trip = Trip(
        **trip.model_dump(),
        driver_id=driver_id,
        total_seats=vehicle.capacity,
        available_seats=vehicle.capacity,
        distance_km=distance_km,
        duration_min=duration_min,
        status="active"
    )
    
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

@router.get("/", response_model=List[TripOut])
def search_trips(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Trip).filter(Trip.status == "active", Trip.available_seats > 0)
    
    if origin:
        query = query.filter(Trip.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Trip.destination.ilike(f"%{destination}%"))
        
    return query.all()

@router.get("/mine", response_model=List[TripOut])
def list_my_trips(current_user: dict = Depends(authenticated), db: Session = Depends(get_db)):
    driver_id = current_user["id"]
    trips = db.query(Trip).filter(Trip.driver_id == driver_id).order_by(Trip.departure_time.desc()).all()
    return trips

@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: str, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.post("/{trip_id}/validate-seats", status_code=status.HTTP_200_OK)
def validate_seats(trip_id: str, seats_data: SeatsUpdate, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.status == "active").first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or not active")
    if trip.available_seats < seats_data.seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")
    return {"status": "ok"}

@router.patch("/{trip_id}/seats", status_code=status.HTTP_200_OK)
def update_seats(trip_id: str, seats_data: SeatsUpdate, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.status == "active").first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or not active")
    
    if seats_data.seats_reserved is not None:
        if trip.available_seats < seats_data.seats_reserved:
            raise HTTPException(status_code=400, detail="Not enough seats available")
        trip.available_seats -= seats_data.seats_reserved
        
    if seats_data.seats_released is not None:
        trip.available_seats += seats_data.seats_released
        if trip.available_seats > trip.total_seats:
            trip.available_seats = trip.total_seats
            
    db.commit()
    db.refresh(trip)
    return {"status": "ok"}

@router.patch("/{trip_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_trip(trip_id: str, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip.status = "cancelled"
    db.commit()
    db.refresh(trip)
    return {"status": "cancelled"}
