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
Developed manually with contributions strictly handled via Git branches. No automated commits.
