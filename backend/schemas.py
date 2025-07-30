from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, date, time
from typing import Optional, List
from models import UserRole, AppointmentStatus

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Login(BaseModel):
    username: str
    password: str

# Patient schemas
class PatientBase(BaseModel):
    patient_id: str
    date_of_birth: date
    gender: str
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    insurance_number: Optional[str] = None

class PatientCreate(PatientBase):
    user: UserCreate

class PatientUpdate(BaseModel):
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    insurance_number: Optional[str] = None

class Patient(PatientBase):
    id: int
    user_id: int
    user: User
    created_at: datetime
    
    class Config:
        from_attributes = True

# Doctor schemas
class DoctorBase(BaseModel):
    doctor_id: str
    specialization: str
    qualification: str
    experience_years: Optional[int] = None
    license_number: str
    consultation_fee: Optional[float] = None
    available_days: Optional[str] = None
    available_hours_start: Optional[time] = None
    available_hours_end: Optional[time] = None

class DoctorCreate(DoctorBase):
    user: UserCreate

class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    available_days: Optional[str] = None
    available_hours_start: Optional[time] = None
    available_hours_end: Optional[time] = None

class Doctor(DoctorBase):
    id: int
    user_id: int
    user: User
    created_at: datetime
    
    class Config:
        from_attributes = True

# Appointment schemas
class AppointmentBase(BaseModel):
    appointment_date: date
    appointment_time: time
    duration_minutes: Optional[int] = 30
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    patient_id: int
    doctor_id: int

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    reason: Optional[str] = None
    notes: Optional[str] = None

class Appointment(AppointmentBase):
    id: int
    appointment_id: str
    patient_id: int
    doctor_id: int
    status: AppointmentStatus
    created_at: datetime
    patient: Patient
    doctor: Doctor
    
    class Config:
        from_attributes = True

# Medical Record schemas
class MedicalRecordBase(BaseModel):
    visit_date: datetime
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    prescription: Optional[str] = None
    vital_signs: Optional[str] = None
    lab_results: Optional[str] = None
    follow_up_date: Optional[date] = None
    notes: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None

class MedicalRecordUpdate(BaseModel):
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    prescription: Optional[str] = None
    vital_signs: Optional[str] = None
    lab_results: Optional[str] = None
    follow_up_date: Optional[date] = None
    notes: Optional[str] = None

class MedicalRecord(MedicalRecordBase):
    id: int
    record_id: str
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_patients: int
    total_doctors: int
    total_appointments: int
    appointments_today: int
    pending_appointments: int
    completed_appointments: int
    recent_appointments: List[Appointment]
    recent_patients: List[Patient]

# Department schemas
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    head_doctor_id: Optional[int] = None
    location: Optional[str] = None
    phone: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True