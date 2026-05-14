from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from typing import List
from app.database import get_db
from app.auth import require_doctor
from app import crud, schemas
from fastapi.encoders import jsonable_encoder
from app.core.redis_client import get_cache, set_cache, invalidate_cache

router = APIRouter(prefix="/doctor", tags=["Doctor"])


@router.get("/appointments/me", response_model=List[schemas.AppointmentResponse])
def get_my_doctor_appointments(
    db: Session = Depends(get_db),
    current_user = Depends(require_doctor)
):
    doctor = crud.get_doctor_by_user_id(db, current_user.id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    appointments = crud.get_doctor_appointments(db, doctor.id)
    return appointments


@router.put("/appointments/{appointment_id}/status")
def update_status(
    appointment_id: int,
    status_update: schemas.AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_doctor)
):
    doctor = crud.get_doctor_by_user_id(db, current_user.id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    appointment = crud.get_appointment_by_id(db, appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="You can only update your own appointments")

    updated = crud.update_appointment_status(db, appointment_id, status_update.status)

    # Invalidate cache
    invalidate_cache("appointments:*")

    return {
        "message": "Appointment status updated successfully",
        "appointment_id": updated.id,
        "new_status": updated.status.value if hasattr(updated.status, "value") else updated.status
    }

from datetime import date
from app.services.booking_service import get_available_slots


@router.get("/all", response_model=List[schemas.DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db)):
    cache_key = "doctors:all"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    doctors = crud.get_all_doctors(db)
    # Serialize the data before caching
    encoded_doctors = jsonable_encoder(doctors)
    set_cache(cache_key, encoded_doctors, expire_seconds=3600)
    
    return encoded_doctors


@router.get("/by-department/{department_name}", response_model=List[schemas.DoctorResponse])
def get_doctors_by_department(
    department_name: str,
    db: Session = Depends(get_db)
):
    cache_key = f"doctors:dept:{department_name}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    doctors = crud.get_doctors_by_department(db, department_name)
    encoded_doctors = jsonable_encoder(doctors)
    set_cache(cache_key, encoded_doctors, expire_seconds=3600)
    
    return encoded_doctors


@router.get("/{doctor_id}/available-slots")
def get_available_slots_for_doctor(
    doctor_id: int,
    target_date: date,
    db: Session = Depends(get_db)
):
    doctor = crud.get_doctor_by_id(db, doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    slots = get_available_slots(db, doctor, target_date)

    return {
        "doctor_id": doctor_id,
        "date": target_date,
        "available_slots": slots
    }