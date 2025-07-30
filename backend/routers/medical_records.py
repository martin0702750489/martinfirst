from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import MedicalRecord, Patient, Doctor, User, UserRole
from schemas import MedicalRecordCreate, MedicalRecord as MedicalRecordSchema, MedicalRecordUpdate
from auth import get_current_user

router = APIRouter()

def generate_record_id() -> str:
    return f"MR-{str(uuid.uuid4())[:8].upper()}"

@router.post("/", response_model=MedicalRecordSchema)
def create_medical_record(
    record: MedicalRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only doctors can create medical records
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only doctors can create medical records")
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == record.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # If user is a doctor, they can only create records for themselves
    if current_user.role == UserRole.DOCTOR:
        current_doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not current_doctor or current_doctor.id != record.doctor_id:
            raise HTTPException(status_code=403, detail="Doctors can only create their own medical records")
    
    # Create medical record
    db_record = MedicalRecord(
        record_id=generate_record_id(),
        patient_id=record.patient_id,
        doctor_id=record.doctor_id,
        appointment_id=record.appointment_id,
        visit_date=record.visit_date,
        chief_complaint=record.chief_complaint,
        diagnosis=record.diagnosis,
        treatment=record.treatment,
        prescription=record.prescription,
        vital_signs=record.vital_signs,
        lab_results=record.lab_results,
        follow_up_date=record.follow_up_date,
        notes=record.notes
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record

@router.get("/", response_model=List[MedicalRecordSchema])
def get_medical_records(
    skip: int = 0,
    limit: int = 100,
    patient_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(MedicalRecord)
    
    # Filter based on user role
    if current_user.role == UserRole.PATIENT:
        # Patients can only see their own records
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(MedicalRecord.patient_id == patient.id)
        else:
            return []
    elif current_user.role == UserRole.DOCTOR:
        # Doctors can see records they created or for their patients
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            query = query.filter(MedicalRecord.doctor_id == doctor.id)
        else:
            return []
    
    # Apply patient filter if provided and user has permission
    if patient_id and current_user.role in [UserRole.ADMIN, UserRole.DOCTOR]:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    
    records = query.order_by(MedicalRecord.visit_date.desc()).offset(skip).limit(limit).all()
    return records

@router.get("/{record_id}", response_model=MedicalRecordSchema)
def get_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or record.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or record.doctor_id != doctor.id:
            # Allow access if doctor is treating the same patient
            patient_records = db.query(MedicalRecord).filter(
                MedicalRecord.patient_id == record.patient_id,
                MedicalRecord.doctor_id == doctor.id
            ).first()
            if not patient_records:
                raise HTTPException(status_code=403, detail="Access denied")
    
    return record

@router.put("/{record_id}", response_model=MedicalRecordSchema)
def update_medical_record(
    record_id: int,
    record_update: MedicalRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    # Only doctors who created the record or admins can update it
    can_update = False
    if current_user.role == UserRole.ADMIN:
        can_update = True
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor and record.doctor_id == doctor.id:
            can_update = True
    
    if not can_update:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    for field, value in record_update.dict(exclude_unset=True).items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    return record

@router.delete("/{record_id}")
def delete_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only admins can delete medical records
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can delete medical records")
    
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    db.delete(record)
    db.commit()
    
    return {"message": "Medical record deleted successfully"}

@router.get("/patient/{patient_id}/history", response_model=List[MedicalRecordSchema])
def get_patient_medical_history(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        if current_user.id != patient.user_id:
            raise HTTPException(status_code=403, detail="Patients can only view their own medical history")
    
    # Get all medical records for the patient
    records = db.query(MedicalRecord).filter(
        MedicalRecord.patient_id == patient_id
    ).order_by(MedicalRecord.visit_date.desc()).all()
    
    return records

@router.get("/by-record-id/{record_id}", response_model=MedicalRecordSchema)
def get_medical_record_by_record_id(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(MedicalRecord).filter(MedicalRecord.record_id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    # Check permissions (same as get_medical_record)
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or record.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or record.doctor_id != doctor.id:
            # Allow access if doctor is treating the same patient
            patient_records = db.query(MedicalRecord).filter(
                MedicalRecord.patient_id == record.patient_id,
                MedicalRecord.doctor_id == doctor.id
            ).first()
            if not patient_records:
                raise HTTPException(status_code=403, detail="Access denied")
    
    return record