from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import hash_password


def seed_admin():
    db: Session = SessionLocal()

    existing_admin = db.query(User).filter(User.username == "admin1").first()

    if not existing_admin:
        admin_user = User(
            username="admin1",
            email="admin1@hospital.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.admin
        )
        db.add(admin_user)
        db.commit()
        print("Admin seeded successfully")
    else:
        print("Admin already exists")

    db.close()