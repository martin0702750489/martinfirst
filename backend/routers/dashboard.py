from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, timedelta

from database import get_db
from models import Patient, Doctor, Appointment, MedicalRecord, User, UserRole, AppointmentStatus
from schemas import DashboardStats
from auth import get_current_user

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Basic counts
    total_patients = db.query(Patient).count()
    total_doctors = db.query(Doctor).count()
    total_appointments = db.query(Appointment).count()
    
    # Today's appointments
    today = date.today()
    appointments_today = db.query(Appointment).filter(
        Appointment.appointment_date == today
    ).count()
    
    # Pending appointments
    pending_appointments = db.query(Appointment).filter(
        Appointment.status == AppointmentStatus.SCHEDULED
    ).count()
    
    # Completed appointments
    completed_appointments = db.query(Appointment).filter(
        Appointment.status == AppointmentStatus.COMPLETED
    ).count()
    
    # Recent appointments (last 7 days)
    week_ago = today - timedelta(days=7)
    recent_appointments = db.query(Appointment).filter(
        Appointment.appointment_date >= week_ago
    ).order_by(Appointment.created_at.desc()).limit(10).all()
    
    # Recent patients (last 30 days)
    month_ago = today - timedelta(days=30)
    recent_patients = db.query(Patient).filter(
        Patient.created_at >= month_ago
    ).order_by(Patient.created_at.desc()).limit(10).all()
    
    return DashboardStats(
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        appointments_today=appointments_today,
        pending_appointments=pending_appointments,
        completed_appointments=completed_appointments,
        recent_appointments=recent_appointments,
        recent_patients=recent_patients
    )

@router.get("/appointments/by-status")
def get_appointments_by_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get appointment counts by status
    status_counts = db.query(
        Appointment.status,
        func.count(Appointment.id).label('count')
    ).group_by(Appointment.status).all()
    
    return [{"status": status.value, "count": count} for status, count in status_counts]

@router.get("/appointments/by-date")
def get_appointments_by_date(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get appointment counts by date for the last N days
    start_date = date.today() - timedelta(days=days)
    
    appointments_by_date = db.query(
        Appointment.appointment_date,
        func.count(Appointment.id).label('count')
    ).filter(
        Appointment.appointment_date >= start_date
    ).group_by(Appointment.appointment_date).order_by(Appointment.appointment_date).all()
    
    return [{"date": apt_date, "count": count} for apt_date, count in appointments_by_date]

@router.get("/doctors/by-specialization")
def get_doctors_by_specialization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get doctor counts by specialization
    specialization_counts = db.query(
        Doctor.specialization,
        func.count(Doctor.id).label('count')
    ).group_by(Doctor.specialization).all()
    
    return [{"specialization": spec, "count": count} for spec, count in specialization_counts]

@router.get("/patients/by-age-group")
def get_patients_by_age_group(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Calculate age groups
    today = date.today()
    
    age_groups = [
        ("0-18", 0, 18),
        ("19-30", 19, 30),
        ("31-50", 31, 50),
        ("51-70", 51, 70),
        ("70+", 71, 150)
    ]
    
    results = []
    for group_name, min_age, max_age in age_groups:
        min_birth_date = today - timedelta(days=max_age * 365.25)
        max_birth_date = today - timedelta(days=min_age * 365.25)
        
        count = db.query(Patient).filter(
            and_(
                Patient.date_of_birth >= min_birth_date,
                Patient.date_of_birth <= max_birth_date
            )
        ).count()
        
        results.append({"age_group": group_name, "count": count})
    
    return results

@router.get("/medical-records/recent")
def get_recent_medical_records(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get recent medical records based on user role
    query = db.query(MedicalRecord)
    
    if current_user.role == UserRole.DOCTOR:
        # Doctors see only their own records
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            query = query.filter(MedicalRecord.doctor_id == doctor.id)
        else:
            return []
    elif current_user.role == UserRole.PATIENT:
        # Patients see only their own records
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(MedicalRecord.patient_id == patient.id)
        else:
            return []
    
    records = query.order_by(MedicalRecord.created_at.desc()).limit(limit).all()
    return records

@router.get("/my-dashboard")
def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard_data = {
        "user": {
            "id": current_user.id,
            "name": f"{current_user.first_name} {current_user.last_name}",
            "role": current_user.role.value,
            "email": current_user.email
        }
    }
    
    if current_user.role == UserRole.PATIENT:
        # Patient dashboard
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            # Upcoming appointments
            upcoming_appointments = db.query(Appointment).filter(
                Appointment.patient_id == patient.id,
                Appointment.appointment_date >= date.today(),
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(5).all()
            
            # Recent medical records
            recent_records = db.query(MedicalRecord).filter(
                MedicalRecord.patient_id == patient.id
            ).order_by(MedicalRecord.visit_date.desc()).limit(5).all()
            
            dashboard_data.update({
                "patient_info": patient,
                "upcoming_appointments": upcoming_appointments,
                "recent_medical_records": recent_records,
                "total_appointments": db.query(Appointment).filter(Appointment.patient_id == patient.id).count(),
                "total_medical_records": db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id).count()
            })
    
    elif current_user.role == UserRole.DOCTOR:
        # Doctor dashboard
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            # Today's appointments
            today_appointments = db.query(Appointment).filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == date.today()
            ).order_by(Appointment.appointment_time).all()
            
            # Upcoming appointments
            upcoming_appointments = db.query(Appointment).filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date > date.today(),
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(5).all()
            
            # Recent patients
            recent_patients = db.query(Patient).join(Appointment).filter(
                Appointment.doctor_id == doctor.id
            ).order_by(Appointment.created_at.desc()).limit(5).all()
            
            dashboard_data.update({
                "doctor_info": doctor,
                "today_appointments": today_appointments,
                "upcoming_appointments": upcoming_appointments,
                "recent_patients": recent_patients,
                "total_appointments": db.query(Appointment).filter(Appointment.doctor_id == doctor.id).count(),
                "total_patients": db.query(Appointment).filter(Appointment.doctor_id == doctor.id).distinct(Appointment.patient_id).count()
            })
    
    return dashboard_data

@router.get("/quick-stats")
def get_quick_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    
    return {
        "today_appointments": db.query(Appointment).filter(Appointment.appointment_date == today).count(),
        "pending_appointments": db.query(Appointment).filter(Appointment.status == AppointmentStatus.SCHEDULED).count(),
        "total_active_patients": db.query(Patient).join(User).filter(User.is_active == True).count(),
        "total_active_doctors": db.query(Doctor).join(User).filter(User.is_active == True).count(),
        "this_month_appointments": db.query(Appointment).filter(
            func.extract('month', Appointment.appointment_date) == today.month,
            func.extract('year', Appointment.appointment_date) == today.year
        ).count()
    }