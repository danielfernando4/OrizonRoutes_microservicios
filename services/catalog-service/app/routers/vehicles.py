import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import authenticated, conductor_required
from ..models.vehicle import Vehicle
from ..models.trip import Trip
from ..schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleOut

logger = logging.getLogger(__name__)

router = APIRouter()

def _get_own_vehicle(vehicle_id: str, current_user: dict, db: Session) -> Vehicle:
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id, Vehicle.driver_id == current_user["id"]
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehicle

@router.post("/", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: VehicleCreate, current_user: dict = Depends(conductor_required), db: Session = Depends(get_db)):
    driver_id = current_user["id"]
    db_vehicle = Vehicle(**vehicle.model_dump(), driver_id=driver_id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    logger.info("Vehículo creado: id=%s driver=%s marca=%s modelo=%s capacidad=%d",
                db_vehicle.id, driver_id, vehicle.brand, vehicle.model, vehicle.capacity)
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

@router.put("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(
    vehicle_id: str,
    vehicle_data: VehicleUpdate,
    current_user: dict = Depends(conductor_required),
    db: Session = Depends(get_db),
):
    db_vehicle = _get_own_vehicle(vehicle_id, current_user, db)
    update_fields = vehicle_data.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    for key, value in update_fields.items():
        setattr(db_vehicle, key, value)
    db.commit()
    db.refresh(db_vehicle)
    logger.info("Vehículo actualizado: id=%s driver=%s cambios=%s",
                db_vehicle.id, current_user["id"], update_fields)
    return db_vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: str,
    current_user: dict = Depends(conductor_required),
    db: Session = Depends(get_db),
):
    vehicle = _get_own_vehicle(vehicle_id, current_user, db)
    trips_deleted = db.query(Trip).filter(Trip.vehicle_id == vehicle_id).delete()
    db.query(Vehicle).filter(Vehicle.id == vehicle_id).delete()
    db.commit()
    logger.info("Vehículo eliminado: id=%s driver=%s marca=%s modelo=%s trips_afectados=%d",
                vehicle_id, current_user["id"], vehicle.brand, vehicle.model, trips_deleted)
