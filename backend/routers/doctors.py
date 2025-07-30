from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Doctor, User, UserRole
from schemas import DoctorCreate, Doctor as DoctorSchema, DoctorUpdate
from auth import get_current_user, require_role, get_password_hash

router = APIRouter()

@router.post("/", response_model=DoctorSchema)
def create_doctor(
    doctor: DoctorCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == doctor.user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(User).filter(User.username == doctor.user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if doctor ID or license number already exists
    db_doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor.doctor_id).first()
    if db_doctor:
        raise HTTPException(status_code=400, detail="Doctor ID already exists")
    
    db_doctor = db.query(Doctor).filter(Doctor.license_number == doctor.license_number).first()
    if db_doctor:
        raise HTTPException(status_code=400, detail="License number already exists")
    
    # Create user first
    hashed_password = get_password_hash(doctor.user.password)
    db_user = User(
        email=doctor.user.email,
        username=doctor.user.username,
        hashed_password=hashed_password,
        first_name=doctor.user.first_name,
        last_name=doctor.user.last_name,
        phone=doctor.user.phone,
        role=UserRole.DOCTOR
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create doctor
    db_doctor = Doctor(
        user_id=db_user.id,
        doctor_id=doctor.doctor_id,
        specialization=doctor.specialization,
        qualification=doctor.qualification,
        experience_years=doctor.experience_years,
        license_number=doctor.license_number,
        consultation_fee=doctor.consultation_fee,
        available_days=doctor.available_days,
        available_hours_start=doctor.available_hours_start,
        available_hours_end=doctor.available_hours_end
    )
    
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    
    return db_doctor

@router.get("/", response_model=List[DoctorSchema])
def get_doctors(
    skip: int = 0,
    limit: int = 100,
    specialization: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Doctor)
    
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    
    doctors = query.offset(skip).limit(limit).all()
    return doctors

@router.get("/{doctor_id}", response_model=DoctorSchema)
def get_doctor(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return doctor

@router.get("/by-doctor-id/{doctor_id}", response_model=DoctorSchema)
def get_doctor_by_doctor_id(
    doctor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return doctor

@router.put("/{doctor_id}", response_model=DoctorSchema)
def update_doctor(
    doctor_id: int,
    doctor_update: DoctorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Doctors can only update their own data unless user is admin
    if (current_user.role == UserRole.DOCTOR and 
        current_user.id != doctor.user_id and
        current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    for field, value in doctor_update.dict(exclude_unset=True).items():
        setattr(doctor, field, value)
    
    db.commit()
    db.refresh(doctor)
    
    return doctor

@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Delete user as well
    user = db.query(User).filter(User.id == doctor.user_id).first()
    
    db.delete(doctor)
    if user:
        db.delete(user)
    db.commit()
    
    return {"message": "Doctor deleted successfully"}

@router.get("/search/{query}", response_model=List[DoctorSchema])
def search_doctors(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Search by name, doctor_id, specialization, or qualification
    doctors = db.query(Doctor).join(User).filter(
        (User.first_name.ilike(f"%{query}%")) |
        (User.last_name.ilike(f"%{query}%")) |
        (Doctor.doctor_id.ilike(f"%{query}%")) |
        (Doctor.specialization.ilike(f"%{query}%")) |
        (Doctor.qualification.ilike(f"%{query}%"))
    ).limit(20).all()
    
    return doctors

@router.get("/specializations/list")
def get_specializations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get unique specializations
    specializations = db.query(Doctor.specialization).distinct().all()
    return [spec[0] for spec in specializations if spec[0]]