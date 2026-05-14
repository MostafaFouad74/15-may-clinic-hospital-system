from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app import schemas, crud
from app.auth import authenticate_user, create_access_token
from app.core.logger import logger

router = APIRouter(tags=["Authentication"])


@router.post("/register")
def register_patient(patient: schemas.PatientRegister, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_username(db, patient.username)
    if existing_user:
        logger.warning(f"Failed registration: Username '{patient.username}' already exists")
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    created_patient = crud.create_patient(db, patient)
    logger.info(f"User registered successfully: {patient.username} (Patient ID: {created_patient.id})")
    return {
        "message": "Patient registered successfully",
        "patient_id": created_patient.id
    }


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})

    logger.info(f"User logged in successfully: {user.username} (Role: {user.role.value})")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value
    }