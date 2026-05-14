from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Appointment, AppointmentStatus, Doctor
from app.services.slot_service import generate_time_slots_for_day


def is_within_doctor_working_hours(doctor: Doctor, appointment_datetime: datetime) -> bool:
    appointment_hour = appointment_datetime.hour
    appointment_minute = appointment_datetime.minute

    if appointment_hour < doctor.work_start_hour or appointment_hour >= doctor.work_end_hour:
        return False

    if appointment_minute not in [0, 15, 30, 45]:
        return False

    return True


def get_booked_slots(db: Session, doctor_id: int, target_date):
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)

    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_of_day,
            Appointment.appointment_date < end_of_day,
            Appointment.status != AppointmentStatus.cancelled
        )
        .all()
    )

    return [appt.appointment_date for appt in appointments]


def get_available_slots(db: Session, doctor: Doctor, target_date):
    all_slots = generate_time_slots_for_day(
        target_date=target_date,
        start_hour=doctor.work_start_hour,
        end_hour=doctor.work_end_hour,
        slot_minutes=15
    )

    booked_slots = get_booked_slots(db, doctor.id, target_date)

    available_slots = [slot for slot in all_slots if slot not in booked_slots]
    return available_slots


def is_slot_available(db: Session, doctor: Doctor, appointment_datetime: datetime) -> bool:
    available_slots = get_available_slots(db, doctor, appointment_datetime.date())
    return appointment_datetime in available_slots