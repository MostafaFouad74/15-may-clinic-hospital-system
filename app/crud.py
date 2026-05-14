from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models, schemas
from app.auth import hash_password
from app.services.booking_service import is_slot_available, is_within_doctor_working_hours
from app.core.logger import logger


# =========================
# CREATE PATIENT (REGISTER)
# =========================

def create_patient(db: Session, patient: schemas.PatientRegister):
    db_user = models.User(
        username=patient.username,
        email=patient.email,
        hashed_password=hash_password(patient.password),
        role=models.UserRole.patient
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_patient = models.Patient(
        user_id=db_user.id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        age=patient.age,
        phone=patient.phone,
        address=patient.address,
        gender=patient.gender,
        email=patient.email,
        department=patient.department
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    logger.info(f"Created patient record for user_id: {db_user.id}")
    return db_patient


# =========================
# GET USER BY USERNAME
# =========================

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_patients(db: Session):
    return db.query(models.Patient).all()

def update_patient(db: Session, patient_id: int, patient_update: schemas.PatientUpdate):
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        return None
    
    update_data = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
        
    db.commit()
    db.refresh(patient)
    logger.info(f"Updated patient record for patient_id: {patient_id}")
    return patient

def delete_patient(db: Session, patient_id: int):
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        return None
    
    # Also delete user
    user = db.query(models.User).filter(models.User.id == patient.user_id).first()
    if user:
        db.delete(user)
        
    db.delete(patient)
    db.commit()
    logger.info(f"Deleted patient record for patient_id: {patient_id}")
    return patient


# =========================
# CREATE DOCTOR (ADMIN ONLY)
# =========================

def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    db_user = models.User(
        username=doctor.username,
        email=doctor.email,
        hashed_password=hash_password(doctor.password),
        role=models.UserRole.doctor
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_doctor = models.Doctor(
        user_id=db_user.id,
        full_name=doctor.full_name,
        specialty=doctor.specialty,
        department=doctor.department,
        availability_status=doctor.availability_status,
        work_start_hour=doctor.work_start_hour,
        work_end_hour=doctor.work_end_hour
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)

    logger.info(f"Created doctor record for user_id: {db_user.id}")
    return db_doctor


# =========================
# GET ALL DOCTORS
# =========================

def get_all_doctors(db: Session):
    return db.query(models.Doctor).all()


def get_doctors_by_department(db: Session, department: str):
    return db.query(models.Doctor).filter(models.Doctor.department == department).all()

def update_doctor(db: Session, doctor_id: int, doctor_update: schemas.DoctorUpdate):
    doctor = get_doctor_by_id_full(db, doctor_id)
    if not doctor:
        return None
    
    update_data = doctor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doctor, key, value)
        
    db.commit()
    db.refresh(doctor)
    logger.info(f"Updated doctor record for doctor_id: {doctor_id}")
    return doctor

def delete_doctor(db: Session, doctor_id: int):
    doctor = get_doctor_by_id_full(db, doctor_id)
    if not doctor:
        return None
        
    user = db.query(models.User).filter(models.User.id == doctor.user_id).first()
    if user:
        db.delete(user)
        
    db.delete(doctor)
    db.commit()
    logger.info(f"Deleted doctor record for doctor_id: {doctor_id}")
    return doctor


def get_patient_by_user_id(db: Session, user_id: int):
    return db.query(models.Patient).filter(models.Patient.user_id == user_id).first()


def get_doctor_by_user_id(db: Session, user_id: int):
    return db.query(models.Doctor).filter(models.Doctor.user_id == user_id).first()


def get_doctor_by_id(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()


def create_appointment(db: Session, patient_id: int, appointment: schemas.AppointmentCreate):
    doctor = get_doctor_by_id(db, appointment.doctor_id)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not is_within_doctor_working_hours(doctor, appointment.appointment_date):
        raise HTTPException(status_code=400, detail="Appointment time is outside doctor's working hours or not on a 15-minute slot")

    if not is_slot_available(db, doctor, appointment.appointment_date):
        raise HTTPException(status_code=400, detail="This appointment slot is already booked")

    db_appointment = models.Appointment(
        doctor_id=appointment.doctor_id,
        patient_id=patient_id,
        appointment_date=appointment.appointment_date,
        status=models.AppointmentStatus.scheduled,
        notes=appointment.notes
    )

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    logger.info(f"Created appointment {db_appointment.id} for patient_id: {patient_id} with doctor_id: {appointment.doctor_id}")
    return db_appointment


def get_patient_appointments(db: Session, patient_id: int):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.patient_id == patient_id)
        .order_by(models.Appointment.appointment_date)
        .all()
    )


def get_doctor_appointments(db: Session, doctor_id: int):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.doctor_id == doctor_id)
        .order_by(models.Appointment.appointment_date)
        .all()
    )


def get_appointment_by_id(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()


def update_appointment_status(db: Session, appointment_id: int, new_status: str):
    appointment = get_appointment_by_id(db, appointment_id)

    if not appointment:
        return None

    current_status = appointment.status.value if hasattr(appointment.status, "value") else str(appointment.status)
    
    # State transition validation
    if current_status in ["Completed", "Cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot change status of a {current_status} appointment")
        
    if new_status not in ["Scheduled", "Completed", "Cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid appointment status")

    appointment.status = new_status
    db.commit()
    db.refresh(appointment)

    logger.info(f"Updated appointment {appointment_id} status to {new_status}")
    return appointment


def get_all_appointments(db: Session):
    return db.query(models.Appointment).all()


def delete_appointment(db: Session, appointment_id: int):
    appointment = get_appointment_by_id(db, appointment_id)

    if not appointment:
        return None

    db.delete(appointment)
    db.commit()
    logger.info(f"Deleted appointment {appointment_id}")
    return appointment


def get_patient_by_id(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()


def get_doctor_by_id_full(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()