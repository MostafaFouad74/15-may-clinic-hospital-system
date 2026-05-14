import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.auth import hash_password
from app import models

# Use a file-based SQLite database for testing to avoid thread locks
import os
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Remove the file if it exists
if os.path.exists("./test.db"):
    os.remove("./test.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed an admin user for testing
    admin_user = models.User(
        username="admin_test",
        email="admin@test.com",
        hashed_password=hash_password("adminpass"),
        role=models.UserRole.admin
    )
    db.add(admin_user)
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client):
    response = client.post(
        "/login",
        data={"username": "admin_test", "password": "adminpass"}
    )
    return response.json()["access_token"]
