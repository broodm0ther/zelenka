# app/routes/doctor_routes.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import SessionLocal, engine
from ..data.specializations import specializations
from ..data.cabinets import cabinets

models.Base.metadata.create_all(bind=engine)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# HTML-форма (получить для регистрации врача)
@router.get("/register/doctor", response_class=HTMLResponse)
def register_doctor_form(request: Request):
    # Возможные места работы
    workplaces = ["Адрес 1", "Адрес 2", "Адрес 3"]
    return templates.TemplateResponse("register_doctor.html", {
        "request": request,
        "workplaces": workplaces,
        "specializations": specializations,
        "cabinets": cabinets
    })

@router.post("/register/doctor", response_class=HTMLResponse)
def register_doctor(
    request: Request,
    last_name: str = Form(...),
    first_name: str = Form(...),
    patronymic: str = Form(...),
    cabinet: str = Form(...),
    specialization: str = Form(...),
    date_of_birth: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    workplace: str = Form(...),
    db: Session = Depends(get_db)
):
    # Создаём объект схемы (возраст вычисляется автоматически,
    # а дата рождения приводится к формату ДД.ММ.ГГГГ)
    doctor_data = schemas.DoctorCreate(
        last_name=last_name,
        first_name=first_name,
        patronymic=patronymic,
        cabinet=cabinet,
        specialization=specialization,
        date_of_birth=date_of_birth,
        phone=phone,
        email=email,
        workplace=workplace
    )
    db_doctor = models.Doctor(**doctor_data.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return RedirectResponse(url="/", status_code=302)

# API-эндпоинты для работы с врачами
@router.post("/api/doctors", response_model=schemas.DoctorCreate)
def create_doctor_api(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    db_doctor = models.Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@router.get("/api/doctors", response_model=list[schemas.DoctorCreate])
def read_doctors_api(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    doctors = db.query(models.Doctor).offset(skip).limit(limit).all()
    return doctors
