from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import Patient, User, UserRole
from schemas import PatientCreate, Patient as PatientSchema, PatientUpdate
from auth import get_current_user, require_role, get_password_hash

router = APIRouter()

@router.post("/", response_model=PatientSchema)
def create_patient(
    patient: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == patient.user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(User).filter(User.username == patient.user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if patient ID already exists
    db_patient = db.query(Patient).filter(Patient.patient_id == patient.patient_id).first()
    if db_patient:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    
    # Create user first
    hashed_password = get_password_hash(patient.user.password)
    db_user = User(
        email=patient.user.email,
        username=patient.user.username,
        hashed_password=hashed_password,
        first_name=patient.user.first_name,
        last_name=patient.user.last_name,
        phone=patient.user.phone,
        role=UserRole.PATIENT
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create patient
    db_patient = Patient(
        user_id=db_user.id,
        patient_id=patient.patient_id,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        address=patient.address,
        emergency_contact_name=patient.emergency_contact_name,
        emergency_contact_phone=patient.emergency_contact_phone,
        blood_group=patient.blood_group,
        allergies=patient.allergies,
        medical_history=patient.medical_history,
        insurance_number=patient.insurance_number
    )
    
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient

@router.get("/", response_model=List[PatientSchema])
def get_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=PatientSchema)
def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Patients can only view their own data unless user is staff
    if (current_user.role == UserRole.PATIENT and 
        current_user.id != patient.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return patient

@router.get("/by-patient-id/{patient_id}", response_model=PatientSchema)
def get_patient_by_patient_id(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Patients can only view their own data unless user is staff
    if (current_user.role == UserRole.PATIENT and 
        current_user.id != patient.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return patient

@router.put("/{patient_id}", response_model=PatientSchema)
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Patients can only update their own data unless user is staff
    if (current_user.role == UserRole.PATIENT and 
        current_user.id != patient.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    for field, value in patient_update.dict(exclude_unset=True).items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Delete user as well
    user = db.query(User).filter(User.id == patient.user_id).first()
    
    db.delete(patient)
    if user:
        db.delete(user)
    db.commit()
    
    return {"message": "Patient deleted successfully"}

@router.get("/search/{query}", response_model=List[PatientSchema])
def search_patients(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Search by name, patient_id, or phone
    patients = db.query(Patient).join(User).filter(
        (User.first_name.ilike(f"%{query}%")) |
        (User.last_name.ilike(f"%{query}%")) |
        (Patient.patient_id.ilike(f"%{query}%")) |
        (User.phone.ilike(f"%{query}%"))
    ).limit(20).all()
    
    return patients