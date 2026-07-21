from pydantic import BaseModel, Field, ConfigDict

class VehicleBase(BaseModel):
    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0, description="Seats available in the vehicle")

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    brand: str | None = Field(None, min_length=1)
    model: str | None = Field(None, min_length=1)
    capacity: int | None = Field(None, gt=0)

class VehicleOut(VehicleBase):
    id: str
    driver_id: str
    
    model_config = ConfigDict(from_attributes=True)
