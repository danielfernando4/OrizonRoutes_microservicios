import uuid
from sqlalchemy import Column, String, Integer
from ..database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_id = Column(String, index=True, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
