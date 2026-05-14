from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from typing import List
from app.database import get_db
from app.auth import require_patient
from app import crud, schemas
from fastapi.encoders import jsonable_encoder
from app.core.redis_client import get_cache, set_cache, invalidate_cache

router = APIRouter(prefix="/patient", tags=["Patient"])


@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user = Depends(require_patient)
):
    cache_key = f"patient_profile:user:{current_user.id}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    patient = crud.get_patient_by_user_id(db, current_user.id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    profile_data = {
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
        "patient": {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "age": patient.age,
            "phone": patient.phone,
            "address": patient.address,
            "gender": patient.gender,
            "email": patient.email
        }
    }
    
    set_cache(cache_key, profile_data, expire_seconds=3600)
    return profile_data


@router.post("/appointments")
def book_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_patient)
):
    patient = crud.get_patient_by_user_id(db, current_user.id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    try:
        created_appointment = crud.create_appointment(db, patient.id, appointment)

        status_value = (
            created_appointment.status.value
            if hasattr(created_appointment.status, "value")
            else str(created_appointment.status)
        )
        
        # Invalidate appointments cache
        invalidate_cache("appointments:*")
        invalidate_cache(f"appointments:patient:{patient.id}")

        return {
            "message": "Appointment booked successfully",
            "appointment_id": created_appointment.id,
            "status": status_value
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Booking error: {str(e)}")


@router.get("/appointments/my", response_model=List[schemas.AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user = Depends(require_patient)
):
    patient = crud.get_patient_by_user_id(db, current_user.id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    cache_key = f"appointments:patient:{patient.id}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    appointments = crud.get_patient_appointments(db, patient.id)
    encoded = jsonable_encoder(appointments)
    set_cache(cache_key, encoded, expire_seconds=600)

    return encoded

@router.delete("/appointments/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_patient)
):
    patient = crud.get_patient_by_user_id(db, current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    appointment = crud.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.patient_id != patient.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own appointments")

    updated = crud.update_appointment_status(db, appointment_id, "Cancelled")
    
    # Invalidate cache
    invalidate_cache("appointments:*")
    invalidate_cache(f"appointments:patient:{patient.id}")

    return {
        "message": "Appointment cancelled successfully",
        "appointment_id": updated.id
    }