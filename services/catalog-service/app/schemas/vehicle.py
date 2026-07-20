from pydantic import BaseModel, Field, ConfigDict

class VehicleBase(BaseModel):
    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0, description="Seats available in the vehicle")

class VehicleCreate(VehicleBase):
    pass

class VehicleOut(VehicleBase):
    id: str
    driver_id: str
    
    model_config = ConfigDict(from_attributes=True)
