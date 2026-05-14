# Hospital Appointment System

## Project Description
The Hospital Appointment System is a robust backend API designed to manage hospital operations. It provides role-based access for Admins, Doctors, and Patients, facilitating seamless appointment booking, doctor management, and user authentication. Built with FastAPI, the system utilizes a PostgreSQL-compatible ORM (via SQLAlchemy), Redis for high-performance caching, and Prometheus/Grafana for monitoring.

## Roles
The system strictly enforces Role-Based Access Control (RBAC):
- **Admin**: Can create new doctors, manage all patients, view all appointments across the hospital, and perform full CRUD operations on doctor and patient records.
- **Doctor**: Can view their own appointments, update the status of their appointments (e.g., Scheduled -> Completed), and manage their availability.
- **Patient**: Can view available doctors, book appointments, view their own appointment history, and cancel upcoming appointments.

## API Endpoints Overview
- **Auth**: `/login`, `/register`
- **Admin (`/admin`)**: `/create-doctor`, `/appointments`, `/doctors/{id}`, `/patients/{id}`, plus full `PUT`/`DELETE` operations.
- **Doctor (`/doctor`)**: `/appointments/me`, `/appointments/{id}/status`, `/{id}/available-slots`, `/all`.
- **Patient (`/patient`)**: `/me`, `/appointments`, `/appointments/my`, `/appointments/{id}` (DELETE).
- **Metrics**: `/metrics` (Prometheus Integration)

## Database Migrations
Currently, the application automatically initializes the database schema using SQLAlchemy's declarative base method:
```python
Base.metadata.create_all(bind=engine)
```
*Note: In future iterations, `alembic` should be introduced to manage schema migrations across versions.*

## Setup Instructions
1. Clone the repository.
2. Create a `.env` file in the root directory (refer to `app/core/config.py` for variables like `DATABASE_URL`, `SECRET_KEY`, `REDIS_HOST`).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server locally:
   ```bash
   uvicorn app.main:app --reload
   ```

## Docker Usage
The entire stack is containerized for seamless deployment.
To start the FastAPI app, Redis, Prometheus, and Grafana:
```bash
docker-compose up --build -d
```
- API: `http://localhost:8000`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

## Team Contributions
Team Contributions
1. Authentication & Security (youssef elbatal)

Responsible for:
User login/register
JWT authentication
Password hashing
Role-based authorization

Code/files:
app/auth.py
app/routers/auth_router.py
app/core/config.py

2. Database & CRUD Operations (Mostafa Fouad)

Responsible for:
Database connection
SQLAlchemy models
CRUD operations for doctors, patients, and appointments

Code/files:
app/database.py
app/models.py
app/schemas.py
app/crud.py

3. Appointment & Scheduling System (abdelrahman badawy)

Responsible for:
Appointment booking/canceling
Preventing double booking
Doctor schedule management
Appointment status updates

Code/files:
app/services/booking_service.py
app/services/slot_service.py
app/routers/patient_router.py
app/routers/doctor_router.py

4. Admin Features, Validation & Testing (mahmoud mohamed)

Responsible for:
Admin dashboard APIs
Managing doctors and patients
Input validation
API testing with Pytest

Code/files:
app/routers/admin_router.py
tests/

5. Frontend, Caching & Monitoring (yousef ragab)

Responsible for:
Frontend UI using HTML/CSS/JavaScript
Redis caching
Logging system
Prometheus/Grafana monitoring
Docker setup

Code/files:
app/templates/
app/static/
app/core/logger.py
app/core/redis_client.py
