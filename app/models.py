from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, index=True)
    first_name = Column(String, index=True)
    patronymic = Column(String, index=True)
    gender = Column(String, index=True)
    date_of_birth = Column(String, index=True)  # хранится как справка
    address = Column(String, index=True)
    phone = Column(String, index=True)
    insurance_policy = Column(String, index=True)
    email = Column(String, index=True)

class Doctor(Base):
    __tablename__ = "doctors"    
    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, index=True)
    first_name = Column(String, index=True)
    patronymic = Column(String, index=True)
    cabinet = Column(String, index=True)
    specialization = Column(String, index=True)
    date_of_birth = Column(String, index=True)
    phone = Column(String, index=True)
    email = Column(String, index=True)

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    service = Column(String, index=True)
    date = Column(Date, index=True)
    status = Column(String, default="Ожидание")  # Возможные значения: "Ожидание", "Завершено", "Перенесено"

    patient = relationship("Patient")
    doctor = relationship("Doctor")
    history = relationship("AppointmentHistory", back_populates="appointment", cascade="all, delete-orphan")

class AppointmentHistory(Base):
    __tablename__ = "appointment_history"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    old_status = Column(String, index=True)
    new_status = Column(String, index=True)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="history")

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    medication_name = Column(String, index=True)
    dosage = Column(String, index=True)

    patient = relationship("Patient")
    appointment = relationship("Appointment")