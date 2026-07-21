from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import authenticated, conductor_required
from ..models.vehicle import Vehicle
from ..schemas.vehicle import VehicleCreate, VehicleOut

router = APIRouter()

# En un entorno real, aquí inyectaríamos una dependencia get_current_user que verifique el JWT
# Para esta implementación, asumiremos que el driver_id viene en los headers o cuerpo (mocked middleware)

@router.post("/", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, current_user: dict = Depends(conductor_required), db: Session = Depends(get_db)):
    driver_id = current_user["id"]
    db_vehicle = Vehicle(**vehicle.model_dump(), driver_id=driver_id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@router.get("/", response_model=list[VehicleOut])
def list_vehicles(current_user: dict = Depends(authenticated), db: Session = Depends(get_db)):
    driver_id = current_user["id"]
    vehicles = db.query(Vehicle).filter(Vehicle.driver_id == driver_id).all()
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
