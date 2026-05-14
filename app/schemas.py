from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


# =========================
# AUTH SCHEMAS
# =========================

class UserLogin(BaseModel):
    username: str
    password: str


# =========================
# PATIENT SCHEMAS
# =========================

class PatientRegister(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    age: int
    phone: str
    address: str
    gender: str
    department: str
    email: Optional[EmailStr] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, value):
        if value <= 0:
            raise ValueError("Age must be greater than 0")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if not re.fullmatch(r"^01[0125][0-9]{8}$", value):
            raise ValueError("Phone number must be a valid Egyptian phone number with 11 digits")
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):
        allowed = ["male", "female"]
        if value.lower() not in allowed:
            raise ValueError("Gender must be either 'male' or 'female'")
        return value.lower()


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None


class PatientResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    age: int
    phone: str
    address: str
    gender: str
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


# =========================
# DOCTOR SCHEMAS
# =========================

class DoctorCreate(BaseModel):
    username: str
    password: str
    full_name: str
    specialty: str
    department: str
    email: Optional[EmailStr] = None
    availability_status: Optional[str] = "available"
    work_start_hour: Optional[int] = 8
    work_end_hour: Optional[int] = 12

    @field_validator("work_start_hour", "work_end_hour")
    @classmethod
    def validate_work_hours(cls, value):
        if value < 0 or value > 23:
            raise ValueError("Work hours must be between 0 and 23")
        return value


class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None
    availability_status: Optional[str] = None
    work_start_hour: Optional[int] = None
    work_end_hour: Optional[int] = None


class DoctorResponse(BaseModel):
    id: int
    full_name: str
    specialty: str
    availability_status: str
    work_start_hour: int
    work_end_hour: int

    class Config:
        from_attributes = True


# =========================
# APPOINTMENT SCHEMAS
# =========================

class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: datetime
    notes: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        allowed = ["Scheduled", "Completed", "Cancelled"]
        if value not in allowed:
            raise ValueError("Status must be Scheduled, Completed, or Cancelled")
        return value


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True