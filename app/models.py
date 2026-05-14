from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


# =========================
# ENUMS
# =========================

class UserRole(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class AppointmentStatus(str, enum.Enum):
    scheduled = "Scheduled"
    completed = "Completed"
    cancelled = "Cancelled"


# =========================
# USERS TABLE
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    patient = relationship("Patient", back_populates="user", uselist=False)
    doctor = relationship("Doctor", back_populates="user", uselist=False)


# =========================
# PATIENTS TABLE
# =========================

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    gender = Column(String(10), nullable=False)
    email = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)

    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")


# =========================
# DOCTORS TABLE
# =========================

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    full_name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    availability_status = Column(String(50), default="available")
    work_start_hour = Column(Integer, default=8)
    work_end_hour = Column(Integer, default=12)

    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")


# =========================
# APPOINTMENTS TABLE
# =========================

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.scheduled)
    notes = Column(String(255), nullable=True)

    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")