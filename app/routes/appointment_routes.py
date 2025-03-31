from fastapi import APIRouter, Depends, Request,Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime

from .. import models, schemas
from ..database import SessionLocal, engine
from ..data.services import services_by_specizalization

models.Base.metadata.create_all(bind=engine)
router = APIRouter()
templates = Jinja2Templates(directory="app.templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/register/appointment", response_class=HTMLResponse)
def register_appointent_form(request: Request, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    doctors =  db.query(models.Doctor).all()
    return templates.TemplateResponse("register_appointment.html", {
        "request":request,
        "patients":patients,
        "doctors":doctor
        "services_by_specizalization":services_by_specizalization
    })

@router.post("/register.appointment", response_class=HTMLResponse)
def register_appointment()