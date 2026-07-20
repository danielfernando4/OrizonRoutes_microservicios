from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class TripBase(BaseModel):
    vehicle_id: str
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    departure_time: datetime
    price_per_seat: float = Field(..., gt=0)

class TripCreate(TripBase):
    pass

class TripOut(TripBase):
    id: str
    driver_id: str
    total_seats: int
    available_seats: int
    distance_km: float
    duration_min: int
    status: str
    
    model_config = ConfigDict(from_attributes=True)
