import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from ..database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(String, index=True, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    
    distance_km = Column(Float, default=0.0)
    duration_min = Column(Integer, default=0)
    
    status = Column(String, default="active") # active, cancelled, finished
