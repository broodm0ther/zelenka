from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime

from .. import models, schemas
from ..database import SessionLocal, engine

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/archives", response_class=HTMLResponse)
def archive_page(request: Request, patient_id: int = None, sort: str = "desc", db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    today = datetime.now().date()
    
    if patient_id is None or patient_id == 0:
        query = db.query(models.Appointment).filter(
            models.Appointment.appointment_day < today
        )
    else:
        query = db.query(models.Appointment).filter(
            models.Appointment.patient_id == patient_id,
            models.Appointment.appointment_day < today
        )

    if sort == "asc":
        query = query.order_by(models.Appointment.appointment_day.asc())
    else:
        query = query.order_by(models.Appointment.appointment_day.desc())
    
    appointments = query.all()

    return templates.TemplateResponse("archives.html", {
        "request": request,
        "patients": patients,
        "appointments": appointments,
        "selected_patient_id": patient_id,
        "sort": sort
    })