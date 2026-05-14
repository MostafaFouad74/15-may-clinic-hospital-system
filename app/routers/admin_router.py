from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from typing import List
from app.database import get_db
from app import schemas, crud
from app.auth import require_admin
from fastapi.encoders import jsonable_encoder
from app.core.redis_client import get_cache, set_cache, invalidate_cache

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/create-doctor")
def create_doctor(
    doctor: schemas.DoctorCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    existing_user = crud.get_user_by_username(db, doctor.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    created_doctor = crud.create_doctor(db, doctor)

    invalidate_cache("doctors:*")

    return {
        "message": "Doctor created successfully",
        "doctor_id": created_doctor.id,
        "doctor_name": created_doctor.full_name,
    }


@router.get("/appointments", response_model=List[schemas.AppointmentResponse])
def get_all_appointments(
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    cache_key = "appointments:all"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    appointments = crud.get_all_appointments(db)
    encoded = jsonable_encoder(appointments)

    set_cache(cache_key, encoded, expire_seconds=600)
    return encoded


@router.delete("/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    deleted = crud.delete_appointment(db, appointment_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Appointment not found")

    invalidate_cache("appointments:*")

    return {"message": "Appointment deleted successfully"}


@router.get("/patients", response_model=List[schemas.PatientResponse])
def get_all_patients(
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    cache_key = "patients:all"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    patients = crud.get_all_patients(db)

    encoded = []
    for patient in patients:
        patient_data = jsonable_encoder(patient)
        patient_data["username"] = patient.user.username
        encoded.append(patient_data)

    set_cache(cache_key, encoded, expire_seconds=3600)
    return encoded


@router.get("/patients/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    cache_key = f"patient:{patient_id}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    patient = crud.get_patient_by_id(db, patient_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    encoded = jsonable_encoder(patient)
    encoded["username"] = patient.user.username

    set_cache(cache_key, encoded, expire_seconds=3600)
    return encoded


@router.put("/patients/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    updated_patient = crud.update_patient(db, patient_id, patient_update)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    encoded = jsonable_encoder(updated_patient)
    encoded["username"] = updated_patient.user.username

    invalidate_cache("patients:*")
    invalidate_cache(f"patient:{patient_id}")
    return encoded


@router.delete("/patients/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    deleted_patient = crud.delete_patient(db, patient_id)
    if not deleted_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    invalidate_cache("patients:*")
    invalidate_cache(f"patient:{patient_id}")
    return {"message": "Patient deleted successfully"}


@router.get("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    cache_key = f"doctor:{doctor_id}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    doctor = crud.get_doctor_by_id_full(db, doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    encoded = jsonable_encoder(doctor)
    set_cache(cache_key, encoded, expire_seconds=3600)
    return encoded


@router.put("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor_update: schemas.DoctorUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    updated_doctor = crud.update_doctor(db, doctor_id, doctor_update)
    if not updated_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    invalidate_cache("doctors:*")
    invalidate_cache(f"doctor:{doctor_id}")
    return updated_doctor


@router.delete("/doctors/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    deleted_doctor = crud.delete_doctor(db, doctor_id)
    if not deleted_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    invalidate_cache("doctors:*")
    invalidate_cache(f"doctor:{doctor_id}")
    return {"message": "Doctor deleted successfully"}