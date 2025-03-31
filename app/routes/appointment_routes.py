from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime

from .. import models, schemas
from ..database import SessionLocal, engine
from ..data.services import services_by_specialization

models.Base.metadata.create_all(bind=engine)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/register/appointment", response_class=HTMLResponse)
def register_appointment_form(request: Request, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    doctors = db.query(models.Doctor).all()
    return templates.TemplateResponse("register_appointment.html", {
        "request": request,
        "patients": patients,
        "doctors": doctors,
        "services_by_specialization": services_by_specialization
    })

# app/routes/appointment_routes.py
@router.post("/register/appointment", response_class=HTMLResponse)
def register_appointment(
    request: Request,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    service: str = Form(...),
    appointment_day: str = Form(...),
    appointment_time: str = Form(...),
    db: Session = Depends(get_db)
):
    appointment_date = datetime.strptime(appointment_day, "%Y-%m-%d").date()

    db_appointment = models.Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        service=service,
        appointment_day=appointment_date,
        appointment_time=appointment_time
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return RedirectResponse(url="/", status_code=302)

@router.get("/api/appointments")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

@router.get("/search/appointments", response_class=HTMLResponse)
def search_appointments_page(request: Request):
    return templates.TemplateResponse("search_appointments.html", {
        "request": request,
        "appointments": [],
        "patient": None
    })

@router.post("/search/appointments", response_class=HTMLResponse)
def search_appointments(
    request: Request,
    full_name: str = Form(...),
    db: Session = Depends(get_db)
):

    name_parts = full_name.strip().split()
    if len(name_parts) < 2:
        return templates.TemplateResponse("search_appointments.html", {
            "request": request,
            "error": "Введите полное ФИО пациента (Фамилия Имя Отчество)",
            "appointments": [],
            "patient": None
        })

    patient = db.query(models.Patient).filter(
        models.Patient.last_name == name_parts[0],
        models.Patient.first_name == name_parts[1],
        models.Patient.patronymic == name_parts[2] if len(name_parts) > 2 else True
    ).first()

    if not patient:
        return templates.TemplateResponse("search_appointments.html", {
            "request": request,
            "error": "Пациент не найден",
            "appointments": [],
            "patient": None
        })

    appointments = db.query(models.Appointment).join(models.Doctor).filter(
        models.Appointment.patient_id == patient.id
    ).all()

    return templates.TemplateResponse("search_appointments.html", {
        "request": request,
        "appointments": appointments,
        "patient": patient
    })

@router.post("/update_status")
def update_status(
    appointment_id: int = Form(...),  # Теперь корректно принимаем ID
    status: str = Form(...),          # И принимаем статус услуги
    db: Session = Depends(get_db)
):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        return JSONResponse(content={"error": "Запись не найдена"}, status_code=404)

    appointment.status = status
    db.commit()

    return JSONResponse(content={"message": "Статус обновлён", "status": status})

@router.post("/appointments/{appointment_id}/cancel", response_class=JSONResponse)
def cancel_appointment(appointment_id: int, reason: str = Form(...), db: Session = Depends(get_db)):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        return JSONResponse(content={"error": "Запись не найдена"}, status_code=404)

    old_status = appointment.status
    appointment.status = "Отменено"
    history = models.AppointmentHistory(
        appointment_id=appointment.id,
        old_status=old_status,
        new_status="Отменено",
        reason=reason
    )
    db.add(history)
    db.commit()
    return JSONResponse(content={"message": "Запись отменена", "new_status": appointment.status})

@router.post("/appointments/{appointment_id}/reschedule", response_class=JSONResponse)
def reschedule_appointment(appointment_id: int, new_date: str = Form(...), new_time: str = Form(...), reason: str = Form(...), db: Session = Depends(get_db)):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        return JSONResponse(content={"error": "Запись не найдена"}, status_code=404)

    old_status = appointment.status
    try:
        new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
    except ValueError:
        return JSONResponse(content={"error": "Неверный формат даты"}, status_code=400)

    appointment.appointment_day = new_date_obj
    appointment.appointment_time = new_time
    appointment.status = "Перенесено"
    history = models.AppointmentHistory(
        appointment_id=appointment.id,
        old_status=old_status,
        new_status="Перенесено",
        reason=reason
    )
    db.add(history)
    db.commit()
    return JSONResponse(content={"message": "Запись перенесена", "new_status": appointment.status})

@router.get("/manage_appointments", response_class=HTMLResponse)
def manage_appointments(request: Request, patient_id: int = 0, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all() if patient_id != 0 else db.query(models.Appointment).all()
    return templates.TemplateResponse("manage_appointments.html", {
        "request": request,
        "patients": patients,
        "appointments": appointments,
        "selected_patient_id": patient_id
    })