from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
from app.core.logger import logger
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import engine, Base
from app import models
from app.routers import auth_router, admin_router, patient_router, doctor_router
from app.seed import seed_admin

app = FastAPI(title="Hospital Appointment System")

Base.metadata.create_all(bind=engine)
seed_admin()

Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming Request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Duration: {process_time:.4f}s"
        )
        return response
    except Exception:
        process_time = time.time() - start_time
        logger.exception(
            f"Error: {request.method} {request.url.path} "
            f"- Duration: {process_time:.4f}s"
        )
        raise


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(patient_router.router)
app.include_router(doctor_router.router)


@app.get("/")
def root():
    return {"message": "Hospital System Running"}


@app.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request},
    )


@app.get("/register-page")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request},
    )


@app.get("/patient-dashboard-page")
def patient_dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patient_dashboard.html",
        context={"request": request},
    )


@app.get("/doctor-dashboard-page")
def doctor_dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="doctor_dashboard.html",
        context={"request": request},
    )


@app.get("/admin-dashboard-page")
def admin_dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={"request": request},
    )