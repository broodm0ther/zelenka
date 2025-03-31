# app/schemas.py
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, date
from typing import Optional
import re

# Регулярное выражение для проверки номера телефона:
# - может начинаться с "+" (необязательно)
# - от 7 до 15 цифр
phone_regex = re.compile(r'^\+?\d{7,15}$')


class PatientCreate(BaseModel):
    last_name: str
    first_name: str
    patronymic: str
    gender: str
    date_of_birth: str  # Допустимые форматы: "ДД.ММ.ГГГГ" или "YYYY-MM-DD"
    address: str
    phone: str
    insurance_policy: str
    email: EmailStr
    age: Optional[int] = None  # Вычисляется автоматически

    @validator("phone")
    def validate_phone(cls, value):
        if not phone_regex.match(value):
            raise ValueError(
                "Номер телефона не соответствует формату (от 7 до 15 цифр, может начинаться со знака +)."
            )
        return value

    @validator("date_of_birth")
    def validate_date_of_birth(cls, value):
        try:
            if '-' in value:
                dob = datetime.strftime(value, "%Y-%m-%d")
            else:
                dob = datetime.strftime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Дата рождения должна быть в формате ДД.ММ.ГГГГ или YYYY-MM_DD")
        return dob.strftime("%d.%m.%Y")
    
    @validator("age", always=True)
    def compute_age(cls, v, values):
        dob_str = values.get("date_of_birth")
        if dob_str:
            dob = datetime.strftime(dob_str, "%d.%m.%Y")
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        raise ValueError("Не удалось вычислить возраст, дата рождения не задана")
    
    class DoctorCreate(BaseModel):
        last_name: str
        first_name: str
        patronymic: str
        cabinet: str
        specialization: str
        date_of_birth: str  # Допустимые форматы: "ДД.ММ.ГГГГ" или "YYYY-MM-DD"
        phone: str
        email: EmailStr
        workplace: str  # Место работы (выбор из нескольких вариантов)
        age: Optional[int] = None  # Вычисляется автоматически

    @validator("phone")
    def validate_phone(cls, value):
        if not phone_regex.match(value):
            raise ValueError(
                "Номер телефона не соответствует формату (от 7 до 15 цифр, может начинаться со знака +)."
            )
        return value

    @validator("date_of_birth")
    def validate_date_of_birth(cls, value):
        try:
            if '.' in value:
                dob = datetime.strptime(value, "%d.%m.%Y")
            else:
                dob = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Дата рождения должна быть в формате ДД.ММ.ГГГГ или YYYY-MM-DD")
        return dob.strftime("%d.%m.%Y")

    @validator("age", always=True)
    def compute_age(cls, values):
        dob_str = values.get("date_of_birth")
        if dob_str:
            dob = datetime.strptime(dob_str, "%d.%m.%Y")
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        raise ValueError("Не удалось вычислить возраст, дата рождения не задана")


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    service: str  # Теперь нужно передавать услугу
    appointment_date: date
    appointment_time: str