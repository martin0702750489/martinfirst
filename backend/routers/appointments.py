from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
import uuid

from database import get_db
from models import Appointment, Patient, Doctor, User, UserRole, AppointmentStatus
from schemas import AppointmentCreate, Appointment as AppointmentSchema, AppointmentUpdate
from auth import get_current_user

router = APIRouter()

def generate_appointment_id() -> str:
    return f"APT-{str(uuid.uuid4())[:8].upper()}"

@router.post("/", response_model=AppointmentSchema)
def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check if patient can only book for themselves
    if (current_user.role == UserRole.PATIENT and 
        current_user.id != patient.user_id):
        raise HTTPException(status_code=403, detail="Patients can only book appointments for themselves")
    
    # Check for conflicting appointments
    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.appointment_time == appointment.appointment_time,
        Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
    ).first()
    
    if existing_appointment:
        raise HTTPException(status_code=400, detail="Doctor is not available at this time")
    
    # Create appointment
    db_appointment = Appointment(
        appointment_id=generate_appointment_id(),
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        duration_minutes=appointment.duration_minutes,
        reason=appointment.reason,
        notes=appointment.notes,
        status=AppointmentStatus.SCHEDULED
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment

@router.get("/", response_model=List[AppointmentSchema])
def get_appointments(
    skip: int = 0,
    limit: int = 100,
    status: AppointmentStatus = None,
    date_from: date = None,
    date_to: date = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Appointment)
    
    # Filter based on user role
    if current_user.role == UserRole.PATIENT:
        # Patients can only see their own appointments
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Appointment.patient_id == patient.id)
        else:
            return []
    elif current_user.role == UserRole.DOCTOR:
        # Doctors can only see their own appointments
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            query = query.filter(Appointment.doctor_id == doctor.id)
        else:
            return []
    
    # Apply filters
    if status:
        query = query.filter(Appointment.status == status)
    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)
    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)
    
    appointments = query.order_by(Appointment.appointment_date, Appointment.appointment_time).offset(skip).limit(limit).all()
    return appointments

@router.get("/{appointment_id}", response_model=AppointmentSchema)
def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or appointment.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return appointment

@router.put("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check permissions
    can_update = False
    if current_user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
        can_update = True
    elif current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient and appointment.patient_id == patient.id:
            can_update = True
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor and appointment.doctor_id == doctor.id:
            can_update = True
    
    if not can_update:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # If updating date/time, check for conflicts
    if appointment_update.appointment_date or appointment_update.appointment_time:
        new_date = appointment_update.appointment_date or appointment.appointment_date
        new_time = appointment_update.appointment_time or appointment.appointment_time
        
        existing_appointment = db.query(Appointment).filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == new_date,
            Appointment.appointment_time == new_time,
            Appointment.id != appointment_id,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
        ).first()
        
        if existing_appointment:
            raise HTTPException(status_code=400, detail="Doctor is not available at this time")
    
    # Update fields
    for field, value in appointment_update.dict(exclude_unset=True).items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    
    return appointment

@router.delete("/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check permissions
    can_cancel = False
    if current_user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
        can_cancel = True
    elif current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient and appointment.patient_id == patient.id:
            can_cancel = True
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor and appointment.doctor_id == doctor.id:
            can_cancel = True
    
    if not can_cancel:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update status to cancelled instead of deleting
    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}

@router.get("/doctor/{doctor_id}/availability")
def get_doctor_availability(
    doctor_id: int,
    date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get existing appointments for the date
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == date,
        Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
    ).all()
    
    booked_times = [apt.appointment_time for apt in appointments]
    
    return {
        "doctor_id": doctor_id,
        "date": date,
        "available_hours_start": doctor.available_hours_start,
        "available_hours_end": doctor.available_hours_end,
        "booked_times": booked_times,
        "available_days": doctor.available_days
    }

@router.get("/today/", response_model=List[AppointmentSchema])
def get_today_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    query = db.query(Appointment).filter(Appointment.appointment_date == today)
    
    # Filter based on user role
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Appointment.patient_id == patient.id)
        else:
            return []
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            query = query.filter(Appointment.doctor_id == doctor.id)
        else:
            return []
    
    appointments = query.order_by(Appointment.appointment_time).all()
    return appointments